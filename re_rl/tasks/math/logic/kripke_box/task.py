"""KripkeBoxTask — необходимость в цепочке миров.

Из мира i есть переход только в i+1. У последнего мира переходов нет, поэтому необходимость там истинна.
В остальных мирах необходимость атома p истинна ровно тогда, когда p истинен в следующем мире.
Число миров растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def box_trace(bits: Sequence[int]) -> List[Tuple[int, int]]:
    total = 0
    trace = []
    last = len(bits) - 1
    for index, _bit in enumerate(bits):
        holds = 1 if index == last or bits[index + 1] == 1 else 0
        total += holds
        trace.append((holds, total))
    return trace


class KripkeBoxTask(BaseMathTask):
    TASK_TYPE = "kripke_box"
    TASK_TYPES = ["boxes", "here"]

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
        self.bits = [random.randint(0, 1) for _ in range(self.n)]
        self.trace = box_trace(self.bits)
        self.boxes = self.trace[-1][1]
        self.k = random.randint(1, self.n)
        self.here = self.trace[self.k - 1][0]
        self.answer = self.boxes if self.task_type == "boxes" else self.here
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        bits = ", ".join(str(bit) for bit in self.bits)
        key = "s0" if self.task_type == "boxes" else "s1"
        return texts.t(key, language, n=self.n, bits=bits, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, bit=bit, holds=holds, total=total)
            for index, (bit, (holds, total)) in enumerate(zip(self.bits, self.trace), 1)
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
