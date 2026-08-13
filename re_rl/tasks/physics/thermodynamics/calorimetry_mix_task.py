"""CalorimetryMixTask — теплообмен смеси N веществ (масштаб по числу веществ).

Подтипы: равновесная температура и восстановление неизвестной начальной
температуры. Проверка числовая (относительный допуск 2%).
"""

import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt


class CalorimetryMixTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """T = Σ(m·c·T)/Σ(m·c); либо восстановление неизвестной T_x при заданном T_eq."""

    TASK_TYPE = "calorimetry_mix"
    TASK_TYPES = ["equilibrium_temp", "missing_temperature"]

    # Характерные удельные теплоёмкости, Дж/(кг·К).
    SPECIFIC_HEATS = [4180, 2400, 900, 897, 385, 450, 130, 235, 840]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "max_m": 3, "T_lo": 10, "T_hi": 60},
        2: {"n": 2, "max_m": 5, "T_lo": 0, "T_hi": 80},
        3: {"n": 3, "max_m": 6, "T_lo": 0, "T_hi": 90},
        4: {"n": 3, "max_m": 8, "T_lo": -10, "T_hi": 95},
        5: {"n": 4, "max_m": 10, "T_lo": -20, "T_hi": 100},
        6: {"n": 5, "max_m": 12, "T_lo": -20, "T_hi": 120},
        7: {"n": 6, "max_m": 15, "T_lo": -30, "T_hi": 150},
        8: {"n": 7, "max_m": 20, "T_lo": -40, "T_hi": 200},
        9: {"n": 8, "max_m": 25, "T_lo": -50, "T_hi": 250},
        10: {"n": 10, "max_m": 30, "T_lo": -60, "T_hi": 300},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)
        self._preset = preset
        n = max(2, int(round(preset["n"])))

        def rnd_row() -> Tuple[float, int, float]:
            m = round(random.uniform(0.2, preset["max_m"]), 2)
            c = random.choice(self.SPECIFIC_HEATS)
            T = round(random.uniform(preset["T_lo"], preset["T_hi"]), 1)
            return (m, c, T)

        if self.task_type == "equilibrium_temp":
            self.rows: List[Tuple[float, int, float]] = [rnd_row() for _ in range(n)]
        else:  # missing_temperature
            # Генерируем все вещества, считаем T_eq, прячем температуру последнего.
            full = [rnd_row() for _ in range(n)]
            num = sum(m * c * T for m, c, T in full)
            den = sum(m * c for m, c, _ in full)
            self._Teq = round(num / den, 3)
            self.m_x, self.c_x, self._Tx = full[-1]
            self.rows = full[:-1]

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _rows_str(self) -> str:
        return ", ".join(f"({m}, {c}, {T})" for m, c, T in self.rows)

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["calorimetry_mix"]["problem"][self.task_type][language]
        if self.task_type == "equilibrium_temp":
            return p.format(rows=self._rows_str())
        return p.format(rows=self._rows_str(), m=self.m_x, c=self.c_x, Teq=self._Teq)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["calorimetry_mix"]["steps"]
        if self.task_type == "equilibrium_temp":
            num = sum(m * c * T for m, c, T in self.rows)
            den = sum(m * c for m, c, _ in self.rows)
            T = num / den
            self.solution_steps.append(steps["balance"][self.language])
            self.solution_steps.append(steps["equilibrium_formula"][self.language])
            self.solution_steps.append(f"T = {fmt(num)}/{fmt(den)} = {fmt(T)} °C")
            self.final_answer = f"T = {fmt(T)} °C"
            self._answer_numbers = [T]
        else:  # missing_temperature
            num_known = sum(m * c * T for m, c, T in self.rows)
            den_all = sum(m * c for m, c, _ in self.rows) + self.m_x * self.c_x
            Tx = (self._Teq * den_all - num_known) / (self.m_x * self.c_x)
            self.solution_steps.append(steps["balance"][self.language])
            self.solution_steps.append(steps["missing_formula"][self.language])
            self.solution_steps.append(f"T_x = {fmt(Tx)} °C")
            self.final_answer = f"T_x = {fmt(Tx)} °C"
            self._answer_numbers = [Tx]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
