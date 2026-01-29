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
        output_format: OutputFormat = "text"
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
        templates = PROMPT_TEMPLATES["center_of_mass"]
        steps = []
        
        # Шаг 1: формула
        steps.append(templates["steps"]["formula"][self.language])
        
        # Шаг 2: общая масса
        steps.append(templates["steps"]["total_mass"][self.language].format(
            total_mass=round(self.total_mass, 2)
        ))
        
        # Шаг 3: взвешенные суммы
        weighted_x = sum(m * pos[0] for m, pos in zip(self.masses, self.positions))
        weighted_y = sum(m * pos[1] for m, pos in zip(self.masses, self.positions))
        weighted_str = f"Σmx = {round(weighted_x, 2)}, Σmy = {round(weighted_y, 2)}"
        steps.append(templates["steps"]["weighted_sum"][self.language].format(
            weighted=weighted_str
        ))
        
        # Ограничиваем количество шагов (без дублирования)
        
        self.solution_steps = steps[:self.detail_level]
        self.final_answer = templates["final_answer"][self.language].format(
            x=self.x_cm,
            y=self.y_cm
        )

    def get_task_type(self):
        return "center_of_mass"
    
    @classmethod
    def generate_random_task(cls, **kwargs):
        return cls(**kwargs)
