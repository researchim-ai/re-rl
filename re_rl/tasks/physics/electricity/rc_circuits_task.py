# re_rl/tasks/physics/electricity/rc_circuits_task.py

import random
import math
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class RCCircuitsTask(BaseMathTask):
    """
    Задачи на RC-цепи (заряд/разряд конденсатора).
    
    Типы задач:
    - charging: зарядка конденсатора
    - discharging: разрядка конденсатора
    - time_constant: постоянная времени
    """
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"R_range": (1, 10), "C_range": (10, 100)},  # кОм, мкФ
        3: {"R_range": (5, 50), "C_range": (1, 50)},
        5: {"R_range": (10, 100), "C_range": (0.5, 20)},
        7: {"R_range": (50, 500), "C_range": (0.1, 10)},
        10: {"R_range": (100, 1000), "C_range": (0.01, 5)},
    }
    
    TASK_TYPES = ["charging", "discharging", "time_constant"]

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        task_type: str = None,
        R: float = None,  # кОм
        C: float = None,  # мкФ
        E: float = None,  # В
        t: float = None,  # с
        Q0: float = None,  # мкКл
        difficulty: int = None,
        output_format: OutputFormat = "text"
    ):
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            R_range = preset.get("R_range", (10, 100))
            C_range = preset.get("C_range", (1, 50))
        else:
            R_range = (10, 100)
            C_range = (1, 50)
        
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        # Генерируем параметры
        self.R = R or round(random.uniform(*R_range), 1)  # кОм
        self.C = C or round(random.uniform(*C_range), 2)  # мкФ
        self.E = E or round(random.uniform(5, 50), 1)  # В
        
        # Постоянная времени τ = RC
        self.tau = self.R * 1000 * self.C * 1e-6  # в секундах
        
        self.t = t or round(random.uniform(0.5, 3) * self.tau, 4)
        self.Q0 = Q0 or round(self.C * self.E, 2)  # мкКл (если C в мкФ, E в В)
        
        # Формируем текст задачи
        problem_text = self._create_problem_text()
        
        super().__init__(problem_text, language=self.language, detail_level=detail_level, output_format=output_format)

    def _create_problem_text(self) -> str:
        templates = PROMPT_TEMPLATES["rc_circuits"]
        
        problem_text = templates["instructions"][self.language] + "\n\n"
        
        if self.task_type == "charging":
            problem_text += templates["problem"]["charging"][self.language].format(
                R=self.R,
                C=self.C,
                E=self.E,
                t=self.t
            )
        elif self.task_type == "discharging":
            problem_text += templates["problem"]["discharging"][self.language].format(
                C=self.C,
                Q0=self.Q0,
                R=self.R,
                t=self.t
            )
        else:  # time_constant
            problem_text += templates["problem"]["time_constant"][self.language].format(
                R=self.R,
                C=self.C
            )
        
        return problem_text

    def solve(self):
        templates = PROMPT_TEMPLATES["rc_circuits"]
        steps = []
        
        # Постоянная времени
        steps.append(templates["steps"]["time_constant"][self.language].format(
            tau=round(self.tau, 6)
        ))
        
        if self.task_type == "charging":
            steps.append(templates["steps"]["charging_formula"][self.language])
            # Q(t) = CE(1 - e^(-t/τ))
            Q_max = self.C * self.E  # мкКл
            Q = Q_max * (1 - math.exp(-self.t / self.tau))
            steps.append(f"Q = {round(Q_max, 2)}·(1 - e^(-{self.t}/{round(self.tau, 6)})) = {round(Q, 4)} мкКл")
            answer = f"Q = {round(Q, 4)} мкКл"
            
        elif self.task_type == "discharging":
            steps.append(templates["steps"]["discharging_formula"][self.language])
            # Q(t) = Q0·e^(-t/τ)
            Q = self.Q0 * math.exp(-self.t / self.tau)
            steps.append(f"Q = {self.Q0}·e^(-{self.t}/{round(self.tau, 6)}) = {round(Q, 4)} мкКл")
            answer = f"Q = {round(Q, 4)} мкКл"
            
        else:  # time_constant
            steps.append(f"τ = R·C = {self.R}·10³ · {self.C}·10⁻⁶ = {round(self.tau, 6)} с")
            answer = f"τ = {round(self.tau, 6)} с = {round(self.tau * 1000, 3)} мс"
        
        while len(steps) < self.detail_level:
            steps.append(steps[-1])
        
        self.solution_steps = steps[:self.detail_level]
        self.final_answer = templates["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "rc_circuits"
    
    @classmethod
    def generate_random_task(cls, **kwargs):
        return cls(**kwargs)
