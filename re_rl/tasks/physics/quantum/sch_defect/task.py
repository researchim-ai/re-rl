"""SchDefectTask — невязка стационарного уравнения Шрёдингера.

Невязка узла равна действию гамильтониана минус пробная энергия, умноженная на волновую функцию.
Сумма квадратов невязок равна нулю только у собственной функции.
Число узлов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _apply(psi: Sequence[int], potential: Sequence[int], index: int) -> int:
    left = psi[index - 1] if index else 0
    right = psi[index + 1] if index + 1 < len(psi) else 0
    center = psi[index]
    return -left + 2 * center - right + potential[index] * center


def defect_trace(psi: Sequence[int], potential: Sequence[int], energy: int) -> List[Tuple[int, int]]:
    squares = 0
    trace = []
    for index, value in enumerate(psi):
        residual = _apply(psi, potential, index) - energy * value
        squares += residual * residual
        trace.append((residual, squares))
    return trace


class SchDefectTask(BaseMathTask):
    TASK_TYPE = "sch_defect"
    TASK_TYPES = ["site", "defect"]

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
        self.psi = [random.randint(-2, 2) for _ in range(self.n)]
        if not any(self.psi):
            self.psi[0] = 1
        self.potential = [random.randint(-2, 3) for _ in range(self.n)]
        self.energy = random.randint(-1, 4)
        self.k = random.randint(1, self.n)
        self.trace = defect_trace(self.psi, self.potential, self.energy)
        self.site = self.trace[self.k - 1][0]
        self.defect = self.trace[-1][1]
        self.answer = self.site if self.task_type == "site" else self.defect
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _row(self, values: Sequence[int]) -> str:
        return " ".join(str(value) for value in values)

    def _descr(self, language):
        key = "s0" if self.task_type == "site" else "s1"
        return texts.t(
            key, language, n=self.n, psi=self._row(self.psi),
            potential=self._row(self.potential), energy=self.energy, k=self.k,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, residual=residual, defect=defect)
            for index, (residual, defect) in enumerate(self.trace, 1)
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
