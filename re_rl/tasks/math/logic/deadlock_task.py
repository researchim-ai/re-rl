"""DeadlockTask — цикл в графе ожидания.

Ребро a->b значит «a ждёт b». Петля — цикл длины 1.
Подтипы: есть ли цикл и сколько процессов лежат хотя бы на одном цикле.
"""

import random
from typing import Any, ClassVar, Dict, List, Set, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def nodes_on_cycles(n: int, edges: List[Tuple[int, int]]) -> Set[int]:
    adj = [[] for _ in range(n)]
    radj = [[] for _ in range(n)]
    loops = set()
    for a, b in edges:
        if a == b:
            loops.add(a)
        else:
            adj[a].append(b)
            radj[b].append(a)
    seen = [False] * n
    order: List[int] = []

    def dfs(u: int):
        seen[u] = True
        for v in adj[u]:
            if not seen[v]:
                dfs(v)
        order.append(u)

    for i in range(n):
        if not seen[i]:
            dfs(i)
    seen = [False] * n

    def dfs2(u: int, comp: List[int]):
        seen[u] = True
        comp.append(u)
        for v in radj[u]:
            if not seen[v]:
                dfs2(v, comp)

    on_cycle = set(loops)
    for u in reversed(order):
        if not seen[u]:
            comp: List[int] = []
            dfs2(u, comp)
            if len(comp) > 1:
                on_cycle.update(comp)
    return on_cycle


class DeadlockTask(BaseMathTask):
    TASK_TYPE = "deadlock"
    TASK_TYPES = ["has_cycle", "cycle_nodes"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "extra": 1}, 2: {"n": 4, "extra": 2}, 3: {"n": 5, "extra": 2},
        4: {"n": 5, "extra": 3}, 5: {"n": 6, "extra": 3}, 6: {"n": 7, "extra": 3},
        7: {"n": 8, "extra": 4}, 8: {"n": 8, "extra": 4}, 9: {"n": 9, "extra": 5},
        10: {"n": 10, "extra": 5},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.extra = int(p["extra"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        edges = set()
        if random.random() < 0.65:
            length = random.randint(1, min(4, self.n))
            cyc = random.sample(range(self.n), length)
            if length == 1:
                edges.add((cyc[0], cyc[0]))
            else:
                for i in range(length):
                    edges.add((cyc[i], cyc[(i + 1) % length]))
        while len(edges) < self.extra:
            edges.add((random.randrange(self.n), random.randrange(self.n)))
        self.edges = sorted(edges)
        self.on_cycle = nodes_on_cycles(self.n, self.edges)
        self.has_cycle = bool(self.on_cycle)
        self.count = len(self.on_cycle)

    def _edge_text(self) -> str:
        if not self.edges:
            return "-"
        return ", ".join(f"{a + 1}->{b + 1}" for a, b in self.edges)

    def _descr(self, language):
        ru = language == "ru"
        head = ((f"Процессы 1..{self.n}. Ребро a->b значит, что a ждёт b. "
                 f"Рёбра: {self._edge_text()}. Петля — цикл длины 1.") if ru else
                (f"Processes 1..{self.n}. Edge a->b means a waits for b. "
                 f"Edges: {self._edge_text()}. A self-loop is a cycle of length 1."))
        if self.task_type == "has_cycle":
            ask = ("Есть ли взаимная блокировка (цикл ожидания)? Ответьте да/нет." if ru else
                   "Is there a deadlock (a cycle in the wait-for graph)? Answer yes/no.")
        else:
            ask = ("Сколько процессов лежат хотя бы на одном цикле?" if ru else
                   "How many processes lie on at least one cycle?")
        return f"{head} {ask}"

    def solve(self):
        ru = self.language == "ru"
        if self.task_type == "has_cycle":
            ans = ("да" if self.has_cycle else "нет") if ru else ("yes" if self.has_cycle else "no")
            step = ((f"Процессов на циклах: {self.count}.") if ru else
                    (f"Processes on cycles: {self.count}."))
        else:
            ans = str(self.count)
            listed = ", ".join(str(v + 1) for v in sorted(self.on_cycle)) or "-"
            step = ((f"На циклах: {listed}.") if ru else (f"On cycles: {listed}."))
        self.solution_steps = [step, (f"Ответ: {ans}." if ru else f"Answer: {ans}.")]
        self.final_answer = ans

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "has_cycle":
            return U.verify_bool(prediction, self.has_cycle)
        return U.verify_int(prediction, self.count)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
