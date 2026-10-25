"""CtcCollapseTask — схлопывание повторных меток и пустышек.

Метка 0 — пустышка. Одинаковые метки подряд дают одну, а пустышка разрывает повтор.
Число входных меток растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def ctc_trace(labels: Sequence[int]) -> List[Tuple[int, int]]:
    previous = None
    emitted: List[int] = []
    trace = []
    for label in labels:
        if label != 0 and label != previous:
            emitted.append(label)
        previous = label
        last = 0 if not emitted else emitted[-1]
        trace.append((len(emitted), last))
    return trace


class CtcCollapseTask(BaseMathTask):
    TASK_TYPE = "ctc_collapse"
    TASK_TYPES = ["length", "last"]

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
        self.labels = [random.randint(0, 2)]
        for _ in range(self.n - 1):
            if random.random() < 0.45:
                self.labels.append(self.labels[-1])
            else:
                self.labels.append(random.randint(0, 2))
        self.trace = ctc_trace(self.labels)
        self.length = self.trace[-1][0]
        self.last = self.trace[-1][1]
        self.answer = self.length if self.task_type == "length" else self.last
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(label) for label in self.labels)
        key = "s0" if self.task_type == "length" else "s1"
        return texts.t(key, language, n=self.n, labels=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, label=label, length=length, last=last)
            for index, (label, (length, last)) in enumerate(zip(self.labels, self.trace), 1)
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
