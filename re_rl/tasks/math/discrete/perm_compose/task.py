"""PermComposeTask — композиция подстановок.

Сначала применяется первая подстановка. Чётность складывается по модулю 2.
Число подстановок растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Perm = List[int]


def inversion_count(perm: Sequence[int]) -> int:
    count = 0
    size = len(perm)
    for i in range(size):
        for j in range(i + 1, size):
            if perm[i] > perm[j]:
                count += 1
    return count


def format_perm(perm: Sequence[int]) -> str:
    return " ".join(str(item) for item in perm)


def compose_perms(perms: Sequence[Perm]) -> Tuple[List[Perm], List[int], List[int]]:
    size = len(perms[0])
    current = list(range(1, size + 1))
    images = []
    signs = []
    inversions = []
    parity = 0
    for perm in perms:
        current = [perm[item - 1] for item in current]
        inv = inversion_count(perm)
        parity ^= inv % 2
        images.append(list(current))
        signs.append(parity)
        inversions.append(inv)
    return images, signs, inversions


class PermComposeTask(BaseMathTask):
    TASK_TYPE = "perm_compose"
    TASK_TYPES = ["image", "sign"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "m": 3}, 2: {"n": 2, "m": 3}, 3: {"n": 3, "m": 4},
        4: {"n": 3, "m": 4}, 5: {"n": 4, "m": 4}, 6: {"n": 5, "m": 5},
        7: {"n": 6, "m": 5}, 8: {"n": 6, "m": 5}, 9: {"n": 7, "m": 6},
        10: {"n": 8, "m": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.m = max(2, int(p["m"]))
        self.perms = []
        for _ in range(self.n):
            perm = list(range(1, self.m + 1))
            random.shuffle(perm)
            self.perms.append(perm)
        self.images, self.signs, self.inversions = compose_perms(self.perms)
        self.k = random.randint(1, self.m)
        self.image = self.images[-1][self.k - 1]
        self.sign = self.signs[-1]
        self.answer = self.image if self.task_type == "image" else self.sign
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(format_perm(perm) for perm in self.perms)
        key = "s0" if self.task_type == "image" else "s1"
        return texts.t(key, language, n=self.n, m=self.m, listing=listing, k=self.k)

    def solve(self):
        steps = []
        for index, (perm, image, sign, inv) in enumerate(
            zip(self.perms, self.images, self.signs, self.inversions), 1
        ):
            steps.append(texts.t(
                "s2", self.language, i=index, listing=format_perm(perm),
                inversions=inv, item=self.k, image=image[self.k - 1], sign=sign,
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
