# re_rl/tasks/math/planning/water_jug_task.py

import random
from math import gcd
from typing import Dict, Any, ClassVar, List, Tuple, Optional
from collections import deque

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class WaterJugTask(BaseMathTask):
    """
    Генерирует и решает задачу о кувшинах с водой.
    
    Параметры сложности:
      - difficulty 1-2: 2 кувшина, маленькие объёмы (3, 5)
      - difficulty 3-4: 2 кувшина, средние объёмы
      - difficulty 5-6: 2 кувшина, большие объёмы
      - difficulty 7-8: 3 кувшина
      - difficulty 9-10: 3 кувшина, сложные цели
    """
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"capacities": (3, 5), "target": 4},
        2: {"capacities": (3, 5), "target": 1},
        3: {"capacities": (4, 7), "target": 5},
        4: {"capacities": (5, 8), "target": 3},
        5: {"capacities": (7, 11), "target": 6},
        6: {"capacities": (8, 13), "target": 5},
        7: {"capacities": (3, 5, 8), "target": 4},
        8: {"capacities": (4, 7, 10), "target": 3},
        9: {"capacities": (5, 8, 13), "target": 7},
        10: {"capacities": (7, 11, 17), "target": 9},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        capacities: Tuple[int, ...] = None,
        target: int = None,
        difficulty: int = None,
        output_format: OutputFormat = "text"
    ):
        """
        :param language: 'ru' или 'en'
        :param detail_level: количество шагов chain-of-thought
        :param capacities: объёмы кувшинов
        :param target: целевое количество воды
        :param difficulty: уровень сложности (1-10)
        :param output_format: формат вывода
        """
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            if capacities is None:
                capacities = preset.get("capacities", (3, 5))
            if target is None:
                target = preset.get("target", 4)
        else:
            capacities = capacities or (3, 5)
            target = target or 4
        
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        
        self.capacities = capacities
        self.target = target
        self.num_jugs = len(capacities)
        
        # Проверяем разрешимость и решаем
        self.is_solvable = self._check_solvable()
        self.solution_path = self._solve() if self.is_solvable else []
        
        # Формируем текст задачи
        problem_text = self._create_problem_text()
        
        super().__init__(problem_text, language=self.language, detail_level=detail_level, output_format=output_format)

    def _create_problem_text(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES["water_jug"]
        
        capacities_str = ", ".join(str(c) for c in self.capacities)
        
        problem_text = templates["instructions"][self.language] + "\n\n"
        problem_text += templates["problem"][self.language].format(
            capacities=capacities_str,
            target=self.target
        )
        
        return problem_text

    def _check_solvable(self) -> bool:
        """Проверяет, разрешима ли задача."""
        # Для двух кувшинов: target должен делиться на НОД объёмов
        # и быть <= максимального объёма
        if max(self.capacities) < self.target:
            return False
        
        if len(self.capacities) == 2:
            g = gcd(self.capacities[0], self.capacities[1])
            return self.target % g == 0
        else:
            # Для трёх+ кувшинов - более сложная проверка
            # Упрощённо: НОД всех объёмов
            g = self.capacities[0]
            for c in self.capacities[1:]:
                g = gcd(g, c)
            return self.target % g == 0

    def _solve(self) -> List[Tuple]:
        """Решает задачу методом BFS."""
        # Состояние: кортеж с уровнями воды в кувшинах
        initial = tuple(0 for _ in self.capacities)
        
        def is_goal(state: Tuple[int, ...]) -> bool:
            return self.target in state
        
        def get_neighbors(state: Tuple[int, ...]): 
            neighbors = []
            
            for i in range(self.num_jugs):
                # Наполнить кувшин i
                if state[i] < self.capacities[i]:
                    new_state = list(state)
                    new_state[i] = self.capacities[i]
                    action = ("fill", i)
                    neighbors.append((tuple(new_state), action))
                
                # Опустошить кувшин i
                if state[i] > 0:
                    new_state = list(state)
                    new_state[i] = 0
                    action = ("empty", i)
                    neighbors.append((tuple(new_state), action))
                
                # Перелить из i в j
                for j in range(self.num_jugs):
                    if i != j and state[i] > 0 and state[j] < self.capacities[j]:
                        # Сколько можно перелить
                        amount = min(state[i], self.capacities[j] - state[j])
                        new_state = list(state)
                        new_state[i] -= amount
                        new_state[j] += amount
                        action = ("pour", i, j)
                        neighbors.append((tuple(new_state), action))
            
            return neighbors
        
        # BFS
        queue = deque([(initial, [(initial, None)])])
        visited = {initial}
        
        while queue:
            current, path = queue.popleft()
            
            if is_goal(current):
                return path
            
            for new_state, action in get_neighbors(current):
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, path + [(new_state, action)]))
        
        return []

    def solve(self):
        """Генерирует пошаговое решение."""
        templates = PROMPT_TEMPLATES["water_jug"]
        steps = []
        
        if not self.is_solvable or not self.solution_path:
            self.solution_steps = [templates["no_solution"][self.language].format(
                target=self.target,
                capacities=", ".join(str(c) for c in self.capacities)
            )]
            self.final_answer = templates["no_solution"][self.language].format(
                target=self.target,
                capacities=", ".join(str(c) for c in self.capacities)
            )
            return
        
        # Подсказка про НОД (для двух кувшинов)
        if len(self.capacities) == 2 and self.detail_level >= 1:
            g = gcd(self.capacities[0], self.capacities[1])
            hint = templates["steps"]["gcd_hint"][self.language].format(
                a=self.capacities[0],
                b=self.capacities[1],
                gcd=g,
                target=self.target
            )
            steps.append(hint)
        
        # Показываем действия
        actions_text = []
        for i in range(1, len(self.solution_path)):
            state, action = self.solution_path[i]
            
            action_text = self._format_action(action)
            state_text = self._format_state(state)
            
            step = templates["steps"]["action"][self.language].format(
                n=i,
                action=action_text,
                state=state_text
            )
            actions_text.append(step)
            
            if len(steps) < self.detail_level:
                steps.append(step)
        
        # Дополняем шаги
        while len(steps) < self.detail_level:
            if actions_text:
                steps.append(actions_text[len(steps) % len(actions_text)])
            else:
                break
        
        self.solution_steps = steps
        
        # Находим кувшин с целевым количеством
        final_state = self.solution_path[-1][0]
        target_jug = final_state.index(self.target) + 1
        
        self.final_answer = templates["final_answer"][self.language].format(
            n=len(self.solution_path) - 1,
            actions="\n".join(actions_text),
            jug=target_jug,
            target=self.target
        )

    def _format_action(self, action: Optional[Tuple]) -> str:
        """Форматирует действие."""
        if action is None:
            return "-"
        
        templates = PROMPT_TEMPLATES["water_jug"]["operations"]
        
        if action[0] == "fill":
            jug = action[1] + 1
            return templates["fill"][self.language].format(
                jug=jug,
                capacity=self.capacities[action[1]]
            )
        elif action[0] == "empty":
            jug = action[1] + 1
            return templates["empty"][self.language].format(jug=jug)
        elif action[0] == "pour":
            from_jug = action[1] + 1
            to_jug = action[2] + 1
            return templates["pour"][self.language].format(
                from_jug=from_jug,
                to_jug=to_jug
            )
        
        return str(action)

    def _format_state(self, state: Tuple[int, ...]) -> str:
        """Форматирует состояние."""
        parts = [f"J{i + 1}={v}л" if self.language == "ru" else f"J{i + 1}={v}L" 
                 for i, v in enumerate(state)]
        return ", ".join(parts)

    def get_task_type(self):
        return "water_jug"
