"""UndoRegTask — регистр с отменой.

Команда set кладёт текущее значение в стопку и пишет новое. Команда undo достаёт прошлое.
Пустая стопка отмену игнорирует. Число команд растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Command = Tuple[str, int]


def undo_trace(commands: Sequence[Command]) -> List[Tuple[int, int]]:
    register = 0
    stack: List[int] = []
    trace = []
    for kind, value in commands:
        if kind == "set":
            stack.append(register)
            register = value
        elif stack:
            register = stack.pop()
        trace.append((register, len(stack)))
    return trace


class UndoRegTask(BaseMathTask):
    TASK_TYPE = "undo_reg"
    TASK_TYPES = ["value", "depth"]

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
        self.commands = []
        depth = 0
        for _ in range(self.n):
            if depth == 0 or random.random() < 0.65:
                self.commands.append(("set", random.randint(1, 9)))
                depth += 1
            else:
                self.commands.append(("undo", 0))
                depth -= 1
        self.trace = undo_trace(self.commands)
        self.value, self.depth = self.trace[-1]
        self.answer = self.value if self.task_type == "value" else self.depth
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        parts = []
        for kind, value in self.commands:
            parts.append(texts.t("s4" if kind == "set" else "s5", language, value=value))
        listing = "; ".join(parts)
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = []
        for index, ((kind, value), (register, depth)) in enumerate(zip(self.commands, self.trace), 1):
            phrase = texts.t("s4" if kind == "set" else "s5", self.language, value=value)
            steps.append(texts.t("s2", self.language, i=index, phrase=phrase, value=register, depth=depth))
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
