"""
LeanNavigator — воспроизведение статьи
"Generating Millions of Lean Theorems with Proofs by Exploring State Transition Graphs"

Ключевые компоненты:
1. TacticTemplateExtractor — извлечение шаблонов тактик из traced data (.ast.json)
2. TacticRAG — FAISS-based retrieval тактик по состоянию
3. LeanNavigatorExplorer — BFS исследование графа переходов через Pantograph

Данные: scripts/fast_trace.py → ~/.cache/re_rl/mathlib4-<version>/mathlib4/

Оригинальный код: leannavigator/utils/lean_rag_utils.py
Изменения:
  - Pantograph вместо Dojo (Lean4Repl) для интерактивного proving
  - sentence-transformers вместо кастомного BERT для embedding
  - Работает напрямую с .ast.json (без lean-dojo TracedRepo)
  - Чистый API без глобальных переменных
"""

import re
import os
import sys
import io
import time
import heapq
import random
import itertools
import json
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any, Set, Callable
from dataclasses import dataclass, field
from collections import defaultdict
from contextlib import contextmanager
from enum import Enum

import numpy as np

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    def tqdm(iterable, **kwargs):
        return iterable

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SBERT_AVAILABLE = True
except ImportError:
    SBERT_AVAILABLE = False

try:
    import nest_asyncio
    nest_asyncio.apply()
except (ImportError, ValueError):
    # ValueError: Ray workers используют uvloop, который nest_asyncio
    # не может патчить. Это нормально — в worker'ах вложенные event loops
    # не нужны (Pantograph создаёт свой loop).
    pass

try:
    from pantograph import Server
    from pantograph.server import TacticFailure, ServerError
    PANTOGRAPH_AVAILABLE = True
except ImportError:
    PANTOGRAPH_AVAILABLE = False


# ============================================================================
# Константы из LeanNavigator
# ============================================================================

MAX_STEPS = 100000          # авторы: 100000 (в статье 200000 для финального прогона)
MAX_TACTIC_FROM_TEMPLATE = 50
PENALTY_SEEN_TARGET_MULTIPLIER = 3
MAX_NUM_DOJO_ATTEMPT = 2    # авторы: retry run_tac до 2 раз
MAX_NUM_OUTPUT_PER_STATE = 50  # макс пар на одно состояние
MAX_DISTANCE = 8            # макс расстояние до ProofFinished
MAX_PROVEN_STATES = 1000    # авторы: макс ProofFinished для обхода

# Тактики Lean 4 (из leannavigator/utils/lean_math_utils.py)
LEAN_TACTICS = [
    "all_goals", "any_goals", "apply", "assumption", "assumption'", "cases",
    "change", "clear", "contradiction", "constructor", "dec_trivial", "exact",
    "existsi", "ext", "fapply", "have", "induction", "injection", "intro", "intros",
    "left", "let", "library_search", "match_target", "refine", "repeat", "replace",
    "revert", "rewrite", "rw", "rintro", "rintros", "rcases", "simp", "solve_by_elim",
    "split", "subst", "tactic.trace", "trivial", "use", "with_cases", "rfl", "refl",
    "simp_all", "specialize", "apply_instance", "norm_num", "norm_cast", "ring",
    "ring2", "linarith", "omega", "tauto", "by_contradiction", "by_cases",
    "trace_state", "work_on_goal", "swap", "rotate", "rename", "guard_expr_eq",
    "set_goals", "clear_except", "apply_with", "run_tac", "done", "unfold", "unfold1",
    "fail_if_success", "success_if_fail", "infer_type", "expr", "retrieve", "push_neg",
    "contrapose", "iterate", "try", "skip", "solve1", "abstract", "generalize",
    "guard_hyp", "guard_target", "guard_hyp_nums", "guard_tags", "guard_proof_term",
    "guard_expr_strict", "discharge", 'obtain', 'simpa', 'rwa', 'simp_rw', 'haveI',
    'by_contra', 'lift', 'letI', 'dsimp', 'split_ifs', 'ext1', 'convert', 'tfae_have',
    'funext', 'congr', 'filter_upwards', 'choose', 'field_simp', 'aesop', 'nth_rw',
    'conv_lhs', 'simp_arith', 'erw', 'delta', 'gcongr', 'positivity', 'right',
    'infer_instance', 'abel', 'nontriviality', 'push_cast', 'borelize', 'inhabit',
    'ring_nf', 'nlinarith', 'fin_cases', 'trans', 'measurability', 'exact_mod_cast',
    'rename_i', 'calc', 'decide', 'symm', 'exfalso', 'aesop_cat', 'subst_vars',
    'ac_rfl', 'continuity', 'tfae_finish', 'rotate_left', 'classical', 'fconstructor',
    'clear_value', 'conv_rhs', 'next', 'assumption_mod_cast', 'substs', 'exists',
    'mono', 'interval_cases', 'show', 'bitwise_assoc_tac', 'triv', 'mfld_set_tac',
    'beta_reduce', 'abel_nf', 'case', 'simp_wf', 'set', 'wlog', 'conv',
]

LEAN_KEYWORDS = [
    "abbrev", "axiom", "begin", "builtin", "by", "calc", "check", "coercion",
    "constant", "constructor", "def", "definition", "derive", "do", "else", "end",
    "example", "export", "extends", "extern", "if", "import", "inductive", "infix",
    "infixl", "infixr", "instance", "let", "macro", "match", "meta", "mutual",
    "namespace", "noncomputable", "notation", "opaque", "open", "partial", "postfix",
    "prefix", "prelude", "private", "protected", "public", "quotation", "reserve",
    "scoped", "section", "set_option", "structure", "suffices", "tactic", "theorem",
    "universe", "universes", "using", "variable", "variables", "where", "with", "without",
]

VARIABLE_PATTERN = r'[a-zA-Z_\'\u03b1-\u03c9][a-zA-Z_\'\u03b1-\u03c9\d₀-₉]*'


# ============================================================================
# Утилиты из lean_math_utils.py (порт)
# ============================================================================

def classify_lean_element(line: str):
    """Классифицирует элемент Lean-состояния."""
    VARIABLE_TYPES = ['ℝ']
    line = line.strip()
    if not line:
        return None, None, None

    parts = line.split(':', 1)
    if len(parts) != 2:
        return None, None, None

    name_part, type_info = parts[0].strip(), parts[1].strip()

    if type_info.startswith('Type'):
        return 'type', name_part.split(), type_info
    if type_info.startswith('Set'):
        return 'set', name_part.split(), type_info
    if type_info.startswith(('∀', '∃', '¬')):
        return 'hypothesis', name_part.split(), type_info
    if type_info in VARIABLE_TYPES:
        return 'variable', name_part.split(), type_info
    if '→' in type_info or 'fun' in type_info or ':=' in type_info:
        if '∀' in type_info or '∃' in type_info:
            return 'hypothesis', name_part.split(), type_info
        return 'function', name_part.split(), type_info
    if 'Prop' in type_info or '¬' in type_info or '∈' in type_info or '∉' in type_info:
        return 'hypothesis', name_part.split(), type_info

    names = name_part.split()
    return 'unknown', names, type_info


def classify_lean_elements(lean_state: str):
    """Классифицирует все элементы Lean-состояния."""
    category_of_name = {}
    type_info_of_name = {}
    lines = lean_state.strip().split('\n')
    for line in lines:
        category, names, type_info = classify_lean_element(line)
        if category is None or names is None:
            continue
        for name in names:
            category_of_name[name] = category
            type_info_of_name[name] = type_info

    names = list(category_of_name.keys())
    for name in names:
        if (category_of_name[name] == 'unknown'
                and type_info_of_name[name] in names
                and category_of_name[type_info_of_name[name]] == 'type'):
            category_of_name[name] = 'variable'

    return category_of_name, type_info_of_name


def is_variable_name(token: str) -> bool:
    return bool(re.match(VARIABLE_PATTERN, token))


def tokenize_lean_tactic(tactic: str) -> List[str]:
    """Токенизация Lean-тактики."""
    variable_pattern = VARIABLE_PATTERN
    operator_pattern = r'[:=<>∈∉≤≥+\-*/^∀∃¬⁻¹]+'
    punctuation_pattern = r'[,⟨⟩\[\](){}|]'
    comment_pattern = r'--.*'

    tactic = re.sub(comment_pattern, '', tactic)
    tokens = []
    while tactic:
        match = re.match(variable_pattern, tactic)
        if match:
            tokens.append(match.group())
            tactic = tactic[match.end():]
            continue
        match = re.match(operator_pattern, tactic)
        if match:
            tokens.append(match.group())
            tactic = tactic[match.end():]
            continue
        match = re.match(punctuation_pattern, tactic)
        if match:
            tokens.append(match.group())
            tactic = tactic[match.end():]
            continue
        tokens.append(tactic[0])
        tactic = tactic[1:]
    return tokens


def parse_lean_state_and_tactic(state_before: str, tactic: str) -> str:
    """Преобразует тактику в шаблон, заменяя переменные на {type}."""
    definition_dict, _ = classify_lean_elements(state_before)
    tactic_parts = tokenize_lean_tactic(tactic)
    if len(tactic_parts) == 1:
        return tactic

    command = None
    transformed_parts = []
    new_var_idx = 0
    while 'nvar' + str(new_var_idx) in tactic_parts:
        new_var_idx += 1
    for tp in tactic_parts:
        if tp in definition_dict:
            transformed_parts.append('{' + definition_dict[tp] + '}')
        else:
            if command is None and tp in LEAN_TACTICS:
                command = tp
            elif (tp != ' '
                  and command in ['intro', 'rintro', 'ext', 'ext1', 'cases', 'rcases',
                                  'by_contra', 'by_cases', 'funext', 'congr', 'gcongr']
                  and is_variable_name(tp)):
                if tp not in LEAN_TACTICS and tp not in LEAN_KEYWORDS:
                    transformed_parts.append('{nvar' + str(new_var_idx) + '}')
                    new_var_idx += 1
                    continue
            transformed_parts.append(tp)

    return ''.join(transformed_parts)


def generate_tactics_from_template(template: str, type_of_item: Dict[str, str],
                                   max_tactics: int = MAX_TACTIC_FROM_TEMPLATE) -> List[str]:
    """Генерирует конкретные тактики из шаблона, подставляя переменные."""
    items_of_type = {'unknown': [], 'variable': [], 'hypothesis': []}
    for item, type_ in type_of_item.items():
        if type_ in items_of_type:
            items_of_type[type_].append(item)

    # Replace {nvar*} with nvar*
    existing_new_var_indices = [x for x in range(32) if 'nvar' + str(x) in type_of_item]
    additional_new_var_idx = (max(existing_new_var_indices) + 1) if existing_new_var_indices else 0
    for new_var_idx in range(32):
        tmp = '{nvar' + str(new_var_idx) + '}'
        if tmp in template:
            template = template.replace(tmp, 'nvar' + str(additional_new_var_idx))
            additional_new_var_idx += 1

    parts = template.split('{')
    fixed_parts = [parts[0]]
    types = []
    for part in parts[1:]:
        if '}' not in part:
            fixed_parts[-1] += '{' + part
            continue
        typ, rest = part.split('}', 1)
        types.append(typ)
        fixed_parts.append(rest)

    if not types:
        return [template]

    replacement_lists = []
    for typ in types:
        if typ in items_of_type:
            replacement_lists.append(items_of_type[typ])
        else:
            return [template]  # unknown type in template

    # Важно: нельзя материализовывать весь product в list — для некоторых целей
    # это даёт взрыв RAM ещё до run_tac. Генерируем только ограниченный набор.
    for repl in replacement_lists:
        if not repl:
            return []

    def _build_sentence(combination) -> str:
        sentence = fixed_parts[0]
        for item, fixed_part in zip(combination, fixed_parts[1:]):
            sentence += item + fixed_part
        return sentence

    total_combinations = 1
    for repl in replacement_lists:
        total_combinations *= len(repl)
        if total_combinations > max_tactics:
            break

    sentences: List[str] = []
    if total_combinations <= max_tactics:
        for combination in itertools.product(*replacement_lists):
            sentences.append(_build_sentence(combination))
    else:
        # Рандомно выбираем уникальные комбинации без построения полного product.
        seen = set()
        max_attempts = max_tactics * 30
        for _ in range(max_attempts):
            combination = tuple(random.choice(repl) for repl in replacement_lists)
            if combination in seen:
                continue
            seen.add(combination)
            sentences.append(_build_sentence(combination))
            if len(sentences) >= max_tactics:
                break
        if not sentences:
            # Теоретический fallback (на случай экстремального совпадения выборок).
            combination = tuple(repl[0] for repl in replacement_lists)
            sentences.append(_build_sentence(combination))

    return sentences


def get_inverse_tactic(tac_template: str) -> Optional[str]:
    """Создаёт обратную тактику для rw."""
    if (not tac_template.startswith('rw')
            or '[' not in tac_template
            or '←' in tac_template
            or '[{' in tac_template):
        return None
    result = tac_template.replace('[', '[← ')
    if ',' in result:
        pos = result.find(',')
        result = result[0:pos] + ']'
    return result


# ============================================================================
# Структуры данных
# ============================================================================

class PriorityQueue:
    """Очередь с приоритетом (min-heap) — из LeanNavigator."""
    def __init__(self):
        self._queue = []
        self._index = 0

    def size(self):
        return len(self._queue)

    def push(self, item, priority):
        heapq.heappush(self._queue, (priority, self._index, item))
        self._index += 1

    def pop(self):
        if len(self._queue) == 0:
            return None
        return heapq.heappop(self._queue)[-1]


@dataclass
class TrainingPair:
    """Пара (state, tactic) для обучения — совместима с state_explorer.TrainingPair."""
    state: str
    tactic: str
    next_state: str
    distance_to_proof: int  # -1 если не на пути к доказательству
    theorem_name: str = ""
    theorem_statement: str = ""  # Исходная формулировка теоремы (goal_expr)


@dataclass
class NavigatorResult:
    """Результат исследования одной теоремы."""
    theorem_name: str
    state_dict: Dict  # граф переходов
    theorem_proven: bool
    pairs: List[TrainingPair]
    n_states: int
    n_steps: int
    elapsed: float
    # Верификация: независимый replay найденных доказательств
    verified: Optional[bool] = None          # None = не проверялось
    proof_tactics: Optional[List[str]] = None # кратчайший путь тактик
    n_proofs_found: int = 0                  # сколько путей к ProofFinished найдено
    n_proofs_verified: int = 0               # сколько из них прошли replay
    # Декомпозиция automation-тактик (--decompose-auto)
    n_decomposed: int = 0                    # сколько simp/aesop разложено в шаги


# ============================================================================
# TacticTemplateExtractor — извлечение шаблонов из traced_repo
# ============================================================================

class TacticTemplateExtractor:
    """
    Извлекает шаблоны тактик из TracedRepo.
    
    Для каждой тактики в каждой теореме:
      1. Берём state_before и tactic
      2. Заменяем переменные на {type} → получаем шаблон
      3. Считаем частоту каждого шаблона
    """

    def __init__(self):
        self.templates: Dict[str, int] = {}  # template -> frequency
        self.template_examples: Dict[str, List[str]] = {}  # template -> example tactics

    def extract_from_ast_dir(self, repo_dir: str, max_files: int = 0,
                              skip_packages: bool = True) -> Dict[str, int]:
        """
        Извлекает шаблоны тактик напрямую из .ast.json + .lean файлов.
        
        Не требует lean-dojo. Работает с данными из fast_trace.py.
        
        Args:
            repo_dir: Путь к Mathlib4 (например ~/.cache/re_rl/mathlib4-v4.26.0/mathlib4)
            max_files: Максимум файлов (0 = все)
            skip_packages: Пропускать .lake/packages (зависимости)
        """
        repo_dir = Path(repo_dir)
        build_ir = repo_dir / ".lake" / "build" / "ir"

        if not build_ir.exists():
            raise FileNotFoundError(
                f"Нет build/ir в {repo_dir}. Запустите: python scripts/fast_trace.py"
            )

        # Собираем .ast.json файлы
        ast_files = sorted(build_ir.rglob("*.ast.json"))
        if skip_packages:
            # Оставляем только Mathlib (не packages)
            ast_files = [f for f in ast_files
                         if "packages" not in str(f.relative_to(build_ir))]

        if max_files > 0 and len(ast_files) > max_files:
            ast_files = random.sample(ast_files, max_files)

        print(f"Извлекаем шаблоны тактик из {len(ast_files)} файлов...")
        total_tactics = 0
        errors = 0
        iterator = tqdm(ast_files, desc="Извлечение шаблонов") if TQDM_AVAILABLE else ast_files

        for ast_file in iterator:
            try:
                # Маппинг: build/ir/Mathlib/Foo.ast.json → Mathlib/Foo.lean
                rel = ast_file.relative_to(build_ir)
                # .ast.json — двойное расширение, нужно убрать оба
                lean_rel = Path(str(rel).replace(".ast.json", ".lean"))
                lean_file = repo_dir / lean_rel

                if not lean_file.exists():
                    continue

                # Lean использует байтовые позиции → читаем как bytes
                source_bytes = lean_file.read_bytes()

                with open(ast_file, "r") as f:
                    data = json.load(f)

                for tac in data.get("tactics", []):
                    state_before = tac.get("stateBefore", "")
                    if state_before == "no goals":
                        continue

                    pos = tac.get("pos", 0)
                    end_pos = tac.get("endPos", 0)
                    tactic_text = source_bytes[pos:end_pos].decode(
                        "utf-8", errors="replace"
                    ).strip()

                    if not tactic_text:
                        continue

                    total_tactics += 1
                    template = parse_lean_state_and_tactic(state_before, tactic_text)
                    self.templates[template] = self.templates.get(template, 0) + 1

                    if template not in self.template_examples:
                        self.template_examples[template] = []
                    if len(self.template_examples[template]) < 3:
                        self.template_examples[template].append(tactic_text)

            except Exception:
                errors += 1
                continue

        print(f"✓ Извлечено {len(self.templates)} уникальных шаблонов "
              f"из {total_tactics} тактик ({errors} ошибок)")
        return self.templates

    def extract_from_traced_repo(self, traced_repo, max_theorems: int = 0,
                                  skip_lake: bool = True) -> Dict[str, int]:
        """Извлекает шаблоны тактик из TracedRepo (legacy, требует lean-dojo)."""
        traced_theorems = list(traced_repo.get_traced_theorems())
        if skip_lake:
            traced_theorems = [t for t in traced_theorems
                               if '.lake/packages' not in str(t.file_path)]

        if max_theorems > 0 and len(traced_theorems) > max_theorems:
            traced_theorems = random.sample(traced_theorems, max_theorems)

        print(f"Извлекаем шаблоны тактик из {len(traced_theorems)} теорем...")

        for i, thm in enumerate(traced_theorems):
            if (i + 1) % 10000 == 0:
                print(f"  {i + 1}/{len(traced_theorems)} теорем обработано, "
                      f"{len(self.templates)} шаблонов")
            try:
                if not thm.has_tactic_proof():
                    continue
                tactics = thm.get_traced_tactics()
                for tac in tactics:
                    if tac.state_before == "no goals":
                        continue
                    template = parse_lean_state_and_tactic(tac.state_before, tac.tactic)
                    self.templates[template] = self.templates.get(template, 0) + 1
                    if template not in self.template_examples:
                        self.template_examples[template] = []
                    if len(self.template_examples[template]) < 3:
                        self.template_examples[template].append(tac.tactic)
            except Exception:
                continue

        print(f"✓ Извлечено {len(self.templates)} уникальных шаблонов тактик")
        return self.templates

    def save(self, path: str):
        """Сохраняет шаблоны в JSON."""
        data = {
            "templates": self.templates,
            "examples": self.template_examples,
        }
        with open(path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ Шаблоны сохранены в {path}")

    def load(self, path: str):
        """Загружает шаблоны из JSON."""
        with open(path) as f:
            data = json.load(f)
        self.templates = data["templates"]
        self.template_examples = data.get("examples", {})
        print(f"✓ Загружено {len(self.templates)} шаблонов из {path}")

    def get_top_templates(self, n: int = 50) -> List[Tuple[str, int]]:
        """Топ-N шаблонов по частоте."""
        return sorted(self.templates.items(), key=lambda x: -x[1])[:n]


# ============================================================================
# TacticRAG — FAISS-based retrieval тактик
# ============================================================================

class TacticRAG:
    """
    Retrieval-Augmented Generation тактик.
    
    Использует sentence-transformers + FAISS для поиска подходящих
    шаблонов тактик по текущему состоянию.
    
    Авторы LeanNavigator использовали BERT + contrastive learning.
    Мы используем sentence-transformers (предобученный) для простоты.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if not SBERT_AVAILABLE:
            raise ImportError("pip install sentence-transformers")
        if not FAISS_AVAILABLE:
            raise ImportError("pip install faiss-cpu")

        self.model = SentenceTransformer(model_name)
        self.index = None
        self.templates: List[str] = []
        self.template_freq: Dict[str, int] = {}

    def build_index(self, template_freq: Dict[str, int], min_freq: int = 2):
        """Строит FAISS index из шаблонов тактик."""
        # Фильтруем по частоте
        self.template_freq = {k: v for k, v in template_freq.items() if v >= min_freq}
        self.templates = list(self.template_freq.keys())

        if not self.templates:
            raise ValueError("Нет шаблонов для индексации")

        print(f"Строим FAISS index для {len(self.templates)} шаблонов...")
        embeddings = self.model.encode(self.templates, show_progress_bar=True,
                                        batch_size=256)
        embeddings = embeddings.astype(np.float32)

        # Нормализуем для cosine similarity
        faiss.normalize_L2(embeddings)

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # Inner Product = cosine после нормализации
        self.index.add(embeddings)

        print(f"✓ FAISS index построен: {len(self.templates)} шаблонов, dim={dim}")

    def get_similar_templates(self, state: str, theorem_code: str = "",
                               num_returned: int = 200) -> List[Tuple[str, float]]:
        """Находит наиболее похожие шаблоны тактик для состояния."""
        if self.index is None:
            raise ValueError("Сначала вызовите build_index()")

        query = (theorem_code + ' # ' + state) if theorem_code else state
        query_embedding = self.model.encode([query]).astype(np.float32)
        faiss.normalize_L2(query_embedding)

        distances, indices = self.index.search(query_embedding, min(num_returned, len(self.templates)))

        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx >= 0:
                results.append((self.templates[idx], float(distances[0][i])))
        return results

    def save(self, path: str):
        """Сохраняет индекс и данные."""
        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(save_path / "faiss.index"))
        with open(save_path / "templates.json", 'w') as f:
            json.dump({"templates": self.templates, "freq": self.template_freq}, f)
        print(f"✓ RAG сохранён в {path}")

    def load(self, path: str):
        """Загружает индекс и данные."""
        load_path = Path(path)
        self.index = faiss.read_index(str(load_path / "faiss.index"))
        with open(load_path / "templates.json") as f:
            data = json.load(f)
        self.templates = data["templates"]
        self.template_freq = data["freq"]
        print(f"✓ RAG загружен из {path}: {len(self.templates)} шаблонов")


# ============================================================================
# PantographDojo — обёртка над Pantograph, совместимая с API LeanNavigator
# ============================================================================

@dataclass
class ProofState:
    """Состояние доказательства (аналог TacticState из lean_dojo)."""
    pp: str  # pretty-printed state
    goal_state: Any = None  # pantograph GoalState
    goal_id: int = 0


class ProofFinished:
    """Маркер завершения доказательства."""
    pass


@contextmanager
def _suppress_pantograph_prints():
    """Подавляет 'Cannot start goal' print из pantograph/server.py."""
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        yield sys.stdout
    finally:
        sys.stdout = old_stdout


class PantographDojo:
    """
    Обёртка над Pantograph Server для интерактивного proving.
    
    Предоставляет API совместимый с LeanNavigator:
      - run_tac(state, tactic) -> ProofState | ProofFinished | None
    """

    def __init__(self, project_path: str, imports: Optional[List[str]] = None,
                 timeout: int = 120, pp_full: bool = True):
        """
        Args:
            project_path: Путь к проекту Lean 4
            imports: Список импортов (default: ["Init"])
            timeout: Таймаут в секундах
            pp_full: Полный pretty-print без обрезки (default: True, отключает ⋯)
        """
        if not PANTOGRAPH_AVAILABLE:
            raise ImportError("pip install 'git+https://github.com/stanford-centaur/PyPantograph.git'")

        self.project_path = project_path
        self.imports = imports or ["Init"]
        self.timeout = timeout
        self.pp_full = pp_full
        self.server = None

    def start(self):
        """Запускает Pantograph сервер."""
        # Lean options для pretty-printing
        options = {}
        if self.pp_full:
            # Увеличиваем лимиты чтобы избежать ⋯ в типах
            # НЕ включаем pp.proofs — proof terms могут быть гигантскими (десятки GB)
            options = {
                "pp.maxSteps": 50000,       # default ~5000, увеличиваем для длинных типов
                "pp.deepTerms": True,       # показывать глубокие термы в типах
                "pp.maxDepth": 100,         # default ~32, умеренное увеличение
            }
        
        self.server = Server(
            imports=self.imports,
            project_path=self.project_path,
            timeout=self.timeout,
            buffer_limit=10_000_000,  # 10MB — нужно для env_catalog на Mathlib
            options=options,
        )
        return self

    def stop(self):
        """Останавливает сервер и убивает процесс pantograph-repl."""
        if self.server:
            # Явно вызываем _close() для terminate процесса
            try:
                self.server._close()
            except Exception:
                pass
            # Дополнительно пробуем kill если proc ещё жив
            try:
                if self.server.proc:
                    self.server.proc.kill()
            except Exception:
                pass
            del self.server
            self.server = None

    def env_inspect(self, name: str) -> Optional[str]:
        """Получает полный тип теоремы по имени через env_inspect.
        
        Returns:
            Pretty-printed тип или None если не найдена.
        """
        try:
            info = self.server.env_inspect(name=name)
            if isinstance(info, dict):
                return info.get("type", {}).get("pp")
            return None
        except Exception:
            return None

    def env_inspect_expr(self, name: str) -> Optional[str]:
        """Получает внутреннее выражение типа (expr) для goal_start.
        
        В отличие от pp (pretty-print), expr содержит universe-переменные
        в закодированном виде, который goal_start может обработать.
        
        Returns:
            Внутреннее выражение типа или None.
        """
        try:
            info = self.server.env_inspect(name=name)
            if isinstance(info, dict):
                return info.get("type", {}).get("expr")
            return None
        except Exception:
            return None

    def env_inspect_full(self, name: str) -> Optional[Dict]:
        """Полная информация из env_inspect: module, pp, expr, source.
        
        Returns:
            Dict с ключами: module, pp, expr, sourceStart, sourceEnd
            или None если не найдена.
        """
        try:
            info = self.server.env_inspect(name=name)
            if not isinstance(info, dict):
                return None
            type_info = info.get("type", {})
            return {
                "module": info.get("module", ""),
                "pp": type_info.get("pp", ""),
                "expr": type_info.get("expr", ""),
                "sourceStart": info.get("sourceStart"),
                "sourceEnd": info.get("sourceEnd"),
            }
        except Exception:
            return None

    def goal_start(self, goal_expr: str) -> Optional[ProofState]:
        """
        Начинает доказательство цели через goal_start API.
        
        Пробует:
        1. _fix_pp(goal_expr) → goal_start
        2. Оригинальный goal_expr → goal_start (если отличается)
        """
        goal_expr_clean = _fix_pp(goal_expr)

        # goal_start с очищенным pp-выражением
        try:
            with _suppress_pantograph_prints():
                goal_state = self.server.goal_start(goal_expr_clean)
            if not goal_state.goals:
                return ProofFinished()
            pp = "\n".join(str(g) for g in goal_state.goals)
            return ProofState(pp=pp, goal_state=goal_state, goal_id=0)
        except ServerError as e:
            self._last_error = str(e)
        except Exception:
            pass

        # goal_start с оригинальным выражением (без _fix_pp)
        if goal_expr != goal_expr_clean:
            try:
                with _suppress_pantograph_prints():
                    goal_state = self.server.goal_start(goal_expr)
                if not goal_state.goals:
                    return ProofFinished()
                pp = "\n".join(str(g) for g in goal_state.goals)
                return ProofState(pp=pp, goal_state=goal_state, goal_id=0)
            except ServerError as e:
                self._last_error = str(e)
            except Exception:
                pass

        return None

    def _goal_via_sorry(self, type_pp: str) -> Optional[ProofState]:
        """
        Начинает доказательство через load_sorry (frontend.distil).
        
        Оборачивает тип в `theorem _sorry_N : <type> := by sorry`.
        В контексте `theorem` Lean автоматически привязывает
        свободные universe переменные (auto-bound implicit).
        
        Это решает проблемы:
        - Type u, Type u_1, Sort v → auto-bound universes
        - CategoryTheory.Category.{v, u} → valid syntax in theorem
        - Type vᵒᵖ → auto-bound
        
        НЕ решает:
        - .τl field notation → pp round-trip limitation
        - Typeclass synthesis failures → missing context
        """
        if not hasattr(self, '_sorry_counter'):
            self._sorry_counter = 0
        self._sorry_counter += 1
        
        # Сначала чистим autoParam (невалидный identifier _auto✝)
        type_clean = _fix_pp(type_pp)
        
        # Пробуем с оригинальным pp (universes auto-bound в theorem context)
        for pp_variant in [type_pp, type_clean] if type_pp != type_clean else [type_pp]:
            src = f'theorem _sorry_{self._sorry_counter} : {pp_variant} := by\n  sorry'
            try:
                targets = self.server.load_sorry(src)
                if targets and targets[0].goal_state.goals:
                    goal_state = targets[0].goal_state
                    pp = "\n".join(str(g) for g in goal_state.goals)
                    return ProofState(pp=pp, goal_state=goal_state, goal_id=0)
                # 0 targets или 0 goals — не ProofFinished, а ошибка парсинга
            except Exception:
                pass
        
        return None

    def _goal_via_source(self, name: str) -> Optional[ProofState]:
        """
        Начинает доказательство через исходный .lean файл модуля.
        
        Когда pp не round-trip'ится (field notation, typeclass synthesis),
        читаем оригинальный исходник — там есть правильные:
        - variable declarations ({m : MeasurableSpace Ω})
        - open/namespace (все имена доступны)
        - Оригинальный синтаксис (MeasurableSet[𝓕.predictable])
        
        Алгоритм:
        1. env_inspect(name) → module, sourceStart, sourceEnd
        2. module → .lean file path
        3. Извлекаем контекст (open, namespace, variable, section)
        4. Извлекаем declaration теоремы, заменяем proof на sorry
        5. load_sorry(context + theorem_sorry)
        
        НЕ включаем определения (def, instance, theorem, lemma, class)
        чтобы не конфликтовать с уже загруженным Mathlib.
        """
        try:
            info = self.server.env_inspect(name=name)
            if not isinstance(info, dict):
                return None
            
            module = info.get("module", "")
            src_start = info.get("sourceStart")
            src_end = info.get("sourceEnd")
            
            if not module or not src_start or not src_end:
                return None
            
            start_line = src_start.get("line", 0)  # 1-indexed
            end_line = src_end.get("line", 0)  # 1-indexed
            
            # Конвертируем module → file path
            fpath = Path(self.project_path) / (module.replace(".", "/") + ".lean")
            if not fpath.exists():
                return None
            
            with open(fpath) as f:
                lines = f.readlines()
            
            if end_line <= 0 or end_line > len(lines):
                return None
            
            # Извлекаем КОНТЕКСТ (до начала теоремы):
            # open, namespace, variable, section, end, set_option, attribute
            # Пропускаем: import, module, def, theorem, lemma, instance, class, structure
            _CONTEXT_PREFIXES = (
                "open ", "namespace ", "variable ", "section", "end ",
                "end\n", "set_option ", "attribute ", "noncomputable ",
                "suppress_compilation", "local ", "scoped ",
            )
            _SKIP_PREFIXES = (
                "import ", "public import ", "module",
                "def ", "theorem ", "lemma ", "instance ", "class ",
                "structure ", "inductive ", "abbrev ", "private ",
                "protected def ", "protected theorem ", "protected lemma ",
                "@[", "-- ", "/-",
            )
            
            context_lines = []
            in_comment = False
            for i in range(start_line - 1):  # До начала теоремы
                line = lines[i].rstrip()
                stripped = line.lstrip()
                
                # Отслеживаем блочные комментарии
                if "/-" in line:
                    in_comment = True
                if "-/" in line:
                    in_comment = False
                    continue
                if in_comment:
                    continue
                
                # Пустые строки — сохраняем для корректной структуры
                if not stripped:
                    context_lines.append("")
                    continue
                
                # Контекстные строки — включаем
                if any(stripped.startswith(p) for p in _CONTEXT_PREFIXES):
                    # Чистим public/expose
                    line = line.replace("@[expose] public section", "section")
                    line = line.replace("public section", "section")
                    context_lines.append(line)
                    continue
                
                # end без пробела (просто "end")
                if stripped == "end":
                    context_lines.append(line)
                    continue
            
            # Извлекаем declaration теоремы (start_line до end_line)
            theorem_lines = []
            for i in range(start_line - 1, end_line):
                theorem_lines.append(lines[i].rstrip())
            
            # Заменяем proof на sorry и переименовываем
            # (имя уже объявлено в Mathlib → конфликт)
            theorem_src = "\n".join(theorem_lines)
            theorem_src = re.sub(
                r'(lemma|theorem|def)\s+\S+', r'\1 _sorry_goal', 
                theorem_src, count=1
            )
            if ":=" in theorem_src:
                idx = theorem_src.index(":=")
                theorem_src = theorem_src[:idx] + ":= by sorry"
            else:
                theorem_src = theorem_src + " := by sorry"
            
            src = "\n".join(context_lines) + "\n" + theorem_src + "\n"
            
            targets = self.server.load_sorry(src)
            if targets and targets[0].goal_state.goals:
                goal_state = targets[0].goal_state
                pp = "\n".join(str(g) for g in goal_state.goals)
                return ProofState(pp=pp, goal_state=goal_state, goal_id=0)
        except Exception:
            pass
        
        return None

    def goal_start_expr(self, name: str, verbose: bool = False) -> Optional[ProofState]:
        """
        Начинает доказательство через имя теоремы.
        
        Цепочка попыток:
        1. env_inspect(name).type.expr → goal_start (внутреннее представление)
        2. env_inspect(name).type.pp → _fix_pp → goal_start (pretty-print)
        3. env_inspect(name).type.pp → load_sorry (theorem context, auto-bound universes)
        4. module source file → load_sorry (оригинальный исходник с контекстом)
        
        Шаг 4 решает все оставшиеся случаи: field notation, typeclass synthesis,
        потерянные instance annotations — оригинальный исходник содержит всё.
        """
        errors = []  # Собираем ошибки для диагностики
        
        # 1. Пробуем expr (внутреннее представление)
        expr = self.env_inspect_expr(name)
        if expr:
            try:
                with _suppress_pantograph_prints():
                    goal_state = self.server.goal_start(expr)
                if not goal_state.goals:
                    return ProofFinished()
                pp = "\n".join(str(g) for g in goal_state.goals)
                return ProofState(pp=pp, goal_state=goal_state, goal_id=0)
            except ServerError as e:
                errors.append(f"expr: {str(e)[:120]}")
            except Exception as e:
                errors.append(f"expr: {type(e).__name__}: {str(e)[:80]}")
        else:
            errors.append("expr: empty")

        # 2. Пробуем pp с _fix_pp → goal_start
        pp_type = self.env_inspect(name)
        if pp_type:
            result = self.goal_start(pp_type)
            if result is not None:
                return result
            errors.append(f"pp: {getattr(self, '_last_error', 'failed')[:120]}")
            
            # 3. Пробуем load_sorry (auto-bound universes в theorem context)
            result = self._goal_via_sorry(pp_type)
            if result is not None:
                return result
            errors.append("sorry: failed")
        else:
            errors.append("pp: empty")

        # 4. Пробуем через исходник модуля (100% fallback)
        result = self._goal_via_source(name)
        if result is not None:
            return result
        errors.append("source: failed")

        if verbose:
            print(f"  FAIL goal_start_expr({name}):")
            for err in errors:
                print(f"    {err}")

        return None

    # Тактики, которые закрывают goal без реального доказательства.
    # sorry/admit вставляют аксиому sorryAx — это НЕ доказательство.
    # native_decide безопасен (Lean верифицирует), но может быть медленным.
    _UNSOUND_TACTICS = frozenset({
        'sorry', 'admit', 'exact sorry', 'exact admit',
    })

    def run_tac(self, state: ProofState, tactic: str):
        """
        Применяет тактику к состоянию.
        
        Returns:
            ProofState — новое состояние
            ProofFinished — доказательство завершено
            None — тактика не применилась (ошибка / unsound)
        """
        if not isinstance(state, ProofState) or state.goal_state is None:
            return None

        # Защита от false-positive: sorry/admit закрывают goal,
        # но через аксиому sorryAx — это не настоящее доказательство.
        tactic_stripped = tactic.strip().lower()
        if tactic_stripped in self._UNSOUND_TACTICS:
            return None
        # Проверяем sorry/admit внутри составных тактик:
        # "first | exact foo | sorry", "try sorry", "<;> sorry" и т.п.
        if re.search(r'\bsorry\b', tactic_stripped) or re.search(r'\badmit\b', tactic_stripped):
            return None

        try:
            next_goal_state = self.server.goal_tactic(
                state.goal_state, tactic
            )
            if not next_goal_state.goals:
                return ProofFinished()
            pp = "\n".join(str(g) for g in next_goal_state.goals)
            return ProofState(pp=pp, goal_state=next_goal_state, goal_id=0)
        except (TacticFailure, ServerError):
            return None
        except Exception:
            return None

    def verify_proof(self, theorem_name: str, tactics: List[str],
                     verbose: bool = False) -> bool:
        """
        Независимая верификация доказательства: replay тактик на свежем goal.
        
        Стартует НОВЫЙ goal (не связан с BFS state), применяет тактики
        по одной. Если все применились и goals = 0 → доказательство верифицировано.
        
        Это исключает:
        - Баги в BFS-трекинге состояний
        - Неправильные goal_state ссылки
        - sorry/admit (отфильтрованы в run_tac)
        
        Args:
            theorem_name: Квалифицированное имя теоремы
            tactics: Последовательность тактик (путь от initial goal до ProofFinished)
            verbose: Подробный вывод
            
        Returns:
            True если доказательство верифицировано, False иначе
        """
        if not tactics:
            return False
        
        # Стартуем свежий goal
        try:
            state = self.goal_start_expr(theorem_name)
        except Exception as e:
            if verbose:
                print(f"    verify: goal_start_expr failed: {e}")
            return False
        
        if state is None:
            if verbose:
                print(f"    verify: cannot start goal for {theorem_name}")
            return False
        
        if isinstance(state, ProofFinished):
            # Тривиально доказано (0 goals сразу) — тактики не нужны
            return len(tactics) == 0
        
        # Применяем тактики последовательно
        for i, tac in enumerate(tactics):
            result = self.run_tac(state, tac)
            
            if result is None:
                if verbose:
                    print(f"    verify FAIL at step {i+1}/{len(tactics)}: "
                          f"tactic '{tac}' failed on state: {state.pp[:100]}")
                return False
            
            if isinstance(result, ProofFinished):
                if i == len(tactics) - 1:
                    # Последняя тактика закрыла все goals — ОК
                    return True
                else:
                    if verbose:
                        print(f"    verify WARN: proof finished early at step "
                              f"{i+1}/{len(tactics)}")
                    # Доказательство закончилось раньше — всё равно верно
                    return True
            
            state = result
        
        # Все тактики применены, но goals остались
        if verbose:
            print(f"    verify FAIL: all {len(tactics)} tactics applied but "
                  f"goals remain: {state.pp[:100]}")
        return False

    def catalog(self, module_prefix: str = "Mathlib") -> List[str]:
        """Получает список всех констант из Lean окружения."""
        try:
            return self.server.env_catalog(module_prefix=module_prefix)
        except Exception as e:
            print(f"env_catalog ошибка: {e}")
            return []

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()


# ============================================================================
# LeanNavigatorExplorer — BFS исследование (порт explore_states)
# ============================================================================

def explore_state_complexity(state_pp: str, base_complexity: Optional[int] = None,
                              seen_target_freq: Optional[Dict] = None) -> float:
    """Оценка сложности состояния (из LeanNavigator)."""
    if '⊢ False' in state_pp:
        return 1000000
    if base_complexity is not None:
        return base_complexity + 1

    complexity = 0
    lines = state_pp.split('\n')
    targets = []
    min_freq = 1000000
    for line in lines:
        if line.startswith("⊢") or '⊢' in line:
            target = line.split('⊢', 1)[-1].strip() if '⊢' in line else line[1:].strip()
            targets.append(target)
            if seen_target_freq is not None:
                if target in seen_target_freq:
                    min_freq = min(min_freq, seen_target_freq[target])
                    seen_target_freq[target] += 1
                else:
                    min_freq = 0
                    seen_target_freq[target] = 1

    if not targets:
        return len(state_pp)

    lengths = [len(x) for x in targets]
    complexity = max(lengths) / 2 + sum(lengths) / 2
    if seen_target_freq is not None and min_freq < 1000000:
        complexity += PENALTY_SEEN_TARGET_MULTIPLIER * min_freq
    return complexity


class LeanNavigatorExplorer:
    """
    BFS исследование графа переходов состояний.
    
    Воспроизводит explore_states() из LeanNavigator:
    1. Начинаем с начального состояния теоремы
    2. Для каждого состояния:
       a. RAG → top-200 шаблонов тактик
       b. Шаблоны → конкретные тактики (подстановка переменных)
       c. Каждая тактика → run_tac через Pantograph
       d. Новые состояния → очередь с приоритетами
    3. Если достигнут ProofFinished → записываем путь
    4. Генерируем training pairs из графа
    """

    # Тактики, которые можно декомпозировать через `?`-вариант.
    # simp → simp? → "simp only [lemma1, lemma2, ...]"
    # Каждая лемма становится отдельным rw-шагом = отдельная training pair.
    _DECOMPOSABLE_ROOTS = {"simp", "simp_all", "aesop", "simpa", "simp_arith", "dsimp"}
    _DECOMPOSE_QUERY = {
        "simp": "simp?",
        "simp_all": "simp_all?",
        "aesop": "aesop?",
        "simpa": "simpa?",
        "simp_arith": "simp_arith?",
        "dsimp": "dsimp?",
    }

    def __init__(self, dojo: PantographDojo, rag: TacticRAG,
                 max_steps: int = MAX_STEPS, max_time: int = 1200,
                 verbose: bool = False, early_stop: bool = True,
                 banned_tactics: Optional[set] = None,
                 decompose_auto: bool = False,
                 max_states: int = 0,
                 max_process_rss_mb: int = 0,
                 max_tactic_rss_jump_mb: int = 0,
                 progress_callback: Optional[Callable[[int, int, float], None]] = None,
                 trace_tactics: bool = False,
                 trace_theorem_substr: str = "",
                 phase_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None):
        """
        Args:
            max_states: Макс уникальных состояний в графе (0 = без лимита).
                Ограничивает память BFS: каждое состояние хранит полный pp.
            max_process_rss_mb: Если > 0, BFS останавливается при превышении
                суммарного RSS процесса (Python + Lean). Позволяет не съедать всю RAM на одной теореме.
            max_tactic_rss_jump_mb: Если > 0, BFS останавливается, когда один вызов run_tac
                увеличивает RSS процесса (Python + Lean) более чем на этот порог в MB.
            progress_callback: Вызывается каждые 200 шагов BFS с (n_steps, n_states, rss_mb).
                Позволяет по последней строке в логе понять, на какой операции произошёл OOM.
            trace_tactics: Если True, пишет before/after run_tac через phase_callback.
            trace_theorem_substr: Ограничить трассировку тактик только теоремами, в имени
                которых есть эта подстрока (пусто = все теоремы).
            phase_callback: Диагностический callback событий фаз BFS.
        """
        self.dojo = dojo
        self.rag = rag
        self.max_steps = max_steps
        self.max_time = max_time
        self.verbose = verbose
        self.early_stop = early_stop
        self.max_states = max_states  # 0 = no limit
        self.max_process_rss_mb = max_process_rss_mb  # 0 = disabled
        self.max_tactic_rss_jump_mb = max_tactic_rss_jump_mb  # 0 = disabled
        self.progress_callback = progress_callback
        self.trace_tactics = trace_tactics
        self.trace_theorem_substr = trace_theorem_substr
        self.phase_callback = phase_callback
        # Множество "корневых" имён тактик, которые BFS не будет применять.
        # Пример: {"simp", "simp_all", "aesop", "omega", "tauto", "decide"}
        # Это заставляет BFS искать многошаговые доказательства вместо
        # одношаговых "нуклеарных" завершений.
        self.banned_tactics = banned_tactics or set()
        # Если True, после BFS декомпозирует automation-тактики (simp, aesop, ...)
        # в цепочки отдельных rw-шагов. Расширяет датасет ~×2-5.
        self.decompose_auto = decompose_auto

    @staticmethod
    def _tactic_root(tactic: str) -> str:
        """Извлекает корневое имя тактики (первое слово, без '·' и пробелов).
        
        Примеры:
            '· simp_all'     → 'simp_all'
            'simp [nvar5]'   → 'simp'
            'rintro ⟨a⟩'    → 'rintro'
            'exact foo'      → 'exact'
        """
        s = tactic.strip()
        if s.startswith("·"):
            s = s[1:].strip()
        # Первое слово (до пробела, [, (, {, ⟨)
        for i, ch in enumerate(s):
            if ch in (' ', '\t', '[', '(', '{', '\u27e8'):  # ⟨
                return s[:i]
        return s

    @staticmethod
    def _parse_simp_suggestion(msg_data: str) -> List[str]:
        """Извлекает леммы из сообщения simp?/aesop?.
        
        Примеры входных сообщений:
            'Try this:\\n  [apply] simp only [add_zero, mul_one]'
            'Try this:\\n\\n  [apply]   simp_all only [and_self]'
        
        Returns:
            Список имён лемм, или пустой список.
        """
        # simp only [...] или simp_all only [...]
        m = re.search(r'simp(?:_all)?\s+only\s+\[([^\]]*)\]', msg_data)
        if m:
            return [l.strip() for l in m.group(1).split(',') if l.strip()]
        return []

    def _create_per_file_dojo(self, module: str) -> 'PantographDojo':
        """
        Создаёт per-file PantographDojo с imports=[module] (подход LeanDojo-v2).
        
        Каждый .lean файл в Mathlib имеет свои open/namespace/variable/instance,
        которые влияют на elaboration. Per-file server импортирует конкретный модуль,
        поэтому все определения файла доступны → goal_start по pp работает 100%.
        
        Сервер создаётся и уничтожается на каждую теорему (как LeanDojo-v2),
        чтобы не копить GoalState в памяти.
        """
        dojo = PantographDojo(
            project_path=self.dojo.project_path,
            imports=["Init", module],
            timeout=self.dojo.timeout,
        )
        dojo.start()
        return dojo

    def explore(self, goal_expr: str, theorem_name: str = "",
                theorem_code: str = "",
                theorem_module: str = "",
                exit_on_finish: bool = False) -> NavigatorResult:
        """
        Исследует граф переходов для теоремы.
        
        Args:
            goal_expr: Lean-выражение цели (тип теоремы)
            theorem_name: Имя теоремы
            theorem_code: Код формулировки теоремы (для RAG query)
            theorem_module: Lean-модуль теоремы (e.g., "Mathlib.Foo.Bar")
                           Если указан, создаётся per-file Server (как LeanDojo-v2)
                           для 100% корректного goal_start.
            exit_on_finish: Остановиться при первом ProofFinished
            
        Returns:
            NavigatorResult с графом переходов и training pairs
        """
        start_time = time.time()

        # Стратегия: shared server → fallback → per-file (тяжёлый, только если надо)
        per_file_dojo = None
        working_dojo = self.dojo
        state_0 = None

        # Способ 1: цепочка goal_start_expr на общем (shared) сервере
        # Быстро, не создаёт новый процесс. Работает для ~97% теорем.
        if theorem_name:
            state_0 = self.dojo.goal_start_expr(
                theorem_name, verbose=self.verbose
            )
        
        # Способ 2: прямой goal_start на выражении
        if state_0 is None and goal_expr:
            state_0 = self.dojo.goal_start(goal_expr)

        # Способ 3 (per-file, тяжёлый): только если shared не смог
        # Создаёт новый Server с imports=[module] — как LeanDojo-v2
        if state_0 is None and theorem_module and theorem_name:
            try:
                per_file_dojo = self._create_per_file_dojo(theorem_module)
                working_dojo = per_file_dojo
                
                pp_type = per_file_dojo.env_inspect(theorem_name)
                if pp_type:
                    state_0 = per_file_dojo.goal_start(pp_type)
                
                if state_0 is None or isinstance(state_0, ProofFinished):
                    state_0 = per_file_dojo.goal_start_expr(
                        theorem_name, verbose=self.verbose
                    )
            except Exception as e:
                if self.verbose:
                    print(f"  per-file dojo failed ({theorem_module}): {e}")
                if per_file_dojo:
                    try:
                        per_file_dojo.stop()
                    except Exception:
                        pass
                    per_file_dojo = None
                working_dojo = self.dojo
                state_0 = None

        if state_0 is None or isinstance(state_0, ProofFinished):
            # Cleanup per-file dojo
            if per_file_dojo:
                try:
                    per_file_dojo.stop()
                except Exception:
                    pass
            return NavigatorResult(
                theorem_name=theorem_name,
                state_dict={}, theorem_proven=isinstance(state_0, ProofFinished),
                pairs=[], n_states=0, n_steps=0, elapsed=0,
            )

        # BFS обёрнут в try/finally чтобы per-file dojo ВСЕГДА закрывался
        try:
            return self._run_bfs(
                state_0, working_dojo, per_file_dojo,
                theorem_name, theorem_code, start_time,
                exit_on_finish,
            )
        finally:
            if per_file_dojo:
                try:
                    per_file_dojo.stop()
                except Exception:
                    pass

    def _run_bfs(self, state_0, working_dojo, per_file_dojo,
                 theorem_name, theorem_code, start_time,
                 exit_on_finish=False):
        """Внутренний BFS — вынесен чтобы explore() мог гарантировать cleanup.
        
        Воспроизводит Algorithm 1 (ExploreStates) из LeanNavigator.
        """
        state_queue = PriorityQueue()
        # state_dict: key=state.pp (или "ProofFinished_N"), 
        # value=(state, [parent_states], [tactics], shortest_path)
        state_dict = {}
        seen_target_freq = {}

        base_complexity = 0
        state_queue.push(state_0,
                         explore_state_complexity(state_0.pp, base_complexity=base_complexity,
                                                   seen_target_freq=seen_target_freq)
                         + random.randint(0, 4))
        base_complexity += 1
        state_dict[state_0.pp] = (state_0, [], [], [])

        # Авторы: удаляют из type_of_item переменные, которых нет в theorem_code.
        # Это уменьшает кол-во подстановок и делает тактики более прицельными.
        unused_vars = []
        if theorem_code:
            tokens = tokenize_lean_tactic(theorem_code)
            tokens = [x for x in tokens if x.strip() != '']
            init_type_of_item, _ = classify_lean_elements(state_0.pp)
            unused_vars = [x for x in init_type_of_item.keys() if x not in tokens]

        n_steps = 0
        theorem_proven = False
        proof_finished_states = []
        memory_limit_reached = False
        trace_this_theorem = self.trace_tactics and (
            not self.trace_theorem_substr or self.trace_theorem_substr in theorem_name
        )

        def _current_rss_mb() -> float:
            """RSS текущего Python процесса + всех дочерних (Lean) в MB."""
            try:
                import psutil
                proc = psutil.Process()
                rss_mb = proc.memory_info().rss / (1024 * 1024)
                for c in proc.children(recursive=True):
                    try:
                        rss_mb += c.memory_info().rss / (1024 * 1024)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                return rss_mb
            except Exception:
                return 0.0

        while state_queue.size() > 0:
            curr_state = state_queue.pop()
            if not isinstance(curr_state, ProofState):
                continue

            # Классифицируем элементы состояния
            type_of_item, def_of_item = classify_lean_elements(curr_state.pp)
            
            # Авторы: удаляем unused_vars из type_of_item
            for var in unused_vars:
                type_of_item.pop(var, None)
                def_of_item.pop(var, None)

            if self.verbose and n_steps == 0:
                print(f"INIT_STATE: {curr_state.pp}")

            # RAG: получаем шаблоны тактик
            # Авторы: query = theorem_code + ' # ' + curr_state.pp
            if trace_this_theorem and self.phase_callback:
                try:
                    self.phase_callback("before_rag_query", {
                        "step": n_steps,
                        "states": len(state_dict),
                        "goal_len": len(curr_state.pp),
                        "rss_mb": round(_current_rss_mb(), 2),
                    })
                except Exception:
                    pass
            query_text = theorem_code if theorem_code else theorem_name
            suggestions = self.rag.get_similar_templates(
                curr_state.pp, theorem_code=query_text, num_returned=200
            )
            if trace_this_theorem and self.phase_callback:
                try:
                    self.phase_callback("after_rag_query", {
                        "step": n_steps,
                        "states": len(state_dict),
                        "n_suggestions": len(suggestions),
                        "rss_mb": round(_current_rss_mb(), 2),
                    })
                except Exception:
                    pass
            tac_templates = [s[0] for s in suggestions]

            # Добавляем обратные rw тактики (точно как у авторов)
            for tac_template in list(tac_templates):
                inv = get_inverse_tactic(tac_template)
                if inv and inv not in tac_templates:
                    tac_templates.append(inv)

            # Генерируем конкретные тактики из шаблонов
            if trace_this_theorem and self.phase_callback:
                try:
                    self.phase_callback("before_tactic_expand", {
                        "step": n_steps,
                        "states": len(state_dict),
                        "n_templates": len(tac_templates),
                        "rss_mb": round(_current_rss_mb(), 2),
                    })
                except Exception:
                    pass
            tactic_set = set()
            for tac_template in tac_templates:
                try:
                    tactics = generate_tactics_from_template(tac_template, type_of_item)
                    # Авторы: лимит MAX_TACTIC_FROM_TEMPLATE=50 на шаблон
                    if len(tactics) > MAX_TACTIC_FROM_TEMPLATE:
                        tactics = random.sample(tactics, MAX_TACTIC_FROM_TEMPLATE)
                except Exception:
                    continue
                for t in tactics:
                    tactic_set.add(t)

            # Базовые структурные тактики — всегда добавляем.
            # RAG может не вернуть intro/intros для ∀-целей если embedding
            # далёк от "structural" шаблонов. Без них BFS застрянет.
            _ALWAYS_TACTICS = [
                "intros", "intro", "constructor", "simp", "rfl", "trivial",
                "exfalso", "push_neg", "contrapose", "by_contra",
                "ext", "funext", "congr", "ring", "omega", "norm_num",
                "aesop", "tauto", "decide", "simp_all", "done",
                "linarith", "norm_cast", "push_cast", "assumption",
            ]
            for tac in _ALWAYS_TACTICS:
                tactic_set.add(tac)
            # intro с новыми переменными
            for i in range(6):
                tactic_set.add(f"intro nvar{i}")
            tactic_set.add("intro nvar0 nvar1")
            tactic_set.add("intro nvar0 nvar1 nvar2")
            tactic_set.add("rintro nvar0")
            tactic_set.add("rintro nvar0 nvar1")
            tactic_set.add("rintro ⟨nvar0⟩")
            tactic_set.add("rintro ⟨nvar0, nvar1⟩")
            tactic_set.add("cases nvar0")
            tactic_set.add("induction nvar0")
            if trace_this_theorem and self.phase_callback:
                try:
                    self.phase_callback("after_tactic_expand", {
                        "step": n_steps,
                        "states": len(state_dict),
                        "n_tactics": len(tactic_set),
                        "rss_mb": round(_current_rss_mb(), 2),
                    })
                except Exception:
                    pass

            # Фильтруем забаненные тактики (наше расширение)
            if self.banned_tactics:
                tactic_set = {
                    t for t in tactic_set
                    if self._tactic_root(t) not in self.banned_tactics
                }
                if trace_this_theorem and self.phase_callback:
                    try:
                        self.phase_callback("after_ban_filter", {
                            "step": n_steps,
                            "states": len(state_dict),
                            "n_tactics": len(tactic_set),
                            "rss_mb": round(_current_rss_mb(), 2),
                        })
                    except Exception:
                        pass

            # Применяем тактики
            proof_finished = False
            for tactic in tactic_set:
                n_steps += 1
                if n_steps % 10000 == 0:
                    print(f"  {n_steps} шагов выполнено, "
                          f"{len(state_dict)} состояний, "
                          f"proven={theorem_proven}")
                if n_steps > self.max_steps:
                    break
                # Каждые 200 шагов: проверка RSS (лимит) + логирование прогресса (диагностика OOM)
                if (self.max_process_rss_mb > 0 or self.progress_callback) and n_steps % 200 == 0:
                    rss_mb = 0.0
                    try:
                        import psutil
                        proc = psutil.Process()
                        rss_mb = proc.memory_info().rss / (1024 * 1024)
                        for c in proc.children(recursive=True):
                            try:
                                rss_mb += c.memory_info().rss / (1024 * 1024)
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                    except Exception:
                        pass
                    if self.max_process_rss_mb > 0 and rss_mb > self.max_process_rss_mb:
                        memory_limit_reached = True
                        if self.phase_callback:
                            try:
                                self.phase_callback("memory_limit_hit", {
                                    "step": n_steps,
                                    "states": len(state_dict),
                                    "rss_mb": rss_mb,
                                })
                            except Exception:
                                pass
                        if self.verbose:
                            print(f"  BFS остановлен: память процесса {rss_mb:.0f}MB > {self.max_process_rss_mb}MB")
                        break
                    if self.progress_callback:
                        try:
                            self.progress_callback(n_steps, len(state_dict), rss_mb)
                        except Exception:
                            pass

                # Авторы: retry до MAX_NUM_DOJO_ATTEMPT раз
                result = None
                measure_tactic_rss = (
                    self.max_tactic_rss_jump_mb > 0
                    or trace_this_theorem
                )
                rss_before = _current_rss_mb() if measure_tactic_rss else 0.0
                if trace_this_theorem and self.phase_callback:
                    try:
                        self.phase_callback("before_run_tac", {
                            "step": n_steps,
                            "states": len(state_dict),
                            "tactic": tactic[:160],
                            "goal_len": len(curr_state.pp),
                            "rss_before_mb": round(rss_before, 2) if measure_tactic_rss else None,
                        })
                    except Exception:
                        pass
                for _attempt in range(MAX_NUM_DOJO_ATTEMPT):
                    try:
                        result = working_dojo.run_tac(curr_state, tactic)
                        break
                    except Exception:
                        continue
                if result is None:
                    rss_after_fail = _current_rss_mb() if measure_tactic_rss else 0.0
                    rss_delta_fail = (rss_after_fail - rss_before) if measure_tactic_rss else 0.0
                    if trace_this_theorem and self.phase_callback:
                        try:
                            self.phase_callback("run_tac_failed", {
                                "step": n_steps,
                                "states": len(state_dict),
                                "tactic": tactic[:160],
                                "rss_after_mb": round(rss_after_fail, 2) if measure_tactic_rss else None,
                                "rss_delta_mb": round(rss_delta_fail, 2) if measure_tactic_rss else None,
                            })
                        except Exception:
                            pass
                    if (self.max_tactic_rss_jump_mb > 0 and measure_tactic_rss
                            and rss_delta_fail > self.max_tactic_rss_jump_mb):
                        memory_limit_reached = True
                        if self.phase_callback:
                            try:
                                self.phase_callback("tactic_rss_spike", {
                                    "step": n_steps,
                                    "states": len(state_dict),
                                    "tactic": tactic[:160],
                                    "rss_before_mb": round(rss_before, 2),
                                    "rss_after_mb": round(rss_after_fail, 2),
                                    "rss_delta_mb": round(rss_delta_fail, 2),
                                })
                            except Exception:
                                pass
                        if self.verbose:
                            print(f"  BFS остановлен: скачок памяти на тактике +{rss_delta_fail:.0f}MB > {self.max_tactic_rss_jump_mb}MB")
                        break
                    continue
                rss_after = _current_rss_mb() if measure_tactic_rss else 0.0
                rss_delta = (rss_after - rss_before) if measure_tactic_rss else 0.0
                if trace_this_theorem and self.phase_callback:
                    try:
                        self.phase_callback("after_run_tac", {
                            "step": n_steps,
                            "states": len(state_dict),
                            "tactic": tactic[:160],
                            "result_type": type(result).__name__,
                            "rss_after_mb": round(rss_after, 2) if measure_tactic_rss else None,
                            "rss_delta_mb": round(rss_delta, 2) if measure_tactic_rss else None,
                        })
                    except Exception:
                        pass
                if (self.max_tactic_rss_jump_mb > 0 and measure_tactic_rss
                        and rss_delta > self.max_tactic_rss_jump_mb):
                    memory_limit_reached = True
                    if self.phase_callback:
                        try:
                            self.phase_callback("tactic_rss_spike", {
                                "step": n_steps,
                                "states": len(state_dict),
                                "tactic": tactic[:160],
                                "rss_before_mb": round(rss_before, 2),
                                "rss_after_mb": round(rss_after, 2),
                                "rss_delta_mb": round(rss_delta, 2),
                            })
                        except Exception:
                            pass
                    if self.verbose:
                        print(f"  BFS остановлен: скачок памяти на тактике +{rss_delta:.0f}MB > {self.max_tactic_rss_jump_mb}MB")
                    break

                if isinstance(result, ProofFinished):
                    proof_finished = True
                    pf_key = f"ProofFinished_{len(proof_finished_states)}"
                    proof_finished_states.append(pf_key)
                    state_dict[pf_key] = (
                        result, [curr_state], [tactic],
                        state_dict[curr_state.pp][3] + [tactic]
                    )
                    if self.verbose:
                        print(f"  ProofFinished! ({tactic})")
                    if exit_on_finish:
                        break
                elif isinstance(result, ProofState):
                    if result.pp in state_dict:
                        # Состояние уже известно — добавляем нового родителя
                        _, parent_states, tactics_list, prefix = state_dict[result.pp]
                        new_prefix = state_dict[curr_state.pp][3] + [tactic]
                        if len(new_prefix) < len(prefix):
                            state_dict[result.pp] = (
                                result,
                                parent_states + [curr_state],
                                tactics_list + [tactic],
                                new_prefix
                            )
                        else:
                            state_dict[result.pp] = (
                                result,
                                parent_states + [curr_state],
                                tactics_list + [tactic],
                                prefix  # оставляем кратчайший
                            )
                    else:
                        # Лимит состояний: защита от OOM (state_dict хранит полный pp каждого состояния)
                        if self.max_states > 0 and len(state_dict) >= self.max_states:
                            continue
                        complexity = explore_state_complexity(
                            result.pp, base_complexity=base_complexity,
                            seen_target_freq=seen_target_freq
                        )
                        base_complexity += 1
                        state_queue.push(result, complexity + random.randint(0, 4))
                        state_dict[result.pp] = (
                            result, [curr_state], [tactic],
                            state_dict[curr_state.pp][3] + [tactic]
                        )

            if proof_finished:
                theorem_proven = True
                if exit_on_finish:
                    break

            # Очищаем goal_state у обработанного состояния — экономия памяти Lean
            # (после обработки run_tac больше не нужен)
            # НО: если decompose_auto, может понадобиться для родителей ProofFinished
            if not self.decompose_auto:
                object.__setattr__(curr_state, 'goal_state', None)

            if n_steps > self.max_steps:
                break
            if memory_limit_reached:
                break
            # Раннее прекращение: если не доказано за 1/3 бюджета — стоп.
            # Эвристика из LeanNavigator для массовой генерации.
            # Отключается через early_stop=False в конструкторе.
            if (self.early_stop and not theorem_proven
                    and n_steps > self.max_steps / 3):
                break
            if (time.time() - start_time) > self.max_time:
                if self.verbose:
                    print("Max run-time exceeded")
                break

        elapsed = time.time() - start_time

        # ================================================================
        # КРИТИЧНО: очищаем goal_state для экономии памяти Lean
        # Сохраняем только те, что нужны для decompose_automation
        # (родители ProofFinished состояний)
        # ================================================================
        needed_for_decompose = set()
        if self.decompose_auto and proof_finished_states:
            for pf_key in proof_finished_states:
                if pf_key in state_dict:
                    _, parent_states, _, _ = state_dict[pf_key]
                    for p in parent_states:
                        if isinstance(p, ProofState):
                            needed_for_decompose.add(p.pp)

        # Очищаем goal_state у всех состояний, кроме нужных для decompose
        for key, (state_obj, _, _, _) in state_dict.items():
            if isinstance(state_obj, ProofState) and key not in needed_for_decompose:
                # Обнуляем goal_state — он больше не нужен
                object.__setattr__(state_obj, 'goal_state', None)

        # Post-BFS: декомпозиция automation-тактик в индивидуальные шаги
        n_decomposed = 0
        if self.decompose_auto and proof_finished_states:
            n_decomposed, n_extra = self._decompose_automation(
                state_dict, proof_finished_states, working_dojo
            )

        # Генерируем training pairs
        # theorem_code содержит формулировку теоремы (goal_expr) для контекста в SFT
        pairs = self._generate_pairs(
            state_dict, proof_finished_states, theorem_name,
            theorem_statement=theorem_code,
        )

        # ================================================================
        # Верификация: replay найденных доказательств на свежем goal
        # ================================================================
        verified = None
        proof_tactics = None
        n_proofs_verified = 0

        if theorem_proven and proof_finished_states:
            # Собираем все уникальные пути тактик к ProofFinished
            proof_paths = []
            for pf_key in proof_finished_states:
                if pf_key in state_dict:
                    path = state_dict[pf_key][3]  # shortest path (list of tactics)
                    if path:
                        proof_paths.append(path)

            if proof_paths:
                # Выбираем кратчайший путь для отчёта
                proof_paths.sort(key=len)
                proof_tactics = proof_paths[0]

                # Верифицируем каждый уникальный путь через replay
                # Используем тот же dojo (общий или per-file) что был в BFS
                seen_paths = set()
                for path in proof_paths:
                    path_key = tuple(path)
                    if path_key in seen_paths:
                        n_proofs_verified += 1  # дубликат уже верифицированного
                        continue
                    seen_paths.add(path_key)

                    ok = working_dojo.verify_proof(
                        theorem_name, path, verbose=self.verbose
                    )
                    if ok:
                        n_proofs_verified += 1
                    elif self.verbose:
                        print(f"  VERIFY FAIL: {theorem_name} path={path}")

                verified = n_proofs_verified > 0

                if self.verbose or not verified:
                    status = "OK" if verified else "FAIL"
                    print(f"  Verify: {status} "
                          f"({n_proofs_verified}/{len(seen_paths)} paths verified, "
                          f"shortest={len(proof_tactics)} tactics)")

                # Если ни один путь не прошёл верификацию — это false positive
                if not verified:
                    theorem_proven = False
                    # Обнуляем pairs — данные ненадёжны
                    pairs = [p for p in pairs if p.distance_to_proof < 0]

        # ================================================================
        # КРИТИЧНО: очищаем state_dict — он больше не нужен, но занимает
        # огромное количество памяти (граф ProofState с циклическими ссылками)
        # ================================================================
        n_states_final = len(state_dict)
        n_proofs_found_final = len(proof_finished_states)
        state_dict.clear()
        del state_dict
        proof_finished_states.clear()
        del proof_finished_states

        # Принудительный GC для освобождения циклических ссылок
        import gc
        gc.collect()

        return NavigatorResult(
            theorem_name=theorem_name,
            state_dict={},  # Пустой — данные больше не нужны
            theorem_proven=theorem_proven,
            pairs=pairs,
            n_states=n_states_final,
            n_steps=n_steps,
            elapsed=elapsed,
            verified=verified,
            proof_tactics=proof_tactics,
            n_proofs_found=n_proofs_found_final,
            n_proofs_verified=n_proofs_verified,
            n_decomposed=n_decomposed,
        )

    def _decompose_automation(self, state_dict: Dict,
                              proof_finished_states: List[str],
                              working_dojo: PantographDojo) -> Tuple[int, int]:
        """
        Post-BFS декомпозиция automation-тактик в индивидуальные шаги.
        
        Для каждого ребра «state → ProofFinished через simp/aesop/…»:
        1. Запускает simp? (или аналог) на исходном состоянии
        2. Парсит сообщение: «simp only [lemma1, lemma2, ...]»
        3. Применяет каждую лемму отдельно: rw [lemma] или simp only [lemma]
        4. Вставляет промежуточные состояния в state_dict
        
        Результат: _generate_pairs() подхватывает новые промежуточные состояния
        и генерирует дополнительные (state, rw [lemma]) training pairs.
        
        Returns:
            (n_decomposed, n_extra_states) — сколько рёбер разложено и 
            сколько новых состояний/ProofFinished добавлено.
        """
        # Собираем рёбра к ProofFinished с decomposable тактиками
        edges = []
        for pf_key in list(proof_finished_states):
            if pf_key not in state_dict:
                continue
            _, parent_states, tactics, _ = state_dict[pf_key]
            for parent, tac in zip(parent_states, tactics):
                root = self._tactic_root(tac)
                if root in self._DECOMPOSABLE_ROOTS and isinstance(parent, ProofState):
                    edges.append((parent, tac, pf_key))

        if not edges:
            return 0, 0

        n_decomposed = 0
        n_extra_states = 0

        for parent_state, original_tactic, pf_key in edges:
            if parent_state.goal_state is None:
                continue

            root = self._tactic_root(original_tactic)
            query_tac = self._DECOMPOSE_QUERY.get(root)
            if not query_tac:
                continue

            # Запускаем simp? (или аналог) на parent state
            try:
                q_result = working_dojo.server.goal_tactic(
                    parent_state.goal_state, query_tac
                )
            except Exception:
                continue

            # Парсим леммы из сообщения
            if not q_result.messages:
                continue
            lemmas = self._parse_simp_suggestion(q_result.messages[0].data)
            if len(lemmas) < 2:
                # Нет выигрыша: 0 или 1 лемма = не детальнее оригинала
                continue

            # Применяем каждую лемму отдельно
            current = parent_state
            steps = []  # [(source_state, tactic_str, result)]

            for lemma in lemmas:
                if not isinstance(current, ProofState) or current.goal_state is None:
                    break

                # Пробуем rw [lemma], затем simp only [lemma]
                result = None
                used_tactic = None
                for try_tac in [f"rw [{lemma}]", f"simp only [{lemma}]"]:
                    try:
                        gs = working_dojo.server.goal_tactic(
                            current.goal_state, try_tac
                        )
                        if not gs.goals:
                            result = ProofFinished()
                        else:
                            pp = "\n".join(str(g) for g in gs.goals)
                            result = ProofState(pp=pp, goal_state=gs, goal_id=0)
                        used_tactic = try_tac
                        break
                    except Exception:
                        continue

                if result is None:
                    break  # Не получилось применить лемму — прерываем цепочку

                steps.append((current, used_tactic, result))
                current = result

            # Нужно минимум 2 шага для пользы
            if len(steps) < 2:
                continue

            # Вставляем промежуточные состояния в state_dict
            n_decomposed += 1
            for src, tac, dst in steps:
                if isinstance(dst, ProofFinished):
                    new_pf_key = f"ProofFinished_{len(proof_finished_states)}"
                    proof_finished_states.append(new_pf_key)
                    src_path = state_dict.get(src.pp, (None, None, None, []))[3]
                    state_dict[new_pf_key] = (
                        dst, [src], [tac], src_path + [tac]
                    )
                    n_extra_states += 1
                elif isinstance(dst, ProofState):
                    if dst.pp in state_dict:
                        # Состояние уже есть — добавляем нового родителя
                        existing = state_dict[dst.pp]
                        state_dict[dst.pp] = (
                            dst,
                            existing[1] + [src],
                            existing[2] + [tac],
                            existing[3],  # оставляем кратчайший путь
                        )
                    else:
                        src_path = state_dict.get(
                            src.pp, (None, None, None, [])
                        )[3]
                        state_dict[dst.pp] = (
                            dst, [src], [tac], src_path + [tac]
                        )
                        n_extra_states += 1

        if self.verbose and n_decomposed > 0:
            print(f"  Decompose: {n_decomposed} automation tactics → "
                  f"{n_extra_states} extra states")

        return n_decomposed, n_extra_states

    def _generate_pairs(self, state_dict: Dict, proof_finished_states: List[str],
                         theorem_name: str, theorem_statement: str = "",
                         max_distance: int = MAX_DISTANCE,
                         negative_ratio: float = 1.0) -> List[TrainingPair]:
        """
        Генерирует training pairs из графа переходов.
        
        Воспроизводит get_state_provability_data() + yield_state_pairs() из LeanNavigator:
        1. Для каждого ProofFinished обходит предков (до max_distance=8, max_parents=10)
        2. Каждый предок = новая теорема с proof_path до ProofFinished
        3. Макс MAX_NUM_OUTPUT_PER_STATE=50 пар на одно состояние
        4. Добавляет negative examples (unprovable states с distance=-1)
        
        Args:
            theorem_statement: Исходная формулировка теоремы (goal_expr) для контекста в SFT
        """
        pairs = []
        seen_state_counts: Dict[str, int] = {}  # сколько пар уже для данного state
        
        # Перемешиваем ProofFinished (как авторы)
        pf_keys = list(proof_finished_states)
        random.shuffle(pf_keys)
        
        for pf_idx, pf_key in enumerate(pf_keys):
            if pf_key not in state_dict:
                continue
            if pf_idx > MAX_PROVEN_STATES:
                break
            
            # yield_state_pairs: обход от ProofFinished к предкам
            # Собираем (ancestor_state, distance, tactic_list)
            ancestor_dict: Dict[str, Tuple[int, List[str]]] = {}
            self._yield_state_pairs(
                pf_key, pf_key, state_dict,
                seen_pps={pf_key}, tactic_list=[],
                max_distance=max_distance, max_parents=10,
                ancestor_dict=ancestor_dict,
            )
            
            for ancestor_pp, (distance, tactic_list) in ancestor_dict.items():
                count = seen_state_counts.get(ancestor_pp, 0)
                if count >= MAX_NUM_OUTPUT_PER_STATE:
                    continue
                
                state_data = state_dict.get(ancestor_pp)
                if state_data is None:
                    continue
                
                # tactic_list[0] = первая тактика от ancestor к proof
                tactic = tactic_list[0] if tactic_list else ""
                if not tactic:
                    continue
                
                # next_state: куда ведёт первая тактика
                next_state_str = "no goals" if distance == 1 else ""
                if distance > 1 and len(tactic_list) > 1:
                    # Ищем next state в state_dict через parent→child
                    # но проще — берём tactic_list[1:] как остаток
                    pass
                
                pairs.append(TrainingPair(
                    state=ancestor_pp,
                    tactic=tactic,
                    next_state=next_state_str,
                    distance_to_proof=distance,
                    theorem_name=theorem_name,
                    theorem_statement=theorem_statement,
                ))
                seen_state_counts[ancestor_pp] = count + 1
        
        # Negative examples: unprovable states (distance=-1)
        # Авторы добавляют столько же negative сколько positive
        num_positive = len(pairs)
        if num_positive > 0 and negative_ratio > 0:
            provable_pps = set(seen_state_counts.keys())
            all_states = [
                (key, data) for key, data in state_dict.items()
                if not key.startswith("ProofFinished") and key not in provable_pps
            ]
            random.shuffle(all_states)
            num_negative = 0
            for key, data in all_states:
                pairs.append(TrainingPair(
                    state=key,
                    tactic="",
                    next_state="",
                    distance_to_proof=-1,
                    theorem_name=theorem_name,
                    theorem_statement=theorem_statement,
                ))
                num_negative += 1
                if num_negative >= int(num_positive * negative_ratio):
                    break
        
        return pairs

    def _yield_state_pairs(self, curr_key: str, leaf_key: str,
                            state_dict: Dict, seen_pps: Set[str],
                            tactic_list: List[str],
                            max_distance: int, max_parents: int,
                            ancestor_dict: Dict):
        """
        Рекурсивный обход от ProofFinished к предкам (как yield_state_pairs авторов).
        
        Собирает ancestor_dict[state.pp] = (distance, tactic_list).
        Обходит до max_parents=10 родителей на каждом узле.
        """
        state_data = state_dict.get(curr_key)
        if state_data is None:
            return

        _, parent_states, tactics, _ = state_data
        distance = len(seen_pps) - 1
        
        # Yield текущее состояние (если distance > 0, т.е. не сам ProofFinished)
        if distance > 0 and curr_key not in [k for k in state_dict if k.startswith("ProofFinished")]:
            if curr_key not in ancestor_dict or distance < ancestor_dict[curr_key][0]:
                ancestor_dict[curr_key] = (distance, list(tactic_list))
        
        if len(seen_pps) > max_distance:
            return
        
        num_parents_checked = 0
        for i in range(len(parent_states)):
            parent = parent_states[i]
            if not isinstance(parent, ProofState):
                continue
            if parent.pp in seen_pps:
                continue
            
            self._yield_state_pairs(
                parent.pp, leaf_key, state_dict,
                seen_pps | {parent.pp},
                [tactics[i]] + tactic_list,
                max_distance, max_parents,
                ancestor_dict,
            )
            num_parents_checked += 1
            if num_parents_checked >= max_parents:
                break


# ============================================================================
# Загрузка теорем из traced данных (без lean-dojo)
# ============================================================================

@dataclass
class TracedTheorem:
    """Теорема из traced данных — минимальная обёртка."""
    name: str             # Полное имя (e.g., Mathlib.Algebra.Group.basic_mul)
    module: str           # Имя модуля (e.g., Mathlib.Algebra.Group)
    goal_state: str       # Начальное состояние (stateBefore первой тактики)
    goal_expr: str        # Выражение цели (⊢ ... часть)
    file_path: str        # Путь к .lean файлу
    tactics: List[Dict]   # Список тактик [{stateBefore, stateAfter, tactic_text}]


def load_theorems_from_ast_dir(
    repo_dir: str,
    skip_packages: bool = True,
    max_files: int = 0,
) -> List[TracedTheorem]:
    """
    Загружает теоремы из .ast.json + .lean файлов.
    
    Каждая группа тактик с уникальным начальным состоянием считается теоремой.
    Имя теоремы восстанавливается из исходного кода.
    
    Args:
        repo_dir: Путь к traced Mathlib4
        skip_packages: Пропускать зависимости
        max_files: Макс файлов (0 = все)
        
    Returns:
        Список TracedTheorem
    """
    repo_dir = Path(repo_dir)
    build_ir = repo_dir / ".lake" / "build" / "ir"

    if not build_ir.exists():
        raise FileNotFoundError(f"Нет build/ir в {repo_dir}")

    ast_files = sorted(build_ir.rglob("*.ast.json"))
    if skip_packages:
        ast_files = [f for f in ast_files
                     if "packages" not in str(f.relative_to(build_ir))]

    if max_files > 0 and len(ast_files) > max_files:
        ast_files = random.sample(ast_files, max_files)

    theorems = []
    # Паттерн для имён теорем/лемм в .lean
    thm_pattern = re.compile(
        r'(?:theorem|lemma|def|instance)\s+([\w.\']+)\s*'
    )

    iterator = tqdm(ast_files, desc="Загрузка теорем") if TQDM_AVAILABLE else ast_files

    for ast_file in iterator:
        try:
            rel = ast_file.relative_to(build_ir)
            lean_rel = Path(str(rel).replace(".ast.json", ".lean"))
            lean_file = repo_dir / lean_rel
            if not lean_file.exists():
                continue

            # Lean использует байтовые позиции → читаем как bytes
            source_bytes = lean_file.read_bytes()
            source_str = source_bytes.decode("utf-8", errors="replace")
            module_name = str(rel).replace(".ast.json", "").replace("/", ".")

            with open(ast_file) as f:
                data = json.load(f)

            tactics = data.get("tactics", [])
            if not tactics:
                continue

            # Группируем тактики по теоремам.
            # Тактики идут последовательно по pos. Каждая "новая" теорема
            # начинается когда stateBefore не является stateAfter предыдущей.
            current_group = []
            for tac in tactics:
                state_before = tac.get("stateBefore", "")
                tactic_text = source_bytes[
                    tac.get("pos", 0):tac.get("endPos", 0)
                ].decode("utf-8", errors="replace").strip()
                tac_entry = {
                    "stateBefore": state_before,
                    "stateAfter": tac.get("stateAfter", ""),
                    "tactic_text": tactic_text,
                    "pos": tac.get("pos", 0),
                }

                if not current_group:
                    current_group.append(tac_entry)
                else:
                    # Если stateAfter предыдущей != stateBefore текущей
                    # И stateBefore содержит ⊢ → начало новой теоремы
                    prev_after = current_group[-1]["stateAfter"]
                    if (state_before != prev_after
                            and "⊢" in state_before
                            and state_before != "no goals"):
                        # Сохраняем предыдущую группу как теорему
                        _save_theorem_group(
                            current_group, theorems, module_name,
                            str(lean_file), source_str, thm_pattern
                        )
                        current_group = [tac_entry]
                    else:
                        current_group.append(tac_entry)

            # Последняя группа
            if current_group:
                _save_theorem_group(
                    current_group, theorems, module_name,
                    str(lean_file), source_str, thm_pattern
                )

        except Exception:
            continue

    print(f"✓ Загружено {len(theorems)} теорем из {len(ast_files)} файлов")
    return theorems


def _save_theorem_group(
    group: List[Dict],
    theorems: List[TracedTheorem],
    module_name: str,
    file_path: str,
    source: str,
    thm_pattern: re.Pattern,
):
    """Сохраняет группу тактик как теорему."""
    if not group:
        return
    goal_state = group[0]["stateBefore"]
    if goal_state == "no goals" or "⊢" not in goal_state:
        return

    # Извлекаем goal expression (часть после ⊢)
    lines = goal_state.split("\n")
    goal_lines = []
    for line in lines:
        if "⊢" in line:
            goal_lines.append(line.split("⊢", 1)[-1].strip())
    goal_expr = "\n".join(goal_lines) if goal_lines else ""

    if not goal_expr:
        return

    # Пытаемся найти имя теоремы из исходника по позиции первой тактики
    pos = group[0].get("pos", 0)
    # Смотрим 500 символов до первой тактики
    context = source[max(0, pos - 500):pos]
    matches = list(thm_pattern.finditer(context))
    if matches:
        name = matches[-1].group(1)
        full_name = f"{module_name}.{name}"
    else:
        full_name = f"{module_name}._proof_{pos}"

    theorems.append(TracedTheorem(
        name=full_name,
        module=module_name,
        goal_state=goal_state,
        goal_expr=goal_expr,
        file_path=file_path,
        tactics=[{
            "stateBefore": t["stateBefore"],
            "stateAfter": t["stateAfter"],
            "tactic_text": t["tactic_text"],
        } for t in group],
    ))


# ============================================================================
# load_theorems_from_env — загрузка теорем из Lean окружения
# ============================================================================

def _is_internal_name(name: str) -> bool:
    """Фильтрует внутренние/авто-генерированные имена Lean."""
    parts = name.split('.')
    for p in parts:
        if p.startswith('_'):
            return True
        if p in ('rec', 'recOn', 'casesOn', 'noConfusion', 'noConfusionType',
                 'mk', 'below', 'brecOn', 'binductionOn', 'ind',
                 'sizeOf_spec', 'sizeOf', 'rawCast', 'ndrec', 'dcases',
                 'drec', 'injEq', 'inl', 'inr'):
            return True
    last = parts[-1] if parts else ""
    if last.startswith('proof_') and last[6:].isdigit():
        return True
    # Auto-generated @[congr]/@[simp] леммы — их типы содержат
    # дефектные instance-зависимости, невозможно начать как proof goal
    if last in ('congr_simp',):
        return True
    # Auto-generated @[simps] леммы с field notation (e.g., comp_τl, map_τr)
    # — pp содержит .τl/.τr field notation, не парсится standalone
    if any(last.endswith(suffix) for suffix in ('_τl', '_τr')):
        return True
    return False


def _is_interesting_type(type_pp: str) -> bool:
    """Фильтрует тривиальные/непригодные для BFS типы."""
    if not type_pp or len(type_pp) < 5:
        return False
    # Пропускаем Sort/Type/Prop — это не теоремы
    if type_pp.strip() in ("Prop", "Type", "Sort"):
        return False
    if type_pp.startswith("Sort ") or type_pp.startswith("Type "):
        return False
    # Слишком длинные — обычно сгенерированные определения
    if len(type_pp) > 2000:
        return False
    return True


def _fix_pp(expr: str) -> str:
    """
    Исправляет pp-строки типов для парсинга Lean.
    
    Проблемы pp-output env_inspect:
    1. Свободные universe переменные: Type u_1, Sort v, Type uR
    2. Explicit universe params: .{v, u}, .{w + 1}
    3. autoParam с внутренними именами: autoParam (X ⊆ M.E) _auto✝
    
    Замены:
    1. Type u_1 → Type _ (Lean выведет уровень)
    2. .{v, u, ...} → удаляется (Lean выведет universes из контекста)
    3. autoParam (expr) _auto✝ → (expr) (Lean обработает без autoParam)
    """
    # 1. autoParam (expr) _auto✝ → (expr)
    #    _auto✝ содержит ✝ (dagger) — невалидный Lean identifier
    expr = re.sub(r'autoParam\s*(\([^)]+\))\s*\S+', r'\1', expr)
    # 2. Type u_1, Type u, Sort v, Type uR, Type uι, Type v₁ и т.д. → Type _ / Sort _
    expr = re.sub(r'(Type|Sort)\s+(?:u_?\w*|[uvw][₀-₉ᵒᵖ\w]*)\b', r'\1 _', expr)
    # 3. .{v, u}, .{w + 1}, .{u_1, u_2, u_3} → убираем
    #    В Lean pp-output .{...} (точка + фигурные) — всегда universe params
    expr = re.sub(r'\.\{[^}]+\}', '', expr)
    return expr


# Обратная совместимость
_fix_universes = _fix_pp


def load_theorems_from_env(
    dojo: PantographDojo,
    module_prefix: str = "Mathlib",
    max_theorems: int = 50,
    cache_dir: Optional[str] = None,
    verbose: bool = False,
    validate_goals: bool = True,
    only_names: Optional[List[str]] = None,
) -> List[TracedTheorem]:
    """
    Загружает теоремы из Lean окружения через Pantograph.

    Использует env_catalog + env_inspect для получения:
    - Правильных квалифицированных имён (namespace, а не модуль)
    - Полных типов (с квантификаторами) — пригодных для goal_start

    Args:
        dojo: Запущенный PantographDojo
        module_prefix: Префикс модуля (e.g., "Mathlib")
        max_theorems: Максимум теорем для загрузки
        cache_dir: Директория кэша (для сохранения каталога)
        verbose: Подробный вывод
        validate_goals: Проверять goal_start_expr перед добавлением (100% рабочие)
        only_names: Если задан — инспектируем только эти полные имена (без семпла, без лимита max_theorems).

    Returns:
        Список TracedTheorem с валидными goal_expr
    """
    theorems = []
    inspected = 0
    failed = 0
    goal_rejected = 0

    if only_names is not None:
        iterator = only_names
        if verbose:
            print(f"Загрузка только указанных имён: {len(only_names)}")
    else:
        # 1. Получаем каталог (с кэшированием)
        catalog_cache = Path(cache_dir) / "env_catalog.json" if cache_dir else None

        if catalog_cache and catalog_cache.exists():
            with open(catalog_cache) as f:
                all_names = json.load(f)
            print(f"Каталог загружен из кэша: {len(all_names)} констант")
        else:
            print(f"Получаем каталог из Lean ({module_prefix})...")
            t0 = time.time()
            all_names = dojo.catalog(module_prefix=module_prefix)
            elapsed = time.time() - t0
            print(f"  Получено {len(all_names)} констант за {elapsed:.1f}с")
            if catalog_cache and len(all_names) > 0:
                catalog_cache.parent.mkdir(parents=True, exist_ok=True)
                with open(catalog_cache, 'w') as f:
                    json.dump(all_names, f)

        # 2. env_catalog возвращает имена с однобуквенным тегом: t=theorem, ...
        theorem_names = [n[1:] for n in all_names if n.startswith('t')]
        print(f"  Теорем (prefix=t): {len(theorem_names)} из {len(all_names)}")

        # 3. Фильтруем внутренние имена
        filtered = [n for n in theorem_names if not _is_internal_name(n)]
        print(f"  После фильтрации: {len(filtered)} (отброшено {len(theorem_names) - len(filtered)} внутренних)")

        # 4. Семплируем
        sample_size = min(max_theorems * 10, len(filtered))
        sample = random.sample(filtered, sample_size) if len(filtered) > sample_size else filtered
        iterator = tqdm(sample, desc="Загрузка типов") if TQDM_AVAILABLE else sample

    consecutive_errors = 0
    MAX_CONSECUTIVE_ERRORS = 10  # Если много подряд — dojo сломан (Lean PANIC убил процесс)

    for name in iterator:
        if only_names is None and len(theorems) >= max_theorems:
            break
        inspected += 1

        # Получаем полную информацию: module, pp, expr
        # Оборачиваем в try/except — Lean PANIC может вызвать исключение
        try:
            info = dojo.env_inspect_full(name)
        except Exception as e:
            # Lean PANIC / краш — пропускаем теорему
            failed += 1
            consecutive_errors += 1
            if verbose:
                print(f"  skip {name}: env_inspect crash: {str(e)[:60]}")
            if TQDM_AVAILABLE and isinstance(iterator, tqdm):
                iterator.set_postfix(found=len(theorems), failed=failed)
            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                print(f"\n⚠ {consecutive_errors} ошибок подряд — Lean/Pantograph вероятно упал (PANIC). "
                      f"Прерываем загрузку. Загружено {len(theorems)} теорем.")
                break
            continue

        if info is None:
            failed += 1
            if TQDM_AVAILABLE and isinstance(iterator, tqdm):
                iterator.set_postfix(found=len(theorems), failed=failed)
            continue

        type_pp = info["pp"]
        real_module = info["module"]  # Реальный Lean модуль (для per-file server)

        if not type_pp or not _is_interesting_type(type_pp):
            failed += 1
            if TQDM_AVAILABLE and isinstance(iterator, tqdm):
                iterator.set_postfix(found=len(theorems), failed=failed)
            continue

        # Валидация: проверяем что goal_start_expr может начать доказательство
        if validate_goals:
            try:
                result = dojo.goal_start_expr(name)
            except Exception as e:
                # Lean PANIC / краш — пропускаем теорему
                goal_rejected += 1
                consecutive_errors += 1
                if verbose:
                    print(f"  skip {name}: goal_start crash: {str(e)[:60]}")
                if TQDM_AVAILABLE and isinstance(iterator, tqdm):
                    iterator.set_postfix(found=len(theorems), failed=failed, skip=goal_rejected)
                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    print(f"\n⚠ {consecutive_errors} ошибок подряд — Lean/Pantograph вероятно упал (PANIC). "
                          f"Прерываем загрузку. Загружено {len(theorems)} теорем.")
                    break
                continue

            if result is None or isinstance(result, ProofFinished):
                goal_rejected += 1
                if verbose:
                    print(f"  skip {name}: {'trivial' if isinstance(result, ProofFinished) else 'cannot start'}")
                if TQDM_AVAILABLE and isinstance(iterator, tqdm):
                    iterator.set_postfix(found=len(theorems), failed=failed, skip=goal_rejected)
                continue

        theorems.append(TracedTheorem(
            name=name,
            module=real_module,  # Реальный module из env_inspect (для per-file server)
            goal_state=f"⊢ {type_pp}",
            goal_expr=type_pp,
            file_path="",
            tactics=[],
        ))
        consecutive_errors = 0  # Сбрасываем счётчик при успехе

        if TQDM_AVAILABLE and isinstance(iterator, tqdm):
            iterator.set_postfix(found=len(theorems), failed=failed, skip=goal_rejected)

    rejected_msg = f", goal_rejected={goal_rejected}" if goal_rejected else ""
    print(f"✓ Загружено {len(theorems)} теорем из Lean env "
          f"(inspected={inspected}, rejected={failed}{rejected_msg})")
    return theorems


# ============================================================================
# Полный pipeline (без lean-dojo)
# ============================================================================

def run_lean_navigator(
    repo_dir: str,
    max_theorems: int = 100,
    max_steps: int = 100000,
    max_time: int = 120,
    rag_model: str = "all-MiniLM-L6-v2",
    min_template_freq: int = 2,
    output_dir: Optional[str] = None,
    templates_path: Optional[str] = None,
    rag_path: Optional[str] = None,
    imports: Optional[List[str]] = None,
    verbose: bool = False,
) -> Tuple[List[TrainingPair], Dict[str, Any]]:
    """
    Полный pipeline LeanNavigator — работает напрямую из traced данных.
    
    1. Извлекает шаблоны тактик из .ast.json + .lean
    2. Строит FAISS index для RAG retrieval
    3. Для каждой теоремы запускает BFS исследование через Pantograph
    4. Собирает training pairs из всех графов
    
    Args:
        repo_dir: Путь к traced Mathlib4 (от fast_trace.py)
        max_theorems: Максимум теорем для исследования
        max_steps: Максимум шагов BFS на теорему
        max_time: Максимум секунд на теорему
        rag_model: Модель для sentence embeddings
        min_template_freq: Минимальная частота шаблона для индексации
        output_dir: Директория для сохранения результатов
        templates_path: Путь к уже сохранённым шаблонам (пропустить шаг 1)
        rag_path: Путь к уже сохранённому RAG индексу (пропустить шаг 2)
        imports: Imports для Pantograph (по умолчанию ["Mathlib"])
        verbose: Подробный вывод
        
    Returns:
        (all_pairs, summary)
    """
    total_start = time.time()
    repo_dir = str(repo_dir)
    if imports is None:
        imports = ["Mathlib"]

    # === Шаг 1: Извлечение шаблонов тактик ===
    print("=" * 60)
    print("Шаг 1: Извлечение шаблонов тактик")
    print("=" * 60)

    extractor = TacticTemplateExtractor()

    if templates_path and Path(templates_path).exists():
        extractor.load(templates_path)
    else:
        extractor.extract_from_ast_dir(repo_dir)
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            extractor.save(str(Path(output_dir) / "tactic_templates.json"))

    top_templates = extractor.get_top_templates(10)
    print("\nТоп-10 шаблонов:")
    for tmpl, freq in top_templates:
        print(f"  [{freq:6d}] {tmpl}")

    # === Шаг 2: Построение FAISS index ===
    print("\n" + "=" * 60)
    print("Шаг 2: Построение FAISS index для RAG")
    print("=" * 60)

    rag = TacticRAG(model_name=rag_model)

    if rag_path and Path(rag_path).exists():
        rag.load(rag_path)
    else:
        rag.build_index(extractor.templates, min_freq=min_template_freq)
        if output_dir:
            rag.save(str(Path(output_dir) / "rag_index"))

    # === Шаг 3+4: Загрузка теорем + BFS ===
    print("\n" + "=" * 60)
    print("Шаг 3: Загрузка теорем из Lean env + BFS")
    print("=" * 60)

    all_pairs = []
    theorem_results = []

    cache_dir = str(Path(output_dir)) if output_dir else None

    with PantographDojo(project_path=repo_dir, imports=imports) as dojo:
        # Загружаем теоремы из Lean окружения (правильные имена + полные типы)
        theorems = load_theorems_from_env(
            dojo, module_prefix="Mathlib",
            max_theorems=max_theorems,
            cache_dir=cache_dir,
            verbose=verbose,
        )
        print(f"Будем исследовать {len(theorems)} теорем")

        explorer = LeanNavigatorExplorer(
            dojo=dojo, rag=rag,
            max_steps=max_steps, max_time=max_time,
            verbose=verbose,
        )

        for i, thm in enumerate(theorems):
            print(f"\n[{i + 1}/{len(theorems)}] {thm.name}")

            try:
                result = explorer.explore(
                    goal_expr=thm.goal_expr,
                    theorem_name=thm.name,
                    theorem_code=thm.goal_state,
                    exit_on_finish=False,
                )

                all_pairs.extend(result.pairs)
                theorem_results.append({
                    "theorem": thm.name,
                    "proven": result.theorem_proven,
                    "verified": result.verified,
                    "states": result.n_states,
                    "steps": result.n_steps,
                    "pairs": len(result.pairs),
                    "proofs_found": result.n_proofs_found,
                    "proofs_verified": result.n_proofs_verified,
                    "proof_length": len(result.proof_tactics) if result.proof_tactics else 0,
                    "time": result.elapsed,
                })

                # Статус: ✓ verified, ⚠ proven but not verified, ○ not proven
                if result.verified:
                    status = "✓"
                    verify_str = f"verified={result.n_proofs_verified}/{result.n_proofs_found}"
                elif result.theorem_proven:
                    status = "⚠"
                    verify_str = "VERIFY_FAIL"
                else:
                    status = "○"
                    verify_str = ""
                
                print(f"  {status} states={result.n_states}, pairs={len(result.pairs)}, "
                      f"proven={'yes' if result.theorem_proven else 'no'}"
                      + (f", {verify_str}" if verify_str else "") +
                      f", time={result.elapsed:.1f}s")

            except Exception as e:
                print(f"  ✗ Ошибка: {str(e)[:80]}")
                theorem_results.append({
                    "theorem": thm.name, "proven": False,
                    "error": str(e), "pairs": 0,
                })

    total_time = time.time() - total_start

    # === Итоги ===
    proofs_found = sum(1 for r in theorem_results if r.get("proven"))
    proofs_verified = sum(1 for r in theorem_results if r.get("verified"))
    verify_failed = sum(1 for r in theorem_results
                        if r.get("proven") and not r.get("verified"))
    total_pairs = len(all_pairs)

    summary = {
        "total_theorems": len(theorems),
        "proofs_found": proofs_found,
        "proofs_verified": proofs_verified,
        "verify_failed": verify_failed,
        "total_pairs": total_pairs,
        "total_time": total_time,
        "unique_tactics": len(set(p.tactic for p in all_pairs)) if all_pairs else 0,
        "theorem_results": theorem_results,
    }

    print("\n" + "=" * 60)
    print("ИТОГИ LeanNavigator")
    print("=" * 60)
    print(f"  Теорем исследовано: {summary['total_theorems']}")
    print(f"  Доказательств найдено: {summary['proofs_found']}")
    print(f"  Доказательств верифицировано: {summary['proofs_verified']}")
    if verify_failed > 0:
        print(f"  ⚠ FALSE POSITIVE (не прошли replay): {verify_failed}")
    print(f"  Training pairs: {summary['total_pairs']}")
    print(f"  Уникальных тактик: {summary['unique_tactics']}")
    print(f"  Общее время: {total_time:.1f}s ({total_time / 60:.1f} мин)")

    # Сохраняем
    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        pairs_path = Path(output_dir) / "training_pairs.jsonl"
        with open(pairs_path, 'w') as f:
            for pair in all_pairs:
                record = {
                    "state": pair.state,
                    "tactic": pair.tactic,
                    "next_state": pair.next_state,
                    "distance_to_proof": pair.distance_to_proof,
                    "theorem_name": pair.theorem_name,
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"  Данные: {pairs_path}")

        with open(Path(output_dir) / "summary.json", 'w') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)

    return all_pairs, summary
