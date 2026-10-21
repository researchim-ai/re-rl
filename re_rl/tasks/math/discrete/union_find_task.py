"""UnionFindTask — система непересекающихся множеств.

Подтипы:
- ``components`` — сколько компонент после серии объединений;
- ``same``       — лежат ли две вершины в одной компоненте;
- ``size``       — размер компоненты, содержащей данную вершину.

Ответ не зависит от эвристик (сжатие путей, объединение по рангу): считается
само разбиение.
"""

import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class _DSU:
    def __init__(self, n: int):
        self.parent = list(range(n + 1))
        self.size = [1] * (n + 1)

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        return True

    def components(self, n: int) -> int:
        return sum(1 for v in range(1, n + 1) if self.find(v) == v)


class UnionFindTask(BaseMathTask):
    TASK_TYPE = "union_find"
    TASK_TYPES = ["components", "same", "size"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 5, "ops": 3}, 2: {"n": 6, "ops": 4}, 3: {"n": 7, "ops": 5},
        4: {"n": 8, "ops": 6}, 5: {"n": 10, "ops": 8}, 6: {"n": 12, "ops": 10},
        7: {"n": 14, "ops": 12}, 8: {"n": 16, "ops": 14}, 9: {"n": 18, "ops": 16},
        10: {"n": 20, "ops": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.ops = int(p["ops"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.unions: List[Tuple[int, int]] = []
        dsu = _DSU(self.n)
        for _ in range(self.ops):
            a = random.randint(1, self.n)
            b = random.randint(1, self.n)
            self.unions.append((a, b))
            dsu.union(a, b)
        self.dsu = dsu
        if self.task_type == "components":
            self.answer = dsu.components(self.n)
        elif self.task_type == "same":
            self.a, self.b = random.sample(range(1, self.n + 1), 2)
            self.answer = dsu.find(self.a) == dsu.find(self.b)
        else:
            self.x = random.randint(1, self.n)
            self.answer = dsu.size[dsu.find(self.x)]

    def _union_str(self) -> str:
        return ", ".join(f"{a}-{b}" for a, b in self.unions)

    def _descr(self, language):
        ru = language == "ru"
        head = ((f"Есть вершины 1..{self.n}, изначально каждая в своей компоненте. "
                 f"Выполнены объединения: {self._union_str()}. Повторное объединение уже "
                 f"связанных вершин ничего не меняет.") if ru else
                (f"Vertices 1..{self.n} each start in their own component. "
                 f"Unions performed: {self._union_str()}. Uniting vertices that are already "
                 f"connected changes nothing."))
        if self.task_type == "components":
            ask = ("Сколько компонент связности получилось?" if ru else
                   "How many connected components are there?")
        elif self.task_type == "same":
            ask = ((f"Лежат ли вершины {self.a} и {self.b} в одной компоненте? Ответьте да/нет.")
                   if ru else
                   (f"Are vertices {self.a} and {self.b} in the same component? Answer yes/no."))
        else:
            ask = ((f"Каков размер компоненты, содержащей вершину {self.x}?") if ru else
                   (f"What is the size of the component containing vertex {self.x}?"))
        return f"{head} {ask}"

    def solve(self):
        ru = self.language == "ru"
        groups: Dict[int, List[int]] = {}
        for v in range(1, self.n + 1):
            groups.setdefault(self.dsu.find(v), []).append(v)
        shown = " | ".join(" ".join(map(str, members)) for members in groups.values())
        if self.task_type == "components":
            ans = str(self.answer)
            detail = (f"Компонент: {self.answer}. Состав: {shown}." if ru else
                      f"Components: {self.answer}. Members: {shown}.")
        elif self.task_type == "same":
            ans = ("да" if self.answer else "нет") if ru else ("yes" if self.answer else "no")
            detail = ((f"Вершины {self.a} и {self.b} {'в одной компоненте' if self.answer else 'в разных компонентах'}."
                       f" Состав: {shown}.") if ru else
                      (f"Vertices {self.a} and {self.b} are "
                       f"{'together' if self.answer else 'in different components'}. Members: {shown}."))
        else:
            ans = str(self.answer)
            detail = ((f"Компонента вершины {self.x} содержит {self.answer} вершин. Состав: {shown}.")
                      if ru else
                      (f"The component of vertex {self.x} has {self.answer} vertices. Members: {shown}."))
        self.solution_steps = [detail, (f"Ответ: {ans}." if ru else f"Answer: {ans}.")]
        self.final_answer = ans

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "same":
            return U.verify_bool(prediction, bool(self.answer))
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
