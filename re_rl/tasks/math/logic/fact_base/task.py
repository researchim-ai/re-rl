"""FactBaseTask — вопросы к базе фактов с добавлением и удалением.

Повторный факт не копируется. Удаление отсутствующего ничего не меняет.
Число команд растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Command = Tuple[int, int]


def fact_trace(commands: Sequence[Command]) -> List[Tuple[int, int]]:
    known = set()
    hits = 0
    trace = []
    for code, item in commands:
        if code == 0:
            known.add(item)
        elif code == 1:
            known.discard(item)
        elif item in known:
            hits += 1
        trace.append((len(known), hits))
    return trace


class FactBaseTask(BaseMathTask):
    TASK_TYPE = "fact_base"
    TASK_TYPES = ["hits", "size"]

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
        self.commands = [(random.randint(0, 2), random.randrange(self.n)) for _ in range(self.n)]
        self.trace = fact_trace(self.commands)
        self.size = self.trace[-1][0]
        self.hits = self.trace[-1][1]
        self.answer = self.hits if self.task_type == "hits" else self.size
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(f"{code} {item}" for code, item in self.commands)
        key = "s0" if self.task_type == "hits" else "s1"
        return texts.t(key, language, n=self.n, commands=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, code=code, item=item, size=size, hits=hits)
            for index, ((code, item), (size, hits)) in enumerate(zip(self.commands, self.trace), 1)
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
