"""JoinWaitTask — точка сбора ждёт нужное число завершённых задач.

Повторное завершение одной задачи не увеличивает счётчик. Неудачная точка сбора ничего не отменяет.
Число событий растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Event = Tuple[int, int]


def barrier_trace(events: Sequence[Event]) -> List[Tuple[int, int]]:
    done = set()
    joins = 0
    trace = []
    for code, arg in events:
        if code == 0:
            done.add(arg)
        elif len(done) >= arg:
            joins += 1
        trace.append((len(done), joins))
    return trace


class JoinWaitTask(BaseMathTask):
    TASK_TYPE = "join_wait"
    TASK_TYPES = ["joins", "finished"]

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
        self.events = []
        for _ in range(self.n):
            if random.randrange(2) == 0:
                self.events.append((0, random.randrange(self.n)))
            else:
                self.events.append((1, random.randint(1, self.n)))
        self.trace = barrier_trace(self.events)
        self.finished = self.trace[-1][0]
        self.joins = self.trace[-1][1]
        self.answer = self.joins if self.task_type == "joins" else self.finished
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(f"{code} {arg}" for code, arg in self.events)
        key = "s0" if self.task_type == "joins" else "s1"
        return texts.t(key, language, n=self.n, events=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, code=code, arg=arg, done=done, joins=joins)
            for index, ((code, arg), (done, joins)) in enumerate(zip(self.events, self.trace), 1)
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
