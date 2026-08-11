"""Формальная логика: классификация формул, подсчёт моделей, 3-SAT,
эквивалентность формул, квантифицированные булевы формулы (мини-QBF)."""

import random
from itertools import product
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_VARS = ["p", "q", "r", "s", "t"]


def _rand_formula(vars: List[str], depth: int, max_depth: int):
    if depth <= 0 or (depth < max_depth and random.random() < 0.35):
        return ("var", random.choice(vars))
    op = random.choice(["not", "and", "or", "imp", "iff"])
    if op == "not":
        return ("not", _rand_formula(vars, depth - 1, max_depth))
    return (op, _rand_formula(vars, depth - 1, max_depth),
            _rand_formula(vars, depth - 1, max_depth))


def _eval(node, assign):
    t = node[0]
    if t == "var":
        return assign[node[1]]
    if t == "not":
        return not _eval(node[1], assign)
    a = _eval(node[1], assign)
    b = _eval(node[2], assign)
    if t == "and":
        return a and b
    if t == "or":
        return a or b
    if t == "imp":
        return (not a) or b
    return a == b


def _render(node):
    t = node[0]
    if t == "var":
        return node[1]
    if t == "not":
        return f"¬{_render(node[1])}"
    sym = {"and": "∧", "or": "∨", "imp": "→", "iff": "↔"}[t]
    return f"({_render(node[1])} {sym} {_render(node[2])})"


class _LogicBase(BaseMathTask):
    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task


class TruthTableTask(_LogicBase):
    TASK_TYPE = "truth_table"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"v": 2, "d": 2}, 2: {"v": 2, "d": 2}, 3: {"v": 2, "d": 3}, 4: {"v": 3, "d": 3},
        5: {"v": 3, "d": 3}, 6: {"v": 3, "d": 4}, 7: {"v": 4, "d": 4}, 8: {"v": 4, "d": 4},
        9: {"v": 4, "d": 5}, 10: {"v": 5, "d": 5},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.vars = _VARS[:int(p["v"])]
        self.max_depth = int(p["d"])
        self.augment = augment
        self.formula = _rand_formula(self.vars, self.max_depth, self.max_depth)
        cnt = sum(1 for bits in product([False, True], repeat=len(self.vars))
                  if _eval(self.formula, dict(zip(self.vars, bits))))
        total = 2 ** len(self.vars)
        self.klass = "tautology" if cnt == total else "contradiction" if cnt == 0 else "contingent"
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        return ((f"Классифицируйте формулу над переменными {', '.join(self.vars)}:\n{_render(self.formula)}\n"
                 f"Ответьте одним словом: «тавтология» (всегда истинна), «противоречие» (всегда ложна) "
                 f"или «нейтральная» (истинна не всегда и не никогда).") if ru else
                (f"Classify the formula over variables {', '.join(self.vars)}:\n{_render(self.formula)}\n"
                 f"Answer with one word: 'tautology', 'contradiction', or 'contingent'."))

    def solve(self):
        ru = self.language == "ru"
        words = {"tautology": ("тавтология", "tautology"),
                 "contradiction": ("противоречие", "contradiction"),
                 "contingent": ("нейтральная", "contingent")}
        w = words[self.klass][0 if ru else 1]
        self.solution_steps = [
            ("Строим таблицу истинности и смотрим, при скольких наборах формула истинна." if ru else
             "Build the truth table and see for how many rows the formula is true."),
            (f"Класс формулы: {w}." if ru else f"Formula class: {w}."),
        ]
        self.final_answer = w

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        syn = {
            "tautology": ["тавтология", "тавтологией", "tautology", "всегда истинна", "тождественно истинна"],
            "contradiction": ["противоречие", "противоречием", "contradiction", "всегда ложна", "тождественно ложна"],
            "contingent": ["нейтральная", "contingent", "выполнимая", "иногда"],
        }
        found = {k: U.verify_label(prediction, v) == 1.0 for k, v in syn.items()}
        if sum(found.values()) != 1:
            return 0.0
        return 1.0 if found[self.klass] else 0.0


class ModelCountingTask(_LogicBase):
    TASK_TYPE = "model_counting"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"v": 2, "d": 2}, 2: {"v": 2, "d": 3}, 3: {"v": 3, "d": 3}, 4: {"v": 3, "d": 3},
        5: {"v": 3, "d": 4}, 6: {"v": 4, "d": 4}, 7: {"v": 4, "d": 4}, 8: {"v": 4, "d": 5},
        9: {"v": 5, "d": 5}, 10: {"v": 5, "d": 5},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.vars = _VARS[:int(p["v"])]
        self.max_depth = int(p["d"])
        self.augment = augment
        self.formula = _rand_formula(self.vars, self.max_depth, self.max_depth)
        self._answer = sum(1 for bits in product([False, True], repeat=len(self.vars))
                           if _eval(self.formula, dict(zip(self.vars, bits))))
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        return ((f"Сколько наборов значений переменных {', '.join(self.vars)} делают формулу истинной?\n"
                 f"{_render(self.formula)}") if ru else
                (f"For how many assignments of {', '.join(self.vars)} is the formula true?\n"
                 f"{_render(self.formula)}"))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            (f"Перебираем все {2 ** len(self.vars)} наборов и считаем истинные строки." if ru else
             f"Enumerate all {2 ** len(self.vars)} assignments and count the true rows."),
            (f"Число моделей = {self._answer}." if ru else f"Number of models = {self._answer}."),
        ]
        self.final_answer = str(self._answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))


class ThreeSatTask(_LogicBase):
    TASK_TYPE = "three_sat"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"v": 3, "c": 3}, 2: {"v": 3, "c": 4}, 3: {"v": 4, "c": 5}, 4: {"v": 4, "c": 6},
        5: {"v": 5, "c": 7}, 6: {"v": 5, "c": 9}, 7: {"v": 6, "c": 10}, 8: {"v": 6, "c": 12},
        9: {"v": 7, "c": 14}, 10: {"v": 7, "c": 16},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.nv = int(p["v"])
        self.nc = int(p["c"])
        self.vars = [f"x{i+1}" for i in range(self.nv)]
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        hidden = [random.randint(0, 1) for _ in range(self.nv)]
        self.hidden = hidden
        self.clauses: List[List[Tuple[int, bool]]] = []  # (var_index, is_positive)
        for _ in range(self.nc):
            idxs = random.sample(range(self.nv), min(3, self.nv))
            clause = [(i, bool(random.getrandbits(1))) for i in idxs]
            if not any((hidden[i] == 1) == pos for i, pos in clause):
                i, _ = clause[0]  # чиним, чтобы клауза была истинна под hidden
                clause[0] = (i, hidden[i] == 1)
            self.clauses.append(clause)

    def _clause_str(self, clause):
        lits = [(f"{self.vars[i]}" if pos else f"¬{self.vars[i]}") for i, pos in clause]
        return "(" + " ∨ ".join(lits) + ")"

    def _descr(self, language):
        ru = language == "ru"
        cnf = " ∧ ".join(self._clause_str(c) for c in self.clauses)
        return ((f"Дана КНФ над переменными {', '.join(self.vars)}:\n{cnf}\n"
                 f"Найдите набор значений (0/1), выполняющий формулу. Укажите значения "
                 f"{', '.join(self.vars)} в этом порядке.") if ru else
                (f"Given a CNF over {', '.join(self.vars)}:\n{cnf}\n"
                 f"Find a satisfying 0/1 assignment. List values for {', '.join(self.vars)} in order."))

    def _satisfies(self, assign):
        for clause in self.clauses:
            if not any((assign[i] == 1) == pos for i, pos in clause):
                return False
        return True

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Каждая клауза должна содержать хотя бы один истинный литерал; подбираем значения." if ru else
             "Each clause needs at least one true literal; pick values accordingly."),
            (f"Подходит набор: {', '.join(f'{v}={b}' for v, b in zip(self.vars, self.hidden))}." if ru else
             f"A satisfying assignment: {', '.join(f'{v}={b}' for v, b in zip(self.vars, self.hidden))}."),
        ]
        self.final_answer = " ".join(str(b) for b in self.hidden)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        ints = U.parse_ints(prediction)
        bits = [x for x in ints if x in (0, 1)]
        if len(bits) < self.nv:
            return 0.0
        assign = bits[-self.nv:]
        return 1.0 if self._satisfies(assign) else 0.0


class LogicalEquivalenceTask(_LogicBase):
    TASK_TYPE = "logical_equivalence"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"v": 2, "d": 2}, 2: {"v": 2, "d": 2}, 3: {"v": 2, "d": 3}, 4: {"v": 3, "d": 3},
        5: {"v": 3, "d": 3}, 6: {"v": 3, "d": 4}, 7: {"v": 4, "d": 4}, 8: {"v": 4, "d": 4},
        9: {"v": 4, "d": 5}, 10: {"v": 5, "d": 5},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.vars = _VARS[:int(p["v"])]
        self.max_depth = int(p["d"])
        self.augment = augment
        self.f1 = _rand_formula(self.vars, self.max_depth, self.max_depth)
        # С вероятностью 50% делаем вторую формулу эквивалентной (лёгкое преобразование).
        if random.random() < 0.5:
            self.f2 = self._maybe_transform(self.f1)
        else:
            self.f2 = _rand_formula(self.vars, self.max_depth, self.max_depth)
        self._answer = all(_eval(self.f1, dict(zip(self.vars, bits))) ==
                           _eval(self.f2, dict(zip(self.vars, bits)))
                           for bits in product([False, True], repeat=len(self.vars)))
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _maybe_transform(self, node):
        # двойное отрицание / коммутативность — сохраняют эквивалентность
        choice = random.random()
        if choice < 0.4:
            return ("not", ("not", node))
        if choice < 0.7 and node[0] in ("and", "or"):
            return (node[0], node[2], node[1])
        return node

    def _descr(self, language):
        ru = language == "ru"
        return ((f"Эквивалентны ли две формулы над {', '.join(self.vars)} (совпадают на всех наборах)?\n"
                 f"A: {_render(self.f1)}\nB: {_render(self.f2)}\nОтветьте да/нет.") if ru else
                (f"Are the two formulas over {', '.join(self.vars)} equivalent (equal on all assignments)?\n"
                 f"A: {_render(self.f1)}\nB: {_render(self.f2)}\nAnswer yes/no."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Сравниваем значения обеих формул на всех наборах переменных." if ru else
             "Compare both formulas' values across all assignments."),
            ((("Значения совпадают всюду — эквивалентны." if self._answer else
               "Есть набор с разными значениями — не эквивалентны.")) if ru else
             (("They agree everywhere — equivalent." if self._answer else
               "Some assignment differs — not equivalent."))),
        ]
        self.final_answer = ("да" if self._answer else "нет") if ru else ("yes" if self._answer else "no")

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_bool(prediction, bool(self._answer))


class QBFTask(_LogicBase):
    TASK_TYPE = "qbf"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"v": 2, "d": 2}, 2: {"v": 2, "d": 2}, 3: {"v": 3, "d": 3}, 4: {"v": 3, "d": 3},
        5: {"v": 3, "d": 3}, 6: {"v": 4, "d": 3}, 7: {"v": 4, "d": 4}, 8: {"v": 4, "d": 4},
        9: {"v": 5, "d": 4}, 10: {"v": 5, "d": 5},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.vars = _VARS[:int(p["v"])]
        self.max_depth = int(p["d"])
        self.augment = augment
        self.quant = [random.choice(["A", "E"]) for _ in self.vars]  # A=∀, E=∃
        self.matrix = _rand_formula(self.vars, self.max_depth, self.max_depth)
        self._answer = self._eval_qbf(0, {})
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _eval_qbf(self, i, assign):
        if i == len(self.vars):
            return _eval(self.matrix, assign)
        v = self.vars[i]
        results = []
        for val in (False, True):
            assign[v] = val
            results.append(self._eval_qbf(i + 1, assign))
        del assign[v]
        return all(results) if self.quant[i] == "A" else any(results)

    def _descr(self, language):
        ru = language == "ru"
        prefix = " ".join((("∀" if q == "A" else "∃") + v) for q, v in zip(self.quant, self.vars))
        return ((f"Истинна ли квантифицированная булева формула?\n{prefix}: {_render(self.matrix)}\n"
                 f"(∀ — «для всех», ∃ — «существует»). Ответьте да/нет.") if ru else
                (f"Is the quantified boolean formula true?\n{prefix}: {_render(self.matrix)}\n"
                 f"(∀ — 'for all', ∃ — 'exists'). Answer yes/no."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Раскрываем кванторы слева направо: ∀ требует истинности при обоих значениях, ∃ — хотя бы при одном." if ru else
             "Expand quantifiers left to right: ∀ needs both values true, ∃ needs at least one."),
            ((("Формула истинна." if self._answer else "Формула ложна.")) if ru else
             (("The formula is true." if self._answer else "The formula is false."))),
        ]
        self.final_answer = ("да" if self._answer else "нет") if ru else ("yes" if self._answer else "no")

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_bool(prediction, bool(self._answer))
