# re_rl/tasks/physics/thermodynamics/phase_transitions_task.py

import random
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class PhaseTransitionsTask(BaseMathTask):
    """Задачи на фазовые переходы."""
    
    SUBSTANCES = {
        "ice": {"lambda": 334, "L": 2260, "c_solid": 2100, "c_liquid": 4186, 
                "T_melt": 0, "T_boil": 100, "name_ru": "льда", "name_en": "ice"},
        "iron": {"lambda": 247, "L": 6090, "c_solid": 450, "c_liquid": 820,
                "T_melt": 1538, "T_boil": 2862, "name_ru": "железа", "name_en": "iron"},
    }
    
    TASK_TYPES = ["melting", "vaporization", "heating_with_phase"]

    def __init__(self, language="ru", detail_level=3, task_type=None, difficulty=None, output_format="text"):
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        self.substance = "ice"  # для простоты используем лёд
        self.m = round(random.uniform(0.1, 5), 2)
        self.T1 = round(random.uniform(-30, -5), 0)
        self.T2 = round(random.uniform(20, 80), 0)
        
        problem_text = self._create_problem_text()
        super().__init__(problem_text, language, detail_level, output_format)

    def _create_problem_text(self):
        t = PROMPT_TEMPLATES["phase_transitions"]
        s = self.SUBSTANCES[self.substance]
        text = t["instructions"][self.language] + "\n\n"
        
        name = s["name_ru"] if self.language == "ru" else s["name_en"]
        
        if self.task_type == "melting":
            text += t["problem"]["melting"][self.language].format(
                m=self.m, substance=name, **{k: v for k, v in s.items() if k != "name_ru" and k != "name_en"}
            )
        elif self.task_type == "vaporization":
            text += t["problem"]["vaporization"][self.language].format(
                m=self.m, substance=name, L=s["L"]
            )
        else:
            text += t["problem"]["heating_with_phase"][self.language].format(
                m=self.m, T1=self.T1, T2=self.T2,
                c_ice=s["c_solid"], c_water=s["c_liquid"], **{k: v for k, v in s.items() if k.startswith("lambda") or k == "lambda"}
            )
        return text

    def solve(self):
        t = PROMPT_TEMPLATES["phase_transitions"]
        s = self.SUBSTANCES[self.substance]
        steps = []
        
        if self.task_type == "melting":
            steps.append(t["steps"]["melting_heat"][self.language])
            Q = s["lambda"] * self.m * 1000  # кДж/кг -> Дж/кг, m в кг
            steps.append(f"Q = {s['lambda']}·{self.m}·1000 = {round(Q/1000, 2)} кДж")
            answer = f"{round(Q/1000, 2)} кДж"
        elif self.task_type == "vaporization":
            steps.append(t["steps"]["vaporization_heat"][self.language])
            Q = s["L"] * self.m * 1000
            steps.append(f"Q = {s['L']}·{self.m}·1000 = {round(Q/1000, 2)} кДж")
            answer = f"{round(Q/1000, 2)} кДж"
        else:
            steps.append(t["steps"]["total_heat"][self.language])
            Q1 = self.m * s["c_solid"] * (0 - self.T1)  # нагрев льда до 0°C
            Q2 = self.m * s["lambda"] * 1000  # плавление
            Q3 = self.m * s["c_liquid"] * self.T2  # нагрев воды
            Q = Q1 + Q2 + Q3
            steps.append(f"Q₁ = {self.m}·{s['c_solid']}·{-self.T1} = {round(Q1/1000, 2)} кДж")
            steps.append(f"Q₂ = {self.m}·{s['lambda']} = {round(Q2/1000, 2)} кДж")
            steps.append(f"Q₃ = {self.m}·{s['c_liquid']}·{self.T2} = {round(Q3/1000, 2)} кДж")
            steps.append(f"Q = {round(Q/1000, 2)} кДж")
            answer = f"{round(Q/1000, 2)} кДж"
        
        # Ограничиваем количество шагов (без дублирования)
        self.solution_steps = steps[:self.detail_level]
        self.final_answer = t["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "phase_transitions"
    
    @classmethod
    def generate_random_task(cls, **kwargs):
        return cls(**kwargs)
