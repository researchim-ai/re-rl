"""AllAreTask — цепочка общих утверждений.

Элемент лежит в множестве 0. Связь «все из i лежат в i+1» переносит его дальше, пока связь не оборвана.
Число связей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def all_trace(links: Sequence[int]) -> List[Tuple[int, int]]:
    far = 0
    opened = 0
    flowing = 1
    trace = []
    for link in links:
        if flowing and link:
            far += 1
            opened += 1
        else:
            flowing = 0
            opened += link
        trace.append((far, opened))
    return trace


class AllAreTask(BaseMathTask):
    TASK_TYPE = "all_are"
    TASK_TYPES = ["far", "links"]

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
        self.links = [random.randint(0, 1) for _ in range(self.n)]
        self.trace = all_trace(self.links)
        self.far, self.opened = self.trace[-1]
        self.answer = self.far if self.task_type == "far" else self.opened
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        links = ", ".join(str(link) for link in self.links)
        key = "s0" if self.task_type == "far" else "s1"
        return texts.t(key, language, n=self.n, links=links)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, link=link, far=far, opened=opened)
            for index, (link, (far, opened)) in enumerate(zip(self.links, self.trace), 1)
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
