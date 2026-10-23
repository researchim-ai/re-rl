"""KnaveNextTask — каждый говорит о следующем: рыцарь или лжец.

Рыцарь говорит правду, лжец говорит наоборот. Тип первого задан, дальше тип выводится из его слов.
Число людей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def knave_trace(first: int, claims: Sequence[int]) -> List[int]:
    kinds = [first]
    for claim in claims:
        speaker = kinds[-1]
        kinds.append(claim if speaker == 1 else 1 - claim)
    return kinds


class KnaveNextTask(BaseMathTask):
    TASK_TYPE = "knave_next"
    TASK_TYPES = ["knights", "kind"]

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
        self.first = random.randint(0, 1)
        self.claims = [random.randint(0, 1) for _ in range(self.n - 1)]
        self.kinds = knave_trace(self.first, self.claims)
        self.knights = sum(self.kinds)
        self.k = random.randint(1, self.n)
        self.kind = self.kinds[self.k - 1]
        self.answer = self.knights if self.task_type == "knights" else self.kind
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        claims = ", ".join(str(claim) for claim in self.claims)
        key = "s0" if self.task_type == "knights" else "s1"
        return texts.t(key, language, n=self.n, first=self.first, claims=claims, k=self.k)

    def solve(self):
        steps = [texts.t("s2", self.language, i=1, kind=self.kinds[0], knights=self.kinds[0])]
        knights = self.kinds[0]
        for index, (claim, kind) in enumerate(zip(self.claims, self.kinds[1:]), 2):
            knights += kind
            steps.append(texts.t(
                "s3", self.language, i=index, claim=claim,
                speaker=self.kinds[index - 2], kind=kind, knights=knights,
            ))
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
