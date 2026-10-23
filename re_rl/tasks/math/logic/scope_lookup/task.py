"""ScopeLookupTask — поиск имени во вложенных областях.

Запись видна из внутренней области и из внешних, пока её не перекрыли.
Число команд растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Command = Tuple


def scope_lookup(stack: Sequence[Dict[int, int]], name: int) -> int:
    for scope in reversed(stack):
        if name in scope:
            return scope[name]
    return 0


def scope_trace(commands: Sequence[Command]) -> List[Tuple[int, int, int, int]]:
    stack: List[Dict[int, int]] = [{}]
    trace = []
    for command in commands:
        kind = command[0]
        if kind == "in":
            stack.append({})
        elif kind == "out" and len(stack) > 1:
            stack.pop()
        elif kind == "set":
            stack[-1][command[1]] = command[2]
        trace.append((
            len(stack),
            scope_lookup(stack, 1),
            scope_lookup(stack, 2),
            scope_lookup(stack, 3),
        ))
    return trace


class ScopeLookupTask(BaseMathTask):
    TASK_TYPE = "scope_lookup"
    TASK_TYPES = ["value", "depth"]

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
        depth = 1
        for _ in range(self.n):
            roll = random.random()
            if roll < 0.25 and depth < 4:
                self.commands.append(("in",))
                depth += 1
            elif roll < 0.45 and depth > 1:
                self.commands.append(("out",))
                depth -= 1
            else:
                self.commands.append(("set", random.randint(1, 3), random.randint(1, 9)))
        self.trace = scope_trace(self.commands)
        self.k = random.randint(1, 3)
        self.depth = self.trace[-1][0]
        self.value = self.trace[-1][self.k]
        self.answer = self.value if self.task_type == "value" else self.depth
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _phrase(self, command, language):
        kind = command[0]
        if kind == "in":
            return texts.t("s4", language)
        if kind == "out":
            return texts.t("s5", language)
        return texts.t("s6", language, name=command[1], value=command[2])

    def _descr(self, language):
        listing = "; ".join(self._phrase(command, language) for command in self.commands)
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = []
        for index, (command, row) in enumerate(zip(self.commands, self.trace), 1):
            steps.append(texts.t(
                "s2", self.language, i=index, phrase=self._phrase(command, self.language),
                depth=row[0], value=row[self.k],
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
