"""JumpAddTask — команды сложения и прыжка вперёд.

Сложение прибавляет число и идёт дальше. Прыжок перескакивает вперёд на указанное число команд.
Команды за прыжком не выполняются. Число команд растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Op = Tuple[int, int]


def jump_trace(ops: Sequence[Op]) -> List[Tuple[int, int]]:
    size = len(ops)
    executed = [0] * size
    cursor = 0
    guard = 0
    while cursor < size and guard <= size:
        executed[cursor] = 1
        code, arg = ops[cursor]
        cursor += 1 if code == 0 else max(1, arg)
        guard += 1
    acc = 0
    ran = 0
    trace = []
    for index, (code, arg) in enumerate(ops):
        if executed[index]:
            ran += 1
            if code == 0:
                acc += arg
        trace.append((acc, ran))
    return trace


class JumpAddTask(BaseMathTask):
    TASK_TYPE = "jump_add"
    TASK_TYPES = ["acc", "ran"]

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
        self.ops = []
        for _ in range(self.n):
            code = random.randint(0, 1)
            arg = random.randint(1, 4) if code == 0 else random.randint(1, 3)
            self.ops.append((code, arg))
        self.trace = jump_trace(self.ops)
        self.acc = self.trace[-1][0]
        self.ran = self.trace[-1][1]
        self.answer = self.acc if self.task_type == "acc" else self.ran
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{code} {arg}" for code, arg in self.ops)
        key = "s0" if self.task_type == "acc" else "s1"
        return texts.t(key, language, n=self.n, ops=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, code=code, arg=arg, acc=acc, ran=ran)
            for index, ((code, arg), (acc, ran)) in enumerate(zip(self.ops, self.trace), 1)
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
