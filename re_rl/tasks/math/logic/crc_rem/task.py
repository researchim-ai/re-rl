"""CrcRemTask — остаток контрольной суммы в регистре из четырёх битов.

Перед сдвигом запоминается старший бит. Если он был равен 1, после сдвига регистр складывается с маской по модулю 2.
Число битов сообщения растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_MASKS = (1, 3, 5, 7, 9, 11, 13, 15)


def crc_trace(bits: Sequence[int], mask: int) -> List[Tuple[int, int]]:
    reg = 0
    xors = 0
    trace = []
    for bit in bits:
        outgoing = (reg >> 3) & 1
        reg = ((reg << 1) | bit) & 15
        if outgoing:
            reg ^= mask
            xors += 1
        trace.append((reg, xors))
    return trace


class CrcRemTask(BaseMathTask):
    TASK_TYPE = "crc_rem"
    TASK_TYPES = ["rem", "xors"]
    WIDTH = 4

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
        self.mask = random.choice(_MASKS)
        self.trace = crc_trace(self.bits, self.mask)
        self.rem = self.trace[-1][0]
        self.xors = self.trace[-1][1]
        self.answer = self.rem if self.task_type == "rem" else self.xors
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        bits = ", ".join(str(bit) for bit in self.bits)
        key = "s0" if self.task_type == "rem" else "s1"
        return texts.t(key, language, n=self.n, bits=bits, mask=self.mask, width=self.WIDTH)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, bit=bit, reg=reg, xors=xors)
            for index, (bit, (reg, xors)) in enumerate(zip(self.bits, self.trace), 1)
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
