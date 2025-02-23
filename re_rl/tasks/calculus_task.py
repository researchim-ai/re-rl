import random
import sympy as sp

class CalculusTask:
    """
    Класс для генерации и решения задач по анализу:
      - "differentiation": найти производную от случайной полиномиальной функции.
      - "integration": найти неопределённый интеграл от случайной полиномиальной функции.
    """

    def __init__(self, task_type="differentiation", degree=2):
        self.task_type = task_type.lower()
        self.degree = degree
        self.function = None
        self.problem = ""
        self.solution_steps = []
        self.final_answer = None

    def generate_function(self):
        """
        Генерирует случайный полином вида:
            a_n*x^n + a_(n-1)*x^(n-1) + ... + a_0,
        где степень полинома равна self.degree, а коэффициенты случайны из диапазона [-5, 5].
        """
        x = sp.symbols('x')
        # Генерируем коэффициенты
        coeffs = [random.randint(-5, 5) for _ in range(self.degree + 1)]
        # Убедимся, что старший коэффициент не равен 0
        while coeffs[-1] == 0:
            coeffs[-1] = random.randint(-5, 5)
        poly = sum(coeffs[i] * x**i for i in range(self.degree + 1))
        self.function = sp.simplify(poly)

    def create_problem_description(self):
        """
        Формирует текст постановки задачи на основе типа (дифференцирование или интегрирование)
        и сгенерированной функции.
        """
        self.generate_function()
        if self.task_type == "differentiation":
            self.problem = f"Найди производную функции f(x) = {sp.pretty(self.function)}."
        elif self.task_type == "integration":
            self.problem = f"Найди неопределённый интеграл функции f(x) = {sp.pretty(self.function)}."
        else:
            self.problem = "Неизвестный тип задачи."

    def solve(self):
        """
        Решает задачу пошагово.
        Для дифференцирования:
          1. Записывается исходная функция.
          2. Вычисляется производная.
        Для интегрирования:
          1. Записывается исходная функция.
          2. Вычисляется неопределённый интеграл (с константой интегрирования).
        """
        x = sp.symbols('x')
        self.create_problem_description()
        if self.task_type == "differentiation":
            self.solution_steps.append(f"Шаг 1: Запишем функцию: f(x) = {sp.pretty(self.function)}.")
            derivative = sp.diff(self.function, x)
            self.solution_steps.append(f"Шаг 2: Вычисляем производную: f'(x) = {sp.pretty(derivative)}.")
            self.final_answer = sp.pretty(derivative)
        elif self.task_type == "integration":
            self.solution_steps.append(f"Шаг 1: Запишем функцию: f(x) = {sp.pretty(self.function)}.")
            integral = sp.integrate(self.function, x)
            self.solution_steps.append(f"Шаг 2: Вычисляем неопределённый интеграл: ∫f(x)dx = {sp.pretty(integral)} + C.")
            self.final_answer = sp.pretty(integral) + " + C"
        else:
            self.solution_steps.append("Неизвестный тип задачи.")
            self.final_answer = "Нет решения"

    def generate_prompt(self):
        """
        Формирует промт с постановкой задачи.
        """
        return f"Задача: {self.problem}\n Пожалуйста, решите задачу пошагово."

    def get_result(self):
        """
        Возвращает словарь с информацией:
          - постановка задачи,
          - промт,
          - пошаговое решение,
          - итоговый ответ.
        Если задача ещё не решена, вызывается метод solve().
        """
        if not self.solution_steps or self.final_answer is None:
            self.solve()
        return {
            "problem": self.problem,
            "prompt": self.generate_prompt(),
            "solution_steps": self.solution_steps,
            "final_answer": self.final_answer
        }

    @classmethod
    def generate_random_task(cls, task_type="differentiation", degree=None):
        """
        Генерирует случайную задачу.
        Если степень не задана, выбирается случайная степень от 1 до 3.
        task_type может быть "differentiation" или "integration".
        """
        if degree is None:
            degree = random.randint(1, 3)
        task = cls(task_type=task_type, degree=degree)
        task.solve()
        return task
