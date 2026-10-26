"""YeeLineTask — схема Йи для одномерного поля.

Электрическое поле на целых узлах, магнитное между ними. Концы электрического поля закреплены в нуле.
После полного шага энергия полушага равна начальной сумме квадратов, если магнитное поле начиналось с нуля.
Число внутренних узлов и шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def maxwell_trace(electric: Sequence[int], steps: int) -> List[Tuple[int, int]]:
    field = list(electric)
    magnetic = [0] * (len(field) + 1)
    initial = sum(value * value for value in field)
    trace = []
    for _ in range(steps):
        previous = field[:]
        bounded = [0] + field + [0]
        magnetic = [
            magnetic[index] - (bounded[index + 1] - bounded[index])
            for index in range(len(magnetic))
        ]
        field = [
            field[index] - (magnetic[index + 1] - magnetic[index])
            for index in range(len(field))
        ]
        half = sum(new * old for new, old in zip(field, previous))
        half += sum(value * value for value in magnetic)
        if half != initial:
            raise RuntimeError("energy mismatch")
        trace.append((sum(field), field[-1]))
    return trace


class YeeLineTask(BaseMathTask):
    TASK_TYPE = "yee_line"
    TASK_TYPES = ["field", "end"]

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
        self.electric = [random.randint(-1, 1) for _ in range(self.n)]
        if not any(self.electric):
            self.electric[0] = 1
        self.trace = maxwell_trace(self.electric, self.n)
        self.field = self.trace[-1][0]
        self.end = self.trace[-1][1]
        self.answer = self.field if self.task_type == "field" else self.end
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return " ".join(str(value) for value in self.electric)

    def _descr(self, language):
        key = "s0" if self.task_type == "field" else "s1"
        return texts.t(key, language, n=self.n, electric=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, field=field, end=end)
            for index, (field, end) in enumerate(self.trace, 1)
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
