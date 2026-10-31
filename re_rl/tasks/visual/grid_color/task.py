"""Подсчёт по цветной сетке (визуальная задача, рендер через PIL).

По изображению сетки из цветных клеток нужно ответить:
- ``count_color`` — сколько клеток заданного цвета;
- ``most_color``  — какого цвета клеток больше всего.

Масштаб задаётся размером сетки и числом цветов.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from PIL import Image, ImageDraw

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.visual._visual_utils import VisualTaskMixin
from re_rl.tasks.math.logic import _logic_utils as U

COLORS = [
    {"rgb": (220, 50, 47), "ru": texts.literal('literals.s9'), "gen": texts.literal('literals.s10'), "en": "red"},
    {"rgb": (38, 139, 210), "ru": texts.literal('literals.s11'), "gen": texts.literal('literals.s12'), "en": "blue"},
    {"rgb": (46, 160, 67), "ru": texts.literal('literals.s13'), "gen": texts.literal('literals.s14'), "en": "green"},
    {"rgb": (245, 205, 0), "ru": texts.literal('literals.s15'), "gen": texts.literal('literals.s16'), "en": "yellow"},
]


class GridColorCountTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = texts.literal('literals.s8')
    TASK_TYPES = ["count_color", "most_color"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "k": 2}, 2: {"n": 3, "k": 3}, 3: {"n": 4, "k": 3},
        4: {"n": 4, "k": 3}, 5: {"n": 5, "k": 3}, 6: {"n": 5, "k": 4},
        7: {"n": 6, "k": 4}, 8: {"n": 6, "k": 4}, 9: {"n": 7, "k": 4},
        10: {"n": 8, "k": 4},
    }
    CELL = 48

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.n = int(p["n"])
        self.k = min(int(p["k"]), len(COLORS))
        self._build()
        super().__init__(self._descr(language), language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _build(self):
        self.palette = random.sample(range(len(COLORS)), self.k)
        for _ in range(200):
            self.grid = [[random.choice(self.palette) for _ in range(self.n)]
                         for _ in range(self.n)]
            counts = {c: sum(row.count(c) for row in self.grid) for c in self.palette}
            self.counts = counts
            top = max(counts.values())
            if list(counts.values()).count(top) == 1:  # уникальный максимум
                break
        else:
            raise ValueError("generation_failed")
        if self.task_type == "count_color":
            self.target = random.choice(self.palette)
            self.answer_int = self.counts[self.target]
        else:
            self.most = max(self.counts, key=lambda c: self.counts[c])

    def render_image(self):
        n, cell = self.n, self.CELL
        img = Image.new("RGB", (n * cell + 1, n * cell + 1), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        for i in range(n):
            for j in range(n):
                rgb = COLORS[self.grid[i][j]]["rgb"]
                draw.rectangle([j * cell, i * cell, (j + 1) * cell, (i + 1) * cell],
                               fill=rgb, outline=(0, 0, 0))
        return img

    def _descr(self, language):
        if self.task_type == "count_color":
            c = COLORS[self.target]
            return ((texts.t('s1', language, n=self.n, n_2=self.n, v2=c[texts.t('s2', language)])))
        return ((texts.t('s0', language, n=self.n, n_2=self.n)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        if self.task_type == "count_color":
            c = COLORS[self.target]
            name = (c[texts.t('s2', self.language)])
            self.solution_steps = [
                ((texts.t('s4', self.language, name=name))),
                ((texts.t('s5', self.language, answer_int=self.answer_int)))]
            self.final_answer = str(self.answer_int)
        else:
            c = COLORS[self.most]
            self.solution_steps = [
                ((texts.t('s6', self.language))),
                (texts.t('s17', self.language, v0=c[texts.t('s7', self.language)], v1=self.counts[self.most]))]
            self.final_answer = (c[texts.t('s3', self.language)])
            self._syns = [c["ru"], c["gen"], c["en"]]

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.task_type == "count_color":
            return U.verify_int(prediction, int(self.answer_int))
        return U.verify_label(prediction, self._syns)

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
