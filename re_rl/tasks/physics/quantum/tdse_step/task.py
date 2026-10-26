"""TdseStepTask — явный шаг временного уравнения Шрёдингера.

При ħ = 1 действительная часть растёт на H от мнимой, мнимая убывает на H от прежней действительной.
Явный шаг не сохраняет норму. Число шагов и узлов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _apply_all(psi: Sequence[int], potential: Sequence[int]) -> List[int]:
    acted = []
    for index, center in enumerate(psi):
        left = psi[index - 1] if index else 0
        right = psi[index + 1] if index + 1 < len(psi) else 0
        acted.append(-left + 2 * center - right + potential[index] * center)
    return acted


def tdse_trace(real: Sequence[int], imag: Sequence[int], potential: Sequence[int],
               ticks: int) -> List[Tuple[int, int]]:
    real_part = list(real)
    imag_part = list(imag)
    trace = []
    for _ in range(ticks):
        real_action = _apply_all(real_part, potential)
        imag_action = _apply_all(imag_part, potential)
        real_part = [value + action for value, action in zip(real_part, imag_action)]
        imag_part = [value - action for value, action in zip(imag_part, real_action)]
        norm = sum(value * value for value in real_part) + sum(value * value for value in imag_part)
        trace.append((norm, sum(real_part)))
    return trace


class TdseStepTask(BaseMathTask):
    TASK_TYPE = "tdse_step"
    TASK_TYPES = ["norm", "real"]

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
        self.real_part = [random.randint(-1, 1) for _ in range(self.n)]
        self.imag_part = [random.randint(-1, 1) for _ in range(self.n)]
        if not any(self.real_part) and not any(self.imag_part):
            self.real_part[0] = 1
        self.potential = [random.randint(0, 2) for _ in range(self.n)]
        self.trace = tdse_trace(self.real_part, self.imag_part, self.potential, self.n)
        self.norm = self.trace[-1][0]
        self.real_sum = self.trace[-1][1]
        self.answer = self.norm if self.task_type == "norm" else self.real_sum
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _row(self, values: Sequence[int]) -> str:
        return " ".join(str(value) for value in values)

    def _descr(self, language):
        key = "s0" if self.task_type == "norm" else "s1"
        return texts.t(
            key, language, n=self.n, real=self._row(self.real_part),
            imag=self._row(self.imag_part), potential=self._row(self.potential),
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, norm=norm, real=real_sum)
            for index, (norm, real_sum) in enumerate(self.trace, 1)
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
