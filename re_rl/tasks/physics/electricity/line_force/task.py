"""LineForceTask — кулоновская сила на пробный заряд от нескольких источников.

Коэффициент в законе Кулона равен 1. Пробный заряд стоит в нуле. Вклад источника равен его заряду, делённому на квадрат координаты, со знаком против координаты.
Число источников растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Source = Tuple[int, int]
PLACES = (-8, -7, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 8)


def field_trace(test: int, sources: Sequence[Source]) -> List[Tuple[int, int, int]]:
    if test == 0:
        raise RuntimeError("force mismatch")
    total = 0
    magnitude = 0
    trace = []
    for charge, place in sources:
        radius = abs(place)
        if radius == 0 or (test * charge) % (radius * radius):
            raise RuntimeError("force mismatch")
        sign = 1 if place > 0 else -1
        force = -test * charge * sign // (radius * radius)
        total += force
        magnitude += abs(force)
        trace.append((force, total, magnitude))
    return trace


class LineForceTask(BaseMathTask):
    TASK_TYPE = "line_force"
    TASK_TYPES = ["net", "spread"]

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
        self.test = random.randint(1, 3)
        places = list(PLACES)
        random.shuffle(places)
        self.sources = []
        for place in places[:self.n]:
            factor = random.randint(-3, 3)
            if factor == 0:
                factor = 1
            self.sources.append((factor * place * place, place))
        self.trace = field_trace(self.test, self.sources)
        self.net = self.trace[-1][1]
        self.spread = self.trace[-1][2]
        self.answer = self.net if self.task_type == "net" else self.spread
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(f"{charge} {place}" for charge, place in self.sources)

    def _descr(self, language):
        key = "s0" if self.task_type == "net" else "s1"
        return texts.t(key, language, n=self.n, test=self.test, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, force=force, net=net, spread=spread)
            for index, (force, net, spread) in enumerate(self.trace, 1)
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
