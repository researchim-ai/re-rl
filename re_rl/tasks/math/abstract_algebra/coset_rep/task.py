"""CosetRepTask — представители смежных классов циклической подгруппы.

Класс числа — орбита вычитания шага по модулю. Представитель — наименьший остаток класса.
Число проверяемых остатков растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def coset_walk(values: Sequence[int], step: int, modulus: int) -> List[Tuple[int, int]]:
    gap = math.gcd(step, modulus)
    seen = set()
    trace = []
    for value in values:
        point = value % modulus
        visited = set()
        while point not in visited:
            visited.add(point)
            point = (point - step) % modulus
        representative = min(visited)
        if representative != value % gap:
            raise RuntimeError("coset mismatch")
        seen.add(representative)
        trace.append((representative, len(seen)))
    return trace


class CosetRepTask(BaseMathTask):
    TASK_TYPE = "coset_rep"
    TASK_TYPES = ["rep", "kinds"]
    MODULI = (6, 8, 9, 10, 12, 14, 15, 16)

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
        self.modulus = random.choice(self.MODULI)
        choices = [step for step in range(1, self.modulus) if math.gcd(step, self.modulus) > 1]
        self.step = random.choice(choices)
        self.values = [random.randint(0, self.modulus - 1) for _ in range(self.n)]
        self.trace = coset_walk(self.values, self.step, self.modulus)
        self.rep = self.trace[-1][0]
        self.kinds = self.trace[-1][1]
        self.answer = self.rep if self.task_type == "rep" else self.kinds
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return " ".join(str(value) for value in self.values)

    def _descr(self, language):
        key = "s0" if self.task_type == "rep" else "s1"
        return texts.t(
            key, language, n=self.n, modulus=self.modulus, step=self.step, listing=self._listing(),
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, rep=rep, kinds=kinds)
            for index, (rep, kinds) in enumerate(self.trace, 1)
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
