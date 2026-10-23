"""DominoChainTask — проверка стыков костяшек.

Стык верен, если правое поле кости совпадает с левым полем следующей.
Число костей растёт с уровнем. Ответ — номер первого разрыва или число верных стыков до него.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def first_break(dominoes: Sequence[Tuple[int, int]]) -> Tuple[int, int]:
    matched = 0
    for index in range(len(dominoes) - 1):
        if dominoes[index][1] != dominoes[index + 1][0]:
            return index + 1, matched
        matched += 1
    return 0, matched


class DominoChainTask(BaseMathTask):
    TASK_TYPE = "domino_chain"
    TASK_TYPES = ["break", "matched"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(3, int(p["n"]))
        left = random.randint(0, 6)
        self.dominoes: List[Tuple[int, int]] = []
        for _ in range(self.n):
            right = random.randint(0, 6)
            self.dominoes.append((left, right))
            left = right
        if random.randrange(2) == 0:
            junction = random.randrange(self.n - 1)
            required = self.dominoes[junction][1]
            new_left = (required + 1 + random.randrange(6)) % 7
            _old_left, right = self.dominoes[junction + 1]
            self.dominoes[junction + 1] = (new_left, right)
        self.break_at, self.matched = first_break(self.dominoes)
        self.answer = self.break_at if self.task_type == "break" else self.matched
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(f"{left}-{right}" for left, right in self.dominoes)
        key = "s0" if self.task_type == "break" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [texts.t("s2", self.language, i=1, a=self.dominoes[0][0], b=self.dominoes[0][1])]
        for index in range(1, self.n):
            previous = self.dominoes[index - 1][1]
            left, right = self.dominoes[index]
            ok = 1 if previous == left else 0
            steps.append(texts.t(
                "s3", self.language, i=index + 1, a=left, b=right, prev=previous, ok=ok,
            ))
        steps.append(texts.t("s4", self.language, break_at=self.break_at, matched=self.matched))
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
