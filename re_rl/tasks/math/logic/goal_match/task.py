"""GoalMatchTask — стопка целей закрывается только точным верхом.

Чужая цель считается ошибкой и стопку не меняет. Число команд растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Command = Tuple


def goal_trace(commands: Sequence[Command]) -> List[Tuple[int, int, int]]:
    stack: List[int] = []
    bad = 0
    deepest = 0
    trace = []
    for command in commands:
        if command[0] == "push":
            stack.append(command[1])
        elif stack and stack[-1] == command[1]:
            stack.pop()
        else:
            bad += 1
        deepest = max(deepest, len(stack))
        top = stack[-1] if stack else 0
        trace.append((top, bad, deepest))
    return trace


class GoalMatchTask(BaseMathTask):
    TASK_TYPE = "goal_match"
    TASK_TYPES = ["bad", "top"]

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
        stack: List[int] = []
        for _ in range(self.n):
            if stack and random.random() < 0.45:
                goal = stack[-1] if random.random() < 0.7 else random.randint(1, 4)
                self.commands.append(("close", goal))
                if stack and stack[-1] == goal:
                    stack.pop()
            else:
                goal = random.randint(1, 4)
                self.commands.append(("push", goal))
                stack.append(goal)
        self.trace = goal_trace(self.commands)
        self.top, self.bad, _ = self.trace[-1]
        self.answer = self.bad if self.task_type == "bad" else self.top
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _phrase(self, command, language):
        key = "s4" if command[0] == "push" else "s5"
        return texts.t(key, language, goal=command[1])

    def _descr(self, language):
        listing = "; ".join(self._phrase(command, language) for command in self.commands)
        key = "s0" if self.task_type == "bad" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t(
                "s2", self.language, i=index, phrase=self._phrase(command, self.language),
                top=top, bad=bad,
            )
            for index, (command, (top, bad, _)) in enumerate(zip(self.commands, self.trace), 1)
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
