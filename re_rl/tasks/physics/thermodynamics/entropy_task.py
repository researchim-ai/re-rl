# re_rl/tasks/physics/thermodynamics/entropy_task.py

import random
import math
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class EntropyTask(BaseMathTask):
    """Задачи на энтропию."""
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n_range": (1, 3)},
        5: {"n_range": (2, 10)},
        10: {"n_range": (5, 50)},
    }
    
    TASK_TYPES = ["isothermal", "heat_transfer", "mixing"]
    R = 8.314  # Дж/(моль·К)

    def __init__(self, language="ru", detail_level=3, task_type=None, difficulty=None, output_format="text", reasoning_mode=False):
        if difficulty:
            preset = self._interpolate_difficulty(difficulty)
            n_range = preset.get("n_range", (1, 10))
        else:
            n_range = (1, 10)
        
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        self.n = round(random.uniform(*n_range), 2)
        self.T = round(random.uniform(273, 500), 0)
        self.ratio = random.randint(2, 10)
        self.Q = round(random.uniform(100, 5000), 0)
        self.m1 = round(random.uniform(0.5, 5), 2)
        self.m2 = round(random.uniform(0.5, 5), 2)
        self.T1 = round(random.uniform(10, 40), 0)
        self.T2 = round(random.uniform(60, 100), 0)
        
        problem_text = self._create_problem_text()
        super().__init__(problem_text, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_text(self):
        t = PROMPT_TEMPLATES["entropy"]
        text = t["instructions"][self.language] + "\n\n"
        
        if self.task_type == "isothermal":
            text += t["problem"]["isothermal"][self.language].format(n=self.n, T=self.T, ratio=self.ratio)
        elif self.task_type == "heat_transfer":
            text += t["problem"]["heat_transfer"][self.language].format(Q=self.Q, T=self.T)
        else:
            text += t["problem"]["mixing"][self.language].format(m1=self.m1, T1=self.T1, m2=self.m2, T2=self.T2)
        return text

    def solve(self):
        t = PROMPT_TEMPLATES["entropy"]
        steps = []
        
        if self.task_type == "isothermal":
            steps.append(t["steps"]["isothermal"][self.language])
            dS = self.n * self.R * math.log(self.ratio)
            steps.append(f"ΔS = {self.n}·{self.R}·ln({self.ratio}) = {round(dS, 2)} Дж/К")
            answer = round(dS, 2)
        elif self.task_type == "heat_transfer":
            steps.append(t["steps"]["definition"][self.language])
            dS = self.Q / self.T
            steps.append(f"ΔS = {self.Q}/{self.T} = {round(dS, 3)} Дж/К")
            answer = round(dS, 3)
        else:
            steps.append(t["steps"]["mixing"][self.language])
            c = 4186  # Дж/(кг·К)
            T1_K, T2_K = self.T1 + 273, self.T2 + 273
            Tf = (self.m1 * T1_K + self.m2 * T2_K) / (self.m1 + self.m2)
            dS = self.m1 * c * math.log(Tf/T1_K) + self.m2 * c * math.log(Tf/T2_K)
            steps.append(f"T_f = {round(Tf, 1)} К")
            steps.append(f"ΔS = {round(dS, 2)} Дж/К")
            answer = round(dS, 2)
        
        # НЕ обрезаем шаги — в reasoning_mode нужны все шаги
        self.solution_steps = steps
        self.final_answer = t["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "entropy"
    
    @classmethod
    def generate_random_task(cls, reasoning_mode=False, **kwargs):
        return cls(reasoning_mode=reasoning_mode, **kwargs)
