"""DecisionListTask — список правил, где срабатывает первое совпадение.

Правило i смотрит на признак i. Если бит совпал, ответ этого правила окончательный.
Иначе действует запасной ответ. Число правил растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Rule = Tuple[int, int]


def first_match(bits: Sequence[int], rules: Sequence[Rule], default: int) -> Tuple[int, int]:
    for index, (required, label) in enumerate(rules, 1):
        if bits[index - 1] == required:
            return label, index
    return default, 0


class DecisionListTask(BaseMathTask):
    TASK_TYPE = "decision_list"
    TASK_TYPES = ["label", "fired"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 7},
        9: {"n": 8}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.bits = [random.randint(0, 1) for _ in range(self.n)]
        self.rules = [(random.randint(0, 1), random.choice((-1, 1))) for _ in range(self.n)]
        self.default = random.choice((-1, 1))
        self.label, self.fired = first_match(self.bits, self.rules, self.default)
        self.answer = self.label if self.task_type == "label" else self.fired
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        bits = " ".join(str(bit) for bit in self.bits)
        rules = "; ".join(f"{index}: {required}->{label}" for index, (required, label) in enumerate(self.rules, 1))
        key = "s0" if self.task_type == "label" else "s1"
        return texts.t(key, language, n=self.n, bits=bits, rules=rules, default=self.default)

    def solve(self):
        steps = []
        chosen = False
        for index, ((required, label), bit) in enumerate(zip(self.rules, self.bits), 1):
            hit = int(bit == required and not chosen)
            if bit == required:
                chosen = True
            steps.append(texts.t(
                "s2", self.language, i=index, bit=bit, required=required, label=label, hit=hit,
            ))
        steps.append(texts.t("s3", self.language, label=self.label, fired=self.fired, default=self.default))
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
