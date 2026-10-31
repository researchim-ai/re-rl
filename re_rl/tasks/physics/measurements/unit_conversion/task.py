from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

# re_rl/tasks/physics/measurements/unit_conversion_task.py

import random
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class UnitConversionTask(BaseMathTask):
    """Задачи на перевод единиц измерения."""
    
    TASK_TYPES = ["simple", "compound", "derived"]
    
    # Коэффициенты перевода
    CONVERSIONS = {
        # length
        (texts.literal('literals.s0'), texts.literal('literals.s1')): 1000,
        (texts.literal('literals.s2'), texts.literal('literals.s3')): 100,
        (texts.literal('literals.s4'), texts.literal('literals.s5')): 1000,
        (texts.literal('literals.s6'), texts.literal('literals.s7')): 1.609,
        (texts.literal('literals.s8'), texts.literal('literals.s9')): 0.3048,
        (texts.literal('literals.s10'), texts.literal('literals.s11')): 2.54,
        # mass
        (texts.literal('literals.s12'), texts.literal('literals.s13')): 1000,
        (texts.literal('literals.s14'), texts.literal('literals.s15')): 1000,
        (texts.literal('literals.s16'), texts.literal('literals.s17')): 0.4536,
        # time
        (texts.literal('literals.s18'), texts.literal('literals.s19')): 60,
        (texts.literal('literals.s20'), texts.literal('literals.s21')): 60,
        (texts.literal('literals.s22'), texts.literal('literals.s23')): 24,
        # speed
        (texts.literal('literals.s24'), texts.literal('literals.s25')): 1/3.6,
        (texts.literal('literals.s26'), texts.literal('literals.s27')): 3.6,
        # energy
        (texts.literal('literals.s28'), texts.literal('literals.s29')): 1000,
        (texts.literal('literals.s30'), texts.literal('literals.s31')): 1.602e-19,
        (texts.literal('literals.s32'), texts.literal('literals.s33')): 4.186,
        # pressure
        (texts.literal('literals.s34'), texts.literal('literals.s35')): 101325,
        (texts.literal('literals.s36'), texts.literal('literals.s37')): 100000,
        (texts.literal('literals.s38'), texts.literal('literals.s39')): 133.322,
        # temperature
        ("°C", "K"): ("add", 273.15),  # особый случай
    }
    def _show(self, unit: str) -> str:
        shown = texts.raw("unit_en").get(unit, unit)
        return {"ru": unit, "en": shown}.get(self.language, shown)

    def __init__(self, language="ru", detail_level=3, task_type=None, difficulty=None, output_format="text", reasoning_mode=False):
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        # Выбираем случайную конверсию
        self.conversion = random.choice(list(self.CONVERSIONS.keys()))
        self.factor = self.CONVERSIONS[self.conversion]
        
        # Генерируем значение
        self.value = round(random.uniform(1, 1000), 2)
        
        problem_text = self._create_problem_text()
        super().__init__(problem_text, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_text(self):
        t = PROMPT_TEMPLATES["unit_conversion"]
        text = t["instructions"][self.language] + "\n\n"
        
        from_unit, to_unit = self._show(self.conversion[0]), self._show(self.conversion[1])
        
        if self.task_type == "simple":
            text += t["problem"]["simple"][self.language].format(
                value=self.value, from_unit=from_unit, to_unit=to_unit)
        elif self.task_type == "compound":
            text += t["problem"]["compound"][self.language].format(
                value=self.value, from_unit=from_unit)
        else:
            text += t["problem"]["derived"][self.language].format(
                value=self.value, from_unit=from_unit)
        return text

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        t = PROMPT_TEMPLATES["unit_conversion"]
        steps = []
        
        from_unit, to_unit = self._show(self.conversion[0]), self._show(self.conversion[1])
        
        if isinstance(self.factor, tuple):
            # Температура
            if self.factor[0] == "add":
                result = self.value + self.factor[1]
                steps.append(f"K = °C + 273.15")
                steps.append(f"{self.value} + 273.15 = {round(result, 2)}")
        else:
            steps.append(t["steps"]["conversion_factor"][self.language].format(
                from_unit=from_unit, factor=self.factor, to_unit=to_unit))
            result = self.value * self.factor
            steps.append(t["steps"]["calculate"][self.language].format(
                value=self.value, factor=self.factor, result=f"{result:.6g}"))
        
        self.solution_steps = steps
        
        if isinstance(self.factor, tuple):
            answer = f"{self.value} {from_unit} = {round(result, 2)} {to_unit}"
        else:
            answer = f"{self.value} {from_unit} = {result:.6g} {to_unit}"
        self.final_answer = t["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "unit_conversion"
    
    @classmethod
    def generate_random_task(cls, reasoning_mode: bool = False, **kwargs):
        return cls(reasoning_mode=reasoning_mode, **kwargs)
