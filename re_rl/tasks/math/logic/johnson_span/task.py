"""JohnsonSpanTask — две машины и порядок Джонсона.

Работа с A <= B идёт в левую группу по возрастанию A. Иначе в правую по убыванию B.
Момент окончания больше суммы времён на второй машине из-за простоев.
Число работ растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def johnson_order(machine_a: Sequence[int], machine_b: Sequence[int]) -> List[int]:
    front = [index for index in range(len(machine_a)) if machine_a[index] <= machine_b[index]]
    back = [index for index in range(len(machine_a)) if machine_a[index] > machine_b[index]]
    front.sort(key=lambda index: (machine_a[index], index))
    back.sort(key=lambda index: (-machine_b[index], index))
    return front + back


def completion(order: Sequence[int], machine_a: Sequence[int], machine_b: Sequence[int]) -> Tuple[int, List[Tuple[int, int, int]]]:
    done_a = 0
    done_b = 0
    trace = []
    for index in order:
        done_a += machine_a[index]
        begin = done_a if done_a > done_b else done_b
        done_b = begin + machine_b[index]
        trace.append((done_a, begin, done_b))
    return done_b, trace


class JohnsonSpanTask(BaseMathTask):
    TASK_TYPE = "johnson_span"
    TASK_TYPES = ["makespan", "idle"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "m": 4}, 2: {"n": 3, "m": 5}, 3: {"n": 4, "m": 5},
        4: {"n": 4, "m": 6}, 5: {"n": 5, "m": 6}, 6: {"n": 6, "m": 6},
        7: {"n": 7, "m": 7}, 8: {"n": 8, "m": 7}, 9: {"n": 9, "m": 8},
        10: {"n": 10, "m": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(3, int(p["n"]))
        limit = max(2, int(p["m"]))
        self.machine_a = [random.randint(1, limit) for _ in range(self.n)]
        self.machine_b = [random.randint(1, limit) for _ in range(self.n)]
        self.order = johnson_order(self.machine_a, self.machine_b)
        self.makespan, self.trace = completion(self.order, self.machine_a, self.machine_b)
        self.idle = self.makespan - sum(self.machine_b)
        self.answer = self.makespan if self.task_type == "makespan" else self.idle
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(
            f"{index}: {self.machine_a[index - 1]}, {self.machine_b[index - 1]}"
            for index in range(1, self.n + 1)
        )
        key = "s0" if self.task_type == "makespan" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        front = texts.t("s4", self.language)
        back = texts.t("s5", self.language)
        steps = []
        for index in self.order:
            side = front if self.machine_a[index] <= self.machine_b[index] else back
            steps.append(texts.t("s2", self.language, job=index + 1, side=side))
        for index, (done_a, begin, done_b) in zip(self.order, self.trace):
            steps.append(texts.t(
                "s3", self.language, job=index + 1, t1=done_a, begin=begin, t2=done_b,
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
