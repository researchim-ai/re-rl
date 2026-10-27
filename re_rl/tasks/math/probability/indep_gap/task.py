"""IndepGapTask — дефект независимости таблицы 2 на 2.

Каждое наблюдение — пара битов. Дефект равен N на число единиц-единиц минус произведение маргиналов.
Его модуль один и тот же для всех четырёх клеток.
Число наблюдений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Bit = Tuple[int, int]


def indep_trace(bits: Sequence[Bit]) -> List[Tuple[int, int]]:
    count = both = row = col = row_only = 0
    trace = []
    for left, right in bits:
        if left not in (0, 1) or right not in (0, 1):
            raise RuntimeError("cell mismatch")
        count += 1
        if left == 1 and right == 1:
            both += 1
        if left == 1 and right == 0:
            row_only += 1
        if left == 1:
            row += 1
        if right == 1:
            col += 1
        signed = count * both - row * col
        other = count * row_only - row * (count - col)
        if other != -signed:
            raise RuntimeError("cell mismatch")
        trace.append((signed, abs(signed)))
    return trace


class IndepGapTask(BaseMathTask):
    TASK_TYPE = "indep_gap"
    TASK_TYPES = ["signed", "gap"]

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
        self.bits = [(random.randint(0, 1), random.randint(0, 1)) for _ in range(self.n)]
        self.trace = indep_trace(self.bits)
        self.signed = self.trace[-1][0]
        self.gap = self.trace[-1][1]
        self.answer = self.signed if self.task_type == "signed" else self.gap
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(f"{left} {right}" for left, right in self.bits)

    def _descr(self, language):
        key = "s0" if self.task_type == "signed" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, signed=signed, gap=gap)
            for index, (signed, gap) in enumerate(self.trace, 1)
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
