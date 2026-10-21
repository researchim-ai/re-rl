"""RoundRobinTask — круговая очередь с квантом времени.

Все заявки приходят в момент 0 и сначала стоят в порядке номеров.
Если процесс не закончил квант, он встаёт в конец очереди.
Ожидание заявки = время завершения - длительность. Всё целое.

Подтипы: суммарное ожидание и суммарное оборотное время.
"""

import random
from collections import deque
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def round_robin(bursts: List[int], quantum: int) -> Tuple[int, int, List[int]]:
    n = len(bursts)
    remaining = list(bursts)
    queue = deque(range(n))
    time = 0
    finish = [0] * n
    while queue:
        i = queue.popleft()
        run = min(quantum, remaining[i])
        time += run
        remaining[i] -= run
        if remaining[i] == 0:
            finish[i] = time
        else:
            queue.append(i)
    wait = sum(finish[i] - bursts[i] for i in range(n))
    turnaround = sum(finish)
    return wait, turnaround, finish


class RoundRobinTask(BaseMathTask):
    TASK_TYPE = "round_robin"
    TASK_TYPES = ["waiting", "turnaround"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "burst": 5, "q": 2}, 2: {"n": 3, "burst": 6, "q": 2},
        3: {"n": 4, "burst": 6, "q": 3}, 4: {"n": 4, "burst": 7, "q": 3},
        5: {"n": 4, "burst": 8, "q": 3}, 6: {"n": 5, "burst": 8, "q": 3},
        7: {"n": 5, "burst": 9, "q": 4}, 8: {"n": 6, "burst": 9, "q": 4},
        9: {"n": 6, "burst": 10, "q": 4}, 10: {"n": 7, "burst": 10, "q": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.burst_max = int(p["burst"])
        self.qmax = int(p["q"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.quantum = random.randint(1, self.qmax)
        self.bursts = [random.randint(1, self.burst_max) for _ in range(self.n)]
        self.wait, self.turnaround, self.finish = round_robin(self.bursts, self.quantum)
        self.answer = self.wait if self.task_type == "waiting" else self.turnaround
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        jobs = ", ".join(f"({i + 1}, {b})" for i, b in enumerate(self.bursts))
        return ((f"Круговая очередь, квант {self.quantum}. Все заявки приходят в момент 0 "
                 f"и сначала идут по номерам. Пары (номер, длительность): {jobs}. "
                 f"Незавершённый процесс встаёт в конец. "
                 f"Найдите суммарное {'время ожидания' if self.task_type == 'waiting' else 'оборотное время'} "
                 f"(оборотное = время завершения при нулевом приходе).") if ru else
                (f"Round-robin, quantum {self.quantum}. Every job arrives at time 0 and starts in index order. "
                 f"Pairs (id, burst): {jobs}. A job that does not finish goes to the back of the queue. "
                 f"Find the total "
                 f"{'waiting time' if self.task_type == 'waiting' else 'turnaround time'} "
                 f"(turnaround is the completion time when arrival is 0)."))

    def solve(self):
        ru = self.language == "ru"
        done = ", ".join(f"{i + 1}->{t}" for i, t in enumerate(self.finish))
        step = ((f"Моменты завершения: {done}. Ожидание {self.wait}, оборотное {self.turnaround}.")
                if ru else
                (f"Completion times: {done}. Waiting {self.wait}, turnaround {self.turnaround}."))
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
