"""AbacusReadTask — число по чёрным косточкам на стержнях.

Правый стержень — единицы. Цифра стержня равна числу чёрных косточек.
Число стержней растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from PIL import Image, ImageDraw

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.visual._visual_utils import VisualTaskMixin


class AbacusReadTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "abacus_read"
    TASK_TYPES = ["value", "digit_sum"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 4}, 7: {"n": 5}, 8: {"n": 5},
        9: {"n": 6}, 10: {"n": 6},
    }
    ROD = 48
    BEAD = 16

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.digits = [random.randint(1, 9)]
        self.digits.extend(random.randint(0, 9) for _ in range(self.n - 1))
        self.value = 0
        for digit in self.digits:
            self.value = self.value * 10 + digit
        self.digit_sum = sum(self.digits)
        self.answer = self.value if self.task_type == "value" else self.digit_sum
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language)

    def render_image(self):
        rod_w, bead = self.ROD, self.BEAD
        width = self.n * rod_w + 24
        height = 20 + 9 * (bead + 6) + 28
        image = Image.new("RGB", (width, height), (244, 236, 220))
        draw = ImageDraw.Draw(image)
        beam = height - 22
        draw.rectangle([10, beam, width - 10, beam + 8], fill=(92, 58, 30))
        for index, digit in enumerate(self.digits):
            cx = 12 + index * rod_w + rod_w // 2
            draw.line([(cx, 12), (cx, beam)], fill=(120, 82, 48), width=4)
            for level in range(digit):
                cy = beam - 12 - level * (bead + 4)
                draw.ellipse(
                    [cx - bead // 2, cy - bead // 2, cx + bead // 2, cy + bead // 2],
                    fill=(20, 20, 20), outline=(20, 20, 20),
                )
        return image

    def solve(self):
        steps = []
        place = 10 ** (self.n - 1)
        for index, digit in enumerate(self.digits, 1):
            steps.append(texts.t("s2", self.language, i=index, digit=digit, place=place))
            place //= 10
        steps.append(texts.t("s3", self.language, value=self.value, digit_sum=self.digit_sum))
        steps.append(texts.common("answer_line", self.language, answer=self.answer))
        self.solution_steps = steps
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
