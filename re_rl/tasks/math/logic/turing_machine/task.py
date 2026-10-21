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

class TuringMachineTask(_SimBase):
    TASK_TYPE = "turing_machine"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"states": 2, "L": 3, "steps": 4}, 2: {"states": 2, "L": 3, "steps": 6},
        3: {"states": 2, "L": 4, "steps": 8}, 4: {"states": 3, "L": 4, "steps": 10},
        5: {"states": 3, "L": 5, "steps": 12}, 6: {"states": 3, "L": 5, "steps": 15},
        7: {"states": 4, "L": 6, "steps": 18}, 8: {"states": 4, "L": 6, "steps": 22},
        9: {"states": 4, "L": 7, "steps": 26}, 10: {"states": 5, "L": 8, "steps": 30},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.nstates, self.L, self.steps = int(p["states"]), int(p["L"]), int(p["steps"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        # transition[(state, read)] = (write, move, next_state); move: +1 (R) / -1 (L)
        self.trans = {}
        for s in range(self.nstates):
            for r in (0, 1):
                self.trans[(s, r)] = (random.randint(0, 1),
                                      random.choice([1, -1]),
                                      random.randrange(self.nstates))
        self.tape0 = [random.randint(0, 1) for _ in range(self.L)]
        self._answer = self._run()

    def _run(self):
        tape = {i: self.tape0[i] for i in range(self.L)}
        pos, state = 0, 0
        for _ in range(self.steps):
            r = tape.get(pos, 0)
            write, move, nxt = self.trans[(state, r)]
            tape[pos] = write
            pos += move
            state = nxt
        return sum(1 for v in tape.values() if v == 1)

    def _descr(self, language):
        rules = "; ".join(
            texts.t('s3', language, s=s, r=r, w=w, v3='R' if mv == 1 else 'L', ns=ns)
            for (s, r), (w, mv, ns) in self.trans.items())
        rules_en = "; ".join(
            f"({s},{r})→(write {w}, {'R' if mv == 1 else 'L'}, state {ns})"
            for (s, r), (w, mv, ns) in self.trans.items())
        tape = "".join(map(str, self.tape0))
        return ((texts.t('s0', language, v0=self.nstates - 1, tape=tape, rules=rules, steps=self.steps)))

    def solve(self):
        self.solution_steps = [
            ((texts.t('s1', self.language))),
            ((texts.t('s2', self.language, _answer=self._answer))),
        ]
        self.final_answer = str(self._answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))
