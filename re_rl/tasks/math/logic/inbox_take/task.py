"""InboxTakeTask — письма двум агентам и чтение самого старого.

Чтение пустого ящика ничего не забирает. Число команд растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Command = Tuple


def inbox_trace(commands: Sequence[Command]) -> List[Tuple[int, int, int, int]]:
    boxes: List[List[int]] = [[], []]
    trace = []
    for command in commands:
        agent = command[1] - 1
        if command[0] == "send":
            boxes[agent].append(command[2])
        elif boxes[agent]:
            boxes[agent].pop(0)
        fronts = [box[0] if box else 0 for box in boxes]
        counts = [len(box) for box in boxes]
        trace.append((fronts[0], counts[0], fronts[1], counts[1]))
    return trace


class InboxTakeTask(BaseMathTask):
    TASK_TYPE = "inbox_take"
    TASK_TYPES = ["front", "pending"]

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
        counts = [0, 0]
        for _ in range(self.n):
            agent = random.randint(1, 2)
            if counts[agent - 1] and random.random() < 0.4:
                self.commands.append(("take", agent))
                counts[agent - 1] -= 1
            else:
                self.commands.append(("send", agent, random.randint(1, 9)))
                counts[agent - 1] += 1
        self.trace = inbox_trace(self.commands)
        self.k = random.randint(1, 2)
        self.front = self.trace[-1][(self.k - 1) * 2]
        self.pending = self.trace[-1][(self.k - 1) * 2 + 1]
        self.answer = self.front if self.task_type == "front" else self.pending
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _phrase(self, command, language):
        if command[0] == "send":
            return texts.t("s4", language, agent=command[1], value=command[2])
        return texts.t("s5", language, agent=command[1])

    def _descr(self, language):
        listing = "; ".join(self._phrase(command, language) for command in self.commands)
        key = "s0" if self.task_type == "front" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = []
        for index, (command, row) in enumerate(zip(self.commands, self.trace), 1):
            steps.append(texts.t(
                "s2", self.language, i=index, phrase=self._phrase(command, self.language),
                front=row[(self.k - 1) * 2], pending=row[(self.k - 1) * 2 + 1],
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
