# re_rl/tasks/math/discrete/nim_game_task.py

import random
from typing import Dict, Any, ClassVar, List, Tuple, Optional
from functools import reduce
from operator import xor

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class NimGameTask(BaseMathTask):
    """
    Генерирует и анализирует позиции в игре Ним.
    
    Правила игры Ним:
    - Два игрока по очереди берут предметы из кучек
    - За один ход можно взять любое количество предметов из одной кучки
    - Проигрывает тот, кто берёт последний предмет (нормальная игра)
    
    Параметры сложности:
      - difficulty 1-2: 2 кучки, маленькие числа (1-5)
      - difficulty 3-4: 3 кучки, числа до 7
      - difficulty 5-6: 3-4 кучки, числа до 10
      - difficulty 7-8: 4 кучки, числа до 15
      - difficulty 9-10: 5+ кучек, большие числа
    """
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"num_piles": 2, "max_size": 3},
        2: {"num_piles": 2, "max_size": 5},
        3: {"num_piles": 3, "max_size": 5},
        4: {"num_piles": 3, "max_size": 7},
        5: {"num_piles": 3, "max_size": 10},
        6: {"num_piles": 4, "max_size": 10},
        7: {"num_piles": 4, "max_size": 15},
        8: {"num_piles": 4, "max_size": 15},
        9: {"num_piles": 5, "max_size": 20},
        10: {"num_piles": 5, "max_size": 25},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        piles: List[int] = None,
        num_piles: int = None,
        max_size: int = None,
        task_type: str = "find_winner",
        difficulty: int = None,
        output_format: OutputFormat = "text"
    ):
        """
        :param language: 'ru' или 'en'
        :param detail_level: количество шагов chain-of-thought
        :param piles: список размеров кучек (если None - генерируется)
        :param num_piles: количество кучек (используется при генерации)
        :param max_size: максимальный размер кучки (используется при генерации)
        :param task_type: тип задачи ('find_winner' или 'find_move')
        :param difficulty: уровень сложности (1-10)
        :param output_format: формат вывода
        """
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            if num_piles is None:
                num_piles = preset.get("num_piles", 3)
            if max_size is None:
                max_size = preset.get("max_size", 10)
        else:
            num_piles = num_piles or 3
            max_size = max_size or 10
        
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self.task_type = task_type
        
        # Генерируем или используем переданные кучки
        if piles is not None:
            self.piles = list(piles)
        else:
            self.piles = self._generate_piles(num_piles, max_size)
        
        # Вычисляем ним-сумму
        self.nim_sum = self._compute_nim_sum(self.piles)
        
        # Определяем выигрышный ход (если есть)
        self.winning_move = self._find_winning_move() if self.nim_sum != 0 else None
        
        # Формируем текст задачи
        problem_text = self._create_problem_text()
        
        super().__init__(problem_text, language=self.language, detail_level=detail_level, output_format=output_format)

    def _generate_piles(self, num_piles: int, max_size: int) -> List[int]:
        """Генерирует случайные кучки."""
        return [random.randint(1, max_size) for _ in range(num_piles)]

    def _compute_nim_sum(self, piles: List[int]) -> int:
        """Вычисляет ним-сумму (XOR всех кучек)."""
        return reduce(xor, piles, 0)

    def _find_winning_move(self) -> Optional[Tuple[int, int, int]]:
        """
        Находит выигрышный ход.
        
        Returns:
            (pile_index, take_amount, new_size) или None
        """
        if self.nim_sum == 0:
            return None
        
        for i, pile in enumerate(self.piles):
            # Новый размер кучки должен быть pile XOR nim_sum
            new_size = pile ^ self.nim_sum
            if new_size < pile:
                take = pile - new_size
                return (i, take, new_size)
        
        return None

    def _create_problem_text(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES["nim_game"]
        
        piles_str = ", ".join(str(p) for p in self.piles)
        
        problem_text = templates["instructions"][self.language] + "\n\n"
        
        if self.task_type == "find_winner":
            problem_text += templates["problem"]["find_winner"][self.language].format(
                piles=piles_str
            )
        else:
            problem_text += templates["problem"]["find_move"][self.language].format(
                piles=piles_str
            )
        
        return problem_text

    def solve(self):
        """Генерирует пошаговое решение."""
        templates = PROMPT_TEMPLATES["nim_game"]
        steps = []
        
        # Шаг 1: Вычисляем XOR
        xor_parts = " ⊕ ".join(str(p) for p in self.piles)
        xor_computation = f"{xor_parts}"
        
        step1 = templates["steps"]["compute_xor"][self.language].format(
            xor_computation=xor_computation,
            xor_result=self.nim_sum
        )
        steps.append(step1)
        
        # Шаг 2: Анализируем результат
        if self.nim_sum == 0:
            step2 = templates["steps"]["xor_zero"][self.language]
            steps.append(step2)
        else:
            step2 = templates["steps"]["xor_nonzero"][self.language].format(
                xor_result=self.nim_sum
            )
            steps.append(step2)
            
            # Шаг 3: Ищем выигрышный ход
            if len(steps) < self.detail_level:
                step3 = templates["steps"]["find_winning_move"][self.language]
                steps.append(step3)
            
            # Шаг 4: Показываем выигрышный ход
            if self.winning_move and len(steps) < self.detail_level:
                pile_idx, take, new_size = self.winning_move
                step4 = templates["steps"]["winning_move"][self.language].format(
                    pile=pile_idx + 1,
                    take=take,
                    before=self.piles[pile_idx],
                    after=new_size
                )
                steps.append(step4)
        
        # Дополняем шаги при необходимости
        while len(steps) < self.detail_level:
            steps.append(steps[-1])
        
        self.solution_steps = steps
        
        # Формируем финальный ответ
        if self.nim_sum == 0:
            self.final_answer = templates["final_answer"]["losing"][self.language]
        else:
            pile_idx, take, new_size = self.winning_move
            new_piles = self.piles.copy()
            new_piles[pile_idx] = new_size
            new_piles_str = ", ".join(str(p) for p in new_piles)
            
            self.final_answer = templates["final_answer"]["winning"][self.language].format(
                pile=pile_idx + 1,
                take=take,
                new_piles=new_piles_str
            )

    def get_task_type(self):
        return "nim_game"
