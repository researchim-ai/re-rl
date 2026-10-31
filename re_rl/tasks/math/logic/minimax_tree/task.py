"""MinimaxTreeTask — значение и ход в дереве максимума и минимума.

Корень максимизирует. Каждый его ход ведёт к узлу минимума, а дальше стоят листья.
При равенстве у корня берётся меньший номер хода.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic.graph_algorithms_shared.base import _GraphBase
from re_rl.tasks.math.logic.graph_algorithms_shared.render_trace import render_trace
from re_rl.tasks.math.logic.graph_algorithms_shared.structural_traces import minimax_trace
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


class MinimaxTreeTask(_GraphBase):
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
        chunks = []
        for index, leaves in enumerate(self.branches):
            nums = " ".join(map(str, leaves))
            chunks.append(
                ((texts.t('s4', language, v0=index + 1, nums=nums)))
            )
        return " ".join(chunks)

    def _descr(self, language):
        rule = ((texts.t('s0', language, v0=self._shown(language))))
        ask = (((texts.t('s2', language)))
               if self.task_type == "value" else
               ((texts.t('s3', language))))
        return f"{rule} {ask}"

    def solve(self):
        self.value, self.choice, self.algorithm_trace = minimax_trace(self.branches)
        self.answer = self.value if self.task_type == 'value' else self.choice
        self.solution_steps = render_trace(self.algorithm_trace, 'minimax', self.language)
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
