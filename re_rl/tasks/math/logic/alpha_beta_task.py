"""AlphaBetaTask — альфа-бета отсечение слева направо.

Корень максимизирует, каждый ход ведёт к минимуму по листьям.
Как только текущий минимум хода стал не больше уже найденной оценки корня,
остальные листья этого хода не читаются.
"""

import random
from typing import Any, ClassVar, Dict, List, Optional, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def alpha_beta(branches: Sequence[Sequence[int]]) -> Tuple[int, int]:
    visited = 0
    alpha: Optional[int] = None
    root: Optional[int] = None
    for leaves in branches:
        node: Optional[int] = None
        for leaf in leaves:
            visited += 1
            node = leaf if node is None else min(node, leaf)
            if alpha is not None and node <= alpha:
                break
        if root is None or node > root:
            root = node
        if alpha is None or node > alpha:
            alpha = node
    return root, visited


class AlphaBetaTask(BaseMathTask):
    TASK_TYPE = "alpha_beta"
    TASK_TYPES = ["value", "visited"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"a": 2, "k": 2, "mag": 6}, 2: {"a": 2, "k": 3, "mag": 6},
        3: {"a": 3, "k": 3, "mag": 8}, 4: {"a": 3, "k": 3, "mag": 8},
        5: {"a": 3, "k": 4, "mag": 9}, 6: {"a": 4, "k": 4, "mag": 9},
        7: {"a": 4, "k": 4, "mag": 10}, 8: {"a": 4, "k": 5, "mag": 12},
        9: {"a": 5, "k": 5, "mag": 12}, 10: {"a": 5, "k": 5, "mag": 15},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n_actions = int(p["a"])
        self.leaves = int(p["k"])
        self.mag = int(p["mag"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.branches: List[List[int]] = [
            [random.randint(-self.mag, self.mag) for _ in range(random.randint(2, self.leaves))]
            for _ in range(self.n_actions)
        ]
        self.value, self.visited = alpha_beta(self.branches)
        self.answer = self.value if self.task_type == "value" else self.visited
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _shown(self, language: str) -> str:
        ru = language == "ru"
        chunks = []
        for index, leaves in enumerate(self.branches):
            nums = " ".join(map(str, leaves))
            chunks.append(
                (f"Ход {index + 1}, листья слева направо: {nums}." if ru else
                 f"Move {index + 1}, leaves left to right: {nums}.")
            )
        return " ".join(chunks)

    def _descr(self, language):
        ru = language == "ru"
        rule = ((f"Корень максимизирует, ходы идут по порядку. Ход берёт минимум прочитанных листьев. "
                 f"Как только этот минимум стал не больше уже найденной оценки корня, "
                 f"остальные листья хода не читаются. {self._shown(language)}") if ru else
                (f"The root maximizes, and moves are tried in order. A move takes the minimum of the leaves read. "
                 f"Once that minimum is no greater than the root value already found, "
                 f"the remaining leaves of the move are not read. {self._shown(language)}"))
        ask = (("Найдите оценку корня." if ru else "Find the value of the root.")
               if self.task_type == "value" else
               ("Сколько листьев будет прочитано?" if ru else "How many leaves are read?"))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        step = ((f"Оценка {self.value}, прочитано листьев {self.visited}.") if ru else
                (f"Value {self.value}, leaves read {self.visited}."))
        self.solution_steps = [step, (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}.")]
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
