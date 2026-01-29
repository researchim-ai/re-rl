# re_rl/tasks/physics/thermodynamics/thermodynamic_cycles_task.py

import random
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class ThermodynamicCyclesTask(BaseMathTask):
    """
    Задачи на термодинамические циклы.
    """
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"T_range": (300, 500)},
        5: {"T_range": (400, 800)},
        10: {"T_range": (500, 2000)},
    }
    
    TASK_TYPES = ["carnot_efficiency", "work_from_heat", "refrigerator_cop"]

    def __init__(self, language="ru", detail_level=3, task_type=None, difficulty=None, output_format="text"):
        if difficulty:
            preset = self._interpolate_difficulty(difficulty)
            T_range = preset.get("T_range", (400, 800))
        else:
            T_range = (400, 800)
        
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        self.T1 = round(random.uniform(*T_range), 0)  # горячий
        self.T2 = round(random.uniform(250, self.T1 - 50), 0)  # холодный
        self.Q1 = round(random.uniform(1000, 10000), 0)  # Дж
        self.eta = round(random.uniform(20, 60), 1)  # %
        
        problem_text = self._create_problem_text()
        super().__init__(problem_text, language, detail_level, output_format)

    def _create_problem_text(self):
        t = PROMPT_TEMPLATES["thermodynamic_cycles"]
        text = t["instructions"][self.language] + "\n\n"
        
        if self.task_type == "carnot_efficiency":
            text += t["problem"]["carnot_efficiency"][self.language].format(T1=self.T1, T2=self.T2)
        elif self.task_type == "work_from_heat":
            text += t["problem"]["work_from_heat"][self.language].format(eta=self.eta, Q1=self.Q1)
        else:
            text += t["problem"]["refrigerator_cop"][self.language].format(T1=self.T1, T2=self.T2)
        return text

    def solve(self):
        t = PROMPT_TEMPLATES["thermodynamic_cycles"]
        steps = []
        
        if self.task_type == "carnot_efficiency":
            eta = 1 - self.T2/self.T1
            steps.append(t["steps"]["carnot_formula"][self.language])
            steps.append(f"η = 1 - {self.T2}/{self.T1} = {round(eta*100, 2)}%")
            answer = f"η = {round(eta*100, 2)}%"
        elif self.task_type == "work_from_heat":
            A = self.Q1 * self.eta / 100
            Q2 = self.Q1 - A
            steps.append(t["steps"]["work_heat"][self.language])
            steps.append(f"A = {self.eta}%·{self.Q1} = {round(A, 1)} Дж")
            steps.append(f"Q₂ = {self.Q1} - {round(A, 1)} = {round(Q2, 1)} Дж")
            answer = f"A = {round(A, 1)} Дж, Q₂ = {round(Q2, 1)} Дж"
        else:
            COP = self.T2 / (self.T1 - self.T2)
            steps.append(t["steps"]["cop_formula"][self.language])
            steps.append(f"COP = {self.T2}/({self.T1} - {self.T2}) = {round(COP, 2)}")
            answer = f"COP = {round(COP, 2)}"
        
        while len(steps) < self.detail_level:
            steps.append(steps[-1])
        self.solution_steps = steps[:self.detail_level]
        self.final_answer = t["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "thermodynamic_cycles"
    
    @classmethod
    def generate_random_task(cls, **kwargs):
        return cls(**kwargs)
