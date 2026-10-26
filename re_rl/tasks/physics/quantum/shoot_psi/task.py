"""ShootPsiTask — интегрирование стационарного уравнения Шрёдингера.

В единицах, где шаг сетки и ħ²/2m равны 1, вторая производная равна (V-E)ψ.
Правый край должен обратиться в нуль, если энергия собственная.
Число внутренних узлов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def shoot_trace(potential: Sequence[int], energy: int) -> List[int]:
    previous = 0
    current = 1
    trace = []
    for value in potential:
        nxt = 2 * current - previous + (value - energy) * current
        trace.append(nxt)
        previous, current = current, nxt
    return trace


class ShootPsiTask(BaseMathTask):
    TASK_TYPE = "shoot_psi"
    TASK_TYPES = ["edge", "inner"]

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
        self.potential = [random.randint(-2, 3) for _ in range(self.n)]
        self.energy = random.randint(0, 4)
        self.trace = shoot_trace(self.potential, self.energy)
        self.edge = self.trace[-1]
        self.inner = self.trace[-2]
        self.answer = self.edge if self.task_type == "edge" else self.inner
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return " ".join(str(value) for value in self.potential)

    def _descr(self, language):
        key = "s0" if self.task_type == "edge" else "s1"
        return texts.t(key, language, n=self.n, potential=self._listing(), energy=self.energy)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value)
            for index, value in enumerate(self.trace, 2)
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
