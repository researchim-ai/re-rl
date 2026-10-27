"""FocusRowTask — действительные изображения цепочки тонких линз.

Расстояние до изображения равно произведению расстояния до предмета и фокуса, делённому на их разность.
Следующая линза стоит за изображением, поэтому предмет для неё действительный.
Число линз растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _divisors(number: int) -> List[int]:
    found = []
    probe = 1
    while probe * probe <= number:
        if number % probe == 0:
            found.append(probe)
            if probe * probe != number:
                found.append(number // probe)
        probe += 1
    return found


def focus_trace(focals: Sequence[int], gaps: Sequence[int], distance: int) -> List[Tuple[int, int]]:
    if len(gaps) != len(focals) - 1 or distance <= 0:
        raise RuntimeError("lens mismatch")
    object_distance = distance
    total = 0
    trace = []
    for index, focal in enumerate(focals):
        if focal <= 0 or object_distance <= focal:
            raise RuntimeError("lens mismatch")
        split = object_distance - focal
        if (object_distance * focal) % split:
            raise RuntimeError("lens mismatch")
        image = (object_distance * focal) // split
        if focal * (object_distance + image) != object_distance * image:
            raise RuntimeError("lens mismatch")
        total += image
        trace.append((image, total))
        if index + 1 < len(focals):
            object_distance = gaps[index] - image
            if object_distance <= 0:
                raise RuntimeError("lens mismatch")
    return trace


class FocusRowTask(BaseMathTask):
    TASK_TYPE = "focus_row"
    TASK_TYPES = ["image", "total"]

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
        focal, distance, image = self._lens()
        self.focals = [focal]
        self.gaps: List[int] = []
        self.distance = distance
        for _ in range(self.n - 1):
            next_focal, next_distance, next_image = self._lens()
            self.gaps.append(image + next_distance)
            self.focals.append(next_focal)
            image = next_image
        self.trace = focus_trace(self.focals, self.gaps, self.distance)
        self.image = self.trace[-1][0]
        self.total = self.trace[-1][1]
        self.answer = self.image if self.task_type == "image" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _lens(self) -> Tuple[int, int, int]:
        focal = random.randint(2, 8)
        split = random.choice(_divisors(focal * focal))
        distance = focal + split
        image = distance * focal // split
        return focal, distance, image

    def _listing_focals(self) -> str:
        return " ".join(str(focal) for focal in self.focals)

    def _listing_gaps(self) -> str:
        return " ".join(str(gap) for gap in self.gaps)

    def _descr(self, language):
        key = "s0" if self.task_type == "image" else "s1"
        return texts.t(
            key, language, n=self.n, distance=self.distance,
            focals=self._listing_focals(), gaps=self._listing_gaps(),
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, image=image, total=total)
            for index, (image, total) in enumerate(self.trace, 1)
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
