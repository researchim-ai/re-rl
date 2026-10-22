"""MixChainTask — несколько замен части раствора.

Объём сосуда не меняется. Доли и концентрации подобраны так, чтобы процент оставался целым.
Число замен растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_VOLUMES = [4, 6, 8, 10, 12, 20, 24, 30]


def replace_once(volume: int, current: int) -> Tuple[int, int, int]:
    outs = [item for item in range(1, volume) if volume % item == 0] or [volume]
    random.shuffle(outs)
    for out in outs:
        options = []
        for added in range(0, 101):
            if (out * (added - current)) % volume != 0:
                continue
            nxt = ((volume - out) * current + out * added) // volume
            if 0 <= nxt <= 100:
                options.append((added, nxt))
        if options:
            added, nxt = random.choice(options)
            return out, added, nxt
    return volume, current, current


class MixChainTask(BaseMathTask):
    TASK_TYPE = "mix_chain"
    TASK_TYPES = ["final"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "v": 6}, 2: {"n": 2, "v": 8}, 3: {"n": 3, "v": 10},
        4: {"n": 3, "v": 12}, 5: {"n": 4, "v": 12}, 6: {"n": 5, "v": 20},
        7: {"n": 6, "v": 20}, 8: {"n": 7, "v": 24}, 9: {"n": 8, "v": 24},
        10: {"n": 10, "v": 30},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = "final"
        self.augment = augment
        self.n = max(2, int(p["n"]))
        allowed = [item for item in _VOLUMES if item <= int(p["v"])] or [4]
        self.volume = random.choice(allowed)
        self.start = random.randint(0, 100)
        self.current = self.start
        self.steps: List[Dict[str, int]] = []
        for _ in range(self.n):
            out, added, nxt = replace_once(self.volume, self.current)
            self.steps.append({"out": out, "added": added, "before": self.current, "after": nxt})
            self.current = nxt
        self.answer = self.current
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        parts = [
            texts.t("s1", language, i=i, out=step["out"], added=step["added"])
            for i, step in enumerate(self.steps, 1)
        ]
        return texts.t(
            "s0", language, volume=self.volume, start=self.start, n=self.n, ops=" ".join(parts),
        )

    def solve(self):
        steps = []
        for index, step in enumerate(self.steps, 1):
            steps.append(texts.t(
                "s2", self.language, i=index, volume=self.volume, before=step["before"],
                out=step["out"], added=step["added"], after=step["after"],
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
