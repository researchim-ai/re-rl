"""ProbFlowTask — ток вероятности комплексной волны.

Между соседними узлами ток равен u v_соседа минус v u_соседа, в единицах ħ = m = 1.
Число связей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def current_trace(real: Sequence[int], imag: Sequence[int]) -> List[Tuple[int, int]]:
    total = 0
    trace = []
    for index in range(len(real) - 1):
        current = real[index] * imag[index + 1] - imag[index] * real[index + 1]
        total += current
        trace.append((current, total))
    return trace


class ProbFlowTask(BaseMathTask):
    TASK_TYPE = "prob_flow"
    TASK_TYPES = ["bond", "total"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.real_part = [random.randint(-2, 2) for _ in range(self.n + 1)]
        self.imag_part = [random.randint(-2, 2) for _ in range(self.n + 1)]
        self.k = random.randint(1, self.n)
        self.trace = current_trace(self.real_part, self.imag_part)
        self.bond = self.trace[self.k - 1][0]
        self.total = self.trace[-1][1]
        self.answer = self.bond if self.task_type == "bond" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _row(self, values: Sequence[int]) -> str:
        return " ".join(str(value) for value in values)

    def _descr(self, language):
        key = "s0" if self.task_type == "bond" else "s1"
        return texts.t(
            key, language, n=self.n, real=self._row(self.real_part),
            imag=self._row(self.imag_part), k=self.k,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, current=current, total=total)
            for index, (current, total) in enumerate(self.trace, 1)
        ]
        steps.append(texts.common("answer_line", self.language, answer=self.answer))
        self.solution_steps = steps
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
