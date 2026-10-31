"""OSSchedulingTask — короткие задачи на планирование.

Подтипы:
- ``sjf_wait``  — суммарное время ожидания при невытесняющем SJF
  (все заявки приходят в момент 0; при равной длительности раньше идёт меньший номер);
- ``fcfs_wait`` — суммарное время ожидания при FCFS
  (раньше пришедшая заявка раньше обслуживается; при равном приходе — меньший номер);
- ``sstf_seek`` — суммарное перемещение головки диска по SSTF
  (при равном расстоянии выбирается меньший номер цилиндра).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class OSSchedulingTask(BaseMathTask):
    TASK_TYPE = "os_scheduling"
    TASK_TYPES = ["sjf_wait", "fcfs_wait", "sstf_seek"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "span": 40}, 2: {"n": 3, "span": 50}, 3: {"n": 4, "span": 60},
        4: {"n": 4, "span": 80}, 5: {"n": 5, "span": 100}, 6: {"n": 5, "span": 120},
        7: {"n": 6, "span": 140}, 8: {"n": 6, "span": 160}, 9: {"n": 7, "span": 180},
        10: {"n": 7, "span": 199},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = kwargs.pop("n", p["n"])
        self.span = kwargs.pop("span", p["span"])
        if type(self.n) is not int or not 1 <= self.n <= 500:
            raise ValueError("invalid_n")
        if type(self.span) is not int or not 1 <= self.span <= 1_000_000:
            raise ValueError("invalid_span")
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        if self.task_type not in self.TASK_TYPES:
            raise ValueError("invalid_task_type")
        if self.task_type == "sstf_seek" and self.n > self.span:
            raise ValueError("insufficient_cylinders")
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        if self.task_type == "sjf_wait":
            self.bursts = [random.randint(1, 9) for _ in range(self.n)]
            if self.n > 1 and random.random() < 0.45:
                self.bursts[1] = self.bursts[0]
            self.order, self.answer = self.sjf_waiting(self.bursts)
        elif self.task_type == "fcfs_wait":
            self.jobs = [(random.randint(0, self.n * 2), random.randint(1, 8)) for _ in range(self.n)]
            if self.n > 1 and random.random() < 0.4:
                arr, burst = self.jobs[0]
                self.jobs[1] = (arr, burst if burst > 1 else burst + 1)
            self.order, self.answer = self.fcfs_waiting(self.jobs)
        else:
            self.start = random.randint(0, self.span)
            # Sample distinct cylinders without allocating a potentially huge range.
            self.reqs = [c if c < self.start else c + 1
                         for c in random.sample(range(self.span), self.n)]
            if len(self.reqs) >= 2:
                mirror = 2 * self.start - self.reqs[0]
                if (mirror != self.reqs[0] and 0 <= mirror <= self.span
                        and mirror != self.start and mirror not in self.reqs
                        and random.random() < 0.5):
                    self.reqs[1] = mirror
            self.order, self.answer = self.sstf(self.start, self.reqs)

    @staticmethod
    def sjf_waiting(bursts: List[int]) -> Tuple[List[int], int]:
        order = sorted(range(len(bursts)), key=lambda i: (bursts[i], i))
        t = 0
        wait = 0
        for i in order:
            wait += t
            t += bursts[i]
        return [i + 1 for i in order], wait

    @staticmethod
    def fcfs_waiting(jobs: List[Tuple[int, int]]) -> Tuple[List[int], int]:
        order = sorted(range(len(jobs)), key=lambda i: (jobs[i][0], i))
        t = 0
        wait = 0
        for i in order:
            arr, burst = jobs[i]
            start = max(t, arr)
            wait += start - arr
            t = start + burst
        return [i + 1 for i in order], wait

    @staticmethod
    def sstf(start: int, reqs: List[int]) -> Tuple[List[int], int]:
        from .solver import schedule
        return schedule("sstf_seek", {"start": start, "reqs": reqs}, [])

    def _descr(self, language):
        if self.task_type == "sjf_wait":
            desc = ", ".join(f"({i + 1}, {b})" for i, b in enumerate(self.bursts))
            return ((texts.t('s1', language, desc=desc)))
        if self.task_type == "fcfs_wait":
            desc = ", ".join(f"({i + 1}, {a}, {b})" for i, (a, b) in enumerate(self.jobs))
            return ((texts.t('s2', language, desc=desc)))
        desc = ", ".join(map(str, self.reqs))
        return ((texts.t('s0', language, start=self.start, desc=desc)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        if self.task_type == "sstf_seek":
            path = " -> ".join([str(self.start)] + [str(x) for x in self.order])
            step = ((texts.t('s3', self.language, path=path)))
        else:
            order = ", ".join(map(str, self.order))
            step = ((texts.t('s4', self.language, order=order, answer=self.answer)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.answer)))]
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        self.solve()
        import re
        value = U.clean(prediction).strip()
        return float(bool(re.fullmatch(r"[+-]?\d+", value)) and int(value) == self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
