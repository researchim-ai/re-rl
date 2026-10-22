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
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


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
        "hydrogen_atom", "uncertainty", texts.literal('literals.s0')
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
        
        max_n = int(preset["max_n"])
        self.n = n if n is not None else random.randint(1, max_n)
        n1_hi = max(1, max_n - 1)
        self.n1 = n1 if n1 is not None else random.randint(1, min(3, n1_hi))
        if n2 is not None:
            self.n2 = n2
        else:
            low = self.n1 + 1
            self.n2 = random.randint(low, max(low, max_n))
        
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
        elif self.task_type == texts.t('s26', self.language):
            template = templates.get(texts.t('s28', self.language), {}).get(self.language, "")
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
        elif self.task_type == texts.t('s27', self.language):
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
            texts.t('s6', self.language, v0=self._format_scientific(self.h), v1=self._format_scientific(self.freq), v2=self._format_scientific(E_photon), E_photon_eV=E_photon_eV)
        )
        
        if E_kinetic > 0:
            self.solution_steps.append(
                texts.t('s21', self.language, E_photon_eV=E_photon_eV, work_function=self.work_function, E_kinetic_eV=E_kinetic_eV)
            )
            self.final_answer = texts.t('s7', self.language, E_kinetic_eV=E_kinetic_eV)
        else:
            self.solution_steps.append(
                texts.t('s22', self.language, E_photon_eV=E_photon_eV, work_function=self.work_function, E_kinetic_eV=E_kinetic_eV)
            )
            self.solution_steps.append(
                texts.t('s23', self.language)
            )
            self.final_answer = texts.t('s8', self.language)
    
    def _solve_compton(self, templates):
        """Δλ = λc(1 - cos θ), где λc = h/(m_e·c)"""
        lambda_c = self.h / (self.m_e * self.c)  # Комптоновская длина волны
        angle_rad = math.radians(self.angle)
        delta_lambda = lambda_c * (1 - math.cos(angle_rad))
        new_wavelength = self.wavelength + delta_lambda
        
        step1 = templates.get("compton_formula", {}).get(self.language, "")
        self.solution_steps.append(step1)
        
        self.solution_steps.append(
            texts.t('s9', self.language, v0=self._format_scientific(lambda_c))
        )
        self.solution_steps.append(
            texts.t('s10', self.language, angle=self.angle, v1=self._format_scientific(delta_lambda))
        )
        self.solution_steps.append(
            texts.t('s11', self.language, v0=self._format_scientific(new_wavelength))
        )
        
        self.final_answer = texts.t('s1', self.language, v0=self._format_scientific(delta_lambda))
    
    def _solve_de_broglie(self, templates):
        """λ = h/p = h/(mv)"""
        momentum = self.mass * self.velocity
        wavelength = self.h / momentum
        
        step1 = templates.get(texts.t('s24', self.language), {}).get(self.language, "")
        self.solution_steps.append(step1)
        
        self.solution_steps.append(
            texts.t('s12', self.language, v0=self._format_scientific(self.mass), v1=self._format_scientific(self.velocity), v2=self._format_scientific(momentum))
        )
        self.solution_steps.append(
            texts.t('s13', self.language, v0=self._format_scientific(self.h), v1=self._format_scientific(momentum), v2=self._format_scientific(wavelength))
        )
        
        self.final_answer = texts.t('s2', self.language, v0=self._format_scientific(wavelength))
    
    def _solve_hydrogen_atom(self, templates):
        """Eₙ = -13.6/n² эВ, ΔE = 13.6(1/n₁² - 1/n₂²) эВ"""
        E1 = -13.6 / (self.n1 ** 2)
        E2 = -13.6 / (self.n2 ** 2)
        delta_E = E2 - E1  # Положительное при поглощении
        
        step1 = templates.get("hydrogen_energy", {}).get(self.language, "")
        self.solution_steps.append(step1)
        
        self.solution_steps.append(texts.t('s14', self.language, n1=self.n1, n1_2=self.n1, E1=E1))
        self.solution_steps.append(texts.t('s15', self.language, n2=self.n2, n2_2=self.n2, E2=E2))
        self.solution_steps.append(texts.t('s16', self.language, n2=self.n2, n1=self.n1, delta_E=delta_E))
        
        # Длина волны излучённого фотона
        delta_E_joules = abs(delta_E) * self.e
        wavelength = self.h * self.c / delta_E_joules
        self.solution_steps.append(texts.t('s17', self.language, v0=self._format_scientific(wavelength)))
        
        self.final_answer = texts.t('s3', self.language, v0=abs(delta_E), v1=self._format_scientific(wavelength))
    
    def _solve_uncertainty(self, templates):
        """Δx·Δp ≥ ℏ/2 => Δp ≥ ℏ/(2Δx)"""
        hbar = self.h / (2 * math.pi)
        delta_p = hbar / (2 * self.delta_x)
        
        step1 = templates.get("uncertainty_formula", {}).get(self.language, "")
        self.solution_steps.append(step1)
        
        self.solution_steps.append(texts.t('s18', self.language, v0=self._format_scientific(hbar)))
        self.solution_steps.append(
            texts.t('s19', self.language, v0=self._format_scientific(hbar), v1=self._format_scientific(self.delta_x), v2=self._format_scientific(delta_p))
        )
        
        self.final_answer = texts.t('s4', self.language, v0=self._format_scientific(delta_p))
    
    def _solve_particle_in_box(self, templates):
        """Eₙ = n²h²/(8mL²)"""
        E_n = (self.n ** 2 * self.h ** 2) / (8 * self.m_e * self.box_length ** 2)
        E_n_eV = E_n / self.e
        
        step1 = templates.get(texts.t('s25', self.language), {}).get(self.language, "")
        self.solution_steps.append(step1)
        
        self.solution_steps.append(
            f"E_{self.n} = {self.n}² × ({self._format_scientific(self.h)})² / "
            f"(8 × {self._format_scientific(self.m_e)} × ({self._format_scientific(self.box_length)})²)"
        )
        self.solution_steps.append(texts.t('s20', self.language, n=self.n, v1=self._format_scientific(E_n), E_n_eV=E_n_eV))
        
        self.final_answer = texts.t('s5', self.language, E_n_eV=E_n_eV)
    
    def get_task_type(self) -> str:
        return "quantum"
    
    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                            detail_level: int = 3, difficulty: int = 5, reasoning_mode: bool = False):
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(task_type=task_type, language=language,
                  detail_level=detail_level, difficulty=difficulty, reasoning_mode=reasoning_mode)
