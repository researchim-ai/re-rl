"""BeamKeepTask — лучевой поиск ширины два.

Каждый шаг добавляет к гипотезе одну из двух оценок токена. Остаются две лучшие суммы.
При равенстве раньше стоит гипотеза левее, затем токен с меньшим номером.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Row = Tuple[int, int]


def beam_trace(rows: Sequence[Row]) -> List[Tuple[int, int, int]]:
    beam = [(0, 0, 0)]
    trace = []
    for left, right in rows:
        candidates = []
        for rank, (score, _token, _rank) in enumerate(beam):
            candidates.append((score + left, rank, 0))
            candidates.append((score + right, rank, 1))
        candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
        beam = candidates[:2]
        best, _parent, token = beam[0]
        second = beam[1][0]
        trace.append((best, second, token))
    return trace


class BeamKeepTask(BaseMathTask):
    TASK_TYPE = "beam_keep"
    TASK_TYPES = ["best", "token"]

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
        self.rows = [(random.randint(-2, 3), random.randint(-2, 3)) for _ in range(self.n)]
        self.trace = beam_trace(self.rows)
        self.best = self.trace[-1][0]
        self.token = self.trace[-1][2]
        self.answer = self.best if self.task_type == "best" else self.token
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(f"{left} {right}" for left, right in self.rows)
        key = "s0" if self.task_type == "best" else "s1"
        return texts.t(key, language, n=self.n, rows=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, left=left, right=right, best=best, second=second, token=token)
            for index, ((left, right), (best, second, token)) in enumerate(zip(self.rows, self.trace), 1)
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
