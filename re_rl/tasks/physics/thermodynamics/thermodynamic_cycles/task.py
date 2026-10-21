from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

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
    
    TASK_TYPES = ["carnot_efficiency", texts.literal('literals.s0'), "refrigerator_cop"]

    def __init__(self, language="ru", detail_level=3, task_type=None, difficulty=None, output_format="text", reasoning_mode=False):
        if difficulty:
            preset = self._interpolate_difficulty(difficulty)
            T_range = preset.get("T_range", (400, 800))
        else:
            T_range = (400, 800)
        
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        self.T1 = round(random.uniform(*T_range), 0)  # горячий
        self.T2 = round(random.uniform(250, self.T1 - 50), 0)  # холодный
        self.Q1 = round(random.uniform(1000, 10000), 0)  # Дж
        self.eta = round(random.uniform(20, 60), 1)  # %
        
        problem_text = self._create_problem_text()
        super().__init__(problem_text, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_text(self):
        t = PROMPT_TEMPLATES["thermodynamic_cycles"]
        text = t["instructions"][self.language] + "\n\n"
        
        if self.task_type == "carnot_efficiency":
            text += t["problem"]["carnot_efficiency"][self.language].format(T1=self.T1, T2=self.T2)
        elif self.task_type == texts.t('s1', self.language):
            text += t["problem"][texts.t('s6', self.language)][self.language].format(eta=self.eta, Q1=self.Q1)
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
        elif self.task_type == texts.t('s2', self.language):
            A = self.Q1 * self.eta / 100
            Q2 = self.Q1 - A
            steps.append(t["steps"]["work_heat"][self.language])
            steps.append(texts.t('s4', self.language, eta=self.eta, Q1=self.Q1, v2=round(A, 1)))
            steps.append(texts.t('s5', self.language, Q1=self.Q1, v1=round(A, 1), v2=round(Q2, 1)))
            answer = texts.t('s3', self.language, v0=round(A, 1), v1=round(Q2, 1))
        else:
            COP = self.T2 / (self.T1 - self.T2)
            steps.append(t["steps"]["cop_formula"][self.language])
            steps.append(f"COP = {self.T2}/({self.T1} - {self.T2}) = {round(COP, 2)}")
            answer = f"COP = {round(COP, 2)}"
        
        # НЕ обрезаем шаги — в reasoning_mode нужны все шаги
        self.solution_steps = steps
        self.final_answer = t["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "thermodynamic_cycles"
    
    @classmethod
    def generate_random_task(cls, reasoning_mode=False, **kwargs):
        return cls(reasoning_mode=reasoning_mode, **kwargs)
