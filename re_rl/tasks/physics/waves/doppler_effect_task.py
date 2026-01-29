# re_rl/tasks/physics/waves/doppler_effect_task.py

import random
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class DopplerEffectTask(BaseMathTask):
    """Задачи на эффект Доплера."""
    
    TASK_TYPES = ["approaching", "receding", "light_redshift"]

    def __init__(self, language="ru", detail_level=3, task_type=None, difficulty=None, output_format="text"):
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        self.f0 = round(random.uniform(200, 2000), 0)  # Гц
        self.vs = round(random.uniform(10, 100), 1)  # м/с
        self.c_sound = 343  # м/с
        self.c_light = 3e8  # м/с
        self.v_galaxy = round(random.uniform(100, 10000), 0)  # км/с
        self.lambda0 = round(random.uniform(400, 700), 0)  # нм
        
        problem_text = self._create_problem_text()
        super().__init__(problem_text, language, detail_level, output_format)

    def _create_problem_text(self):
        t = PROMPT_TEMPLATES["doppler_effect"]
        text = t["instructions"][self.language] + "\n\n"
        
        if self.task_type == "approaching":
            text += t["problem"]["approaching"][self.language].format(
                f0=self.f0, vs=self.vs, c=self.c_sound)
        elif self.task_type == "receding":
            text += t["problem"]["receding"][self.language].format(
                f0=self.f0, vs=self.vs)
        else:
            text += t["problem"]["light_redshift"][self.language].format(
                v=self.v_galaxy, lambda0=self.lambda0)
        return text

    def solve(self):
        t = PROMPT_TEMPLATES["doppler_effect"]
        steps = []
        
        if self.task_type == "approaching":
            steps.append(t["steps"]["approaching"][self.language])
            f = self.f0 * self.c_sound / (self.c_sound - self.vs)
            steps.append(f"f = {self.f0}·{self.c_sound}/({self.c_sound} - {self.vs}) = {round(f, 1)} Гц")
            answer = f"f = {round(f, 1)} Гц"
        elif self.task_type == "receding":
            steps.append(t["steps"]["sound_formula"][self.language])
            f = self.f0 * self.c_sound / (self.c_sound + self.vs)
            steps.append(f"f = {self.f0}·{self.c_sound}/({self.c_sound} + {self.vs}) = {round(f, 1)} Гц")
            answer = f"f = {round(f, 1)} Гц"
        else:
            steps.append(t["steps"]["light_formula"][self.language])
            v_ms = self.v_galaxy * 1000  # км/с -> м/с
            delta_lambda = self.lambda0 * v_ms / self.c_light
            lambda_obs = self.lambda0 + delta_lambda
            steps.append(f"Δλ = {self.lambda0}·{self.v_galaxy}·10³/{self.c_light:.0e} = {round(delta_lambda, 4)} нм")
            steps.append(f"λ = {self.lambda0} + {round(delta_lambda, 4)} = {round(lambda_obs, 4)} нм")
            answer = f"Δλ = {round(delta_lambda, 4)} нм, λ = {round(lambda_obs, 4)} нм"
        
        while len(steps) < self.detail_level:
            steps.append(steps[-1])
        self.solution_steps = steps[:self.detail_level]
        self.final_answer = t["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "doppler_effect"
    
    @classmethod
    def generate_random_task(cls, **kwargs):
        return cls(**kwargs)
