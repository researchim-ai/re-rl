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

class DFASimulationTask(_SimBase):
    TASK_TYPE = "dfa_simulation"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 2, "L": 3}, 2: {"m": 2, "L": 4}, 3: {"m": 3, "L": 5}, 4: {"m": 3, "L": 6},
        5: {"m": 3, "L": 7}, 6: {"m": 4, "L": 8}, 7: {"m": 4, "L": 9}, 8: {"m": 4, "L": 10},
        9: {"m": 5, "L": 12}, 10: {"m": 5, "L": 14},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.m, self.L = int(p["m"]), int(p["L"])
        self.alphabet = ["a", "b"]
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.delta = {s: {sym: random.randrange(self.m) for sym in self.alphabet}
                      for s in range(self.m)}
        self.accepting = set(s for s in range(self.m) if random.random() < 0.5)
        if not self.accepting:
            self.accepting = {random.randrange(self.m)}
        self.word = "".join(random.choice(self.alphabet) for _ in range(self.L))
        self._answer = self._run()

    def _run(self):
        s = 0
        for ch in self.word:
            s = self.delta[s][ch]
        return s in self.accepting

    def _descr(self, language):
        trans = "; ".join(f"δ({s},{sym})={self.delta[s][sym]}"
                          for s in range(self.m) for sym in self.alphabet)
        acc = ", ".join(map(str, sorted(self.accepting)))
        return ((texts.t('s0', language, v0=self.m - 1, acc=acc, trans=trans, word=self.word)))

    def solve(self):
        self.solution_steps = [
            ((texts.t('s3', self.language))),
            ((texts.t('s4', self.language) if self._answer else texts.t('s5', self.language))),
        ]
        self.final_answer = (texts.t('s1', self.language) if self._answer else texts.t('s2', self.language))

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_bool(prediction, bool(self._answer))
