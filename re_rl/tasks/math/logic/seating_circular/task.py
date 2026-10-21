"""Дедуктивные задачи: логическая сетка соответствий, круговая рассадка,
турнирные подсчёты (круговой и на выбывание)."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from itertools import permutations
from typing import Any, ClassVar, Dict, List, Optional, Tuple
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.math.logic.deduction2_shared.base import _DedBase, _NAMES, _NAMES_EN

class SeatingCircularTask(_DedBase):
    TASK_TYPE = "seating_circular"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 5}, 5: {"n": 5},
        6: {"n": 6}, 7: {"n": 6}, 8: {"n": 6}, 9: {"n": 6}, 10: {"n": 6},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.augment = augment
        self.people = (({"ru": (_NAMES), "en": (_NAMES_EN)}.get(language, (_NAMES_EN))))[:self.n]
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _adjacent(self, order, x, y):
        i = order.index(x)
        n = len(order)
        return order[(i + 1) % n] == y or order[(i - 1) % n] == y

    def _neighbors(self, order, x):
        i = order.index(x)
        n = len(order)
        return {order[(i + 1) % n], order[(i - 1) % n]}

    def _build(self):
        order = self.people[:]
        random.shuffle(order)
        self.true_order = order
        n = self.n
        pos_pairs = [(order[i], order[(i + 1) % n]) for i in range(n)]
        pool = [("next", a, b) for a, b in pos_pairs]
        # несколько отрицаний
        for _ in range(n):
            a, b = random.sample(self.people, 2)
            if not self._adjacent(order, a, b):
                pool.append(("notnext", a, b))
        random.shuffle(pool)

        self.query = random.choice(self.people)
        self.answer_neighbors = self._neighbors(order, self.query)

        clues = []
        for cl in pool:
            clues.append(cl)
            if self._neighbors_unique(clues):
                break
        if not self._neighbors_unique(clues):
            clues = pool
        pruned = clues[:]
        for cl in clues:
            trial = [x for x in pruned if x is not cl]
            if self._neighbors_unique(trial):
                pruned = trial
        random.shuffle(pruned)
        self.clues = pruned

    def _clue_ok(self, cl, order):
        kind, a, b = cl
        if kind == "next":
            return self._adjacent(order, a, b)
        return not self._adjacent(order, a, b)

    def _neighbors_unique(self, clues):
        found = set()
        base = self.people
        for perm in permutations(base[1:]):  # фиксируем первого — убираем вращения
            order = [base[0]] + list(perm)
            if all(self._clue_ok(c, order) for c in clues):
                found.add(frozenset(self._neighbors(order, self.query)))
                if len(found) > 1:
                    return False
        return len(found) == 1

    def _clue_text(self, cl):
        kind, a, b = cl
        if kind == "next":
            return ((texts.t('s3', self.language, a=a, b=b)))
        return ((texts.t('s0', self.language, a=a, b=b)))

    def _descr(self, language):
        head = ((texts.t('s1', language, n=self.n, v1=', '.join(self.people))))
        body = "\n".join(f"- {self._clue_text(c)}" for c in self.clues)
        q = ((texts.t('s2', language, query=self.query)))
        return head + body + q

    def solve(self):
        nb = ", ".join(sorted(self.answer_neighbors))
        self.solution_steps = [
            ((texts.t('s4', self.language))),
            ((texts.t('s5', self.language, query=self.query, nb=nb))),
        ]
        self.final_answer = nb

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        found = set(U.extract_name_sequence(prediction, self.people))
        return 1.0 if self.answer_neighbors.issubset(found) and self.query not in found else 0.0
