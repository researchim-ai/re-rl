"""MemoCallTask — повторный вызов инструмента берёт сохранённый результат.

Первый вызов пары инструмент-аргумент считает формулу. Такой же вызов потом не считает её снова.
Число вызовов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Call = Tuple[int, int]


def memo_trace(calls: Sequence[Call], modulo: int = 10) -> List[Tuple[int, int, int]]:
    cache: Dict[Call, int] = {}
    hits = 0
    total = 0
    trace = []
    for tool, arg in calls:
        pair = (tool, arg)
        if pair in cache:
            hits += 1
            result = cache[pair]
        else:
            result = (arg * (tool + 1) + tool) % modulo
            cache[pair] = result
        total += result
        trace.append((result, hits, total))
    return trace


class MemoCallTask(BaseMathTask):
    TASK_TYPE = "memo_call"
    TASK_TYPES = ["total", "hits"]
    MODULO = 10

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
        self.calls = [(random.randint(0, 1), random.randint(0, 6)) for _ in range(self.n)]
        self.trace = memo_trace(self.calls, self.MODULO)
        self.total = self.trace[-1][2]
        self.hits = self.trace[-1][1]
        self.answer = self.total if self.task_type == "total" else self.hits
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(f"{tool} {arg}" for tool, arg in self.calls)
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, calls=shown, mod=self.MODULO)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, tool=tool, arg=arg, result=result, hits=hits, total=total)
            for index, ((tool, arg), (result, hits, total)) in enumerate(zip(self.calls, self.trace), 1)
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
