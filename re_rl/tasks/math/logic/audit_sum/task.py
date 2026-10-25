"""AuditSumTask — проверка заявленной суммы против настоящего накопления.

Ошибка — это шаг, где заявленное число не равно сумме прибавок. Подсчёт идёт дальше.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Pair = Tuple[int, int]


def audit_trace(pairs: Sequence[Pair]) -> List[Tuple[int, int]]:
    true_total = 0
    misses = 0
    trace = []
    for value, claimed in pairs:
        true_total += value
        if claimed != true_total:
            misses += 1
        trace.append((true_total, misses))
    return trace


class AuditSumTask(BaseMathTask):
    TASK_TYPE = "audit_sum"
    TASK_TYPES = ["misses", "total"]

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
        self.pairs = []
        running = 0
        for _ in range(self.n):
            value = random.randint(1, 6)
            running += value
            if random.randrange(2) == 0:
                claimed = running
            else:
                claimed = max(0, running + random.choice((-2, -1, 1, 2)))
            self.pairs.append((value, claimed))
        self.trace = audit_trace(self.pairs)
        self.true_total = self.trace[-1][0]
        self.misses = self.trace[-1][1]
        self.answer = self.misses if self.task_type == "misses" else self.true_total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(f"{value} {claimed}" for value, claimed in self.pairs)
        key = "s0" if self.task_type == "misses" else "s1"
        return texts.t(key, language, n=self.n, pairs=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value, claimed=claimed, total=total, misses=misses)
            for index, ((value, claimed), (total, misses)) in enumerate(zip(self.pairs, self.trace), 1)
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
