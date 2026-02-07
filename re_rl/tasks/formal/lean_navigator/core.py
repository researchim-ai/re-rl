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
from typing import List, Dict, Tuple, Optional, Any, Set
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
except ImportError:
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

MAX_STEPS = 200000
MAX_TACTIC_FROM_TEMPLATE = 50
PENALTY_SEEN_TARGET_MULTIPLIER = 3
MAX_NUM_OUTPUT_PER_STATE = 50
MAX_DISTANCE = 8  # макс расстояние до ProofFinished

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

    combinations = list(itertools.product(*replacement_lists))
    if len(combinations) > max_tactics:
        combinations = random.sample(combinations, max_tactics)

    sentences = []
    for combination in combinations:
        sentence = fixed_parts[0]
        for item, fixed_part in zip(combination, fixed_parts[1:]):
            sentence += item + fixed_part
        sentences.append(sentence)

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
                 timeout: int = 120):
        if not PANTOGRAPH_AVAILABLE:
            raise ImportError("pip install 'git+https://github.com/stanford-centaur/PyPantograph.git'")

        self.project_path = project_path
        self.imports = imports or ["Init"]
        self.timeout = timeout
        self.server = None

    def start(self):
        """Запускает Pantograph сервер."""
        self.server = Server(
            imports=self.imports,
            project_path=self.project_path,
            timeout=self.timeout,
            buffer_limit=10_000_000,  # 10MB — нужно для env_catalog на Mathlib
        )
        return self

    def stop(self):
        """Останавливает сервер."""
        if self.server:
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

    def __init__(self, dojo: PantographDojo, rag: TacticRAG,
                 max_steps: int = MAX_STEPS, max_time: int = 1200,
                 verbose: bool = False):
        self.dojo = dojo
        self.rag = rag
        self.max_steps = max_steps
        self.max_time = max_time
        self.verbose = verbose

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
        """Внутренний BFS — вынесен чтобы explore() мог гарантировать cleanup."""
        state_queue = PriorityQueue()
        # state_dict: key=state.pp, value=(state, [parent_states], [tactics], shortest_path)
        state_dict = {}
        seen_target_freq = {}

        base_complexity = 0
        state_queue.push(state_0,
                         explore_state_complexity(state_0.pp, base_complexity=base_complexity,
                                                   seen_target_freq=seen_target_freq)
                         + random.randint(0, 4))
        base_complexity += 1
        state_dict[state_0.pp] = (state_0, [], [], [])

        n_steps = 0
        theorem_proven = False
        proof_finished_states = []

        while state_queue.size() > 0:
            curr_state = state_queue.pop()
            if not isinstance(curr_state, ProofState):
                continue

            # Классифицируем элементы состояния
            type_of_item, _ = classify_lean_elements(curr_state.pp)

            if self.verbose and n_steps == 0:
                print(f"INIT_STATE: {curr_state.pp}")

            # RAG: получаем шаблоны тактик
            query_text = theorem_code if theorem_code else theorem_name
            suggestions = self.rag.get_similar_templates(
                curr_state.pp, theorem_code=query_text, num_returned=200
            )
            tac_templates = [s[0] for s in suggestions]

            # Добавляем обратные rw тактики
            for tac_template in list(tac_templates):
                inv = get_inverse_tactic(tac_template)
                if inv and inv not in tac_templates:
                    tac_templates.append(inv)

            # Генерируем конкретные тактики из шаблонов
            tactic_set = set()
            for tac_template in tac_templates:
                try:
                    tactics = generate_tactics_from_template(tac_template, type_of_item)
                    for t in tactics:
                        tactic_set.add(t)
                except Exception:
                    continue

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

                result = working_dojo.run_tac(curr_state, tactic)
                if result is None:
                    continue

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
                        _, parent_states, tactics, prefix = state_dict[result.pp]
                        state_dict[result.pp] = (
                            result,
                            parent_states + [curr_state],
                            tactics + [tactic],
                            prefix  # оставляем кратчайший путь
                        )
                        # Обновляем кратчайший путь если нашли короче
                        new_prefix = state_dict[curr_state.pp][3] + [tactic]
                        if len(new_prefix) < len(prefix):
                            state_dict[result.pp] = (
                                result,
                                parent_states + [curr_state],
                                tactics + [tactic],
                                new_prefix
                            )
                    else:
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

            if n_steps > self.max_steps:
                break
            if not theorem_proven and n_steps > self.max_steps / 3:
                break
            if (time.time() - start_time) > self.max_time:
                if self.verbose:
                    print("Max run-time exceeded")
                break

        elapsed = time.time() - start_time

        # Генерируем training pairs
        pairs = self._generate_pairs(state_dict, proof_finished_states, theorem_name)

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

        return NavigatorResult(
            theorem_name=theorem_name,
            state_dict=state_dict,
            theorem_proven=theorem_proven,
            pairs=pairs,
            n_states=len(state_dict),
            n_steps=n_steps,
            elapsed=elapsed,
            verified=verified,
            proof_tactics=proof_tactics,
            n_proofs_found=len(proof_finished_states),
            n_proofs_verified=n_proofs_verified,
        )

    def _generate_pairs(self, state_dict: Dict, proof_finished_states: List[str],
                         theorem_name: str, max_distance: int = MAX_DISTANCE) -> List[TrainingPair]:
        """
        Генерирует training pairs из графа переходов.
        
        Для каждого ProofFinished находим все пути длины ≤ max_distance
        и создаём pairs (state, tactic, next_state, distance_to_proof).
        """
        pairs = []
        seen_pairs: Set[Tuple[str, str]] = set()

        for pf_key in proof_finished_states:
            if pf_key not in state_dict:
                continue
            # Обратный обход от ProofFinished
            self._collect_pairs_recursive(
                pf_key, state_dict, theorem_name,
                pairs, seen_pairs, distance=0, max_distance=max_distance
            )

        return pairs

    def _collect_pairs_recursive(self, state_key: str, state_dict: Dict,
                                  theorem_name: str, pairs: List[TrainingPair],
                                  seen_pairs: Set, distance: int, max_distance: int):
        """Рекурсивно собирает pairs от ProofFinished к предкам."""
        if distance > max_distance:
            return

        state_data = state_dict.get(state_key)
        if state_data is None:
            return

        _, parent_states, tactics, _ = state_data

        for i, (parent, tactic) in enumerate(zip(parent_states, tactics)):
            if not isinstance(parent, ProofState):
                continue

            pair_key = (parent.pp, tactic)
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            # next_state
            if state_key.startswith("ProofFinished"):
                next_state_str = "no goals"
            else:
                next_state_str = state_key  # это pp состояния

            pairs.append(TrainingPair(
                state=parent.pp,
                tactic=tactic,
                next_state=next_state_str,
                distance_to_proof=distance,
                theorem_name=theorem_name,
            ))

            # Рекурсия к предкам
            self._collect_pairs_recursive(
                parent.pp, state_dict, theorem_name,
                pairs, seen_pairs, distance + 1, max_distance
            )


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
        
    Returns:
        Список TracedTheorem с валидными goal_expr
    """
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

    # 2. env_catalog возвращает имена с однобуквенным тегом:
    #    t=theorem, d=def, c=constructor, r=recursor, i=inductive, o=opaque
    #    Берём только теоремы (t) и стрипаем префикс
    theorem_names = [n[1:] for n in all_names if n.startswith('t')]
    print(f"  Теорем (prefix=t): {len(theorem_names)} из {len(all_names)}")

    # 3. Фильтруем внутренние имена
    filtered = [n for n in theorem_names if not _is_internal_name(n)]
    print(f"  После фильтрации: {len(filtered)} (отброшено {len(theorem_names) - len(filtered)} внутренних)")

    # 4. Семплируем больше чем нужно (часть не пройдёт env_inspect / validate)
    sample_size = min(max_theorems * 10, len(filtered))
    sample = random.sample(filtered, sample_size) if len(filtered) > sample_size else filtered

    # 5. Инспектируем типы через env_inspect
    theorems = []
    inspected = 0
    failed = 0
    goal_rejected = 0

    iterator = tqdm(sample, desc="Загрузка типов") if TQDM_AVAILABLE else sample

    for name in iterator:
        if len(theorems) >= max_theorems:
            break
        inspected += 1
        
        # Получаем полную информацию: module, pp, expr
        info = dojo.env_inspect_full(name)
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
            result = dojo.goal_start_expr(name)
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
