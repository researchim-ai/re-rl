"""AnfFoldTask — алгебраическая нормальная форма булевой функции.

Каждый бит маски прогоняет преобразование Мёбиуса по модулю 2. Число переменных растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def anf_trace(table: Sequence[int]) -> List[Tuple[int, int]]:
    size = len(table)
    if size == 0 or size & (size - 1):
        raise RuntimeError("anf mismatch")
    values = [int(bit) & 1 for bit in table]
    bits = size.bit_length() - 1
    trace = []
    for bit in range(bits):
        step = 1 << bit
        for mask in range(size):
            if mask & step:
                values[mask] ^= values[mask ^ step]
        weight = sum(values)
        degree = 0
        for mask, flag in enumerate(values):
            if flag:
                degree = max(degree, mask.bit_count())
        trace.append((weight, degree))
    check = values[:]
    for bit in range(bits):
        step = 1 << bit
        for mask in range(size):
            if mask & step:
                check[mask] ^= check[mask ^ step]
    if check != [int(bit) & 1 for bit in table] or values[0] != (int(table[0]) & 1):
        raise RuntimeError("anf mismatch")
    return trace


class AnfFoldTask(BaseMathTask):
    TASK_TYPE = "anf_fold"
    TASK_TYPES = ["terms", "degree"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 6},
        9: {"n": 6}, 10: {"n": 7},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.size = 1 << self.n
        self.table = [random.randint(0, 1) for _ in range(self.size)]
        if not any(self.table):
            self.table[random.randrange(self.size)] = 1
        self.trace = anf_trace(self.table)
        self.terms = self.trace[-1][0]
        self.degree = self.trace[-1][1]
        self.answer = self.terms if self.task_type == "terms" else self.degree
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return " ".join(str(bit) for bit in self.table)

    def _descr(self, language):
        key = "s0" if self.task_type == "terms" else "s1"
        return texts.t(key, language, n=self.n, size=self.size, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, terms=terms, degree=degree)
            for index, (terms, degree) in enumerate(self.trace, 1)
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
