"""HanoiDiskTask — ходы башни до правого стержня.

Диски уже разложены по стержням. Больший не лежит на меньшем.
Число дисков растёт с уровнем. Раскладка есть только на картинке.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from PIL import Image, ImageDraw

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.visual._visual_utils import VisualTaskMixin

COLORS = [
    (38, 139, 210), (220, 50, 47), (46, 160, 67), (230, 170, 20),
    (140, 70, 190), (240, 120, 30), (0, 150, 160), (180, 40, 90),
]


def hanoi_trace(pegs: List[int]) -> Tuple[List[Tuple[int, int, int, int]], int]:
    size = len(pegs) - 1
    trace: List[Tuple[int, int, int, int]] = []

    def walk(disk: int, goal: int) -> int:
        if disk == 0:
            return 0
        peg = pegs[disk]
        if peg == goal:
            cost = walk(disk - 1, goal)
            trace.append((disk, peg, 0, cost))
            return cost
        spare = 6 - peg - goal
        gather = walk(disk - 1, spare)
        cost = gather + (1 << (disk - 1))
        trace.append((disk, peg, 1, cost))
        return cost

    total = walk(size, 3)
    return trace, total


class HanoiDiskTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "hanoi_disk"
    TASK_TYPES = ["moves", "home"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 6},
        9: {"n": 7}, 10: {"n": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.pegs = [0] + [random.randint(1, 3) for _ in range(self.n)]
        self.trace, self.moves = hanoi_trace(self.pegs)
        self.home = sum(peg == 3 for peg in self.pegs[1:])
        self.answer = self.moves if self.task_type == "moves" else self.home
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "moves" else "s1"
        return texts.t(key, language)

    def render_image(self):
        disk_h = 18
        margin = 28
        span = 130
        height = margin + self.n * disk_h + 16
        width = span * 2 + 80
        image = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        base = height - 14
        peg_x = [40 + index * span for index in range(3)]
        draw.line([(16, base), (width - 16, base)], fill=(40, 40, 40), width=6)
        for x in peg_x:
            draw.line([(x, base), (x, margin)], fill=(90, 90, 90), width=4)
        stacks = {1: [], 2: [], 3: []}
        for disk in range(self.n, 0, -1):
            stacks[self.pegs[disk]].append(disk)
        for peg, disks in stacks.items():
            for level, disk in enumerate(disks):
                half = 16 + disk * 12
                x = peg_x[peg - 1]
                y = base - (level + 1) * disk_h
                draw.rounded_rectangle(
                    [x - half, y + 2, x + half, y + disk_h - 2],
                    radius=4,
                    fill=COLORS[disk - 1],
                    outline=(20, 20, 20),
                )
        return image

    def solve(self):
        steps = [
            texts.t("s2", self.language, k=disk, peg=peg, flag=flag, cost=cost)
            for disk, peg, flag, cost in self.trace
        ]
        steps.append(texts.t("s3", self.language, moves=self.moves, home=self.home))
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
