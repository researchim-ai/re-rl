"""HandoffAskTask — вопрос идёт по цепочке агентов до совпадения навыка.

Совпавший агент тоже считается посещённым. Если навыка нет ни у кого, просматриваются все.
Число вопросов равно числу агентов и растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def hand_trace(skills: Sequence[int], queries: Sequence[int]) -> List[Tuple[int, int, int]]:
    hops = 0
    found = 0
    trace = []
    for query in queries:
        seen = 0
        hit = 0
        for skill in skills:
            seen += 1
            if skill == query:
                hit = 1
                break
        hops += seen
        found += hit
        trace.append((seen, hops, found))
    return trace


class HandoffAskTask(BaseMathTask):
    TASK_TYPE = "handoff_ask"
    TASK_TYPES = ["found", "hops"]

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
        self.skills = [random.randint(0, 2) for _ in range(self.n)]
        self.queries = [random.randint(0, 3) for _ in range(self.n)]
        self.trace = hand_trace(self.skills, self.queries)
        self.found = self.trace[-1][2]
        self.hops = self.trace[-1][1]
        self.answer = self.found if self.task_type == "found" else self.hops
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        skills = ", ".join(str(skill) for skill in self.skills)
        queries = ", ".join(str(query) for query in self.queries)
        key = "s0" if self.task_type == "found" else "s1"
        return texts.t(key, language, n=self.n, skills=skills, queries=queries)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, query=query, seen=seen, hops=hops, found=found)
            for index, (query, (seen, hops, found)) in enumerate(zip(self.queries, self.trace), 1)
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
