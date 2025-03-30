import random
from re_rl.tasks.base_task import BaseTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES

# Подключаем Z3
from z3 import Solver, Int, And, Distinct, sat

class FutoshikiTask(BaseTask):
    """
    Задача Futoshiki (неравенства) на N×N поле, 
    решается с помощью Z3. 
    """

    def __init__(self, language="ru", detail_level=5, size=None, num_inequalities=None):
        """
        :param language: 'ru' или 'en'
        :param detail_level: сколько шагов (chain-of-thought) выводить
        :param size: размер поля (None -> случайно 4..5, например)
        :param num_inequalities: сколько неравенств генерировать (None -> случайно)
        """
        self.language = language.lower()
        self.detail_level = detail_level
        
        if size is None:
            size = random.randint(4, 5)  # для примера возьмём 4 или 5
        self.size = size
        
        if num_inequalities is None:
            num_inequalities = random.randint(size, size*2)  # кол-во неравенств
        
        self.inequalities = self._generate_random_inequalities(num_inequalities)
        
        # Теперь решаем паззл через Z3
        self.solution = self._solve_with_z3()
        
        # Формируем текст постановки задачи
        problem_template = PROMPT_TEMPLATES["futoshiki"]["problem"][self.language]
        # Представим неравенства в читабельном виде
        ineq_str = ""
        for (r1,c1, r2,c2) in self.inequalities:
            ineq_str += f"({r1},{c1}) < ({r2},{c2})\n"
        
        problem_text = problem_template.format(
            size=self.size,
            inequalities=ineq_str
        )
        
        super().__init__(problem_text)

    def _generate_random_inequalities(self, num_ineq):
        """
        Генерируем список случайных неравенств вида (r1,c1) < (r2,c2).
        Для Futoshiki обычно (r2,c2) — клетка, смежная с (r1,c1) 
        (по вертикали или горизонтали). 
        Но для простоты можно делать и не только смежные.
        """
        ineqs = set()
        while len(ineqs) < num_ineq:
            r1 = random.randint(0, self.size-1)
            c1 = random.randint(0, self.size-1)
            r2 = random.randint(0, self.size-1)
            c2 = random.randint(0, self.size-1)
            # Добавим условие, чтобы (r1,c1) != (r2,c2) 
            # и не повторять зеркально
            if (r1,c1) != (r2,c2) and (r2,c2, r1,c1) not in ineqs:
                # (r1,c1) < (r2,c2)
                ineqs.add((r1,c1, r2,c2))
        return list(ineqs)

    def get_task_type(self):
        
        return "futoshiki"


    def _solve_with_z3(self):
        """
        Строим модель Z3:
          - Определяем переменные cell[r][c] (Int)
          - Добавляем ограничения: 1 <= cell[r][c] <= size
          - distinct по каждой строке и столбцу
          - неравенства
        Возвращаем решение в виде двумерного массива (size×size).
        Если unsat, вернём None (или бросим исключение).
        """
        s = Solver()
        
        # Создадим матрицу Z3-переменных: cell[r][c]
        self.cells = [
            [Int(f"cell_{r}_{c}") for c in range(self.size)]
            for r in range(self.size)
        ]
        
        # Базовые ограничения: 1 <= cell[r][c] <= size
        for r in range(self.size):
            for c in range(self.size):
                s.add(self.cells[r][c] >= 1, self.cells[r][c] <= self.size)
        
        # Уникальность в каждой строке
        for r in range(self.size):
            s.add(Distinct(*self.cells[r]))
        
        # Уникальность в каждом столбце
        for c in range(self.size):
            col_vars = [self.cells[r][c] for r in range(self.size)]
            s.add(Distinct(*col_vars))
        
        # Неравенства
        for (r1,c1, r2,c2) in self.inequalities:
            s.add(self.cells[r1][c1] < self.cells[r2][c2])
        
        # Попытаемся найти решение
        result = s.check()
        if result != sat:
            # Нет решения (или не единственное). 
            # Для примера: пусть возвращает None
            return None
        
        m = s.model()
        # Формируем итоговую матрицу
        solution_matrix = [[0]*self.size for _ in range(self.size)]
        for r in range(self.size):
            for c in range(self.size):
                solution_matrix[r][c] = m[self.cells[r][c]].as_long()
        return solution_matrix

    def solve(self):
        """
        Генерируем цепочку рассуждений (solution_steps). 
        Псевдо: берём несколько шаблонов step_explanations.
        """
        steps_templates = PROMPT_TEMPLATES["futoshiki"]["step_explanations"][self.language]
        
        max_steps = min(self.detail_level, len(steps_templates))
        self.solution_steps = []
        
        for i in range(max_steps):
            tpl = steps_templates[i]
            row = random.randint(0, self.size-1)
            col = random.randint(0, self.size-1)
            # Для неравенств
            if self.inequalities:
                inq = random.choice(self.inequalities)
                r1, c1, r2, c2 = inq
            else:
                r1, c1, r2, c2 = 0,0,1,1
            step_str = tpl.format(row=row, col=col, r1=r1, c1=c1, r2=r2, c2=c2)
            self.solution_steps.append(step_str)
        
        # Формируем final_answer
        if self.solution is None:
            # unsat
            self.final_answer = "No solution found" if self.language == "en" else "Нет решения"
        else:
            final_templ = PROMPT_TEMPLATES["futoshiki"]["final_answer"][self.language]
            grid_repr = self._format_solution()
            self.final_answer = final_templ.format(grid_repr=grid_repr)

    def _format_solution(self):
        if self.solution is None:
            return ""
        lines = []
        for r in range(self.size):
            line = " ".join(str(self.solution[r][c]) for c in range(self.size))
            lines.append(line)
        return "\n".join(lines)

    def get_result(self):
        if not self.solution_steps or self.final_answer is None:
            self.solve()
        return {
            "problem": self.description,
            "prompt": self.generate_prompt(),
            "solution_steps": self.solution_steps,
            "final_answer": self.final_answer
        }
