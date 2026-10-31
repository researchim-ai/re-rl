from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

# re_rl/tasks/math/planning/tower_of_hanoi_task.py

import random
from typing import Dict, Any, ClassVar, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class TowerOfHanoiTask(BaseMathTask):
    """
    Генерирует и решает задачу 'Ханойская башня'.
    
    Параметры сложности:
      - difficulty 1-2: 2-3 диска
      - difficulty 3-4: 3-4 диска
      - difficulty 5-6: 4-5 дисков
      - difficulty 7-8: 5-6 дисков
      - difficulty 9-10: 6-7 дисков
    """
    
    TASK_TYPE = "tower_of_hanoi"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"num_disks": 2},
        2: {"num_disks": 3},
        3: {"num_disks": 3},
        4: {"num_disks": 4},
        5: {"num_disks": 4},
        6: {"num_disks": 5},
        7: {"num_disks": 5},
        8: {"num_disks": 6},
        9: {"num_disks": 6},
        10: {"num_disks": 7},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        num_disks: int = None,
        source: str = "A",
        target: str = "C",
        auxiliary: str = "B",
        difficulty: int = None,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False
    ):
        """
        :param language: 'ru' или 'en'
        :param detail_level: количество шагов chain-of-thought
        :param num_disks: количество дисков (2-10)
        :param source: начальный стержень
        :param target: целевой стержень
        :param auxiliary: вспомогательный стержень
        :param difficulty: уровень сложности (1-10)
        :param output_format: формат вывода
        """
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            if num_disks is None:
                num_disks = preset.get("num_disks", 3)
        else:
            num_disks = 3 if num_disks is None else num_disks
        
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        
        if type(num_disks) is not int or not 0 <= num_disks <= 12:
            raise ValueError('invalid_disks')
        if any(not isinstance(p,str) or not p.strip() or '\n' in p for p in (source,target,auxiliary)) or len({source,target,auxiliary}) != 3:
            raise ValueError('invalid_pegs')
        self.num_disks = num_disks
        self.source = source
        self.target = target
        self.auxiliary = auxiliary
        
        # Решаем задачу
        self.moves = []
        self._solve_hanoi(num_disks, source, target, auxiliary)
        
        # Формируем текст задачи
        problem_text = self._create_problem_text()
        
        super().__init__(problem_text, language=self.language, detail_level=detail_level, output_format=output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_text(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES[texts.t('s1', self.language)]
        
        problem_text = templates["instructions"][self.language] + "\n\n"
        problem_text += templates["problem"][self.language].format(
            n=self.num_disks,
            source=self.source,
            target=self.target,
            auxiliary=self.auxiliary
        )
        
        return problem_text

    def _solve_hanoi(self, n: int, source: str, target: str, auxiliary: str):
        """Рекурсивно решает Ханойскую башню."""
        if n == 0:
            return
        
        # Перемещаем n-1 дисков с source на auxiliary
        self._solve_hanoi(n - 1, source, auxiliary, target)
        
        # Перемещаем самый большой диск с source на target
        self.moves.append((n, source, target))
        
        # Перемещаем n-1 дисков с auxiliary на target
        self._solve_hanoi(n - 1, auxiliary, target, source)

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        """Генерирует пошаговое решение."""
        templates = PROMPT_TEMPLATES[texts.t('s2', self.language)]
        steps = []
        
        # Объясняем рекурсивный подход
        if self.detail_level >= 1:
            step = templates["steps"]["recursive_explain"][self.language].format(
                n=self.num_disks,
                from_peg=self.source,
                to_peg=self.target,
                aux_peg=self.auxiliary
            )
            steps.append(step)
        
        # Показываем ходы
        moves_text = []
        for i, (disk, from_peg, to_peg) in enumerate(self.moves):
            move = templates["steps"]["move"][self.language].format(
                n=i + 1,
                disk=disk,
                from_peg=from_peg,
                to_peg=to_peg
            )
            moves_text.append(move)
            steps.append(move)
        
        self.solution_steps = steps
        
        optimal = 2 ** self.num_disks - 1
        self.final_answer = templates["final_answer"][self.language].format(
            n=len(self.moves),
            disks=self.num_disks,
            optimal=optimal,
            moves="\n".join(moves_text)
        )

    def verify(self, prediction):
        from re_rl.tasks.math.planning.plan_verification import hanoi_verify
        return hanoi_verify(self,prediction)

    def get_task_type(self):
        return texts.t('s0', self.language)
