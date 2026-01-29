# re_rl/tasks/physics/electricity/electromagnetic_induction_task.py

import random
import math
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class ElectromagneticInductionTask(BaseMathTask):
    """
    Задачи на электромагнитную индукцию.
    
    Типы задач:
    - emf_flux_change: ЭДС при изменении потока
    - emf_moving_rod: ЭДС движущегося проводника
    - emf_rotating_coil: ЭДС вращающейся катушки
    """
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"B_range": (0.01, 0.1), "simple": True},
        3: {"B_range": (0.05, 0.5), "simple": True},
        5: {"B_range": (0.1, 1.0), "simple": False},
        7: {"B_range": (0.5, 2.0), "simple": False},
        10: {"B_range": (1.0, 5.0), "simple": False},
    }
    
    TASK_TYPES = ["emf_flux_change", "emf_moving_rod", "emf_rotating_coil"]

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        task_type: str = None,
        difficulty: int = None,
        output_format: OutputFormat = "text"
    ):
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            B_range = preset.get("B_range", (0.1, 1.0))
        else:
            B_range = (0.1, 1.0)
        
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        # Генерируем параметры
        self.B = round(random.uniform(*B_range), 3)
        self.L = round(random.uniform(0.1, 2.0), 2)  # длина проводника
        self.v = round(random.uniform(1, 20), 1)  # скорость
        self.N = random.randint(10, 500)  # число витков
        self.A = round(random.uniform(0.01, 0.5), 3)  # площадь
        self.f = round(random.uniform(10, 100), 1)  # частота
        self.t = round(random.uniform(0.1, 2), 2)  # время
        
        # Формируем текст задачи
        problem_text = self._create_problem_text()
        
        super().__init__(problem_text, language=self.language, detail_level=detail_level, output_format=output_format)

    def _create_problem_text(self) -> str:
        templates = PROMPT_TEMPLATES["electromagnetic_induction"]
        
        problem_text = templates["instructions"][self.language] + "\n\n"
        
        if self.task_type == "emf_flux_change":
            # Φ(t) = B·A·sin(ωt)
            self.flux_formula = f"{self.B}·{self.A}·sin({round(2*math.pi*self.f, 2)}·t)"
            problem_text += templates["problem"]["emf_flux_change"][self.language].format(
                flux_formula=self.flux_formula,
                t=self.t
            )
        elif self.task_type == "emf_moving_rod":
            problem_text += templates["problem"]["emf_moving_rod"][self.language].format(
                L=self.L,
                v=self.v,
                B=self.B
            )
        else:  # emf_rotating_coil
            problem_text += templates["problem"]["emf_rotating_coil"][self.language].format(
                N=self.N,
                A=self.A,
                B=self.B,
                f=self.f
            )
        
        return problem_text

    def solve(self):
        templates = PROMPT_TEMPLATES["electromagnetic_induction"]
        steps = []
        
        if self.task_type == "emf_flux_change":
            steps.append(templates["steps"]["faraday_law"][self.language])
            # ε = -dΦ/dt = -B·A·ω·cos(ωt)
            omega = 2 * math.pi * self.f
            emf = self.B * self.A * omega * math.cos(omega * self.t)
            steps.append(f"ε = B·A·ω·cos(ωt) = {self.B}·{self.A}·{round(omega, 2)}·cos({round(omega * self.t, 2)})")
            steps.append(f"ε = {round(abs(emf), 4)} В")
            self.emf = abs(emf)
        elif self.task_type == "emf_moving_rod":
            steps.append(templates["steps"]["motional_emf"][self.language])
            emf = self.B * self.L * self.v
            steps.append(f"ε = {self.B}·{self.L}·{self.v} = {round(emf, 4)} В")
            self.emf = emf
        else:  # emf_rotating_coil
            steps.append(templates["steps"]["rotating_coil"][self.language])
            omega = 2 * math.pi * self.f
            emf_max = self.N * self.B * self.A * omega
            steps.append(f"ε_max = {self.N}·{self.B}·{self.A}·{round(omega, 2)} = {round(emf_max, 2)} В")
            self.emf = emf_max
        
        while len(steps) < self.detail_level:
            steps.append(steps[-1])
        
        self.solution_steps = steps[:self.detail_level]
        self.final_answer = templates["final_answer"][self.language].format(
            emf=round(self.emf, 4)
        )

    def get_task_type(self):
        return "electromagnetic_induction"
    
    @classmethod
    def generate_random_task(cls, **kwargs):
        return cls(**kwargs)
