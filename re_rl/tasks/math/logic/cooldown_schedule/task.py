"""CooldownScheduleTask — задачи в заданном порядке с паузой между одинаковыми.

Порядок менять нельзя. Если та же задача встречалась меньше чем c слотов назад, вставляются пустые слоты.
Число задач растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class CooldownScheduleTask(BaseMathTask):
    TASK_TYPE = "cooldown_schedule"
    TASK_TYPES = ["time", "idles"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "c": 1, "k": 2}, 2: {"n": 3, "c": 1, "k": 2},
        3: {"n": 4, "c": 2, "k": 2}, 4: {"n": 4, "c": 2, "k": 3},
        5: {"n": 5, "c": 2, "k": 3}, 6: {"n": 6, "c": 2, "k": 3},
        7: {"n": 7, "c": 3, "k": 3}, 8: {"n": 8, "c": 3, "k": 4},
        9: {"n": 9, "c": 3, "k": 4}, 10: {"n": 10, "c": 4, "k": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.cooldown = max(1, int(p["c"]))
        kinds = max(1, int(p["k"]))
        self.tasks = [random.randint(1, kinds) for _ in range(self.n)]
        self.trace: List[Dict[str, int]] = []
        clock = 0
        self.idles = 0
        last: Dict[int, int] = {}
        for task_id in self.tasks:
            idle = 0
            if task_id in last:
                earliest = last[task_id] + self.cooldown + 1
                if clock + 1 < earliest:
                    idle = earliest - (clock + 1)
                    self.idles += idle
                    clock += idle
            clock += 1
            last[task_id] = clock
            self.trace.append({"task": task_id, "idle": idle, "slot": clock})
        self.time = clock
        self.answer = self.time if self.task_type == "time" else self.idles
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(item) for item in self.tasks)
        key = "s0" if self.task_type == "time" else "s1"
        return texts.t(key, language, n=self.n, cooldown=self.cooldown, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=i, task=item["task"], idle=item["idle"], slot=item["slot"])
            for i, item in enumerate(self.trace, 1)
        ]
        steps.append(texts.t("s3", self.language, time=self.time, idles=self.idles))
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
