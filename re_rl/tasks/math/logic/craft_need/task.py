"""CraftNeedTask — сбор предметов и один рецепт.

Рецепт забирает по одному предмету 1 и 2 и даёт предмет 3. Нехватки не меняют запас.
Число команд растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Command = Tuple


def craft_trace(commands: Sequence[Command]) -> List[Tuple[int, int, int, int]]:
    stock = [0, 0, 0]
    fails = 0
    trace = []
    for command in commands:
        if command[0] == "gather":
            stock[command[1] - 1] += 1
        elif stock[0] >= 1 and stock[1] >= 1:
            stock[0] -= 1
            stock[1] -= 1
            stock[2] += 1
        else:
            fails += 1
        trace.append((stock[0], stock[1], stock[2], fails))
    return trace


class CraftNeedTask(BaseMathTask):
    TASK_TYPE = "craft_need"
    TASK_TYPES = ["stock", "fails"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 7}, 6: {"n": 8}, 7: {"n": 9}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.commands = []
        have = [0, 0]
        for _ in range(self.n):
            if have[0] and have[1] and random.random() < 0.45:
                self.commands.append(("craft",))
                have[0] -= 1
                have[1] -= 1
            else:
                item = random.randint(1, 3)
                self.commands.append(("gather", item))
                if item <= 2:
                    have[item - 1] += 1
        self.trace = craft_trace(self.commands)
        self.k = random.randint(1, 3)
        self.stock = self.trace[-1][self.k - 1]
        self.fails = self.trace[-1][3]
        self.answer = self.stock if self.task_type == "stock" else self.fails
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _phrase(self, command, language):
        if command[0] == "gather":
            return texts.t("s4", language, item=command[1])
        return texts.t("s5", language)

    def _descr(self, language):
        listing = "; ".join(self._phrase(command, language) for command in self.commands)
        key = "s0" if self.task_type == "stock" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t(
                "s2", self.language, i=index, phrase=self._phrase(command, self.language),
                a=row[0], b=row[1], c=row[2], fails=row[3],
            )
            for index, (command, row) in enumerate(zip(self.commands, self.trace), 1)
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
