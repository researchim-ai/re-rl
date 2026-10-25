"""MarginPushTask — шаг, если знак на значение меньше запаса.

Запас равен 1. Иначе счёт не меняется. Число примеров растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Example = Tuple[int, int]


def push_trace(examples: Sequence[Example], margin: int = 1) -> List[Tuple[int, int]]:
    score = 0
    skips = 0
    trace = []
    for label, feature in examples:
        if label * score < margin:
            score += label * feature
        else:
            skips += 1
        trace.append((score, skips))
    return trace


class MarginPushTask(BaseMathTask):
    TASK_TYPE = "margin_push"
    TASK_TYPES = ["score", "skips"]
    MARGIN = 1

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
        self.examples = [(random.choice((-1, 1)), random.randint(1, 4)) for _ in range(self.n)]
        self.trace = push_trace(self.examples, self.MARGIN)
        self.score = self.trace[-1][0]
        self.skips = self.trace[-1][1]
        self.answer = self.score if self.task_type == "score" else self.skips
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(f"{label} {feature}" for label, feature in self.examples)
        key = "s0" if self.task_type == "score" else "s1"
        return texts.t(key, language, n=self.n, margin=self.MARGIN, examples=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, label=label, feature=feature, score=score, skips=skips)
            for index, ((label, feature), (score, skips)) in enumerate(zip(self.examples, self.trace), 1)
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
