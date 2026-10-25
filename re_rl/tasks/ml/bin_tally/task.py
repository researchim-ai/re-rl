"""BinTallyTask — попадания и ошибки внутри одной корзины счёта.

Корзины нумеруются 1, 2 и 3. Метка 1 — верный ответ, метка 0 — ошибка.
Число предметов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Row = Tuple[int, int]


def bin_trace(rows: Sequence[Row], bucket: int) -> List[Tuple[int, int]]:
    correct = 0
    wrong = 0
    trace = []
    for bin_id, label in rows:
        if bin_id == bucket:
            if label:
                correct += 1
            else:
                wrong += 1
        trace.append((correct, wrong))
    return trace


class BinTallyTask(BaseMathTask):
    TASK_TYPE = "bin_tally"
    TASK_TYPES = ["correct", "wrong"]

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
        self.rows = [(random.randint(1, 3), random.randint(0, 1)) for _ in range(self.n)]
        self.bucket = random.randint(1, 3)
        self.trace = bin_trace(self.rows, self.bucket)
        self.correct = self.trace[-1][0]
        self.wrong = self.trace[-1][1]
        self.answer = self.correct if self.task_type == "correct" else self.wrong
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{bin_id}:{label}" for bin_id, label in self.rows)
        key = "s0" if self.task_type == "correct" else "s1"
        return texts.t(key, language, n=self.n, rows=shown, bucket=self.bucket)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, bin_id=bin_id, label=label, correct=correct, wrong=wrong)
            for index, ((bin_id, label), (correct, wrong)) in enumerate(zip(self.rows, self.trace), 1)
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
