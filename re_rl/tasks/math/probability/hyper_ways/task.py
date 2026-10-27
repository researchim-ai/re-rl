"""HyperWaysTask — число гипергеометрических исходов.

Способы выбрать меченые и немеченые считаются по очереди: на шаге i произведение умножается на очередной множитель и делится на i.
Число вынутых шаров растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _choose(total: int, take: int) -> List[int]:
    ways = 1
    steps = []
    for index in range(1, take + 1):
        factor = total - take + index
        if (ways * factor) % index:
            raise RuntimeError("ways mismatch")
        ways = ways * factor // index
        steps.append(ways)
    return steps


def hyper_trace(marked: int, plain: int, take_mark: int, take_plain: int) -> List[Tuple[int, int]]:
    if take_mark < 0 or take_plain < 0 or take_mark > marked or take_plain > plain:
        raise RuntimeError("ways mismatch")
    marked_steps = _choose(marked, take_mark)
    plain_steps = _choose(plain, take_plain)
    choose = marked_steps[-1] if marked_steps else 1
    ways = choose
    trace = [(item, item) for item in marked_steps]
    for item in plain_steps:
        ways = choose * item
        trace.append((ways, choose))
    expect = math.comb(marked, take_mark) * math.comb(plain, take_plain)
    if ways != expect or choose != math.comb(marked, take_mark):
        raise RuntimeError("ways mismatch")
    return trace


class HyperWaysTask(BaseMathTask):
    TASK_TYPE = "hyper_ways"
    TASK_TYPES = ["ways", "choose"]

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
        self.take_mark = random.randint(0, self.n)
        self.take_plain = self.n - self.take_mark
        self.marked = self.take_mark + random.randint(0, 4)
        self.plain = self.take_plain + random.randint(0, 4)
        self.trace = hyper_trace(self.marked, self.plain, self.take_mark, self.take_plain)
        self.ways = self.trace[-1][0]
        self.choose = self.trace[-1][1]
        self.answer = self.ways if self.task_type == "ways" else self.choose
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "ways" else "s1"
        return texts.t(
            key, language, n=self.n, marked=self.marked, plain=self.plain,
            take_mark=self.take_mark, take_plain=self.take_plain,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, ways=ways, choose=choose)
            for index, (ways, choose) in enumerate(self.trace, 1)
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
