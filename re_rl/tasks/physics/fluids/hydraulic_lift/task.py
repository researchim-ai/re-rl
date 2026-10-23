"""HydraulicLiftTask — сила на широком поршне гидравлического пресса.

Выходная сила равна входной, умноженной на широкую площадь и делённой на узкую.
Число нажатий растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Press = Tuple[int, int, int]


def hydraulic_trace(presses: Sequence[Press]) -> List[Tuple[int, int]]:
    total = 0
    trace = []
    for force, narrow, wide in presses:
        output = force * wide // narrow
        total += output
        trace.append((output, total))
    return trace


class HydraulicLiftTask(BaseMathTask):
    TASK_TYPE = "hydraulic_lift"
    TASK_TYPES = ["output", "total"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.presses = []
        for _ in range(self.n):
            narrow = random.randint(1, 4)
            ratio = random.randint(1, 4)
            force = random.randint(1, 6)
            self.presses.append((force, narrow, narrow * ratio))
        self.trace = hydraulic_trace(self.presses)
        self.k = random.randint(1, self.n)
        self.output = self.trace[self.k - 1][0]
        self.total = self.trace[-1][1]
        self.answer = self.output if self.task_type == "output" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(
            f"{force}, {narrow}, {wide}" for force, narrow, wide in self.presses
        )
        key = "s0" if self.task_type == "output" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, output=output, total=total)
            for index, (output, total) in enumerate(self.trace, 1)
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
