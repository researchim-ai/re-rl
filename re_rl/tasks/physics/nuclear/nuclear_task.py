# re_rl/tasks/physics/nuclear/nuclear_task.py

"""
NuclearTask — задачи по ядерной физике.

Типы задач:
- radioactive_decay: закон радиоактивного распада
- half_life: период полураспада
- binding_energy: энергия связи ядра
- mass_defect: дефект массы
- activity: активность источника
"""

import random
import math
from typing import Dict, Any, ClassVar
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import get_constant


# Данные о ядрах (A, Z, масса в а.е.м.)
NUCLEI_DATA = {
    "H-1": {"A": 1, "Z": 1, "mass": 1.007825},
    "H-2": {"A": 2, "Z": 1, "mass": 2.014102},
    "He-3": {"A": 3, "Z": 2, "mass": 3.016029},
    "He-4": {"A": 4, "Z": 2, "mass": 4.002603},
    "Li-7": {"A": 7, "Z": 3, "mass": 7.016003},
    "C-12": {"A": 12, "Z": 6, "mass": 12.000000},
    "N-14": {"A": 14, "Z": 7, "mass": 14.003074},
    "O-16": {"A": 16, "Z": 8, "mass": 15.994915},
    "Fe-56": {"A": 56, "Z": 26, "mass": 55.934939},
    "U-235": {"A": 235, "Z": 92, "mass": 235.043924},
    "U-238": {"A": 238, "Z": 92, "mass": 238.050786},
}

# Периоды полураспада (в секундах)
HALF_LIVES = {
    "C-14": 5730 * 365.25 * 24 * 3600,  # 5730 лет
    "Co-60": 5.27 * 365.25 * 24 * 3600,  # 5.27 лет
    "I-131": 8.02 * 24 * 3600,  # 8.02 дней
    "Ra-226": 1600 * 365.25 * 24 * 3600,  # 1600 лет
    "Sr-90": 28.8 * 365.25 * 24 * 3600,  # 28.8 лет
    "Cs-137": 30.17 * 365.25 * 24 * 3600,  # 30.17 лет
}


class NuclearTask(BaseMathTask):
    """Генератор задач по ядерной физике."""
    
    TASK_TYPES = [
        "radioactive_decay", "half_life", "binding_energy", 
        "mass_defect", "activity"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_A": 20, "max_t_half": 5},
        2: {"max_A": 40, "max_t_half": 10},
        3: {"max_A": 60, "max_t_half": 20},
        4: {"max_A": 100, "max_t_half": 50},
        5: {"max_A": 150, "max_t_half": 100},
        6: {"max_A": 200, "max_t_half": 200},
        7: {"max_A": 220, "max_t_half": 500},
        8: {"max_A": 238, "max_t_half": 1000},
        9: {"max_A": 250, "max_t_half": 5000},
        10: {"max_A": 260, "max_t_half": 10000},
    }
    
    # Константы
    M_PROTON = 1.007276  # а.е.м.
    M_NEUTRON = 1.008665  # а.е.м.
    AMU_TO_MEV = 931.5  # 1 а.е.м. = 931.5 МэВ
    
    def __init__(
        self,
        task_type: str = "radioactive_decay",
        N0: float = None,
        t: float = None,
        t_half: float = None,
        nucleus: str = None,
        A: int = None,
        Z: int = None,
        activity: float = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        **kwargs
    ):
        self.task_type = task_type.lower()
        self.difficulty = difficulty
        self.language = language
        
        preset = self._interpolate_difficulty(difficulty)
        
        # Параметры для распада
        self.N0 = N0 if N0 is not None else random.randint(1000, 1000000)
        self.t_half = t_half if t_half is not None else random.uniform(1, preset["max_t_half"])
        self.t = t if t is not None else self.t_half * random.uniform(0.5, 5)
        
        # Параметры для ядер
        if nucleus and nucleus in NUCLEI_DATA:
            self.nucleus = nucleus
            data = NUCLEI_DATA[nucleus]
            self.A = data["A"]
            self.Z = data["Z"]
            self.mass = data["mass"]
        else:
            self.nucleus = random.choice(list(NUCLEI_DATA.keys()))
            data = NUCLEI_DATA[self.nucleus]
            self.A = A if A is not None else data["A"]
            self.Z = Z if Z is not None else data["Z"]
            self.mass = data["mass"]
        
        self.activity = activity if activity is not None else random.randint(100, 100000)
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level)
    
    def _create_problem_description(self) -> str:
        templates = PROMPT_TEMPLATES.get("nuclear", {}).get("problem", {})
        
        if self.task_type == "radioactive_decay":
            template = templates.get("radioactive_decay", {}).get(self.language, "")
            return template.format(N0=self.N0, t_half=self.t_half, t=self.t)
        elif self.task_type == "half_life":
            template = templates.get("half_life", {}).get(self.language, "")
            self.N_final = self.N0 / (2 ** random.randint(1, 5))
            return template.format(N0=self.N0, N=int(self.N_final), t=self.t)
        elif self.task_type == "binding_energy":
            template = templates.get("binding_energy", {}).get(self.language, "")
            return template.format(nucleus=self.nucleus, A=self.A, Z=self.Z)
        elif self.task_type == "mass_defect":
            template = templates.get("mass_defect", {}).get(self.language, "")
            return template.format(nucleus=self.nucleus, A=self.A, Z=self.Z, mass=self.mass)
        elif self.task_type == "activity":
            template = templates.get("activity", {}).get(self.language, "")
            return template.format(N0=self.N0, t_half=self.t_half)
        return ""
    
    def solve(self):
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("nuclear", {}).get("steps", {})
        
        if self.task_type == "radioactive_decay":
            self._solve_radioactive_decay(templates)
        elif self.task_type == "half_life":
            self._solve_half_life(templates)
        elif self.task_type == "binding_energy":
            self._solve_binding_energy(templates)
        elif self.task_type == "mass_defect":
            self._solve_mass_defect(templates)
        elif self.task_type == "activity":
            self._solve_activity(templates)
        
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def _solve_radioactive_decay(self, templates):
        """N(t) = N₀ · e^(-λt) = N₀ · (1/2)^(t/T½)"""
        decay_const = math.log(2) / self.t_half
        N_t = self.N0 * math.exp(-decay_const * self.t)
        
        step1 = templates.get("decay_law", {}).get(self.language, "")
        self.solution_steps.append(step1)
        
        self.solution_steps.append(f"λ = ln(2)/T½ = ln(2)/{self.t_half} = {decay_const:.6f}")
        self.solution_steps.append(f"N(t) = {self.N0} × e^(-{decay_const:.6f} × {self.t})")
        self.solution_steps.append(f"N(t) = {N_t:.0f}")
        
        self.final_answer = f"N = {N_t:.0f}"
    
    def _solve_half_life(self, templates):
        """N = N₀ · (1/2)^(t/T½) => T½ = t / log₂(N₀/N)"""
        n_halves = math.log2(self.N0 / self.N_final)
        t_half = self.t / n_halves
        
        step1 = templates.get("half_life_formula", {}).get(self.language, "")
        self.solution_steps.append(step1)
        
        self.solution_steps.append(f"N₀/N = {self.N0}/{int(self.N_final)} = {self.N0/self.N_final:.2f}")
        self.solution_steps.append(f"Число периодов = log₂({self.N0/self.N_final:.2f}) = {n_halves:.2f}")
        self.solution_steps.append(f"T½ = t/n = {self.t}/{n_halves:.2f} = {t_half:.4f}")
        
        self.final_answer = f"T½ = {t_half:.4f}"
    
    def _solve_binding_energy(self, templates):
        """Eсв = Δm × c² = [Z·m_p + (A-Z)·m_n - M] × 931.5 МэВ"""
        N = self.A - self.Z  # Число нейтронов
        theoretical_mass = self.Z * self.M_PROTON + N * self.M_NEUTRON
        mass_defect = theoretical_mass - self.mass
        binding_energy = mass_defect * self.AMU_TO_MEV
        binding_per_nucleon = binding_energy / self.A
        
        step1 = templates.get("binding_formula", {}).get(self.language, "")
        self.solution_steps.append(step1)
        
        self.solution_steps.append(
            f"m_теор = {self.Z}×{self.M_PROTON} + {N}×{self.M_NEUTRON} = {theoretical_mass:.6f} а.е.м."
        )
        self.solution_steps.append(f"Δm = {theoretical_mass:.6f} - {self.mass:.6f} = {mass_defect:.6f} а.е.м.")
        self.solution_steps.append(f"Eсв = {mass_defect:.6f} × 931.5 = {binding_energy:.2f} МэВ")
        self.solution_steps.append(f"Eсв/A = {binding_energy:.2f}/{self.A} = {binding_per_nucleon:.2f} МэВ/нуклон")
        
        self.final_answer = f"Eсв = {binding_energy:.2f} МэВ ({binding_per_nucleon:.2f} МэВ/нуклон)"
    
    def _solve_mass_defect(self, templates):
        """Δm = Z·m_p + (A-Z)·m_n - M"""
        N = self.A - self.Z
        theoretical_mass = self.Z * self.M_PROTON + N * self.M_NEUTRON
        mass_defect = theoretical_mass - self.mass
        
        step1 = templates.get("mass_defect_formula", {}).get(self.language, "")
        self.solution_steps.append(step1)
        
        self.solution_steps.append(
            f"m_теор = {self.Z}×{self.M_PROTON} + {N}×{self.M_NEUTRON} = {theoretical_mass:.6f} а.е.м."
        )
        self.solution_steps.append(f"Δm = {theoretical_mass:.6f} - {self.mass:.6f} = {mass_defect:.6f} а.е.м.")
        
        self.final_answer = f"Δm = {mass_defect:.6f} а.е.м."
    
    def _solve_activity(self, templates):
        """A = λN = (ln2/T½)·N"""
        decay_const = math.log(2) / self.t_half
        activity = decay_const * self.N0
        
        step1 = templates.get("activity_formula", {}).get(self.language, "")
        self.solution_steps.append(step1)
        
        self.solution_steps.append(f"λ = ln(2)/T½ = {decay_const:.6e} с⁻¹")
        self.solution_steps.append(f"A = λN = {decay_const:.6e} × {self.N0} = {activity:.4e} Бк")
        
        self.final_answer = f"A = {activity:.4e} Бк"
    
    def get_task_type(self) -> str:
        return "nuclear"
    
    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                            detail_level: int = 3, difficulty: int = 5):
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(task_type=task_type, language=language,
                  detail_level=detail_level, difficulty=difficulty)
