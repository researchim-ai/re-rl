"""PageRankTask — точный PageRank при затухании 1/2.

У каждой вершины есть исходящая дуга. Ранги — дроби и в сумме дают 1.
При равном максимуме берётся меньший номер. Номера вершин с 1.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence, Set, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction

Arc = Tuple[int, int]


def solve_linear(matrix: List[List[Fraction]], rhs: List[Fraction]) -> List[Fraction]:
    size = len(rhs)
    rows = [matrix[i][:] + [rhs[i]] for i in range(size)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda row: abs(rows[row][col]))
        if rows[pivot][col] == 0:
            raise RuntimeError("система PageRank вырождена")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scale = rows[col][col]
        for index in range(col, size + 1):
            rows[col][index] /= scale
        for row in range(size):
            if row == col:
                continue
            factor = rows[row][col]
            for index in range(col, size + 1):
                rows[row][index] -= factor * rows[col][index]
    return [rows[i][size] for i in range(size)]


def pagerank(n: int, arcs: Sequence[Arc], damping: Fraction = Fraction(1, 2)) -> List[Fraction]:
    outgoing: List[Set[int]] = [set() for _ in range(n)]
    for src, dst in arcs:
        outgoing[src].add(dst)
    matrix = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    for node in range(n):
        matrix[node][node] = Fraction(1)
        degree = len(outgoing[node])
        if degree == 0:
            raise RuntimeError("у вершины нет исходящих дуг")
        share = damping / degree
        for dst in outgoing[node]:
            matrix[dst][node] -= share
    base = Fraction(1 - damping, n)
    ranks = solve_linear(matrix, [base for _ in range(n)])
    if sum(ranks, Fraction(0)) != 1:
        raise RuntimeError("ранги не дают единицу")
    return ranks


class PageRankTask(BaseMathTask):
    TASK_TYPE = "pagerank"
    TASK_TYPES = ["rank", "argmax"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "extra": 0}, 2: {"n": 3, "extra": 1}, 3: {"n": 3, "extra": 2},
        4: {"n": 3, "extra": 2}, 5: {"n": 4, "extra": 2}, 6: {"n": 4, "extra": 3},
        7: {"n": 4, "extra": 4}, 8: {"n": 4, "extra": 4}, 9: {"n": 5, "extra": 4},
        10: {"n": 5, "extra": 5},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.extra = int(p["extra"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        arcs = {(i, (i + 1) % self.n) for i in range(self.n)}
        for _ in range(self.extra):
            arcs.add((random.randrange(self.n), random.randrange(self.n)))
        self.arcs = sorted(arcs)
        self.ranks = pagerank(self.n, self.arcs)
        self.node = random.randrange(self.n)
        best = max(self.ranks)
        self.argmax = min(i for i, rank in enumerate(self.ranks) if rank == best) + 1
        self.answer = self.ranks[self.node] if self.task_type == "rank" else Fraction(self.argmax)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _shown(self) -> str:
        return ", ".join(f"{src + 1}->{dst + 1}" for src, dst in self.arcs)

    def _descr(self, language):
        ru = language == "ru"
        rule = ((f"PageRank, затухание d = 1/2, вершины с 1. Дуги: {self._shown()}. "
                 f"Ранг вершины равен (1 - d) / n плюс d, умноженное на сумму рангов предшественников, "
                 f"делённых на число их различных исходящих дуг. "
                 f"При равном наибольшем ранге берётся меньший номер. "
                 f"Ответ — целое или несократимая дробь.") if ru else
                (f"PageRank, damping d = 1/2, vertices start at 1. Arcs: {self._shown()}. "
                 f"A vertex rank is (1 - d) / n plus d times the sum of predecessor ranks "
                 f"divided by their numbers of distinct outgoing arcs. "
                 f"The greatest rank breaks ties toward the smaller index. "
                 f"Answer with an integer or a reduced fraction."))
        if self.task_type == "rank":
            ask = ((f"Найдите ранг вершины {self.node + 1}.") if ru else
                   (f"Find the rank of vertex {self.node + 1}."))
        else:
            ask = (("Какая вершина имеет наибольший ранг?" if ru else
                    "Which vertex has the greatest rank?"))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = str(self.argmax) if self.task_type == "argmax" else fmt_fraction(self.ranks[self.node])
        ranks = ", ".join(fmt_fraction(rank) for rank in self.ranks)
        step = ((f"Ранги: {ranks}. Наибольший у вершины {self.argmax}.") if ru else
                (f"Ranks: {ranks}. The greatest is at vertex {self.argmax}."))
        self.solution_steps = [step, (f"Ответ: {shown}." if ru else f"Answer: {shown}.")]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "argmax":
            return U.verify_int(prediction, self.argmax)
        return verify_fraction(prediction, self.ranks[self.node])

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
