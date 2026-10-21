from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

# re_rl/tasks/physics/waves/doppler_effect_task.py

import random
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class DopplerEffectTask(BaseMathTask):
    """Задачи на эффект Доплера."""
    
    TASK_TYPES = ["approaching", "receding", "light_redshift"]

    def __init__(self, language="ru", detail_level=3, task_type=None, difficulty=None, output_format="text", reasoning_mode=False):
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        self.f0 = round(random.uniform(200, 2000), 0)  # Гц
        self.vs = round(random.uniform(10, 100), 1)  # м/с
        self.c_sound = 343  # м/с
        self.c_light = 3e8  # м/с
        self.v_galaxy = round(random.uniform(100, 10000), 0)  # км/с
        self.lambda0 = round(random.uniform(400, 700), 0)  # нм
        
        problem_text = self._create_problem_text()
        super().__init__(problem_text, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

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
            steps.append(texts.t('s1', self.language, f0=self.f0, c_sound=self.c_sound, c_sound_2=self.c_sound, vs=self.vs, v4=round(f, 1)))
            answer = texts.t('s0', self.language, v0=round(f, 1))
        elif self.task_type == "receding":
            steps.append(t["steps"]["sound_formula"][self.language])
            f = self.f0 * self.c_sound / (self.c_sound + self.vs)
            steps.append(texts.t('s4', self.language, f0=self.f0, c_sound=self.c_sound, c_sound_2=self.c_sound, vs=self.vs, v4=round(f, 1)))
            answer = texts.t('s2', self.language, v0=round(f, 1))
        else:
            steps.append(t["steps"]["light_formula"][self.language])
            v_ms = self.v_galaxy * 1000  # км/с -> м/с
            delta_lambda = self.lambda0 * v_ms / self.c_light
            lambda_obs = self.lambda0 + delta_lambda
            steps.append(texts.t('s5', self.language, lambda0=self.lambda0, v_galaxy=self.v_galaxy, c_light=self.c_light, v3=round(delta_lambda, 4)))
            steps.append(texts.t('s6', self.language, lambda0=self.lambda0, v1=round(delta_lambda, 4), v2=round(lambda_obs, 4)))
            answer = texts.t('s3', self.language, v0=round(delta_lambda, 4), v1=round(lambda_obs, 4))
        
        self.solution_steps = steps
        self.final_answer = t["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "doppler_effect"
    
    @classmethod
    def generate_random_task(cls, reasoning_mode=False, **kwargs):
        return cls(reasoning_mode=reasoning_mode, **kwargs)
