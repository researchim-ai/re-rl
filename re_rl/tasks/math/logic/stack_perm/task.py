"""StackPermTask — можно ли получить перестановку стеком.

Числа 1..n кладут в стек по возрастанию. Очередное нужное число снимают, если оно на вершине, иначе кладут дальше.
Длина растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def stack_trace(target: Sequence[int]) -> List[Tuple[int, int, int, int]]:
    size = len(target)
    stack: List[int] = []
    nxt = 1
    pops = 0
    ok = 1
    trace = []
    for want in target:
        pushed = 0
        while ok and (not stack or stack[-1] != want) and nxt <= size:
            stack.append(nxt)
            nxt += 1
            pushed += 1
        if stack and stack[-1] == want:
            stack.pop()
            pops += 1
        else:
            ok = 0
        trace.append((pushed, pops, len(stack), ok))
    return trace


class StackPermTask(BaseMathTask):
    TASK_TYPE = "stack_perm"
    TASK_TYPES = ["ok", "pops"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 9},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.target = list(range(1, self.n + 1))
        random.shuffle(self.target)
        self.trace = stack_trace(self.target)
        self.ok = self.trace[-1][3]
        self.pops = self.trace[-1][1]
        self.answer = self.ok if self.task_type == "ok" else self.pops
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        target = ", ".join(str(item) for item in self.target)
        key = "s0" if self.task_type == "ok" else "s1"
        return texts.t(key, language, n=self.n, target=target)

    def solve(self):
        steps = [
            texts.t(
                "s2", self.language, i=index, want=want, pushed=pushed,
                pops=pops, height=height, ok=ok,
            )
            for index, (want, (pushed, pops, height, ok)) in enumerate(zip(self.target, self.trace), 1)
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
