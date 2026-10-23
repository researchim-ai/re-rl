"""TreeTimesTask — время входа и размер поддерева при обходе в глубину.

Корень — узел 1. Дети идут по возрастанию номеров. Обход линейный по числу узлов.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def tree_times(parents: Sequence[int]) -> Tuple[List[int], List[int]]:
    children = [[] for _ in parents]
    for node in range(2, len(parents)):
        children[parents[node]].append(node)
    enter = [0] * len(parents)
    size = [0] * len(parents)
    clock = 0

    def walk(node: int) -> None:
        nonlocal clock
        clock += 1
        enter[node] = clock
        size[node] = 1
        for child in children[node]:
            walk(child)
            size[node] += size[child]

    walk(1)
    return enter, size


class TreeTimesTask(BaseMathTask):
    TASK_TYPE = "tree_times"
    TASK_TYPES = ["enter", "size"]

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
        self.parents = [0, 0]
        for node in range(2, self.n + 1):
            self.parents.append(random.randint(1, node - 1))
        self.enter, self.sizes = tree_times(self.parents)
        self.k = random.randint(1, self.n)
        self.enter_k = self.enter[self.k]
        self.size = self.sizes[self.k]
        self.answer = self.enter_k if self.task_type == "enter" else self.size
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{node}-{self.parents[node]}" for node in range(2, self.n + 1))
        key = "s0" if self.task_type == "enter" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=node, enter=self.enter[node], size=self.sizes[node])
            for node in range(1, self.n + 1)
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
