"""
RAG Trainer — обучение BERT-based retriever для тактик Lean 4.

Воспроизводит подход из LeanNavigator:
  1. Генерация triplet (query, positive_tactic, negative_tactic) из traced данных
  2. Обучение BERT с triplet loss (contrastive learning)
  3. Построение FAISS L2 индекса из обученных embeddings
  4. Drop-in замена TacticRAG для BFS exploration

Оригинальный код: leannavigator/tactic_proximity.ipynb, utils/lean_rag_utils.py
Ключевые параметры из оригинала:
  - Модель: bert-base-uncased
  - Query max_length=256, tactic max_length=64
  - TripletLoss margin=1.0
  - Adam lr=1e-5
  - FAISS IndexFlatL2
"""

import json
import os
import random
import time
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field

import numpy as np

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from transformers import BertTokenizer, BertModel, AutoTokenizer, AutoModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    def tqdm(iterable, **kwargs):
        return iterable


# ============================================================================
# Triplet Dataset — воспроизводит TripletDataset из leannavigator
# ============================================================================

class TacticTripletDataset(Dataset):
    """
    Dataset из троек (query, positive_tactic, negative_tactic).
    
    query = theorem_code + ' # ' + state_before
    positive = шаблон тактики, которая реально была применена
    negative = случайный шаблон (hard negative из FAISS при наличии)
    
    Воспроизводит TripletDataset из leannavigator/utils/lean_rag_utils.py:50
    """

    def __init__(self, triplets: List[Tuple[str, str, str]], tokenizer,
                 query_max_length: int = 256, tactic_max_length: int = 64):
        self.triplets = triplets
        self.tokenizer = tokenizer
        self.query_max_length = query_max_length
        self.tactic_max_length = tactic_max_length

    def __len__(self):
        return len(self.triplets)

    def __getitem__(self, index):
        q, pos, neg = self.triplets[index]
        q_enc = self.tokenizer(q, padding='max_length', max_length=self.query_max_length,
                               truncation=True, return_tensors='pt')
        pos_enc = self.tokenizer(pos, padding='max_length', max_length=self.tactic_max_length,
                                 truncation=True, return_tensors='pt')
        neg_enc = self.tokenizer(neg, padding='max_length', max_length=self.tactic_max_length,
                                 truncation=True, return_tensors='pt')
        return q_enc, pos_enc, neg_enc


class TripletLoss(nn.Module):
    """
    Triplet Loss из leannavigator/utils/lean_rag_utils.py:65
    
    L = max(0, ||q - pos||₂ - ||q - neg||₂ + margin)
    """

    def __init__(self, margin: float = 1.0):
        super().__init__()
        self.margin = margin

    def forward(self, q_embed, pos_embed, neg_embed):
        dist_pos = torch.norm(q_embed - pos_embed, p=2, dim=1)
        dist_neg = torch.norm(q_embed - neg_embed, p=2, dim=1)
        loss = torch.mean(torch.relu(dist_pos - dist_neg + self.margin))
        return loss


# ============================================================================
# TripletDataGenerator — генерация обучающих троек из traced данных
# ============================================================================

class TripletDataGenerator:
    """
    Генерирует triplet training data из .ast.json + .lean файлов.
    
    Для каждой тактики в traced данных создаёт:
    - query: theorem_code + ' # ' + state_before 
    - positive: шаблон тактики (parse_lean_state_and_tactic)
    - negative: случайный шаблон из того же набора (или hard negative)
    
    Данные генерируются из того же трейсинга что и шаблоны тактик.
    """

    def __init__(self):
        self.triplets: List[Tuple[str, str, str]] = []
        self.all_templates: List[str] = []

    def generate_from_ast_dir(
        self,
        repo_dir: str,
        templates: Optional[Dict[str, int]] = None,
        max_files: int = 0,
        skip_packages: bool = True,
        min_template_freq: int = 2,
    ) -> List[Tuple[str, str, str]]:
        """
        Генерирует тройки из .ast.json файлов.
        
        Args:
            repo_dir: Путь к traced Mathlib4
            templates: Словарь {template: freq} (если None — строим на лету)
            max_files: Макс файлов (0 = все)
            skip_packages: Пропускать зависимости
            min_template_freq: Мин частота для negative sampling
            
        Returns:
            Список троек (query, positive_template, negative_template)
        """
        from re_rl.tasks.formal.lean_navigator.core import (
            TacticTemplateExtractor,
            parse_lean_state_and_tactic,
        )

        repo_path = Path(repo_dir)
        build_ir = repo_path / ".lake" / "build" / "ir"

        if not build_ir.exists():
            raise FileNotFoundError(f"Нет build/ir в {repo_dir}")

        # Если шаблоны не переданы, загрузим/сгенерируем
        if templates is None:
            extractor = TacticTemplateExtractor()
            extractor.extract_from_ast_dir(repo_dir)
            templates = extractor.templates

        # Фильтруем по частоте
        filtered_templates = {k: v for k, v in templates.items() if v >= min_template_freq}
        self.all_templates = list(filtered_templates.keys())

        if not self.all_templates:
            raise ValueError("Нет шаблонов с достаточной частотой")

        print(f"Шаблонов для negative sampling: {len(self.all_templates)}")

        # Собираем AST файлы
        ast_files = sorted(build_ir.rglob("*.ast.json"))
        if skip_packages:
            ast_files = [f for f in ast_files
                         if "packages" not in str(f.relative_to(build_ir))]

        if max_files > 0 and len(ast_files) > max_files:
            ast_files = random.sample(ast_files, max_files)

        self.triplets = []
        errors = 0

        iterator = tqdm(ast_files, desc="Генерация triplets") if TQDM_AVAILABLE else ast_files

        for ast_file in iterator:
            try:
                rel = ast_file.relative_to(build_ir)
                lean_rel = Path(str(rel).replace(".ast.json", ".lean"))
                lean_file = repo_path / lean_rel
                if not lean_file.exists():
                    continue

                source_bytes = lean_file.read_bytes()
                # Для theorem_code берём первые 200 символов файла как контекст
                # (авторы используют premise['code'] — формулировку теоремы)
                module_name = str(rel).replace(".ast.json", "").replace("/", ".")

                with open(ast_file) as f:
                    data = json.load(f)

                tactics = data.get("tactics", [])
                if not tactics:
                    continue

                # Для каждой тактики генерируем тройку
                for tac in tactics:
                    state_before = tac.get("stateBefore", "")
                    state_after = tac.get("stateAfter", "")

                    if state_before == "no goals" or "⊢" not in state_before:
                        continue

                    # Извлекаем текст тактики из исходника
                    pos_start = tac.get("pos", 0)
                    pos_end = tac.get("endPos", 0)
                    tactic_text = source_bytes[pos_start:pos_end].decode(
                        "utf-8", errors="replace"
                    ).strip()

                    if not tactic_text or len(tactic_text) > 500:
                        continue

                    # Парсим в шаблон
                    try:
                        template = parse_lean_state_and_tactic(state_before, tactic_text)
                    except Exception:
                        errors += 1
                        continue

                    if template not in filtered_templates:
                        continue

                    # Ищем ближайшую теорему/лемму для theorem_code
                    context_start = max(0, pos_start - 500)
                    context = source_bytes[context_start:pos_start].decode(
                        "utf-8", errors="replace"
                    )
                    # Берём последний def/theorem/lemma как theorem_code
                    thm_match = re.findall(
                        r'(?:theorem|lemma|def|instance)\s+[\w.\']+[^:]*:[^:=]*',
                        context
                    )
                    theorem_code = thm_match[-1].strip()[:200] if thm_match else module_name

                    # Query = theorem_code + ' # ' + state_before (как у авторов)
                    query = theorem_code + ' # ' + state_before

                    # Positive = шаблон тактики
                    positive = template

                    # Negative = случайный шаблон (простой random negative)
                    negative = random.choice(self.all_templates)
                    # Не берём тот же шаблон
                    attempts = 0
                    while negative == positive and attempts < 5:
                        negative = random.choice(self.all_templates)
                        attempts += 1

                    self.triplets.append((query, positive, negative))

            except Exception:
                errors += 1
                continue

        print(f"✓ Сгенерировано {len(self.triplets)} троек ({errors} ошибок)")
        return self.triplets

    def generate_hard_negatives(
        self,
        model,
        tokenizer,
        device: str = "cpu",
        top_k: int = 50,
        batch_size: int = 256,
    ) -> List[Tuple[str, str, str]]:
        """
        Перегенерирует negative примеры используя hard negative mining.
        
        Для каждого query находит ближайшие шаблоны в текущем embedding space
        и берёт ближайший неправильный как negative.
        
        Это даёт более информативные negative примеры для обучения.
        """
        if not self.triplets or not self.all_templates:
            raise ValueError("Сначала вызовите generate_from_ast_dir()")

        print("Mining hard negatives...")

        # Encode все шаблоны
        model.eval()
        all_embeddings = []

        for i in range(0, len(self.all_templates), batch_size):
            batch = self.all_templates[i:i + batch_size]
            with torch.no_grad():
                encoded = tokenizer(
                    batch, padding=True, truncation=True,
                    max_length=64, return_tensors='pt'
                ).to(device)
                outputs = model(**encoded)
                embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
                all_embeddings.append(embeddings)

        all_embeddings = np.vstack(all_embeddings).astype(np.float32)

        # Строим FAISS L2 индекс
        index = faiss.IndexFlatL2(all_embeddings.shape[1])
        index.add(all_embeddings)

        # Template → index mapping
        template_to_idx = {t: i for i, t in enumerate(self.all_templates)}

        # Для каждой тройки: ищем hard negative
        hard_triplets = []
        for query, positive, _ in tqdm(self.triplets, desc="Hard negatives"):
            # Encode query
            with torch.no_grad():
                q_enc = tokenizer(
                    query, padding=True, truncation=True,
                    max_length=256, return_tensors='pt'
                ).to(device)
                q_out = model(**q_enc)
                q_emb = q_out.last_hidden_state[:, 0, :].cpu().numpy().astype(np.float32)

            # Ищем ближайшие
            _, indices = index.search(q_emb, top_k)

            # Берём ближайший который != positive
            hard_neg = None
            pos_idx = template_to_idx.get(positive, -1)
            for idx in indices[0]:
                if idx != pos_idx and idx >= 0:
                    hard_neg = self.all_templates[idx]
                    break

            if hard_neg is None:
                hard_neg = random.choice(self.all_templates)

            hard_triplets.append((query, positive, hard_neg))

        self.triplets = hard_triplets
        print(f"✓ {len(hard_triplets)} hard negatives сгенерировано")
        return self.triplets

    def save(self, path: str):
        """Сохраняет тройки в JSON."""
        data = {
            "triplets": self.triplets,
            "all_templates": self.all_templates,
        }
        with open(path, 'w') as f:
            json.dump(data, f, ensure_ascii=False)
        print(f"✓ {len(self.triplets)} троек сохранено в {path}")

    def load(self, path: str):
        """Загружает тройки из JSON."""
        with open(path) as f:
            data = json.load(f)
        self.triplets = [tuple(t) for t in data["triplets"]]
        self.all_templates = data["all_templates"]
        print(f"✓ {len(self.triplets)} троек загружено из {path}")
        return self.triplets


# ============================================================================
# TacticBERTTrainer — обучение BERT retriever
# ============================================================================

class TacticBERTTrainer:
    """
    Обучает BERT модель с triplet loss для retrieval тактик.
    
    Воспроизводит подход из leannavigator/tactic_proximity.ipynb:
    - BERT encoder → [CLS] embedding
    - Triplet loss (margin=1.0)
    - Adam optimizer (lr=1e-5)
    - Единая модель для query и tactic (shared encoder)
    
    Авторы обучали на ~60K тактиках, получая loss ~0.047.
    """

    def __init__(
        self,
        model_name: str = "bert-base-uncased",
        margin: float = 1.0,
        lr: float = 1e-5,
        device: Optional[str] = None,
    ):
        if not TORCH_AVAILABLE:
            raise ImportError("pip install torch")
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("pip install transformers")

        self.model_name = model_name
        self.margin = margin
        self.lr = lr

        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        print(f"Инициализация {model_name} на {self.device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.loss_fn = TripletLoss(margin=margin)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)

        # Статистика
        self.train_losses: List[float] = []

    def train(
        self,
        triplets: List[Tuple[str, str, str]],
        num_epochs: int = 1,
        batch_size: int = 64,
        log_every: int = 100,
        save_every: int = 5000,
        save_dir: Optional[str] = None,
        query_max_length: int = 256,
        tactic_max_length: int = 64,
    ) -> float:
        """
        Обучает модель на тройках.
        
        Args:
            triplets: Список (query, positive, negative)
            num_epochs: Число эпох
            batch_size: Размер батча
            log_every: Логировать каждые N батчей
            save_every: Сохранять checkpoint каждые N батчей
            save_dir: Директория для checkpoint'ов
            query_max_length: Max tokens для query
            tactic_max_length: Max tokens для тактик
            
        Returns:
            Финальный loss
        """
        dataset = TacticTripletDataset(
            triplets, self.tokenizer,
            query_max_length=query_max_length,
            tactic_max_length=tactic_max_length,
        )
        dataloader = DataLoader(
            dataset, batch_size=batch_size, shuffle=True,
            num_workers=0, pin_memory=True,
        )

        if save_dir:
            Path(save_dir).mkdir(parents=True, exist_ok=True)

        self.model.train()
        total_loss = 0.0
        num_batches = 0
        global_step = 0

        print(f"Обучение: {len(triplets)} троек, {num_epochs} эпох, batch={batch_size}")
        print(f"  Шагов за эпоху: {len(dataloader)}")
        print(f"  Device: {self.device}")
        print()

        for epoch in range(num_epochs):
            epoch_loss = 0.0
            epoch_batches = 0
            t0 = time.time()

            for batch_idx, (q_batch, pos_batch, neg_batch) in enumerate(dataloader):
                # Перемещаем на device и убираем batch dimension от tokenizer
                q_ids = q_batch['input_ids'].squeeze(1).to(self.device)
                q_mask = q_batch['attention_mask'].squeeze(1).to(self.device)
                pos_ids = pos_batch['input_ids'].squeeze(1).to(self.device)
                pos_mask = pos_batch['attention_mask'].squeeze(1).to(self.device)
                neg_ids = neg_batch['input_ids'].squeeze(1).to(self.device)
                neg_mask = neg_batch['attention_mask'].squeeze(1).to(self.device)

                # Forward
                q_out = self.model(input_ids=q_ids, attention_mask=q_mask)
                pos_out = self.model(input_ids=pos_ids, attention_mask=pos_mask)
                neg_out = self.model(input_ids=neg_ids, attention_mask=neg_mask)

                # [CLS] token embeddings
                q_emb = q_out.last_hidden_state[:, 0, :]
                pos_emb = pos_out.last_hidden_state[:, 0, :]
                neg_emb = neg_out.last_hidden_state[:, 0, :]

                # Loss
                loss = self.loss_fn(q_emb, pos_emb, neg_emb)

                # Backward
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

                batch_loss = loss.item()
                total_loss += batch_loss
                epoch_loss += batch_loss
                num_batches += 1
                epoch_batches += 1
                global_step += 1

                self.train_losses.append(batch_loss)

                if (batch_idx + 1) % log_every == 0:
                    avg = epoch_loss / epoch_batches
                    elapsed = time.time() - t0
                    speed = epoch_batches / elapsed
                    print(f"  Epoch {epoch+1} [{batch_idx+1}/{len(dataloader)}] "
                          f"loss={batch_loss:.4f} avg={avg:.4f} "
                          f"speed={speed:.1f} batch/s")

                if save_dir and save_every > 0 and global_step % save_every == 0:
                    self._save_checkpoint(save_dir, global_step)

            epoch_avg = epoch_loss / max(epoch_batches, 1)
            elapsed = time.time() - t0
            print(f"  Epoch {epoch+1}/{num_epochs} done: "
                  f"avg_loss={epoch_avg:.4f}, time={elapsed:.1f}s")

        final_loss = total_loss / max(num_batches, 1)
        print(f"\n✓ Обучение завершено: final_avg_loss={final_loss:.4f}")
        return final_loss

    def _save_checkpoint(self, save_dir: str, step: int):
        """Сохраняет checkpoint."""
        path = Path(save_dir) / f"checkpoint_step{step}"
        path.mkdir(parents=True, exist_ok=True)
        self.model.save_pretrained(str(path))
        self.tokenizer.save_pretrained(str(path))
        # Сохраняем loss history
        with open(path / "train_losses.json", 'w') as f:
            json.dump(self.train_losses, f)
        print(f"  Checkpoint: {path}")

    def save(self, path: str):
        """Сохраняет финальную модель."""
        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)
        self.model.save_pretrained(str(save_path))
        self.tokenizer.save_pretrained(str(save_path))
        # Метаданные
        meta = {
            "model_name": self.model_name,
            "margin": self.margin,
            "lr": self.lr,
            "train_steps": len(self.train_losses),
            "final_loss": self.train_losses[-1] if self.train_losses else None,
        }
        with open(save_path / "training_meta.json", 'w') as f:
            json.dump(meta, f, indent=2)
        with open(save_path / "train_losses.json", 'w') as f:
            json.dump(self.train_losses, f)
        print(f"✓ Модель сохранена в {path}")

    def encode_texts(self, texts: List[str], max_length: int = 64,
                     batch_size: int = 256) -> np.ndarray:
        """Кодирует тексты в embeddings через обученную модель."""
        self.model.eval()
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            with torch.no_grad():
                encoded = self.tokenizer(
                    batch, padding=True, truncation=True,
                    max_length=max_length, return_tensors='pt'
                ).to(self.device)
                outputs = self.model(**encoded)
                embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
                all_embeddings.append(embeddings)

        return np.vstack(all_embeddings).astype(np.float32)


# ============================================================================
# TrainedTacticRAG — drop-in замена TacticRAG с обученным BERT
# ============================================================================

class TrainedTacticRAG:
    """
    FAISS-based retrieval тактик с обученным BERT.
    
    Drop-in замена TacticRAG из lean_navigator.py.
    Использует обученный BERT + FAISS IndexFlatL2 (как у авторов).
    
    Основное отличие от TacticRAG:
    - Обученный BERT вместо pretrained sentence-transformers
    - IndexFlatL2 вместо IndexFlatIP (L2 distance, не cosine)
    - Query format: theorem_code + ' # ' + state (идентично оригиналу)
    """

    def __init__(self, model_path: Optional[str] = None):
        if not TORCH_AVAILABLE:
            raise ImportError("pip install torch")
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("pip install transformers")
        if not FAISS_AVAILABLE:
            raise ImportError("pip install faiss-cpu")

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self.index = None
        self.templates: List[str] = []
        self.template_freq: Dict[str, int] = {}

        if model_path:
            self.load_model(model_path)

    def load_model(self, model_path: str):
        """Загружает обученную BERT модель."""
        print(f"Загрузка BERT из {model_path}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModel.from_pretrained(model_path).to(self.device)
        self.model.eval()
        print(f"  Device: {self.device}")

    def build_index(self, template_freq: Dict[str, int], min_freq: int = 2,
                    batch_size: int = 256):
        """Строит FAISS L2 индекс из шаблонов тактик."""
        if self.model is None:
            raise ValueError("Сначала загрузите модель: load_model()")

        self.template_freq = {k: v for k, v in template_freq.items() if v >= min_freq}
        self.templates = list(self.template_freq.keys())

        if not self.templates:
            raise ValueError("Нет шаблонов для индексации")

        print(f"Строим FAISS L2 index для {len(self.templates)} шаблонов...")

        # Encode все шаблоны через обученный BERT
        embeddings = self._encode_batch(self.templates, max_length=64,
                                        batch_size=batch_size)

        # FAISS IndexFlatL2 — как у авторов (не cosine!)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        print(f"✓ FAISS L2 index: {len(self.templates)} шаблонов, dim={dim}")

    def get_similar_templates(self, state: str, theorem_code: str = "",
                              num_returned: int = 200) -> List[Tuple[str, float]]:
        """
        Находит ближайшие шаблоны тактик для текущего состояния.
        
        Совместимо с TacticRAG API.
        """
        if self.index is None:
            raise ValueError("Сначала вызовите build_index()")

        # Query формат как у авторов: theorem_code + ' # ' + state
        query = (theorem_code + ' # ' + state) if theorem_code else state

        # Encode query
        query_emb = self._encode_batch([query], max_length=256)

        # Search
        distances, indices = self.index.search(
            query_emb, min(num_returned, len(self.templates))
        )

        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx >= 0:
                # Similarity из L2 distance (как у авторов)
                dist = float(distances[0][i])
                similarity = 1.0 / (1.0 + dist * dist / 1000.0)
                results.append((self.templates[idx], similarity))

        return sorted(results, key=lambda x: -x[1])

    def _encode_batch(self, texts: List[str], max_length: int = 64,
                      batch_size: int = 256) -> np.ndarray:
        """Кодирует тексты через BERT."""
        self.model.eval()
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            with torch.no_grad():
                encoded = self.tokenizer(
                    batch, padding=True, truncation=True,
                    max_length=max_length, return_tensors='pt'
                ).to(self.device)
                outputs = self.model(**encoded)
                embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
                all_embeddings.append(embeddings)

        return np.vstack(all_embeddings).astype(np.float32)

    def save(self, path: str):
        """Сохраняет индекс и метаданные."""
        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(save_path / "faiss_l2.index"))
        with open(save_path / "templates.json", 'w') as f:
            json.dump({
                "templates": self.templates,
                "freq": self.template_freq,
            }, f, ensure_ascii=False)
        print(f"✓ TrainedRAG сохранён в {path}")

    def load(self, path: str):
        """Загружает индекс и метаданные."""
        load_path = Path(path)
        self.index = faiss.read_index(str(load_path / "faiss_l2.index"))
        with open(load_path / "templates.json") as f:
            data = json.load(f)
        self.templates = data["templates"]
        self.template_freq = data["freq"]
        print(f"✓ TrainedRAG загружен из {path}: {len(self.templates)} шаблонов")


# ============================================================================
# Полный pipeline обучения
# ============================================================================

def train_tactic_rag(
    repo_dir: str,
    output_dir: str,
    templates_path: Optional[str] = None,
    triplets_path: Optional[str] = None,
    model_name: str = "bert-base-uncased",
    num_epochs: int = 1,
    batch_size: int = 64,
    lr: float = 1e-5,
    margin: float = 1.0,
    min_template_freq: int = 3,
    max_files: int = 0,
    hard_negative_rounds: int = 0,
    device: Optional[str] = None,
) -> str:
    """
    Полный pipeline обучения RAG retriever.
    
    1. Загружает/генерирует шаблоны тактик
    2. Генерирует triplet training data
    3. Обучает BERT с triplet loss
    4. Опционально: hard negative mining + переобучение
    5. Строит FAISS L2 индекс
    6. Сохраняет модель + индекс
    
    Args:
        repo_dir: Путь к traced Mathlib4
        output_dir: Директория для результатов
        templates_path: Путь к кэшированным шаблонам
        triplets_path: Путь к кэшированным тройкам
        model_name: Имя BERT модели
        num_epochs: Число эпох обучения
        batch_size: Размер батча
        lr: Learning rate
        margin: Margin для triplet loss
        min_template_freq: Мин частота шаблона
        max_files: Макс AST файлов (0=все)
        hard_negative_rounds: Раундов hard negative mining (0=без)
        device: cuda/cpu (auto если None)
        
    Returns:
        Путь к сохранённой модели
    """
    from re_rl.tasks.formal.lean_navigator.core import TacticTemplateExtractor

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    total_start = time.time()

    # === 1. Шаблоны тактик ===
    print("=" * 60)
    print("Шаг 1: Загрузка шаблонов тактик")
    print("=" * 60)

    extractor = TacticTemplateExtractor()
    if templates_path and Path(templates_path).exists():
        extractor.load(templates_path)
    else:
        extractor.extract_from_ast_dir(repo_dir)
        extractor.save(str(output_path / "tactic_templates.json"))

    print(f"  Всего шаблонов: {len(extractor.templates)}")

    # === 2. Triplet data ===
    print("\n" + "=" * 60)
    print("Шаг 2: Генерация training triplets")
    print("=" * 60)

    generator = TripletDataGenerator()
    triplets_file = output_path / "triplets.json"

    if triplets_path and Path(triplets_path).exists():
        generator.load(triplets_path)
    elif triplets_file.exists():
        generator.load(str(triplets_file))
    else:
        generator.generate_from_ast_dir(
            repo_dir,
            templates=extractor.templates,
            max_files=max_files,
            min_template_freq=min_template_freq,
        )
        generator.save(str(triplets_file))

    print(f"  Training triplets: {len(generator.triplets)}")

    # === 3. Обучение BERT ===
    print("\n" + "=" * 60)
    print("Шаг 3: Обучение BERT retriever")
    print("=" * 60)

    trainer = TacticBERTTrainer(
        model_name=model_name,
        margin=margin,
        lr=lr,
        device=device,
    )

    final_loss = trainer.train(
        generator.triplets,
        num_epochs=num_epochs,
        batch_size=batch_size,
        save_dir=str(output_path / "checkpoints"),
        save_every=5000,
    )

    # === 4. Hard negative mining (опционально) ===
    for round_idx in range(hard_negative_rounds):
        print(f"\n{'=' * 60}")
        print(f"Шаг 4.{round_idx+1}: Hard negative mining (round {round_idx+1})")
        print("=" * 60)

        generator.generate_hard_negatives(
            trainer.model, trainer.tokenizer,
            device=str(trainer.device),
        )

        final_loss = trainer.train(
            generator.triplets,
            num_epochs=1,
            batch_size=batch_size,
            save_dir=str(output_path / "checkpoints"),
        )

    # === 5. Сохранение модели ===
    model_path = str(output_path / "bert_rag_model")
    trainer.save(model_path)

    # === 6. Построение FAISS индекса ===
    print("\n" + "=" * 60)
    print("Шаг 5: Построение FAISS L2 индекса")
    print("=" * 60)

    rag = TrainedTacticRAG(model_path=model_path)
    rag.build_index(extractor.templates, min_freq=min_template_freq)
    rag.save(str(output_path / "trained_rag_index"))

    total_time = time.time() - total_start
    print(f"\n{'=' * 60}")
    print(f"✓ Обучение завершено за {total_time:.1f}с ({total_time/60:.1f} мин)")
    print(f"  Модель: {model_path}")
    print(f"  RAG index: {output_path / 'trained_rag_index'}")
    print(f"  Final loss: {final_loss:.4f}")
    print(f"{'=' * 60}")

    return model_path
