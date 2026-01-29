# re_rl/tasks/physics/quantum/radioactive_decay_task.py

import random
import math
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class RadioactiveDecayTask(BaseMathTask):
    """Задачи на радиоактивный распад."""
    
    TASK_TYPES = ["remaining", "activity", "age", "decay_constant"]

    def __init__(self, language="ru", detail_level=3, task_type=None, difficulty=None, output_format="text"):
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        # Разные единицы времени
        time_units = ["years", "days", "hours", "seconds"]
        self.time_unit = random.choice(time_units)
        
        if self.time_unit == "years":
            self.T = round(random.uniform(1, 1000), 0)  # лет
            self.t = round(self.T * random.uniform(0.5, 5), 1)
        elif self.time_unit == "days":
            self.T = round(random.uniform(1, 30), 1)  # дней
            self.t = round(self.T * random.uniform(0.5, 5), 2)
        elif self.time_unit == "hours":
            self.T = round(random.uniform(1, 24), 1)  # часов
            self.t = round(self.T * random.uniform(0.5, 5), 2)
        else:
            self.T = round(random.uniform(1, 1000), 0)  # секунд
            self.t = round(self.T * random.uniform(0.5, 5), 1)
        
        self.A0 = round(random.uniform(1000, 100000), 0)  # Бк
        self.percent = round(random.uniform(5, 50), 1)  # %
        
        problem_text = self._create_problem_text()
        super().__init__(problem_text, language, detail_level, output_format)

    def _get_time_unit_name(self):
        units = {
            "years": {"ru": "лет", "en": "years"},
            "days": {"ru": "дней", "en": "days"},
            "hours": {"ru": "часов", "en": "hours"},
            "seconds": {"ru": "с", "en": "s"},
        }
        return units[self.time_unit][self.language]

    def _create_problem_text(self):
        t = PROMPT_TEMPLATES["radioactive_decay"]
        text = t["instructions"][self.language] + "\n\n"
        unit = self._get_time_unit_name()
        
        if self.task_type == "remaining":
            text += t["problem"]["remaining"][self.language].format(T=self.T, t=self.t)
        elif self.task_type == "activity":
            text += t["problem"]["activity"][self.language].format(A0=self.A0, T=self.T, t=self.t)
        elif self.task_type == "age":
            text += t["problem"]["age"][self.language].format(percent=self.percent, T=self.T)
        else:
            text += t["problem"]["decay_constant"][self.language].format(T=f"{self.T} {unit}")
        return text

    def solve(self):
        t = PROMPT_TEMPLATES["radioactive_decay"]
        steps = []
        unit = self._get_time_unit_name()
        
        if self.task_type == "remaining":
            steps.append(t["steps"]["decay_law"][self.language])
            n_half = self.t / self.T
            fraction = (0.5) ** n_half
            steps.append(f"N/N₀ = (1/2)^(t/T₁/₂) = (1/2)^({self.t}/{self.T}) = (1/2)^{round(n_half, 3)}")
            steps.append(f"N/N₀ = {round(fraction * 100, 2)}%")
            answer = f"{round(fraction * 100, 2)}%"
        elif self.task_type == "activity":
            steps.append(t["steps"]["activity"][self.language])
            n_half = self.t / self.T
            A = self.A0 * (0.5) ** n_half
            steps.append(f"A = {self.A0}·(1/2)^({self.t}/{self.T}) = {round(A, 1)} Бк")
            answer = f"A = {round(A, 1)} Бк"
        elif self.task_type == "age":
            steps.append(t["steps"]["age_formula"][self.language])
            fraction = self.percent / 100
            t_age = self.T * math.log(1/fraction) / math.log(2)
            steps.append(f"t = T₁/₂·ln(100/{self.percent})/ln(2) = {self.T}·ln({round(1/fraction, 3)})/ln(2)")
            steps.append(f"t = {round(t_age, 2)} {unit}")
            answer = f"t = {round(t_age, 2)} {unit}"
        else:
            steps.append(t["steps"]["decay_constant"][self.language])
            lam = math.log(2) / self.T
            steps.append(f"λ = ln(2)/T₁/₂ = 0.693/{self.T} = {lam:.6f} {unit}⁻¹")
            answer = f"λ = {lam:.6f} {unit}⁻¹"
        
        # Ограничиваем количество шагов (без дублирования)
        self.solution_steps = steps[:self.detail_level]
        self.final_answer = t["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "radioactive_decay"
    
    @classmethod
    def generate_random_task(cls, **kwargs):
        return cls(**kwargs)
