# re_rl/tasks/physics/mechanics/momentum_task.py

"""
MomentumTask — задачи на импульс и столкновения.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Dict, Any, ClassVar
from re_rl.tasks.base_task import BaseMathTask, OutputFormat, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template
from re_rl.tasks.physics.units import format_with_units


class MomentumTask(BaseMathTask):
    """Генератор задач на импульс."""
    
    TASK_TYPES = ["momentum", "impulse", "inelastic_collision", "elastic_collision"]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_m": 10, "max_v": 10, "max_F": 50, "max_t": 5},
        2: {"max_m": 20, "max_v": 20, "max_F": 100, "max_t": 10},
        3: {"max_m": 30, "max_v": 30, "max_F": 200, "max_t": 10},
        4: {"max_m": 50, "max_v": 50, "max_F": 300, "max_t": 15},
        5: {"max_m": 50, "max_v": 50, "max_F": 500, "max_t": 15},
        6: {"max_m": 100, "max_v": 100, "max_F": 500, "max_t": 20},
        7: {"max_m": 100, "max_v": 100, "max_F": 1000, "max_t": 20},
        8: {"max_m": 200, "max_v": 150, "max_F": 1000, "max_t": 30},
        9: {"max_m": 200, "max_v": 200, "max_F": 2000, "max_t": 30},
        10: {"max_m": 500, "max_v": 300, "max_F": 5000, "max_t": 60},
    }
    
    def __init__(
        self,
        task_type: str = "momentum",
        m: float = None,
        m1: float = None,
        m2: float = None,
        v: float = None,
        v1: float = None,
        F: float = None,
        t: float = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        **kwargs
    ):
        self.task_type = task_type.lower()
        self.difficulty = difficulty
        self._output_format = output_format
        self.language = language
        self._reasoning_mode = reasoning_mode
        
        preset = self._interpolate_difficulty(difficulty)
        
        self.m = m if m is not None else random.randint(1, preset["max_m"])
        self.m1 = m1 if m1 is not None else random.randint(1, preset["max_m"])
        self.m2 = m2 if m2 is not None else random.randint(1, preset["max_m"])
        self.v = v if v is not None else random.randint(5, preset["max_v"])
        self.v1 = v1 if v1 is not None else random.randint(5, preset["max_v"])
        self.F = F if F is not None else random.randint(10, preset["max_F"])
        self.t = t if t is not None else random.randint(1, preset["max_t"])
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode
    
    def _create_problem_description(self) -> str:
        templates = PROMPT_TEMPLATES.get("momentum", {}).get("problem", {})
        
        if self.task_type == "momentum":
            template = templates.get("momentum", {}).get(self.language, "")
            return template.format(m=self.m, v=self.v)
        elif self.task_type == "impulse":
            template = templates.get("impulse", {}).get(self.language, "")
            return template.format(F=self.F, t=self.t)
        elif self.task_type == "inelastic_collision":
            template = templates.get("inelastic_collision", {}).get(self.language, "")
            return template.format(m1=self.m1, v1=self.v1, m2=self.m2)
        elif self.task_type == "elastic_collision":
            template = templates.get("elastic_collision", {}).get(self.language, "")
            return template.format(m1=self.m1, v1=self.v1, m2=self.m2)
        return ""
    
    def solve(self):
        self.solution_steps = []
        
        if self.task_type == "momentum":
            p = self.m * self.v
            if self.reasoning_mode:
                self.add_given({"m": self.m, "v": self.v}, {"m": texts.t('s5', self.language), "v": texts.t('s6', self.language)})
                self.add_find("p", get_template(PROMPT_TEMPLATES["inline"], texts.t('s7', self.language), self.language, augment=False))
            self.add_formula("p = mv")
            self.add_substitution(f"p = {self.m} × {self.v}")
            self.add_calculation(f"{self.m} × {self.v}", p, texts.t('s1', self.language))
            if self.reasoning_mode:
                self.add_dimension_check(texts.literal('literals.s3'))
            self.final_answer = texts.t('s0', self.language, p=p)
        
        elif self.task_type == "impulse":
            J = self.F * self.t
            if self.reasoning_mode:
                self.add_given({"F": self.F, "t": self.t}, {"F": texts.t('s11', self.language), "t": texts.t('s12', self.language)})
                self.add_find("J", get_template(PROMPT_TEMPLATES["inline"], texts.t('s13', self.language), self.language, augment=False))
            self.add_formula("J = F·t")
            self.add_substitution(f"J = {self.F} × {self.t}")
            self.add_calculation(f"{self.F} × {self.t}", J, texts.t('s4', self.language))
            if self.reasoning_mode:
                self.add_dimension_check(texts.literal('literals.s8'))
            self.final_answer = texts.t('s2', self.language, J=J)
        
        elif self.task_type == "inelastic_collision":
            v_final = self.m1 * self.v1 / (self.m1 + self.m2)
            if self.reasoning_mode:
                self.add_given({"m₁": self.m1, "v₁": self.v1, "m₂": self.m2, "v₂": 0}, 
                              {"m₁": texts.t('s16', self.language), "v₁": texts.t('s17', self.language), "m₂": texts.t('s18', self.language), "v₂": texts.t('s19', self.language)})
                self.add_find("v'", get_template(PROMPT_TEMPLATES["inline"], texts.t('s20', self.language), self.language, augment=False))
                self.add_analysis(get_template(PROMPT_TEMPLATES["inline"], texts.t('s21', self.language), self.language, augment=False))
            self.add_formula("m₁v₁ + m₂v₂ = (m₁+m₂)v' → v' = m₁v₁/(m₁+m₂)")
            self.add_substitution(f"v' = {self.m1} × {self.v1} / ({self.m1} + {self.m2})")
            self.add_calculation(f"{self.m1 * self.v1}/{self.m1 + self.m2}", round(v_final, 4), texts.t('s9', self.language))
            self.final_answer = format_with_units(v_final, "m/s", self.language)
        
        elif self.task_type == "elastic_collision":
            v1_final = (self.m1 - self.m2) / (self.m1 + self.m2) * self.v1
            v2_final = 2 * self.m1 / (self.m1 + self.m2) * self.v1
            if self.reasoning_mode:
                self.add_given({"m₁": self.m1, "v₁": self.v1, "m₂": self.m2, "v₂": 0},
                              {"m₁": texts.t('s22', self.language), "v₁": texts.t('s23', self.language), "m₂": texts.t('s24', self.language), "v₂": texts.t('s25', self.language)})
                self.add_find("v₁', v₂'", get_template(PROMPT_TEMPLATES["inline"], texts.t('s26', self.language), self.language, augment=False))
                self.add_analysis(get_template(PROMPT_TEMPLATES["inline"], texts.t('s27', self.language), self.language, augment=False))
            self.add_formula("v₁' = (m₁-m₂)/(m₁+m₂)·v₁")
            self.add_substitution(f"v₁' = ({self.m1}-{self.m2})/({self.m1}+{self.m2}) × {self.v1}")
            self.add_calculation(f"({self.m1-self.m2}/{self.m1+self.m2}) × {self.v1}", round(v1_final, 4), texts.t('s14', self.language))
            self.add_formula("v₂' = 2m₁/(m₁+m₂)·v₁")
            self.add_substitution(f"v₂' = 2×{self.m1}/({self.m1}+{self.m2}) × {self.v1}")
            self.add_calculation(f"(2×{self.m1}/{self.m1+self.m2}) × {self.v1}", round(v2_final, 4), texts.t('s15', self.language))
            self.final_answer = texts.t('s10', self.language, v0=round(v1_final, 4), v1=round(v2_final, 4))
    
    def get_task_type(self) -> str:
        return "momentum"
    
    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                            detail_level: int = 3, difficulty: int = 5, reasoning_mode: bool = False):
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(task_type=task_type, language=language,
                  detail_level=detail_level, difficulty=difficulty, reasoning_mode=reasoning_mode)
