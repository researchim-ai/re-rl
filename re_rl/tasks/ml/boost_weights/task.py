"""BoostWeightsTask — целочисленные веса, которые удваиваются на ошибке.

У каждого примера метка +1 или -1 и начальный вес 1.
В раунде неверный прогноз удваивает вес примера. Число раундов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def double_weights(labels: Sequence[int], rounds: Sequence[Sequence[int]]) -> List[List[int]]:
    weights = [1] * len(labels)
    history = []
    for predictions in rounds:
        weights = [
            weight * 2 if prediction != label else weight
            for weight, prediction, label in zip(weights, predictions, labels)
        ]
        history.append(list(weights))
    return history


class BoostWeightsTask(BaseMathTask):
    TASK_TYPE = "boost_weights"
    TASK_TYPES = ["weight", "total"]
    EXAMPLES = 3

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
        self.labels = [random.choice((-1, 1)) for _ in range(self.EXAMPLES)]
        self.rounds = [
            [random.choice((-1, 1)) for _ in range(self.EXAMPLES)] for _ in range(self.n)
        ]
        self.history = double_weights(self.labels, self.rounds)
        self.k = random.randint(1, self.EXAMPLES)
        self.weight = self.history[-1][self.k - 1]
        self.total = sum(self.history[-1])
        self.answer = self.weight if self.task_type == "weight" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _row(self, values: Sequence[int]) -> str:
        return ", ".join(str(value) for value in values)

    def _descr(self, language):
        rounds = "; ".join(
            f"{index}: {self._row(predictions)}" for index, predictions in enumerate(self.rounds, 1)
        )
        key = "s0" if self.task_type == "weight" else "s1"
        return texts.t(key, language, n=self.n, labels=self._row(self.labels), rounds=rounds, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, weights=self._row(weights))
            for index, weights in enumerate(self.history, 1)
        ]
        steps.append(texts.t("s3", self.language, k=self.k, weight=self.weight, total=self.total))
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
