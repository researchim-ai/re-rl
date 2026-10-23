"""HornFireTask — прямой вывод по правилам Хорна.

Атом 1 дан. Правило срабатывает, только если обе посылки уже выведены. Атом 0 не дан и не выводится.
Число правил растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Set, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Rule = Tuple[int, int, int]


def horn_trace(rules: Sequence[Rule]) -> Tuple[List[Tuple[int, int]], Set[int]]:
    known: Set[int] = {1}
    fired = 0
    trace = []
    for left, right, conclusion in rules:
        ok = 1 if left in known and right in known else 0
        if ok:
            known.add(conclusion)
            fired += 1
        trace.append((ok, fired))
    return trace, known


class HornFireTask(BaseMathTask):
    TASK_TYPE = "horn_fire"
    TASK_TYPES = ["fired", "holds"]

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
        self.rules: List[Rule] = []
        for conclusion in range(2, self.n + 2):
            left = random.randint(1, conclusion - 1)
            if random.random() < 0.35:
                right = 0
            else:
                right = random.randint(1, conclusion - 1)
            self.rules.append((left, right, conclusion))
        self.trace, self.known = horn_trace(self.rules)
        self.fired = self.trace[-1][1]
        self.k = random.randint(1, self.n + 1)
        self.holds = 1 if self.k in self.known else 0
        self.answer = self.fired if self.task_type == "fired" else self.holds
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        rules = ", ".join(f"{left}+{right}->{conclusion}" for left, right, conclusion in self.rules)
        key = "s0" if self.task_type == "fired" else "s1"
        return texts.t(key, language, n=self.n, rules=rules, k=self.k)

    def solve(self):
        steps = [
            texts.t(
                "s2", self.language, i=index, left=left, right=right,
                conclusion=conclusion, ok=ok, fired=fired,
            )
            for index, ((left, right, conclusion), (ok, fired)) in enumerate(zip(self.rules, self.trace), 1)
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
