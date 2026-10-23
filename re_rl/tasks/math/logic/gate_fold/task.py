"""GateFoldTask — цепочка логических вентилей.

Накопитель начинает с первого бита. Дальше каждый вентиль соединяет его со следующим битом.
Число вентилей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def apply_gate(op: int, acc: int, bit: int) -> int:
    if op == 0:
        return acc & bit
    if op == 1:
        return acc | bit
    return acc ^ bit


def gate_trace(start: int, ops: Sequence[int], bits: Sequence[int]) -> List[int]:
    acc = start
    trace = []
    for op, bit in zip(ops, bits):
        acc = apply_gate(op, acc, bit)
        trace.append(acc)
    return trace


class GateFoldTask(BaseMathTask):
    TASK_TYPE = "gate_fold"
    TASK_TYPES = ["bit", "highs"]

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
        self.start = random.randint(0, 1)
        self.ops = [random.randint(0, 2) for _ in range(self.n)]
        self.bits = [random.randint(0, 1) for _ in range(self.n)]
        self.trace = gate_trace(self.start, self.ops, self.bits)
        self.bit = self.trace[-1]
        self.highs = sum(self.trace)
        self.answer = self.bit if self.task_type == "bit" else self.highs
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        bits = ", ".join(str(bit) for bit in self.bits)
        ops = ", ".join(str(op) for op in self.ops)
        key = "s0" if self.task_type == "bit" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, bits=bits, ops=ops)

    def solve(self):
        keys = ("s2", "s3", "s4")
        steps = [texts.t("s5", self.language, bit=self.start)]
        for index, (op, bit, acc) in enumerate(zip(self.ops, self.bits, self.trace), 1):
            steps.append(texts.t(keys[op], self.language, i=index, bit=bit, acc=acc))
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
