"""CheckpointRollTask — одна сохранённая отметка значения.

Новая отметка заменяет старую. Возврат без отметки ставит ноль.
Число команд растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Optional, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Command = Tuple


def checkpoint_trace(commands: Sequence[Command]) -> List[Tuple[int, int]]:
    value = 0
    mark: Optional[int] = None
    saves = 0
    trace = []
    for command in commands:
        if command[0] == "add":
            value += command[1]
        elif command[0] == "mark":
            mark = value
            saves += 1
        else:
            value = 0 if mark is None else mark
        trace.append((value, saves))
    return trace


class CheckpointRollTask(BaseMathTask):
    TASK_TYPE = "checkpoint_roll"
    TASK_TYPES = ["value", "saves"]

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
        for _ in range(self.n):
            roll = random.random()
            if roll < 0.5:
                self.commands.append(("add", random.randint(-3, 4)))
            elif roll < 0.75:
                self.commands.append(("mark",))
            else:
                self.commands.append(("roll",))
        self.trace = checkpoint_trace(self.commands)
        self.value, self.saves = self.trace[-1]
        self.answer = self.value if self.task_type == "value" else self.saves
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _phrase(self, command, language):
        if command[0] == "add":
            return texts.t("s4", language, value=command[1])
        if command[0] == "mark":
            return texts.t("s5", language)
        return texts.t("s6", language)

    def _descr(self, language):
        listing = "; ".join(self._phrase(command, language) for command in self.commands)
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t(
                "s2", self.language, i=index, phrase=self._phrase(command, self.language),
                value=value, saves=saves,
            )
            for index, (command, (value, saves)) in enumerate(zip(self.commands, self.trace), 1)
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
