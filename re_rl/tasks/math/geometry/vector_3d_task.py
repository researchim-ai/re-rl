# re_rl/tasks/vector_3d_task.py

"""
Vector3DTask — задачи по векторной алгебре в 3D.

Поддерживаемые типы:
- cross_product: векторное произведение
- triple_scalar: смешанное произведение
- plane_equation: уравнение плоскости
- distance_point_plane: расстояние от точки до плоскости
- angle_vectors: угол между векторами
- projection: проекция вектора
- parallelpiped_volume: объём параллелепипеда
"""

import random
import math
from typing import List, Dict, Any, ClassVar, Tuple
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class Vector3DTask(BaseMathTask):
    """Генератор задач по векторам в 3D."""
    
    TASK_TYPES = [
        "cross_product", "triple_scalar", "plane_equation",
        "distance_point_plane", "angle_vectors", "projection",
        "parallelpiped_volume"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_coord": 3, "simple_coords": True},
        2: {"max_coord": 5, "simple_coords": True},
        3: {"max_coord": 5, "simple_coords": False},
        4: {"max_coord": 7, "simple_coords": False},
        5: {"max_coord": 10, "simple_coords": False},
        6: {"max_coord": 10, "simple_coords": False},
        7: {"max_coord": 15, "simple_coords": False},
        8: {"max_coord": 15, "simple_coords": False},
        9: {"max_coord": 20, "simple_coords": False},
        10: {"max_coord": 20, "simple_coords": False},
    }
    
    def __init__(
        self,
        task_type: str = "cross_product",
        vector_a: Tuple[float, float, float] = None,
        vector_b: Tuple[float, float, float] = None,
        vector_c: Tuple[float, float, float] = None,
        point: Tuple[float, float, float] = None,
        plane_coeffs: Tuple[float, float, float, float] = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        **kwargs
    ):
        self.task_type = task_type.lower()
        self.difficulty = difficulty
        self._output_format = output_format
        self.language = language.lower()  # ВАЖНО: установить ДО _create_problem_description
        
        # Получаем параметры сложности
        preset = self._interpolate_difficulty(difficulty)
        self.max_coord = preset.get("max_coord", 10)
        self.simple_coords = preset.get("simple_coords", False)
        
        # Генерируем векторы
        self.vector_a = vector_a if vector_a else self._generate_vector()
        self.vector_b = vector_b if vector_b else self._generate_vector()
        self.vector_c = vector_c if vector_c else self._generate_vector()
        self.point = point if point else self._generate_vector()
        self.plane_coeffs = plane_coeffs if plane_coeffs else self._generate_plane()
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
    
    def _generate_vector(self) -> Tuple[int, int, int]:
        """Генерирует случайный вектор."""
        if self.simple_coords:
            return tuple(random.randint(-self.max_coord, self.max_coord) for _ in range(3))
        else:
            return tuple(random.randint(-self.max_coord, self.max_coord) for _ in range(3))
    
    def _generate_plane(self) -> Tuple[int, int, int, int]:
        """Генерирует коэффициенты плоскости Ax + By + Cz + D = 0."""
        A = random.randint(1, 5)
        B = random.randint(1, 5)
        C = random.randint(1, 5)
        D = random.randint(-10, 10)
        return (A, B, C, D)
    
    def _vector_str(self, v: Tuple) -> str:
        """Форматирует вектор в строку."""
        return f"({v[0]}, {v[1]}, {v[2]})"
    
    def _create_problem_description(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES.get("vector_3d", {}).get("problem", {})
        
        if self.task_type == "cross_product":
            template = templates.get("cross_product", {}).get(self.language, "")
            return template.format(a=self._vector_str(self.vector_a), b=self._vector_str(self.vector_b))
        
        elif self.task_type == "triple_scalar":
            template = templates.get("triple_scalar", {}).get(self.language, "")
            return template.format(
                a=self._vector_str(self.vector_a),
                b=self._vector_str(self.vector_b),
                c=self._vector_str(self.vector_c)
            )
        
        elif self.task_type == "plane_equation":
            template = templates.get("plane_equation", {}).get(self.language, "")
            return template.format(
                a=self._vector_str(self.vector_a),
                b=self._vector_str(self.vector_b),
                c=self._vector_str(self.vector_c)
            )
        
        elif self.task_type == "distance_point_plane":
            A, B, C, D = self.plane_coeffs
            plane_str = f"{A}x + {B}y + {C}z + {D} = 0"
            template = templates.get("distance_point_plane", {}).get(self.language, "")
            return template.format(p=self._vector_str(self.point), plane=plane_str)
        
        elif self.task_type == "angle_vectors":
            template = templates.get("angle_vectors", {}).get(self.language, "")
            return template.format(a=self._vector_str(self.vector_a), b=self._vector_str(self.vector_b))
        
        elif self.task_type == "projection":
            template = templates.get("projection", {}).get(self.language, "")
            return template.format(a=self._vector_str(self.vector_a), b=self._vector_str(self.vector_b))
        
        elif self.task_type == "parallelpiped_volume":
            template = templates.get("parallelpiped_volume", {}).get(self.language, "")
            return template.format(
                a=self._vector_str(self.vector_a),
                b=self._vector_str(self.vector_b),
                c=self._vector_str(self.vector_c)
            )
        
        return ""
    
    def solve(self):
        """Решает задачу пошагово."""
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("vector_3d", {}).get("steps", {})
        
        if self.task_type == "cross_product":
            self._solve_cross_product(templates)
        elif self.task_type == "triple_scalar":
            self._solve_triple_scalar(templates)
        elif self.task_type == "plane_equation":
            self._solve_plane_equation(templates)
        elif self.task_type == "distance_point_plane":
            self._solve_distance_point_plane(templates)
        elif self.task_type == "angle_vectors":
            self._solve_angle_vectors(templates)
        elif self.task_type == "projection":
            self._solve_projection(templates)
        elif self.task_type == "parallelpiped_volume":
            self._solve_parallelpiped_volume(templates)
        
        # Ограничиваем по detail_level
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def _cross_product(self, a: Tuple, b: Tuple) -> Tuple[float, float, float]:
        """Вычисляет векторное произведение."""
        return (
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]
        )
    
    def _dot_product(self, a: Tuple, b: Tuple) -> float:
        """Вычисляет скалярное произведение."""
        return sum(ai * bi for ai, bi in zip(a, b))
    
    def _magnitude(self, v: Tuple) -> float:
        """Вычисляет длину вектора."""
        return math.sqrt(sum(x ** 2 for x in v))
    
    def _solve_cross_product(self, templates):
        """Векторное произведение."""
        a = self.vector_a
        b = self.vector_b
        
        step1 = templates.get("cross_formula", {}).get(self.language, "")
        self.solution_steps.append(step1.format(
            a1=a[0], a2=a[1], a3=a[2], b1=b[0], b2=b[1], b3=b[2]
        ))
        
        result = self._cross_product(a, b)
        
        step2 = templates.get("cross_compute", {}).get(self.language, "")
        self.solution_steps.append(step2.format(
            a1=a[0], a2=a[1], a3=a[2], b1=b[0], b2=b[1], b3=b[2],
            result=self._vector_str(result)
        ))
        
        self.final_answer = self._vector_str(result)
    
    def _solve_triple_scalar(self, templates):
        """Смешанное произведение."""
        a = self.vector_a
        b = self.vector_b
        c = self.vector_c
        
        # (a, b, c) = a · (b × c)
        cross_bc = self._cross_product(b, c)
        result = self._dot_product(a, cross_bc)
        
        step = templates.get("triple_product", {}).get(self.language, "")
        self.solution_steps.append(step.format(step=1, result=result))
        
        self.final_answer = str(result)
    
    def _solve_plane_equation(self, templates):
        """Уравнение плоскости через три точки."""
        A = self.vector_a
        B = self.vector_b
        C = self.vector_c
        
        # Векторы AB и AC
        AB = (B[0] - A[0], B[1] - A[1], B[2] - A[2])
        AC = (C[0] - A[0], C[1] - A[1], C[2] - A[2])
        
        # Нормаль = AB × AC
        normal = self._cross_product(AB, AC)
        
        step1 = templates.get("plane_normal", {}).get(self.language, "")
        self.solution_steps.append(step1.format(step=1, normal=self._vector_str(normal)))
        
        # Уравнение: n · (r - A) = 0  =>  ax + by + cz + d = 0
        # d = -(a*A[0] + b*A[1] + c*A[2])
        a, b, c = normal
        d = -(a * A[0] + b * A[1] + c * A[2])
        
        step2 = templates.get("plane_result", {}).get(self.language, "")
        self.solution_steps.append(step2.format(step=2, a=a, b=b, c=c, d=d))
        
        self.final_answer = f"{a}x + {b}y + {c}z + {d} = 0"
    
    def _solve_distance_point_plane(self, templates):
        """Расстояние от точки до плоскости."""
        A, B, C, D = self.plane_coeffs
        x0, y0, z0 = self.point
        
        # d = |Ax0 + By0 + Cz0 + D| / sqrt(A² + B² + C²)
        numerator = abs(A * x0 + B * y0 + C * z0 + D)
        denominator = math.sqrt(A ** 2 + B ** 2 + C ** 2)
        distance = numerator / denominator
        
        step = templates.get("distance_formula", {}).get(self.language, "")
        self.solution_steps.append(step.format(step=1, distance=f"{distance:.4f}"))
        
        self.final_answer = f"{distance:.4f}"
    
    def _solve_angle_vectors(self, templates):
        """Угол между векторами."""
        a = self.vector_a
        b = self.vector_b
        
        dot = self._dot_product(a, b)
        mag_a = self._magnitude(a)
        mag_b = self._magnitude(b)
        
        step1 = templates.get("dot_product", {}).get(self.language, "")
        self.solution_steps.append(step1.format(
            step=1, a1=a[0], a2=a[1], a3=a[2], b1=b[0], b2=b[1], b3=b[2], result=dot
        ))
        
        step2 = templates.get("magnitudes", {}).get(self.language, "")
        self.solution_steps.append(step2.format(step=2, mag_a=f"{mag_a:.4f}", mag_b=f"{mag_b:.4f}"))
        
        cos_val = dot / (mag_a * mag_b) if mag_a * mag_b != 0 else 0
        cos_val = max(-1, min(1, cos_val))  # Ограничиваем для acos
        angle_rad = math.acos(cos_val)
        angle_deg = math.degrees(angle_rad)
        
        step3 = templates.get("angle_formula", {}).get(self.language, "")
        self.solution_steps.append(step3.format(
            step=3, cos_val=f"{cos_val:.4f}", angle=f"{angle_deg:.2f}"
        ))
        
        self.final_answer = f"{angle_deg:.2f}°"
    
    def _solve_projection(self, templates):
        """Проекция вектора a на вектор b."""
        a = self.vector_a
        b = self.vector_b
        
        dot_ab = self._dot_product(a, b)
        dot_bb = self._dot_product(b, b)
        
        if dot_bb == 0:
            self.final_answer = "(0, 0, 0)"
            return
        
        scalar = dot_ab / dot_bb
        proj = (scalar * b[0], scalar * b[1], scalar * b[2])
        
        step = templates.get("projection_formula", {}).get(self.language, "")
        self.solution_steps.append(step.format(
            step=1, result=f"({proj[0]:.4f}, {proj[1]:.4f}, {proj[2]:.4f})"
        ))
        
        self.final_answer = f"({proj[0]:.4f}, {proj[1]:.4f}, {proj[2]:.4f})"
    
    def _solve_parallelpiped_volume(self, templates):
        """Объём параллелепипеда = |смешанное произведение|."""
        a = self.vector_a
        b = self.vector_b
        c = self.vector_c
        
        cross_bc = self._cross_product(b, c)
        volume = abs(self._dot_product(a, cross_bc))
        
        step = templates.get("triple_product", {}).get(self.language, "")
        self.solution_steps.append(step.format(step=1, result=f"|{self._dot_product(a, cross_bc)}| = {volume}"))
        
        self.final_answer = str(volume)
    
    def get_task_type(self) -> str:
        return "vector_3d"
    
    @classmethod
    def generate_random_task(
        cls,
        task_type: str = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text"
    ):
        """Генерирует случайную задачу по векторам 3D."""
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(
            task_type=task_type,
            language=language,
            detail_level=detail_level,
            difficulty=difficulty,
            output_format=output_format
        )
