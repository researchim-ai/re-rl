"""MinimaxTreeTask — значение и ход в дереве максимума и минимума.

Корень максимизирует. Каждый его ход ведёт к узлу минимума, а дальше стоят листья.
При равенстве у корня берётся меньший номер хода.
"""

import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def minimax_tree(branches: Sequence[Sequence[int]]) -> Tuple[int, int]:
    best = None
    chosen = 1
    for index, leaves in enumerate(branches):
        value = min(leaves)
        if best is None or value > best:
            best = value
            chosen = index + 1
    return best, chosen


class MinimaxTreeTask(BaseMathTask):
    TASK_TYPE = "minimax_tree"
    TASK_TYPES = ["value", "action"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"a": 2, "k": 2, "mag": 5}, 2: {"a": 2, "k": 3, "mag": 6},
        3: {"a": 3, "k": 3, "mag": 6}, 4: {"a": 3, "k": 3, "mag": 8},
        5: {"a": 3, "k": 4, "mag": 8}, 6: {"a": 4, "k": 4, "mag": 10},
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
        self.value, self.choice = minimax_tree(self.branches)
        self.answer = self.value if self.task_type == "value" else self.choice
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _shown(self, language: str) -> str:
        ru = language == "ru"
        chunks = []
        for index, leaves in enumerate(self.branches):
            nums = " ".join(map(str, leaves))
            chunks.append(
                (f"Ход {index + 1}, листья минимума: {nums}." if ru else
                 f"Move {index + 1}, leaves of the minimizing node: {nums}.")
            )
        return " ".join(chunks)

    def _descr(self, language):
        ru = language == "ru"
        rule = ((f"Корень максимизирует. Каждый ход ведёт к узлу, который берёт минимум своих листьев. "
                 f"При равенстве у корня выбирается меньший номер хода. {self._shown(language)}") if ru else
                (f"The root maximizes. Each move leads to a node that takes the minimum of its leaves. "
                 f"Ties at the root take the smaller move index. {self._shown(language)}"))
        ask = (("Найдите оценку корня." if ru else "Find the value of the root.")
               if self.task_type == "value" else
               ("Какой ход выбирает корень?" if ru else "Which move does the root choose?"))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        step = ((f"Оценка {self.value}, ход {self.choice}.") if ru else
                (f"Value {self.value}, move {self.choice}."))
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
