# re_rl/tasks/geometry_task.py

"""
GeometryTask — геометрические задачи.

Поддерживаемые типы:
- triangle_area_coords: площадь треугольника по координатам
- triangle_area_sides: площадь треугольника по сторонам (формула Герона)
- distance_2d: расстояние между точками на плоскости
- distance_3d: расстояние между точками в пространстве
- circle_area: площадь круга
- circle_circumference: длина окружности
- sphere_volume: объём шара
- cylinder_volume: объём цилиндра
- cone_volume: объём конуса
- angle_between_vectors: угол между векторами
- dot_product: скалярное произведение
- cross_product: векторное произведение
- line_equation: уравнение прямой
- midpoint: середина отрезка
"""

import random
import math
from typing import List, Dict, Any, Optional, Tuple, ClassVar
from dataclasses import dataclass

from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class GeometryTask(BaseMathTask):
    """Геометрические задачи."""
    
    TASK_TYPES = [
        "triangle_area_coords", "triangle_area_sides", "distance_2d", "distance_3d",
        "circle_area", "circle_circumference", "sphere_volume", "cylinder_volume",
        "cone_volume", "angle_between_vectors", "dot_product", "cross_product",
        "line_equation", "midpoint"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_coord": 5, "max_radius": 5},
        2: {"max_coord": 10, "max_radius": 10},
        3: {"max_coord": 15, "max_radius": 15},
        4: {"max_coord": 20, "max_radius": 20},
        5: {"max_coord": 30, "max_radius": 30},
        6: {"max_coord": 50, "max_radius": 50},
        7: {"max_coord": 75, "max_radius": 75},
        8: {"max_coord": 100, "max_radius": 100},
        9: {"max_coord": 150, "max_radius": 150},
        10: {"max_coord": 200, "max_radius": 200},
    }
    
    def __init__(
        self,
        task_type: str = "distance_2d",
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        **kwargs
    ):
        self.task_type = task_type.lower()
        self.difficulty = difficulty
        self.kwargs = kwargs
        
        # Получаем параметры из пресета
        preset = self._interpolate_difficulty(difficulty)
        self.max_coord = kwargs.get("max_coord", preset.get("max_coord", 30))
        self.max_radius = kwargs.get("max_radius", preset.get("max_radius", 30))
        
        # Генерируем параметры задачи
        self._generate_task_params()
        
        # Создаём описание
        description = self._create_problem_description()
        super().__init__(description, language, detail_level)
    
    def _rand_coord(self) -> int:
        """Генерирует случайную координату."""
        return random.randint(-self.max_coord, self.max_coord)
    
    def _generate_task_params(self):
        """Генерирует параметры задачи."""
        if self.task_type == "triangle_area_coords":
            self.x1, self.y1 = self._rand_coord(), self._rand_coord()
            self.x2, self.y2 = self._rand_coord(), self._rand_coord()
            self.x3, self.y3 = self._rand_coord(), self._rand_coord()
            # Убеждаемся, что точки не лежат на одной прямой
            while self._collinear():
                self.x3, self.y3 = self._rand_coord(), self._rand_coord()
        
        elif self.task_type == "triangle_area_sides":
            # Генерируем валидный треугольник
            self._generate_valid_triangle_sides()
        
        elif self.task_type == "distance_2d":
            self.x1, self.y1 = self._rand_coord(), self._rand_coord()
            self.x2, self.y2 = self._rand_coord(), self._rand_coord()
        
        elif self.task_type == "distance_3d":
            self.x1, self.y1, self.z1 = self._rand_coord(), self._rand_coord(), self._rand_coord()
            self.x2, self.y2, self.z2 = self._rand_coord(), self._rand_coord(), self._rand_coord()
        
        elif self.task_type in ["circle_area", "circle_circumference"]:
            self.r = self.kwargs.get("r", random.randint(1, self.max_radius))
        
        elif self.task_type == "sphere_volume":
            self.r = self.kwargs.get("r", random.randint(1, self.max_radius))
        
        elif self.task_type == "cylinder_volume":
            self.r = self.kwargs.get("r", random.randint(1, self.max_radius))
            self.h = self.kwargs.get("h", random.randint(1, self.max_radius))
        
        elif self.task_type == "cone_volume":
            self.r = self.kwargs.get("r", random.randint(1, self.max_radius))
            self.h = self.kwargs.get("h", random.randint(1, self.max_radius))
        
        elif self.task_type in ["angle_between_vectors", "dot_product"]:
            self.ax, self.ay = self._rand_coord(), self._rand_coord()
            self.bx, self.by = self._rand_coord(), self._rand_coord()
            # Убеждаемся, что векторы ненулевые
            while self.ax == 0 and self.ay == 0:
                self.ax, self.ay = self._rand_coord(), self._rand_coord()
            while self.bx == 0 and self.by == 0:
                self.bx, self.by = self._rand_coord(), self._rand_coord()
        
        elif self.task_type == "cross_product":
            self.ax, self.ay, self.az = self._rand_coord(), self._rand_coord(), self._rand_coord()
            self.bx, self.by, self.bz = self._rand_coord(), self._rand_coord(), self._rand_coord()
        
        elif self.task_type == "line_equation":
            self.x1, self.y1 = self._rand_coord(), self._rand_coord()
            self.x2, self.y2 = self._rand_coord(), self._rand_coord()
            # Точки не должны совпадать
            while self.x1 == self.x2 and self.y1 == self.y2:
                self.x2, self.y2 = self._rand_coord(), self._rand_coord()
        
        elif self.task_type == "midpoint":
            self.x1, self.y1 = self._rand_coord(), self._rand_coord()
            self.x2, self.y2 = self._rand_coord(), self._rand_coord()
    
    def _collinear(self) -> bool:
        """Проверяет, лежат ли три точки на одной прямой."""
        return (self.y2 - self.y1) * (self.x3 - self.x2) == (self.y3 - self.y2) * (self.x2 - self.x1)
    
    def _generate_valid_triangle_sides(self):
        """Генерирует валидные стороны треугольника."""
        while True:
            self.a = random.randint(3, self.max_coord)
            self.b = random.randint(3, self.max_coord)
            self.c = random.randint(3, self.max_coord)
            # Проверяем неравенство треугольника
            if (self.a + self.b > self.c and 
                self.a + self.c > self.b and 
                self.b + self.c > self.a):
                break
    
    def _create_problem_description(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES.get("geometry", {}).get("problem", {})
        
        if self.task_type == "triangle_area_coords":
            template = templates.get("triangle_area_coords", {}).get(self.language, "")
            return template.format(
                x1=self.x1, y1=self.y1,
                x2=self.x2, y2=self.y2,
                x3=self.x3, y3=self.y3
            )
        
        elif self.task_type == "triangle_area_sides":
            template = templates.get("triangle_area_sides", {}).get(self.language, "")
            return template.format(a=self.a, b=self.b, c=self.c)
        
        elif self.task_type == "distance_2d":
            template = templates.get("distance_2d", {}).get(self.language, "")
            return template.format(x1=self.x1, y1=self.y1, x2=self.x2, y2=self.y2)
        
        elif self.task_type == "distance_3d":
            template = templates.get("distance_3d", {}).get(self.language, "")
            return template.format(
                x1=self.x1, y1=self.y1, z1=self.z1,
                x2=self.x2, y2=self.y2, z2=self.z2
            )
        
        elif self.task_type == "circle_area":
            template = templates.get("circle_area", {}).get(self.language, "")
            return template.format(r=self.r)
        
        elif self.task_type == "circle_circumference":
            template = templates.get("circle_circumference", {}).get(self.language, "")
            return template.format(r=self.r)
        
        elif self.task_type == "sphere_volume":
            template = templates.get("sphere_volume", {}).get(self.language, "")
            return template.format(r=self.r)
        
        elif self.task_type == "cylinder_volume":
            template = templates.get("cylinder_volume", {}).get(self.language, "")
            return template.format(r=self.r, h=self.h)
        
        elif self.task_type == "cone_volume":
            template = templates.get("cone_volume", {}).get(self.language, "")
            return template.format(r=self.r, h=self.h)
        
        elif self.task_type == "angle_between_vectors":
            template = templates.get("angle_between_vectors", {}).get(self.language, "")
            return template.format(ax=self.ax, ay=self.ay, bx=self.bx, by=self.by)
        
        elif self.task_type == "dot_product":
            template = templates.get("dot_product", {}).get(self.language, "")
            return template.format(
                ax=self.ax, ay=self.ay, az=0,
                bx=self.bx, by=self.by, bz=0
            )
        
        elif self.task_type == "cross_product":
            template = templates.get("cross_product", {}).get(self.language, "")
            return template.format(
                ax=self.ax, ay=self.ay, az=self.az,
                bx=self.bx, by=self.by, bz=self.bz
            )
        
        elif self.task_type == "line_equation":
            template = templates.get("line_equation", {}).get(self.language, "")
            return template.format(x1=self.x1, y1=self.y1, x2=self.x2, y2=self.y2)
        
        elif self.task_type == "midpoint":
            template = templates.get("midpoint", {}).get(self.language, "")
            return template.format(x1=self.x1, y1=self.y1, x2=self.x2, y2=self.y2)
        
        return ""
    
    def solve(self):
        """Решает задачу пошагово."""
        self.solution_steps = []
        steps_templates = PROMPT_TEMPLATES.get("geometry", {}).get("steps", {})
        
        if self.task_type == "triangle_area_coords":
            self._solve_triangle_area_coords(steps_templates)
        elif self.task_type == "triangle_area_sides":
            self._solve_triangle_area_sides(steps_templates)
        elif self.task_type == "distance_2d":
            self._solve_distance_2d(steps_templates)
        elif self.task_type == "distance_3d":
            self._solve_distance_3d(steps_templates)
        elif self.task_type == "circle_area":
            self._solve_circle_area(steps_templates)
        elif self.task_type == "circle_circumference":
            self._solve_circumference(steps_templates)
        elif self.task_type == "sphere_volume":
            self._solve_sphere_volume(steps_templates)
        elif self.task_type == "cylinder_volume":
            self._solve_cylinder_volume(steps_templates)
        elif self.task_type == "cone_volume":
            self._solve_cone_volume(steps_templates)
        elif self.task_type == "angle_between_vectors":
            self._solve_angle_between_vectors(steps_templates)
        elif self.task_type == "dot_product":
            self._solve_dot_product(steps_templates)
        elif self.task_type == "cross_product":
            self._solve_cross_product(steps_templates)
        elif self.task_type == "line_equation":
            self._solve_line_equation(steps_templates)
        elif self.task_type == "midpoint":
            self._solve_midpoint(steps_templates)
        
        # Ограничиваем по detail_level
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def _solve_triangle_area_coords(self, templates):
        """Площадь треугольника по координатам."""
        area = abs(
            self.x1 * (self.y2 - self.y3) +
            self.x2 * (self.y3 - self.y1) +
            self.x3 * (self.y1 - self.y2)
        ) / 2
        
        template = templates.get("triangle_area_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, result=area))
        
        self.final_answer = str(area)
    
    def _solve_triangle_area_sides(self, templates):
        """Площадь треугольника по формуле Герона."""
        p = (self.a + self.b + self.c) / 2
        area = math.sqrt(p * (p - self.a) * (p - self.b) * (p - self.c))
        
        template = templates.get("heron_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, p=p, result=round(area, 4)))
        
        self.final_answer = f"{area:.4f}"
    
    def _solve_distance_2d(self, templates):
        """Расстояние между точками на плоскости."""
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        distance = math.sqrt(dx ** 2 + dy ** 2)
        
        template = templates.get("distance_formula_2d", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, dx=dx, dy=dy, result=round(distance, 4)))
        
        self.final_answer = f"{distance:.4f}"
    
    def _solve_distance_3d(self, templates):
        """Расстояние между точками в пространстве."""
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        dz = self.z2 - self.z1
        distance = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
        
        template = templates.get("distance_formula_3d", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, result=round(distance, 4)))
        
        self.final_answer = f"{distance:.4f}"
    
    def _solve_circle_area(self, templates):
        """Площадь круга."""
        area = math.pi * self.r ** 2
        
        template = templates.get("circle_area_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, r=self.r, result=round(area, 4)))
        
        self.final_answer = f"{area:.4f}"
    
    def _solve_circumference(self, templates):
        """Длина окружности."""
        circumference = 2 * math.pi * self.r
        
        template = templates.get("circumference_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, r=self.r, result=round(circumference, 4)))
        
        self.final_answer = f"{circumference:.4f}"
    
    def _solve_sphere_volume(self, templates):
        """Объём шара."""
        volume = (4 / 3) * math.pi * self.r ** 3
        
        template = templates.get("sphere_volume_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, r=self.r, result=round(volume, 4)))
        
        self.final_answer = f"{volume:.4f}"
    
    def _solve_cylinder_volume(self, templates):
        """Объём цилиндра."""
        volume = math.pi * self.r ** 2 * self.h
        
        template = templates.get("cylinder_volume_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, r=self.r, h=self.h, result=round(volume, 4)))
        
        self.final_answer = f"{volume:.4f}"
    
    def _solve_cone_volume(self, templates):
        """Объём конуса."""
        volume = (1 / 3) * math.pi * self.r ** 2 * self.h
        
        template = templates.get("cone_volume_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, r=self.r, h=self.h, result=round(volume, 4)))
        
        self.final_answer = f"{volume:.4f}"
    
    def _solve_angle_between_vectors(self, templates):
        """Угол между векторами."""
        dot = self.ax * self.bx + self.ay * self.by
        mag_a = math.sqrt(self.ax ** 2 + self.ay ** 2)
        mag_b = math.sqrt(self.bx ** 2 + self.by ** 2)
        cos_val = dot / (mag_a * mag_b)
        # Ограничиваем значение для избежания ошибок округления
        cos_val = max(-1, min(1, cos_val))
        angle_rad = math.acos(cos_val)
        angle_deg = math.degrees(angle_rad)
        
        template = templates.get("angle_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(
            step=1, cos_val=round(cos_val, 4), angle=round(angle_deg, 2)
        ))
        
        self.final_answer = f"{angle_deg:.2f}°"
    
    def _solve_dot_product(self, templates):
        """Скалярное произведение."""
        dot = self.ax * self.bx + self.ay * self.by
        
        template = templates.get("dot_product_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, result=dot))
        
        self.final_answer = str(dot)
    
    def _solve_cross_product(self, templates):
        """Векторное произведение."""
        i_comp = self.ay * self.bz - self.az * self.by
        j_comp = self.az * self.bx - self.ax * self.bz
        k_comp = self.ax * self.by - self.ay * self.bx
        
        template = templates.get("cross_product_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(
            step=1, i_comp=i_comp, j_comp=j_comp, k_comp=k_comp
        ))
        
        self.final_answer = f"({i_comp}, {j_comp}, {k_comp})"
    
    def _solve_line_equation(self, templates):
        """Уравнение прямой."""
        if self.x2 - self.x1 == 0:
            # Вертикальная прямая
            self.final_answer = f"x = {self.x1}"
            step = templates.get("vertical_line", {}).get(self.language, "")
            self.solution_steps.append(step.format(x=self.x1))
        else:
            slope = (self.y2 - self.y1) / (self.x2 - self.x1)
            intercept = self.y1 - slope * self.x1
            
            template1 = templates.get("line_slope", {}).get(self.language, "")
            self.solution_steps.append(template1.format(step=1, slope=round(slope, 4)))
            
            template2 = templates.get("line_equation_result", {}).get(self.language, "")
            self.solution_steps.append(template2.format(
                step=2, slope=round(slope, 4), intercept=round(intercept, 4)
            ))
            
            self.final_answer = f"y = {slope:.4f}x + {intercept:.4f}"
    
    def _solve_midpoint(self, templates):
        """Середина отрезка."""
        mx = (self.x1 + self.x2) / 2
        my = (self.y1 + self.y2) / 2
        
        template = templates.get("midpoint_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, mx=mx, my=my))
        
        self.final_answer = f"({mx}, {my})"
    
    def get_task_type(self) -> str:
        return "geometry"
    
    @classmethod
    def generate_random_task(
        cls,
        task_type: str = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5
    ):
        """Генерирует случайную геометрическую задачу."""
        if task_type is None:
            task_type = random.choice(cls.TASK_TYPES)
        return cls(
            task_type=task_type,
            language=language,
            detail_level=detail_level,
            difficulty=difficulty
        )
