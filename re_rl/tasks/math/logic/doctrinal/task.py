"""DoctrinalTask — посылочный и выводной итог согласованных судей.

Каждый судья принимает заключение ровно тогда, когда принимает обе посылки.
Большинство по посылкам может дать другое заключение, чем большинство самих заключений.
Число судей нечётно и растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def doctrine_trace(votes: Sequence[Tuple[int, int]]) -> List[Tuple[int, int, int]]:
    yes_p = 0
    yes_q = 0
    yes_c = 0
    trace = []
    for premise, second in votes:
        conclusion = premise & second
        yes_p += premise
        yes_q += second
        yes_c += conclusion
        trace.append((yes_p, yes_q, yes_c))
    return trace


def doctrine_result(votes: Sequence[Tuple[int, int]]) -> Tuple[List[Tuple[int, int, int]], int, int, int]:
    trace = doctrine_trace(votes)
    size = len(votes)
    yes_p, yes_q, yes_c = trace[-1]
    premise = 1 if yes_p * 2 > size and yes_q * 2 > size else 0
    stated = 1 if yes_c * 2 > size else 0
    return trace, premise, stated, 1 if premise != stated else 0


class DoctrinalTask(BaseMathTask):
    TASK_TYPE = "doctrinal"
    TASK_TYPES = ["premise", "clash"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 5}, 4: {"n": 5},
        5: {"n": 7}, 6: {"n": 7}, 7: {"n": 9}, 8: {"n": 9},
        9: {"n": 11}, 10: {"n": 13},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(3, int(p["n"]))
        self.votes = [(random.randint(0, 1), random.randint(0, 1)) for _ in range(self.n)]
        self.trace, self.premise, self.stated, self.clash = doctrine_result(self.votes)
        self.answer = self.premise if self.task_type == "premise" else self.clash
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{premise} {second}" for premise, second in self.votes)
        key = "s0" if self.task_type == "premise" else "s1"
        return texts.t(key, language, n=self.n, votes=shown)

    def solve(self):
        steps = []
        for index, ((premise, second), (yes_p, yes_q, yes_c)) in enumerate(zip(self.votes, self.trace), 1):
            steps.append(texts.t(
                "s2", self.language, i=index, p=premise, q=second, c=premise & second,
                yp=yes_p, yq=yes_q, yc=yes_c,
            ))
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
