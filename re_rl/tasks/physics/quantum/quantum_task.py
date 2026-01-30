# re_rl/tasks/physics/quantum/quantum_task.py

"""
QuantumTask — задачи по квантовой механике.

Типы задач:
- photoelectric: фотоэффект (уравнение Эйнштейна)
- compton: эффект Комптона
- de_broglie: волны де Бройля
- hydrogen_atom: энергетические уровни атома водорода
- uncertainty: принцип неопределённости Гейзенберга
- particle_in_box: частица в потенциальной яме
"""

import random
import math
from typing import Dict, Any, ClassVar
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import get_constant


class QuantumTask(BaseMathTask):
    """Генератор задач по квантовой механике."""
    
    TASK_TYPES = [
        "photoelectric", "compton", "de_broglie", 
        "hydrogen_atom", "uncertainty", "particle_in_box"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_freq": 1e15, "max_n": 3, "max_v": 1e6},
        2: {"max_freq": 2e15, "max_n": 4, "max_v": 5e6},
        3: {"max_freq": 5e15, "max_n": 5, "max_v": 1e7},
        4: {"max_freq": 1e16, "max_n": 6, "max_v": 5e7},
        5: {"max_freq": 2e16, "max_n": 7, "max_v": 1e8},
        6: {"max_freq": 5e16, "max_n": 8, "max_v": 1.5e8},
        7: {"max_freq": 1e17, "max_n": 10, "max_v": 2e8},
        8: {"max_freq": 2e17, "max_n": 12, "max_v": 2.5e8},
        9: {"max_freq": 5e17, "max_n": 15, "max_v": 2.8e8},
        10: {"max_freq": 1e18, "max_n": 20, "max_v": 2.9e8},
    }
    
    def __init__(
        self,
        task_type: str = "photoelectric",
        freq: float = None,
        wavelength: float = None,
        work_function: float = None,
        n: int = None,
        n1: int = None,
        n2: int = None,
        velocity: float = None,
        mass: float = None,
        box_length: float = None,
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
        self._reasoning_mode = reasoning_mode
        self.language = language
        
        # Физические константы
        self.h = get_constant("h")  # Постоянная Планка
        self.c = get_constant("c")  # Скорость света
        self.m_e = get_constant("m_e")  # Масса электрона
        self.e = get_constant("e")  # Заряд электрона
        
        preset = self._interpolate_difficulty(difficulty)
        
        # Генерируем параметры
        self.freq = freq if freq is not None else random.uniform(1e14, preset["max_freq"])
        self.wavelength = wavelength if wavelength is not None else self.c / self.freq
        
        # Работа выхода в эВ (типичные значения для металлов)
        self.work_function = work_function if work_function is not None else random.uniform(2.0, 5.0)
        
        self.n = n if n is not None else random.randint(1, preset["max_n"])
        self.n1 = n1 if n1 is not None else random.randint(1, 3)
        self.n2 = n2 if n2 is not None else random.randint(self.n1 + 1, preset["max_n"])
        
        self.velocity = velocity if velocity is not None else random.uniform(1e5, preset["max_v"])
        self.mass = mass if mass is not None else self.m_e
        self.box_length = box_length if box_length is not None else random.uniform(1e-10, 1e-9)
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode
    
    def _format_scientific(self, value: float, precision: int = 3) -> str:
        """Форматирует число в научную нотацию."""
        if abs(value) < 1e-3 or abs(value) > 1e6:
            return f"{value:.{precision}e}"
        return f"{value:.{precision}f}"
    
    def _create_problem_description(self) -> str:
        templates = PROMPT_TEMPLATES.get("quantum", {}).get("problem", {})
        
        if self.task_type == "photoelectric":
            template = templates.get("photoelectric", {}).get(self.language, "")
            return template.format(
                freq=self._format_scientific(self.freq),
                work_function=self.work_function
            )
        elif self.task_type == "compton":
            template = templates.get("compton", {}).get(self.language, "")
            angle = random.choice([30, 45, 60, 90, 120, 180])
            self.angle = angle
            return template.format(
                wavelength=self._format_scientific(self.wavelength),
                angle=angle
            )
        elif self.task_type == "de_broglie":
            template = templates.get("de_broglie", {}).get(self.language, "")
            return template.format(
                mass=self._format_scientific(self.mass),
                velocity=self._format_scientific(self.velocity)
            )
        elif self.task_type == "hydrogen_atom":
            template = templates.get("hydrogen_atom", {}).get(self.language, "")
            return template.format(n1=self.n1, n2=self.n2)
        elif self.task_type == "uncertainty":
            template = templates.get("uncertainty", {}).get(self.language, "")
            self.delta_x = random.uniform(1e-11, 1e-9)
            return template.format(delta_x=self._format_scientific(self.delta_x))
        elif self.task_type == "particle_in_box":
            template = templates.get("particle_in_box", {}).get(self.language, "")
            return template.format(
                L=self._format_scientific(self.box_length),
                n=self.n
            )
        return ""
    
    def solve(self):
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("quantum", {}).get("steps", {})
        
        if self.task_type == "photoelectric":
            self._solve_photoelectric(templates)
        elif self.task_type == "compton":
            self._solve_compton(templates)
        elif self.task_type == "de_broglie":
            self._solve_de_broglie(templates)
        elif self.task_type == "hydrogen_atom":
            self._solve_hydrogen_atom(templates)
        elif self.task_type == "uncertainty":
            self._solve_uncertainty(templates)
        elif self.task_type == "particle_in_box":
            self._solve_particle_in_box(templates)
    
    def _solve_photoelectric(self, templates):
        """hν = A + Eₖ => Eₖ = hν - A"""
        # Энергия фотона в Дж
        E_photon = self.h * self.freq
        # Энергия фотона в эВ
        E_photon_eV = E_photon / self.e
        # Работа выхода в Дж
        A_joules = self.work_function * self.e
        # Кинетическая энергия в Дж
        E_kinetic = E_photon - A_joules
        # Кинетическая энергия в эВ
        E_kinetic_eV = E_photon_eV - self.work_function
        
        step1 = templates.get("einstein_equation", {}).get(self.language, "")
        self.solution_steps.append(step1)
        
        self.solution_steps.append(
            f"E_фотона = hν = {self._format_scientific(self.h)} × {self._format_scientific(self.freq)} = "
            f"{self._format_scientific(E_photon)} Дж = {E_photon_eV:.2f} эВ"
        )
        
        if E_kinetic > 0:
            self.solution_steps.append(
                f"Eₖ = hν - A = {E_photon_eV:.2f} - {self.work_function} = {E_kinetic_eV:.2f} эВ"
            )
            self.final_answer = f"{E_kinetic_eV:.4f} эВ"
        else:
            self.final_answer = "Фотоэффект не происходит (hν < A)"
    
    def _solve_compton(self, templates):
        """Δλ = λc(1 - cos θ), где λc = h/(m_e·c)"""
        lambda_c = self.h / (self.m_e * self.c)  # Комптоновская длина волны
        angle_rad = math.radians(self.angle)
        delta_lambda = lambda_c * (1 - math.cos(angle_rad))
        new_wavelength = self.wavelength + delta_lambda
        
        step1 = templates.get("compton_formula", {}).get(self.language, "")
        self.solution_steps.append(step1)
        
        self.solution_steps.append(
            f"λc = h/(m_e·c) = {self._format_scientific(lambda_c)} м"
        )
        self.solution_steps.append(
            f"Δλ = λc(1 - cos {self.angle}°) = {self._format_scientific(delta_lambda)} м"
        )
        self.solution_steps.append(
            f"λ' = λ + Δλ = {self._format_scientific(new_wavelength)} м"
        )
        
        self.final_answer = f"Δλ = {self._format_scientific(delta_lambda)} м"
    
    def _solve_de_broglie(self, templates):
        """λ = h/p = h/(mv)"""
        momentum = self.mass * self.velocity
        wavelength = self.h / momentum
        
        step1 = templates.get("de_broglie_formula", {}).get(self.language, "")
        self.solution_steps.append(step1)
        
        self.solution_steps.append(
            f"p = mv = {self._format_scientific(self.mass)} × {self._format_scientific(self.velocity)} = "
            f"{self._format_scientific(momentum)} кг·м/с"
        )
        self.solution_steps.append(
            f"λ = h/p = {self._format_scientific(self.h)} / {self._format_scientific(momentum)} = "
            f"{self._format_scientific(wavelength)} м"
        )
        
        self.final_answer = f"{self._format_scientific(wavelength)} м"
    
    def _solve_hydrogen_atom(self, templates):
        """Eₙ = -13.6/n² эВ, ΔE = 13.6(1/n₁² - 1/n₂²) эВ"""
        E1 = -13.6 / (self.n1 ** 2)
        E2 = -13.6 / (self.n2 ** 2)
        delta_E = E2 - E1  # Положительное при поглощении
        
        step1 = templates.get("hydrogen_energy", {}).get(self.language, "")
        self.solution_steps.append(step1)
        
        self.solution_steps.append(f"E_{self.n1} = -13.6/{self.n1}² = {E1:.4f} эВ")
        self.solution_steps.append(f"E_{self.n2} = -13.6/{self.n2}² = {E2:.4f} эВ")
        self.solution_steps.append(f"ΔE = E_{self.n2} - E_{self.n1} = {delta_E:.4f} эВ")
        
        # Длина волны излучённого фотона
        delta_E_joules = abs(delta_E) * self.e
        wavelength = self.h * self.c / delta_E_joules
        self.solution_steps.append(f"λ = hc/|ΔE| = {self._format_scientific(wavelength)} м")
        
        self.final_answer = f"ΔE = {abs(delta_E):.4f} эВ, λ = {self._format_scientific(wavelength)} м"
    
    def _solve_uncertainty(self, templates):
        """Δx·Δp ≥ ℏ/2 => Δp ≥ ℏ/(2Δx)"""
        hbar = self.h / (2 * math.pi)
        delta_p = hbar / (2 * self.delta_x)
        
        step1 = templates.get("uncertainty_formula", {}).get(self.language, "")
        self.solution_steps.append(step1)
        
        self.solution_steps.append(f"ℏ = h/(2π) = {self._format_scientific(hbar)} Дж·с")
        self.solution_steps.append(
            f"Δp ≥ ℏ/(2Δx) = {self._format_scientific(hbar)} / (2 × {self._format_scientific(self.delta_x)}) = "
            f"{self._format_scientific(delta_p)} кг·м/с"
        )
        
        self.final_answer = f"Δp ≥ {self._format_scientific(delta_p)} кг·м/с"
    
    def _solve_particle_in_box(self, templates):
        """Eₙ = n²h²/(8mL²)"""
        E_n = (self.n ** 2 * self.h ** 2) / (8 * self.m_e * self.box_length ** 2)
        E_n_eV = E_n / self.e
        
        step1 = templates.get("particle_box_formula", {}).get(self.language, "")
        self.solution_steps.append(step1)
        
        self.solution_steps.append(
            f"E_{self.n} = {self.n}² × ({self._format_scientific(self.h)})² / "
            f"(8 × {self._format_scientific(self.m_e)} × ({self._format_scientific(self.box_length)})²)"
        )
        self.solution_steps.append(f"E_{self.n} = {self._format_scientific(E_n)} Дж = {E_n_eV:.4f} эВ")
        
        self.final_answer = f"{E_n_eV:.4f} эВ"
    
    def get_task_type(self) -> str:
        return "quantum"
    
    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                            detail_level: int = 3, difficulty: int = 5, reasoning_mode: bool = False):
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(task_type=task_type, language=language,
                  detail_level=detail_level, difficulty=difficulty, reasoning_mode=reasoning_mode)
