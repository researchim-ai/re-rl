"""SandpilePathTask — обвалы фишек на дорожке.

Порог клетки равен 2. Две фишки уходят соседям, а с края недостающая фишка теряется.
Обвал всегда у самой левой готовой клетки. В центр кладут 2n фишек.
Число клеток растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def stabilize(length: int, chips: int, cell: int) -> Tuple[List[int], int, int, List[Tuple[int, Tuple[int, ...]]]]:
    heights = [0] * length
    heights[cell] = chips
    lost = 0
    trace: List[Tuple[int, Tuple[int, ...]]] = []
    while True:
        index = next((i for i, value in enumerate(heights) if value >= 2), None)
        if index is None:
            break
        heights[index] -= 2
        if index > 0:
            heights[index - 1] += 1
        else:
            lost += 1
        if index + 1 < length:
            heights[index + 1] += 1
        else:
            lost += 1
        trace.append((index, tuple(heights)))
    return heights, len(trace), lost, trace


class SandpilePathTask(BaseMathTask):
    TASK_TYPE = "sandpile_path"
    TASK_TYPES = ["topples", "remaining"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 9}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(3, int(p["n"]))
        self.chips = 2 * self.n
        self.cell = random.randrange(self.n)
        self.heights, self.topples, self.lost, self.trace = stabilize(self.n, self.chips, self.cell)
        self.remaining = sum(self.heights)
        self.answer = self.topples if self.task_type == "topples" else self.remaining
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "topples" else "s1"
        return texts.t(key, language, n=self.n, cell=self.cell + 1, chips=self.chips)

    def solve(self):
        steps = []
        for index, (cell, heights) in enumerate(self.trace, 1):
            shown = ", ".join(str(value) for value in heights)
            steps.append(texts.t("s2", self.language, i=index, cell=cell + 1, heights=shown))
        steps.append(texts.t(
            "s3", self.language, topples=self.topples, remaining=self.remaining, lost=self.lost,
        ))
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
