# re_rl/tasks/math/planning/river_crossing_task.py

import random
from typing import Dict, Any, ClassVar, List, Tuple, Set, Optional
from collections import deque

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class RiverCrossingTask(BaseMathTask):
    """
    Генерирует и решает задачи о переправе через реку.
    
    Типы задач:
      - classic: волк, коза, капуста
      - missionaries: миссионеры и каннибалы
      - jealous_husbands: ревнивые мужья
    
    Параметры сложности:
      - difficulty 1-3: классическая задача (волк, коза, капуста)
      - difficulty 4-6: миссионеры и каннибалы (3+3)
      - difficulty 7-8: миссионеры и каннибалы (4+4)
      - difficulty 9-10: ревнивые мужья или большие числа
    """
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"problem_type": "classic"},
        2: {"problem_type": "classic"},
        3: {"problem_type": "classic"},
        4: {"problem_type": "missionaries", "missionaries": 3, "cannibals": 3, "capacity": 2},
        5: {"problem_type": "missionaries", "missionaries": 3, "cannibals": 3, "capacity": 2},
        6: {"problem_type": "missionaries", "missionaries": 3, "cannibals": 3, "capacity": 2},
        7: {"problem_type": "missionaries", "missionaries": 4, "cannibals": 4, "capacity": 2},
        8: {"problem_type": "missionaries", "missionaries": 4, "cannibals": 4, "capacity": 3},
        9: {"problem_type": "jealous_husbands", "num_couples": 3, "capacity": 2},
        10: {"problem_type": "jealous_husbands", "num_couples": 4, "capacity": 3},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        problem_type: str = None,
        missionaries: int = 3,
        cannibals: int = 3,
        num_couples: int = 3,
        capacity: int = 2,
        difficulty: int = None,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False
    ):
        """
        :param language: 'ru' или 'en'
        :param detail_level: количество шагов chain-of-thought
        :param problem_type: тип задачи ('classic', 'missionaries', 'jealous_husbands')
        :param missionaries: количество миссионеров
        :param cannibals: количество каннибалов
        :param num_couples: количество пар (для jealous_husbands)
        :param capacity: вместимость лодки
        :param difficulty: уровень сложности (1-10)
        :param output_format: формат вывода
        """
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            if problem_type is None:
                problem_type = preset.get("problem_type", "classic")
            missionaries = preset.get("missionaries", missionaries)
            cannibals = preset.get("cannibals", cannibals)
            num_couples = preset.get("num_couples", num_couples)
            capacity = preset.get("capacity", capacity)
        else:
            problem_type = problem_type or "classic"
        
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        
        self.problem_type = problem_type
        self.missionaries = missionaries
        self.cannibals = cannibals
        self.num_couples = num_couples
        self.capacity = capacity
        
        # Решаем задачу
        self.solution_path = self._solve()
        
        # Формируем текст задачи
        problem_text = self._create_problem_text()
        
        super().__init__(problem_text, language=self.language, detail_level=detail_level, output_format=output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_text(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES["river_crossing"]
        
        problem_text = templates["instructions"][self.language] + "\n\n"
        
        if self.problem_type == "classic":
            problem_text += templates["problem"]["classic"][self.language]
        elif self.problem_type == "missionaries":
            problem_text += templates["problem"]["missionaries"][self.language].format(
                missionaries=self.missionaries,
                cannibals=self.cannibals,
                capacity=self.capacity
            )
        elif self.problem_type == "jealous_husbands":
            problem_text += templates["problem"]["jealous_husbands"][self.language].format(
                n=self.num_couples,
                capacity=self.capacity
            )
        
        return problem_text

    def _solve(self) -> List[Tuple]:
        """Решает задачу методом BFS."""
        if self.problem_type == "classic":
            return self._solve_classic()
        elif self.problem_type == "missionaries":
            return self._solve_missionaries()
        else:
            return self._solve_missionaries()  # Упрощённо используем тот же алгоритм

    def _solve_classic(self) -> List[Tuple]:
        """Решает классическую задачу (волк, коза, капуста)."""
        # Состояние: (farmer_side, wolf_side, goat_side, cabbage_side)
        # 0 = левый берег, 1 = правый берег
        initial = (0, 0, 0, 0)  # Все на левом
        goal = (1, 1, 1, 1)     # Все на правом
        
        def is_safe(state: Tuple[int, int, int, int]) -> bool:
            farmer, wolf, goat, cabbage = state
            # Волк и коза без фермера
            if wolf == goat and wolf != farmer:
                return False
            # Коза и капуста без фермера
            if goat == cabbage and goat != farmer:
                return False
            return True
        
        def get_neighbors(state: Tuple[int, int, int, int]) -> List[Tuple]:
            farmer, wolf, goat, cabbage = state
            new_side = 1 - farmer
            neighbors = []
            
            # Фермер едет один
            new_state = (new_side, wolf, goat, cabbage)
            if is_safe(new_state):
                neighbors.append((new_state, "farmer"))
            
            # Фермер берёт волка
            if wolf == farmer:
                new_state = (new_side, new_side, goat, cabbage)
                if is_safe(new_state):
                    neighbors.append((new_state, "wolf"))
            
            # Фермер берёт козу
            if goat == farmer:
                new_state = (new_side, wolf, new_side, cabbage)
                if is_safe(new_state):
                    neighbors.append((new_state, "goat"))
            
            # Фермер берёт капусту
            if cabbage == farmer:
                new_state = (new_side, wolf, goat, new_side)
                if is_safe(new_state):
                    neighbors.append((new_state, "cabbage"))
            
            return neighbors
        
        # BFS
        queue = deque([(initial, [(initial, None)])])
        visited = {initial}
        
        while queue:
            current, path = queue.popleft()
            
            if current == goal:
                return path
            
            for new_state, item in get_neighbors(current):
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, path + [(new_state, item)]))
        
        return []

    def _solve_missionaries(self) -> List[Tuple]:
        """Решает задачу миссионеров и каннибалов."""
        # Состояние: (missionaries_left, cannibals_left, boat_side)
        # boat_side: 0 = левый, 1 = правый
        initial = (self.missionaries, self.cannibals, 0)
        goal = (0, 0, 1)
        
        def is_safe(state: Tuple[int, int, int]) -> bool:
            m_left, c_left, _ = state
            m_right = self.missionaries - m_left
            c_right = self.cannibals - c_left
            
            # На левом берегу
            if m_left > 0 and c_left > m_left:
                return False
            # На правом берегу
            if m_right > 0 and c_right > m_right:
                return False
            # Проверка границ
            if m_left < 0 or c_left < 0 or m_left > self.missionaries or c_left > self.cannibals:
                return False
            
            return True
        
        def get_neighbors(state: Tuple[int, int, int]) -> List[Tuple]:
            m_left, c_left, boat = state
            neighbors = []
            direction = -1 if boat == 0 else 1
            
            # Все возможные комбинации перевозки
            for m in range(self.capacity + 1):
                for c in range(self.capacity + 1 - m):
                    if m + c == 0 or m + c > self.capacity:
                        continue
                    
                    new_m = m_left - direction * m
                    new_c = c_left - direction * c
                    new_boat = 1 - boat
                    new_state = (new_m, new_c, new_boat)
                    
                    # Проверяем, есть ли достаточно людей на берегу
                    if boat == 0:  # Едем с левого
                        if m > m_left or c > c_left:
                            continue
                    else:  # Едем с правого
                        if m > self.missionaries - m_left or c > self.cannibals - c_left:
                            continue
                    
                    if is_safe(new_state):
                        neighbors.append((new_state, (m, c)))
            
            return neighbors
        
        # BFS
        queue = deque([(initial, [(initial, None)])])
        visited = {initial}
        
        while queue:
            current, path = queue.popleft()
            
            if current == goal:
                return path
            
            for new_state, move in get_neighbors(current):
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, path + [(new_state, move)]))
        
        return []

    def solve(self):
        """Генерирует пошаговое решение."""
        templates = PROMPT_TEMPLATES["river_crossing"]
        steps = []
        
        if not self.solution_path:
            self.solution_steps = [templates["problem"]["classic"][self.language]]
            self.final_answer = PROMPT_TEMPLATES["default"]["no_solution"][self.language]
            return
        
        # Начальное состояние
        initial_state = self.solution_path[0][0]
        left, right = self._format_state(initial_state)
        boat_side = templates["directions"]["left"][self.language]
        
        step = templates["steps"]["initial_state"][self.language].format(
            left=left, right=right, boat_side=boat_side
        )
        steps.append(step)
        
        # Переправы
        crossings = []
        for i in range(1, len(self.solution_path)):
            state, move = self.solution_path[i]
            prev_state = self.solution_path[i - 1][0]
            
            # Определяем направление
            if self.problem_type == "classic":
                direction = "right" if prev_state[0] == 0 else "left"
                items = self._get_item_name(move)
            else:
                boat_prev = prev_state[2]
                direction = "right" if boat_prev == 0 else "left"
                items = self._format_move(move)
            
            dir_text = templates["directions"][direction][self.language]
            
            crossing = templates["steps"]["crossing"][self.language].format(
                n=i, items=items, direction=dir_text
            )
            crossings.append(crossing)
            steps.append(crossing)
                
            # Состояние после переправы
            left, right = self._format_state(state)
            state_step = templates["steps"]["state_after"][self.language].format(
                left=left, right=right
            )
            steps.append(state_step)
        
        self.solution_steps = steps
        self.final_answer = templates["final_answer"][self.language].format(
            n=len(self.solution_path) - 1,
            crossings="\n".join(crossings)
        )

    def _format_state(self, state: Tuple) -> Tuple[str, str]:
        """Форматирует состояние для отображения."""
        templates = PROMPT_TEMPLATES["river_crossing"]["items"]
        
        if self.problem_type == "classic":
            farmer, wolf, goat, cabbage = state
            left_items = []
            right_items = []
            
            for item, side in [("farmer", farmer), ("wolf", wolf), ("goat", goat), ("cabbage", cabbage)]:
                name = templates[item][self.language]
                if side == 0:
                    left_items.append(name)
                else:
                    right_items.append(name)
            
            return ", ".join(left_items) or "-", ", ".join(right_items) or "-"
        else:
            m_left, c_left, _ = state
            m_right = self.missionaries - m_left
            c_right = self.cannibals - c_left
            
            m_name = templates["missionary"][self.language]
            c_name = templates["cannibal"][self.language]
            
            left = f"{m_left} {m_name}, {c_left} {c_name}"
            right = f"{m_right} {m_name}, {c_right} {c_name}"
            
            return left, right

    def _get_item_name(self, item: str) -> str:
        """Получает название предмета на нужном языке."""
        if item is None:
            item = "farmer"
        templates = PROMPT_TEMPLATES["river_crossing"]["items"]
        return templates.get(item, {}).get(self.language, item)

    def _format_move(self, move: Tuple[int, int]) -> str:
        """Форматирует ход для миссионеров."""
        if move is None:
            return "-"
        m, c = move
        templates = PROMPT_TEMPLATES["river_crossing"]["items"]
        m_name = templates["missionary"][self.language]
        c_name = templates["cannibal"][self.language]
        
        parts = []
        if m > 0:
            parts.append(f"{m} {m_name}")
        if c > 0:
            parts.append(f"{c} {c_name}")
        
        return ", ".join(parts) if parts else "-"

    def get_task_type(self):
        return "river_crossing"
