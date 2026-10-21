"""EliminationQueryTask — точный вывод в цепочке бинарных признаков.

Каждый следующий признак зависит только от предыдущего.
Считается вероятность последнего признака и апостериорная вероятность первого.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Optional, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction

Step = Tuple[Fraction, Fraction]


def chain_marginal(start: Fraction, steps: Sequence[Step]) -> Fraction:
    prob = start
    for yes, no in steps:
        prob = yes * prob + no * (1 - prob)
    return prob


def chain_answers(start: Fraction, steps: Sequence[Step]) -> Optional[Tuple[Fraction, Fraction]]:
    marginal = chain_marginal(start, steps)
    if marginal == 0:
        return None
    given_yes = chain_marginal(Fraction(1), steps)
    return marginal, given_yes * start / marginal


class EliminationQueryTask(BaseMathTask):
    TASK_TYPE = "elimination_query"
    TASK_TYPES = ["marginal", "posterior"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "den": 2}, 2: {"n": 3, "den": 3}, 3: {"n": 3, "den": 3},
        4: {"n": 4, "den": 4}, 5: {"n": 4, "den": 4}, 6: {"n": 4, "den": 5},
        7: {"n": 5, "den": 5}, 8: {"n": 5, "den": 6}, 9: {"n": 5, "den": 6},
        10: {"n": 6, "den": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n_vars = int(p["n"])
        self.den = int(p["den"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        found = None
        for _ in range(40):
            self.start = self._prob()
            self.steps = [(self._prob(), self._prob()) for _ in range(self.n_vars - 1)]
            found = chain_answers(self.start, self.steps)
            if found is not None:
                break
        if found is None:
            self.start = Fraction(1, 2)
            self.steps = [(Fraction(1), Fraction(0)) for _ in range(self.n_vars - 1)]
            found = chain_answers(self.start, self.steps)
        self.marginal, self.posterior = found
        self.answer = self.marginal if self.task_type == "marginal" else self.posterior
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _prob(self) -> Fraction:
        return Fraction(random.randint(0, self.den), self.den)

    def _descr(self, language):
        ru = language == "ru"
        lines = []
        for index, (yes, no) in enumerate(self.steps, start=2):
            lines.append(
                (f"признак {index}: если предыдущий 1, то {fmt_fraction(yes)}; "
                 f"если предыдущий 0, то {fmt_fraction(no)}" if ru else
                 f"feature {index}: {fmt_fraction(yes)} if the previous is 1; "
                 f"{fmt_fraction(no)} if the previous is 0")
            )
        chain = "; ".join(lines)
        rule = ((f"Цепочка из {self.n_vars} бинарных признаков. Каждый зависит только от предыдущего. "
                 f"Вероятность, что признак 1 равен 1: {fmt_fraction(self.start)}. "
                 f"Вероятность, что следующий равен 1: {chain}. "
                 f"Ответ — целое или несократимая дробь.") if ru else
                (f"A chain of {self.n_vars} binary features. Each depends only on the previous one. "
                 f"The probability that feature 1 equals 1 is {fmt_fraction(self.start)}. "
                 f"The probability that the next feature equals 1: {chain}. "
                 f"Answer with an integer or a reduced fraction."))
        if self.task_type == "marginal":
            ask = ((f"Найдите вероятность, что признак {self.n_vars} равен 1.") if ru else
                   (f"Find the probability that feature {self.n_vars} equals 1."))
        else:
            ask = ((f"Найдите вероятность, что признак 1 равен 1, если признак {self.n_vars} равен 1.")
                   if ru else
                   (f"Find the probability that feature 1 equals 1 given that feature {self.n_vars} equals 1."))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = fmt_fraction(self.answer)
        step = ((f"Маргинальная вероятность последнего {fmt_fraction(self.marginal)}, "
                 f"апостериорная первого {fmt_fraction(self.posterior)}.") if ru else
                (f"Marginal probability of the last feature {fmt_fraction(self.marginal)}, "
                 f"posterior of the first {fmt_fraction(self.posterior)}."))
        self.solution_steps = [step, (f"Ответ: {shown}." if ru else f"Answer: {shown}.")]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return verify_fraction(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
