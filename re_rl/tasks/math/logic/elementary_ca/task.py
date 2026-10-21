"""Симуляция автоматов и клеточных систем.

- DFASimulationTask: принимает ли ДКА заданную строку;
- TuringMachineTask: число единиц на ленте после N шагов машины Тьюринга;
- GameOfLifeTask: состояние поля «Жизни» после k шагов;
- ElementaryCATask: строка одномерного клеточного автомата после k шагов.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from typing import Any, ClassVar, Dict, List, Optional
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.math.logic.automata_sim_shared.base import _SimBase

class ElementaryCATask(_SimBase):
    TASK_TYPE = "elementary_ca"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"L": 5, "k": 1}, 2: {"L": 6, "k": 1}, 3: {"L": 7, "k": 2}, 4: {"L": 7, "k": 2},
        5: {"L": 9, "k": 2}, 6: {"L": 9, "k": 3}, 7: {"L": 11, "k": 3}, 8: {"L": 11, "k": 4},
        9: {"L": 13, "k": 4}, 10: {"L": 15, "k": 5},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.L, self.k = int(p["L"]), int(p["k"])
        self.rule = random.choice([30, 90, 110, 54, 150, 60])
        self.augment = augment
        self.row0 = [random.randint(0, 1) for _ in range(self.L)]
        self.row = self.row0[:]
        for _ in range(self.k):
            self.row = self._step(self.row)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _step(self, row):
        L = self.L
        new = [0] * L
        for i in range(L):
            left = row[i - 1] if i - 1 >= 0 else 0
            mid = row[i]
            right = row[i + 1] if i + 1 < L else 0
            idx = (left << 2) | (mid << 1) | right
            new[i] = (self.rule >> idx) & 1
        return new

    def _descr(self, language):
        r0 = "".join(map(str, self.row0))
        return ((texts.t('s0', language, rule=self.rule, r0=r0, k=self.k, L=self.L)))

    def solve(self):
        self.solution_steps = [
            ((texts.t('s1', self.language, rule=self.rule))),
            ((texts.t('s2', self.language, v0=''.join(map(str, self.row))))),
        ]
        self.final_answer = " ".join(map(str, self.row))

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        ints = [x for x in U.parse_ints(prediction) if x in (0, 1)]
        if len(ints) < self.L:
            return 0.0
        return 1.0 if ints[-self.L:] == self.row else 0.0
