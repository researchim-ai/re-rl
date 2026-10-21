"""HmmDecodeTask — алгоритм вперед и путь Витерби.

Вероятности — дроби и в каждой строке дают 1.
Если несколько предыдущих состояний одинаково хороши, берётся меньший номер.
В конце при равенстве тоже берётся меньший номер. Номера состояний с 1.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Optional, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction

_SYMBOLS = "abc"


def _simplex(width: int) -> List[Fraction]:
    weights = [random.randint(1, 3) for _ in range(width)]
    total = sum(weights)
    return [Fraction(weight, total) for weight in weights]


def forward_probability(start: Sequence[Fraction], trans: Sequence[Sequence[Fraction]],
                        emit: Sequence[Sequence[Fraction]], observations: Sequence[int]) -> Fraction:
    alpha = [start[state] * emit[state][observations[0]] for state in range(len(start))]
    for time in range(1, len(observations)):
        alpha = [
            sum(alpha[prev] * trans[prev][state] for prev in range(len(start))) * emit[state][observations[time]]
            for state in range(len(start))
        ]
    return sum(alpha, Fraction(0))


def viterbi_path(start: Sequence[Fraction], trans: Sequence[Sequence[Fraction]],
                 emit: Sequence[Sequence[Fraction]], observations: Sequence[int]) -> List[int]:
    n_states = len(start)
    scores = [start[state] * emit[state][observations[0]] for state in range(n_states)]
    backs: List[List[int]] = []
    for time in range(1, len(observations)):
        new_scores: List[Fraction] = []
        back: List[int] = []
        for state in range(n_states):
            best: Optional[Fraction] = None
            arg = 0
            for prev in range(n_states):
                cand = scores[prev] * trans[prev][state] * emit[state][observations[time]]
                if best is None or cand > best or (cand == best and prev < arg):
                    best = cand
                    arg = prev
            new_scores.append(best)
            back.append(arg)
        scores = new_scores
        backs.append(back)
    end = 0
    best_end: Optional[Fraction] = None
    for state, score in enumerate(scores):
        if best_end is None or score > best_end or (score == best_end and state < end):
            best_end = score
            end = state
    path = [end]
    for back in reversed(backs):
        end = back[end]
        path.append(end)
    path.reverse()
    return path


class HmmDecodeTask(BaseMathTask):
    TASK_TYPE = "hmm_decode"
    TASK_TYPES = ["likelihood", "path"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"s": 2, "o": 2, "t": 2}, 2: {"s": 2, "o": 2, "t": 3},
        3: {"s": 2, "o": 2, "t": 3}, 4: {"s": 2, "o": 2, "t": 4},
        5: {"s": 2, "o": 3, "t": 4}, 6: {"s": 3, "o": 2, "t": 4},
        7: {"s": 3, "o": 3, "t": 5}, 8: {"s": 3, "o": 3, "t": 5},
        9: {"s": 3, "o": 3, "t": 6}, 10: {"s": 3, "o": 3, "t": 7},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n_states = int(p["s"])
        self.n_symbols = int(p["o"])
        self.length = int(p["t"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.start = _simplex(self.n_states)
        self.trans = [_simplex(self.n_states) for _ in range(self.n_states)]
        self.emit = [_simplex(self.n_symbols) for _ in range(self.n_states)]
        self.observations = [random.randrange(self.n_symbols) for _ in range(self.length)]
        self.likelihood = forward_probability(self.start, self.trans, self.emit, self.observations)
        self.path = [state + 1 for state in viterbi_path(self.start, self.trans, self.emit, self.observations)]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _row(self, values: Sequence[Fraction]) -> str:
        return ", ".join(fmt_fraction(value) for value in values)

    def _descr(self, language):
        ru = language == "ru"
        symbols = " ".join(_SYMBOLS[index] for index in self.observations)
        trans = "; ".join(
            (f"из {state + 1}: {self._row(row)}" if ru else f"from {state + 1}: {self._row(row)}")
            for state, row in enumerate(self.trans)
        )
        emit = "; ".join(
            (f"состояние {state + 1}: {self._row(row)}" if ru else f"state {state + 1}: {self._row(row)}")
            for state, row in enumerate(self.emit)
        )
        obs_names = ", ".join(_SYMBOLS[:self.n_symbols])
        rule = ((f"Скрытая марковская модель, состояния с 1, символы {obs_names}. "
                 f"Начальные вероятности: {self._row(self.start)}. Переходы: {trans}. "
                 f"Вероятности символов в том же порядке: {emit}. Наблюдения: {symbols}. "
                 f"Если несколько предыдущих состояний дают одну вероятность, берётся меньший номер; "
                 f"в конце при равенстве тоже меньший номер.") if ru else
                (f"Hidden Markov model, states start at 1, symbols {obs_names}. "
                 f"Initial probabilities: {self._row(self.start)}. Transitions: {trans}. "
                 f"Symbol probabilities in that same order: {emit}. Observations: {symbols}. "
                 f"If several previous states give the same probability, take the smaller index; "
                 f"at the end, ties also take the smaller index."))
        if self.task_type == "likelihood":
            ask = (("Найдите вероятность наблюдений. Ответ — целое или несократимая дробь.") if ru else
                   ("Find the probability of the observations. Answer with an integer or a reduced fraction."))
        else:
            ask = (("Выпишите путь Витерби номерами состояний через запятую.") if ru else
                   ("Write the Viterbi path as comma-separated state indices."))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        path = ", ".join(map(str, self.path))
        shown = fmt_fraction(self.likelihood) if self.task_type == "likelihood" else path
        step = ((f"Вероятность {fmt_fraction(self.likelihood)}, путь {path}.") if ru else
                (f"Probability {fmt_fraction(self.likelihood)}, path {path}."))
        self.solution_steps = [step, (f"Ответ: {shown}." if ru else f"Answer: {shown}.")]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "path":
            return U.verify_int_sequence(prediction, self.path)
        return verify_fraction(prediction, self.likelihood)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
