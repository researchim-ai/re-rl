# re_rl/tasks/physics/measurements/dimensional_analysis_task.py

import random
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class DimensionalAnalysisTask(BaseMathTask):
    """Задачи на анализ размерностей."""
    
    TASK_TYPES = ["check_formula", "derive_formula", "find_units"]
    
    # Формулы для проверки (некоторые правильные, некоторые нет)
    FORMULAS = {
        "kinetic_energy": {"formula": "E = mv²/2", "correct": True, "dims": "[M][L]²[T]⁻²"},
        "period_pendulum": {"formula": "T = 2π√(l/g)", "correct": True, "dims": "[T]"},
        "force_wrong": {"formula": "F = mv", "correct": False, "dims_left": "[M][L][T]⁻²", "dims_right": "[M][L][T]⁻¹"},
        "pressure": {"formula": "P = F/S", "correct": True, "dims": "[M][L]⁻¹[T]⁻²"},
        "velocity_wrong": {"formula": "v = at²", "correct": False, "dims_left": "[L][T]⁻¹", "dims_right": "[L][T]⁻¹"},
        "work": {"formula": "A = Fs", "correct": True, "dims": "[M][L]²[T]⁻²"},
    }

    def __init__(self, language="ru", detail_level=3, task_type=None, difficulty=None, output_format="text"):
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        self.formula_key = random.choice(list(self.FORMULAS.keys()))
        self.formula_data = self.FORMULAS[self.formula_key]
        
        problem_text = self._create_problem_text()
        super().__init__(problem_text, language, detail_level, output_format)

    def _create_problem_text(self):
        t = PROMPT_TEMPLATES["dimensional_analysis"]
        text = t["instructions"][self.language] + "\n\n"
        
        if self.task_type == "check_formula":
            text += t["problem"]["check_formula"][self.language].format(formula=self.formula_data["formula"])
        elif self.task_type == "derive_formula":
            text += t["problem"]["derive_formula"][self.language]
        else:
            text += t["problem"]["find_units"][self.language].format(formula=self.formula_data["formula"])
        return text

    def solve(self):
        t = PROMPT_TEMPLATES["dimensional_analysis"]
        steps = []
        
        if self.task_type == "check_formula":
            steps.append(t["steps"]["write_dimensions"][self.language].format(dimensions=self.formula_data["formula"]))
            if self.formula_data["correct"]:
                steps.append(f"Левая часть: {self.formula_data['dims']}")
                steps.append(f"Правая часть: {self.formula_data['dims']}")
                result = "Формула размерностно верна" if self.language == "ru" else "Formula is dimensionally correct"
            else:
                steps.append(f"Левая часть: {self.formula_data.get('dims_left', '[?]')}")
                steps.append(f"Правая часть: {self.formula_data.get('dims_right', '[?]')}")
                result = "Формула размерностно неверна" if self.language == "ru" else "Formula is dimensionally incorrect"
            steps.append(t["steps"]["conclusion"][self.language].format(result=result))
            answer = result
        elif self.task_type == "derive_formula":
            steps.append("[T] = [L]^α·[L][T]^(-2)]^β")
            steps.append("[T] = [L]^(α+β)·[T]^(-2β)")
            steps.append("α + β = 0, -2β = 1 → β = -1/2, α = 1/2")
            steps.append("T ∝ √(l/g)")
            answer = "T = C·√(l/g), где C = 2π"
        else:
            steps.append(t["steps"]["write_dimensions"][self.language].format(dimensions=self.formula_data["formula"]))
            steps.append(f"Размерность: {self.formula_data['dims']}")
            answer = f"[{self.formula_data['dims']}]"
        
        # Ограничиваем количество шагов (без дублирования)
        self.solution_steps = steps[:self.detail_level]
        self.final_answer = t["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "dimensional_analysis"
    
    @classmethod
    def generate_random_task(cls, **kwargs):
        return cls(**kwargs)
