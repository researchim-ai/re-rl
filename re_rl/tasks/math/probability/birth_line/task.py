"""BirthLineTask — одна траектория ветвящегося процесса.

Потомки читаются слева направо. Поколение забирает столько чисел, сколько особей было в предыдущем.
Сумма этих чисел — следующее поколение. Ноль означает вымирание.
Длина списка растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def birth_trace(offspring: Sequence[int]) -> List[Tuple[int, int]]:
    population = 1
    used = 0
    running = 0
    extinct = 0
    finished = 0
    trace = []
    for index, child in enumerate(offspring, 1):
        if child < 0:
            raise RuntimeError("birth mismatch")
        if population == 0:
            trace.append((0, extinct))
            continue
        running += child
        used += 1
        if used == population:
            finished += population
            population = running
            running = 0
            used = 0
            if population == 0 and extinct == 0:
                extinct = index
        trace.append((population, extinct))
    if finished > len(offspring):
        raise RuntimeError("birth mismatch")
    return trace


class BirthLineTask(BaseMathTask):
    TASK_TYPE = "birth_line"
    TASK_TYPES = ["pop", "extinct"]

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
        self.offspring = [random.randint(0, 2) for _ in range(self.n)]
        self.trace = birth_trace(self.offspring)
        self.pop = self.trace[-1][0]
        self.extinct = self.trace[-1][1]
        self.answer = self.pop if self.task_type == "pop" else self.extinct
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return " ".join(str(child) for child in self.offspring)

    def _descr(self, language):
        key = "s0" if self.task_type == "pop" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, pop=pop, extinct=extinct)
            for index, (pop, extinct) in enumerate(self.trace, 1)
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
