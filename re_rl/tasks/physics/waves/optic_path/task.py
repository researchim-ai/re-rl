"""OpticPathTask — оптический путь через слои.

Вклад слоя — показатель преломления, умноженный на толщину.
Число слоёв растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Layer = Tuple[int, int]


def optic_trace(layers: Sequence[Layer]) -> List[Tuple[int, int, int]]:
    total = 0
    best = -1
    which = 1
    trace = []
    for index, (index_n, thickness) in enumerate(layers, 1):
        piece = index_n * thickness
        total += piece
        if piece > best:
            best = piece
            which = index
        trace.append((piece, total, which))
    return trace


class OpticPathTask(BaseMathTask):
    TASK_TYPE = "optic_path"
    TASK_TYPES = ["path", "layer"]

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
        self.layers = [
            (random.randint(1, 4), random.randint(1, 5))
            for _ in range(self.n)
        ]
        self.trace = optic_trace(self.layers)
        _, self.path, self.layer = self.trace[-1]
        self.answer = self.path if self.task_type == "path" else self.layer
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{index_n}, {thickness}" for index_n, thickness in self.layers)
        key = "s0" if self.task_type == "path" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, piece=piece, path=path, layer=layer)
            for index, (piece, path, layer) in enumerate(self.trace, 1)
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
