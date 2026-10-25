"""DraftAcceptTask — принятие черновика до первого расхождения.

Слева направо черновик и проверка совпадают. Первое различие останавливает принятие, но просмотр идёт до конца.
Число позиций растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Pair = Tuple[int, int]


def draft_trace(pairs: Sequence[Pair]) -> List[Tuple[int, int]]:
    taken = 0
    reject = 0
    trace = []
    for index, (draft, target) in enumerate(pairs, 1):
        if reject == 0 and draft == target:
            taken += 1
        elif reject == 0:
            reject = index
        trace.append((taken, reject))
    return trace


class DraftAcceptTask(BaseMathTask):
    TASK_TYPE = "draft_accept"
    TASK_TYPES = ["taken", "at"]

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
        self.pairs = [(random.randint(0, 4), random.randint(0, 4)) for _ in range(self.n)]
        if random.random() < 0.7:
            cut = random.randint(0, self.n - 1)
            self.pairs[cut] = (self.pairs[cut][0], (self.pairs[cut][0] + 1) % 5)
        self.trace = draft_trace(self.pairs)
        self.taken = self.trace[-1][0]
        self.at = self.trace[-1][1]
        self.answer = self.taken if self.task_type == "taken" else self.at
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{draft}/{target}" for draft, target in self.pairs)
        key = "s0" if self.task_type == "taken" else "s1"
        return texts.t(key, language, n=self.n, pairs=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, draft=draft, target=target, taken=taken, at=at)
            for index, ((draft, target), (taken, at)) in enumerate(zip(self.pairs, self.trace), 1)
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
