"""ReduceRhoTask — частичный след чистого состояния двух частиц.

Вторая частица суммируется. Диагональ редуцированной матрицы — суммы квадратов,
вне диагонали — суммы произведений. Чистота Tr(ρ²) меньше квадрата полной нормы, если есть запутанность.
Число базисных состояний второй частицы растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def rho_accum(row0: Sequence[int], row1: Sequence[int]) -> List[Tuple[int, int, int]]:
    pop0 = pop1 = coh = 0
    trace = []
    for left, right in zip(row0, row1):
        pop0 += left * left
        pop1 += right * right
        coh += left * right
        purity = pop0 * pop0 + pop1 * pop1 + 2 * coh * coh
        trace.append((pop0, coh, purity))
    return trace


class ReduceRhoTask(BaseMathTask):
    TASK_TYPE = "reduce_rho"
    TASK_TYPES = ["pop", "purity"]

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
        self.row0 = [random.randint(-2, 2) for _ in range(self.n)]
        self.row1 = [random.randint(-2, 2) for _ in range(self.n)]
        if not any(self.row0) and not any(self.row1):
            self.row0[0] = 1
        self.trace = rho_accum(self.row0, self.row1)
        self.pop = self.trace[-1][0]
        self.purity = self.trace[-1][2]
        self.answer = self.pop if self.task_type == "pop" else self.purity
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _row(self, values: Sequence[int]) -> str:
        return " ".join(str(value) for value in values)

    def _descr(self, language):
        key = "s0" if self.task_type == "pop" else "s1"
        return texts.t(key, language, n=self.n, row0=self._row(self.row0), row1=self._row(self.row1))

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, pop=pop, coh=coh, purity=purity)
            for index, (pop, coh, purity) in enumerate(self.trace, 1)
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
