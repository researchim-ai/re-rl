"""ExpectimaxTask — значение и ход в дереве с узлами случая.

Корень максимизирует. Каждый ход ведёт к узлу случая с двумя или тремя исходами.
При равенстве выбирается меньший номер хода. Номера ходов с 1.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction

Outcome = Tuple[Fraction, int]
_PAIRS = [
    (Fraction(1, 2), Fraction(1, 2)),
    (Fraction(1, 3), Fraction(2, 3)),
    (Fraction(2, 3), Fraction(1, 3)),
    (Fraction(1, 4), Fraction(3, 4)),
    (Fraction(3, 4), Fraction(1, 4)),
]
_TRIPLES = [
    (Fraction(1, 3), Fraction(1, 3), Fraction(1, 3)),
    (Fraction(1, 2), Fraction(1, 4), Fraction(1, 4)),
    (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)),
    (Fraction(2, 3), Fraction(1, 6), Fraction(1, 6)),
]


def expectimax(actions: Sequence[Sequence[Outcome]]) -> Tuple[Fraction, int]:
    best = None
    chosen = 1
    for index, outcomes in enumerate(actions):
        value = sum((prob * utility for prob, utility in outcomes), Fraction(0))
        if best is None or value > best:
            best = value
            chosen = index + 1
    return best, chosen


class ExpectimaxTask(BaseMathTask):
    TASK_TYPE = "expectimax"
    TASK_TYPES = ["value", "action"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"a": 2, "mag": 4, "triple": 0}, 2: {"a": 2, "mag": 5, "triple": 0},
        3: {"a": 3, "mag": 5, "triple": 0}, 4: {"a": 3, "mag": 6, "triple": 0},
        5: {"a": 3, "mag": 6, "triple": 0}, 6: {"a": 4, "mag": 8, "triple": 0},
        7: {"a": 4, "mag": 8, "triple": 1}, 8: {"a": 4, "mag": 10, "triple": 1},
        9: {"a": 5, "mag": 10, "triple": 1}, 10: {"a": 5, "mag": 12, "triple": 1},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n_actions = int(p["a"])
        self.mag = int(p["mag"])
        self.triple = int(p["triple"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.actions: List[List[Outcome]] = []
        for _ in range(self.n_actions):
            if self.triple and random.random() < 0.5:
                probs = random.choice(_TRIPLES)
            else:
                probs = random.choice(_PAIRS[:2 + min(3, difficulty // 2)])
            self.actions.append([
                (prob, random.randint(-self.mag, self.mag)) for prob in probs
            ])
        self.value, self.choice = expectimax(self.actions)
        self.answer = self.value if self.task_type == "value" else Fraction(self.choice)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _shown(self, language: str) -> str:
        chunks = []
        for index, outcomes in enumerate(self.actions):
            bits = ", ".join(
                ((texts.t('s5', language, utility=utility, v1=fmt_fraction(prob))))
                for prob, utility in outcomes
            )
            label = (texts.t('s2', language, v0=index + 1, bits=bits))
            chunks.append(label)
        return " ".join(chunks)

    def _descr(self, language):
        rule = ((texts.t('s0', language, v0=self._shown(language))))
        ask = (((texts.t('s3', language)))
               if self.task_type == "value" else
               ((texts.t('s4', language))))
        return f"{rule} {ask}"

    def solve(self):
        shown = str(self.choice) if self.task_type == "action" else fmt_fraction(self.value)
        step = ((texts.t('s1', self.language, v0=fmt_fraction(self.value), choice=self.choice)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=shown)))]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "action":
            return U.verify_int(prediction, self.choice)
        return verify_fraction(prediction, self.value)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
