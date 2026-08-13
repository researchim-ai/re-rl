"""Чтение столбчатой диаграммы (визуальная задача).

По изображению диаграммы нужно ответить:
- ``max_category`` / ``min_category`` — категория с наибольшим/наименьшим столбцом;
- ``difference``                      — разница между наибольшим и наименьшим;
- ``total``                           — сумма всех значений.

Значения на столбцах НЕ подписаны — читаются по сетке оси Y. Масштаб — число категорий.
"""

import random
import string
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image
from re_rl.tasks.math.logic import _logic_utils as U


class BarChartReadTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "bar_chart_read"
    TASK_TYPES = ["max_category", "min_category", "difference", "total"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "max_v": 8}, 2: {"n": 3, "max_v": 10}, 3: {"n": 4, "max_v": 10},
        4: {"n": 4, "max_v": 12}, 5: {"n": 5, "max_v": 12}, 6: {"n": 5, "max_v": 15},
        7: {"n": 6, "max_v": 15}, 8: {"n": 6, "max_v": 18}, 9: {"n": 7, "max_v": 20},
        10: {"n": 8, "max_v": 20},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.n = int(p["n"])
        self.max_v = int(p["max_v"])
        self._build()
        super().__init__(self._descr(language), language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _build(self):
        self.labels = list(string.ascii_uppercase[:self.n])
        # значения с уникальными максимумом и минимумом
        for _ in range(200):
            self.values = [random.randint(1, self.max_v) for _ in range(self.n)]
            if self.values.count(max(self.values)) == 1 and self.values.count(min(self.values)) == 1:
                break
        self.data = dict(zip(self.labels, self.values))
        self.i_max = max(range(self.n), key=lambda i: self.values[i])
        self.i_min = min(range(self.n), key=lambda i: self.values[i])

    def render_image(self):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(0.7 * self.n + 1.5, 4.0))
        ax.bar(self.labels, self.values, color="#2aa198", edgecolor="black")
        ax.set_yticks(range(0, self.max_v + 2))
        ax.grid(True, axis="y", linestyle=":", alpha=0.6)
        ax.set_ylim(0, self.max_v + 1)
        ax.set_xlabel("Категория")
        ax.set_ylabel("Значение")
        ax.set_title("Диаграмма")
        return fig_to_image(fig)

    def _descr(self, language):
        ru = language == "ru"
        if self.task_type == "max_category":
            return ("На столбчатой диаграмме показаны значения по категориям. У какой категории "
                    "самый высокий столбец? Укажите её букву." if ru else
                    "The bar chart shows values per category. Which category has the tallest bar? "
                    "Give its letter.")
        if self.task_type == "min_category":
            return ("На столбчатой диаграмме показаны значения по категориям. У какой категории "
                    "самый низкий столбец? Укажите её букву." if ru else
                    "The bar chart shows values per category. Which category has the shortest bar? "
                    "Give its letter.")
        if self.task_type == "difference":
            return ("На диаграмме показаны значения по категориям. Чему равна разница между самым "
                    "высоким и самым низким столбцами?" if ru else
                    "The chart shows values per category. What is the difference between the tallest "
                    "and the shortest bar?")
        return ("На диаграмме показаны значения по категориям. Чему равна сумма всех значений?"
                if ru else
                "The chart shows values per category. What is the total of all values?")

    def solve(self):
        ru = self.language == "ru"
        if self.task_type in ("max_category", "min_category"):
            idx = self.i_max if self.task_type == "max_category" else self.i_min
            lbl = self.labels[idx]
            word = ("наибольший" if self.task_type == "max_category" else "наименьший") if ru else (
                "largest" if self.task_type == "max_category" else "smallest")
            self.solution_steps = [
                (f"Сравниваем высоты столбцов и находим {word}." if ru else
                 f"Compare bar heights and find the {word}."),
                (f"Ответ: категория {lbl} (значение {self.values[idx]})." if ru else
                 f"Answer: category {lbl} (value {self.values[idx]}).")]
            self.final_answer = lbl
            self._label_answer = lbl
        elif self.task_type == "difference":
            diff = self.values[self.i_max] - self.values[self.i_min]
            self.solution_steps = [
                (f"Максимум = {self.values[self.i_max]}, минимум = {self.values[self.i_min]}."
                 if ru else
                 f"Max = {self.values[self.i_max]}, min = {self.values[self.i_min]}."),
                (f"Разница = {diff}." if ru else f"Difference = {diff}.")]
            self.final_answer = str(diff)
        else:
            total = sum(self.values)
            self.solution_steps = [
                ("Складываем высоты всех столбцов." if ru else "Add up all bar heights."),
                (f"Сумма = {total}." if ru else f"Total = {total}.")]
            self.final_answer = str(total)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.task_type in ("max_category", "min_category"):
            return U.verify_label(prediction, [self._label_answer])
        return U.verify_int(prediction, int(self.final_answer))

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
