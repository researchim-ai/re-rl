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


class PantographDojo:
    """
    Обёртка над Pantograph Server для интерактивного proving.
    
    Предоставляет API совместимый с LeanNavigator:
      - run_tac(state, tactic) -> ProofState | ProofFinished | None
    """

    def __init__(self, project_path: str, imports: Optional[List[str]] = None,
                 timeout: int = 5):
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

    def goal_start(self, goal_expr: str) -> Optional[ProofState]:
        """Начинает доказательство цели."""
        try:
            goal_state = self.server.goal_start(goal_expr)
            if not goal_state.goals:
                return ProofFinished()
            pp = "\n".join(str(g) for g in goal_state.goals)
            return ProofState(pp=pp, goal_state=goal_state, goal_id=0)
        except Exception as e:
            return None

    def run_tac(self, state: ProofState, tactic: str):
        """
        Применяет тактику к состоянию.
        
        Returns:
            ProofState — новое состояние
            ProofFinished — доказательство завершено
            None — тактика не применилась (ошибка)
        """
        if not isinstance(state, ProofState) or state.goal_state is None:
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

    def explore(self, goal_expr: str, theorem_name: str = "",
                theorem_code: str = "",
                exit_on_finish: bool = False) -> NavigatorResult:
        """
        Исследует граф переходов для теоремы.
        
        Args:
            goal_expr: Lean-выражение цели (тип теоремы)
            theorem_name: Имя теоремы
            theorem_code: Код формулировки теоремы (для RAG query)
            exit_on_finish: Остановиться при первом ProofFinished
            
        Returns:
            NavigatorResult с графом переходов и training pairs
        """
        start_time = time.time()

        # Инициализация
        state_0 = self.dojo.goal_start(goal_expr)
        if state_0 is None or isinstance(state_0, ProofFinished):
            return NavigatorResult(
                theorem_name=theorem_name,
                state_dict={}, theorem_proven=isinstance(state_0, ProofFinished),
                pairs=[], n_states=0, n_steps=0, elapsed=0,
            )

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

                result = self.dojo.run_tac(curr_state, tactic)
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

        return NavigatorResult(
            theorem_name=theorem_name,
            state_dict=state_dict,
            theorem_proven=theorem_proven,
            pairs=pairs,
            n_states=len(state_dict),
            n_steps=n_steps,
            elapsed=elapsed,
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

    # === Шаг 3: Загрузка теорем ===
    print("\n" + "=" * 60)
    print("Шаг 3: Загрузка теорем для исследования")
    print("=" * 60)

    theorems = load_theorems_from_ast_dir(repo_dir)

    # Фильтруем: нужны теоремы с тактическими доказательствами
    theorems = [t for t in theorems if len(t.tactics) >= 1]

    if max_theorems > 0 and len(theorems) > max_theorems:
        theorems = random.sample(theorems, max_theorems)

    print(f"Будем исследовать {len(theorems)} теорем")

    # === Шаг 4: BFS исследование ===
    print("\n" + "=" * 60)
    print("Шаг 4: BFS исследование через Pantograph")
    print("=" * 60)

    all_pairs = []
    theorem_results = []

    with PantographDojo(project_path=repo_dir, imports=imports) as dojo:
        explorer = LeanNavigatorExplorer(
            dojo=dojo, rag=rag,
            max_steps=max_steps, max_time=max_time,
            verbose=verbose,
        )

        # Пробуем получить полные типы через env_inspect
        resolved = 0
        for thm in theorems:
            full_type = dojo.env_inspect(thm.name)
            if full_type:
                thm.goal_expr = full_type
                resolved += 1
        print(f"  Разрешено типов через env_inspect: {resolved}/{len(theorems)}")

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
                    "states": result.n_states,
                    "steps": result.n_steps,
                    "pairs": len(result.pairs),
                    "time": result.elapsed,
                })

                status = "✓" if result.theorem_proven else "○"
                print(f"  {status} states={result.n_states}, pairs={len(result.pairs)}, "
                      f"proven={'yes' if result.theorem_proven else 'no'}, "
                      f"time={result.elapsed:.1f}s")

            except Exception as e:
                print(f"  ✗ Ошибка: {str(e)[:80]}")
                theorem_results.append({
                    "theorem": thm.name, "proven": False,
                    "error": str(e), "pairs": 0,
                })

    total_time = time.time() - total_start

    # === Итоги ===
    proofs_found = sum(1 for r in theorem_results if r.get("proven"))
    total_pairs = len(all_pairs)

    summary = {
        "total_theorems": len(theorems),
        "proofs_found": proofs_found,
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
