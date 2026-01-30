# re_rl/tasks/physics/mechanics/center_of_mass_task.py

import random
from typing import Dict, Any, ClassVar, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class CenterOfMassTask(BaseMathTask):
    """
    Задачи на нахождение центра масс системы тел.
    """
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n_bodies": 2, "coord_range": (-5, 5), "mass_range": (1, 5)},
        3: {"n_bodies": 3, "coord_range": (-10, 10), "mass_range": (1, 10)},
        5: {"n_bodies": 3, "coord_range": (-20, 20), "mass_range": (1, 20)},
        7: {"n_bodies": 4, "coord_range": (-50, 50), "mass_range": (1, 50)},
        10: {"n_bodies": 5, "coord_range": (-100, 100), "mass_range": (1, 100)},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        masses: List[float] = None,
        positions: List[Tuple[float, float]] = None,
        difficulty: int = None,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False
    ):
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            n_bodies = preset.get("n_bodies", 3)
            coord_range = preset.get("coord_range", (-10, 10))
            mass_range = preset.get("mass_range", (1, 10))
        else:
            n_bodies = 3
            coord_range = (-10, 10)
            mass_range = (1, 10)
        
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        
        # Генерируем или используем переданные данные
        if masses is not None and positions is not None:
            self.masses = masses
            self.positions = positions
        else:
            self.masses = [round(random.uniform(*mass_range), 1) for _ in range(n_bodies)]
            self.positions = [(round(random.uniform(*coord_range), 1), 
                              round(random.uniform(*coord_range), 1)) 
                             for _ in range(n_bodies)]
        
        self.n = len(self.masses)
        
        # Вычисляем центр масс
        self._calculate()
        
        # Формируем текст задачи
        problem_text = self._create_problem_text()
        
        super().__init__(problem_text, language=self.language, detail_level=detail_level, output_format=output_format)
        self.reasoning_mode = reasoning_mode

    def _calculate(self):
        """Вычисляет координаты центра масс."""
        total_mass = sum(self.masses)
        
        x_cm = sum(m * pos[0] for m, pos in zip(self.masses, self.positions)) / total_mass
        y_cm = sum(m * pos[1] for m, pos in zip(self.masses, self.positions)) / total_mass
        
        self.total_mass = total_mass
        self.x_cm = round(x_cm, 3)
        self.y_cm = round(y_cm, 3)

    def _create_problem_text(self) -> str:
        templates = PROMPT_TEMPLATES["center_of_mass"]
        
        problem_text = templates["instructions"][self.language] + "\n\n"
        
        masses_str = ", ".join(str(m) for m in self.masses)
        positions_str = ", ".join(str(pos) for pos in self.positions)
        
        problem_text += templates["problem"][self.language].format(
            n=self.n,
            masses=masses_str,
            positions=positions_str
        )
        
        return problem_text

    def solve(self):
        self.solution_steps = []
        
        weighted_x = sum(m * pos[0] for m, pos in zip(self.masses, self.positions))
        weighted_y = sum(m * pos[1] for m, pos in zip(self.masses, self.positions))
        
        if self.reasoning_mode:
            masses_str = ", ".join(f"m{i+1}={m}" for i, m in enumerate(self.masses))
            self.add_given({"массы": masses_str}, {"массы": "кг"})
            self.add_find("(x_c, y_c)", "координаты центра масс" if self.language == "ru" else "center of mass coordinates")
        
        self.add_formula("x_c = Σ(mᵢxᵢ)/Σmᵢ, y_c = Σ(mᵢyᵢ)/Σmᵢ")
        self.add_substitution(f"M = Σmᵢ = {round(self.total_mass, 2)} кг")
        self.add_substitution(f"Σmx = {round(weighted_x, 2)}, Σmy = {round(weighted_y, 2)}")
        self.add_calculation(f"x_c = {round(weighted_x, 2)}/{round(self.total_mass, 2)}", self.x_cm, "м")
        self.add_calculation(f"y_c = {round(weighted_y, 2)}/{round(self.total_mass, 2)}", self.y_cm, "м")
        
        self.final_answer = f"Центр масс: ({self.x_cm}, {self.y_cm}) м"

    def get_task_type(self):
        return "center_of_mass"
    
    @classmethod
    def generate_random_task(cls, reasoning_mode: bool = False, **kwargs):
        return cls(reasoning_mode=reasoning_mode, **kwargs)
