import random
import sympy as sp

class MathTask:
    """
    Класс для решения различных математических уравнений.
    
    Поддерживаемые типы уравнений:
      - "linear": линейное уравнение вида a*x + b = c
      - "quadratic": квадратное уравнение вида a*x² + b*x + c = 0
      - "cubic": кубическое уравнение вида a*x³ + b*x² + c*x + d = 0
      - "exponential": экспоненциальное уравнение вида a*exp(b*x) + c = d
      - "logarithmic": логарифмическое уравнение вида a*log(b*x) + c = d
      
    Метод generate_random_task() генерирует случайное уравнение из списка.
    """
    def __init__(self, equation_type: str, *coeffs: float):
        self.equation_type = equation_type.lower()
        self.coeffs = coeffs  # набор коэффициентов (количество зависит от типа)
        self.solution_steps = []
        self.final_answer = None
        self.problem = self._create_problem_description()

    @staticmethod
    def _format_term(coefficient, variable="", power=None, first=False):
        """
        Форматирует отдельный член уравнения с учетом знака и степени.
        Если variable не пустой, то коэффициент умножается на variable^power (если power > 1) или просто variable.
        Если first=True, не добавляется знак "+" для положительных чисел.
        """
        coeff = coefficient
        sign = ""
        if first:
            # для первого члена, если коэффициент равен 1 или -1, опускаем 1
            if coeff == 1:
                coeff_str = ""
            elif coeff == -1:
                coeff_str = "-"
            else:
                coeff_str = f"{coeff}"
        else:
            if coeff >= 0:
                sign = " + "
            else:
                sign = " - "
            coeff = abs(coeff)
            if coeff == 1 and variable:
                coeff_str = ""
            else:
                coeff_str = f"{coeff}"
        if variable:
            if power is not None and power != 1:
                term = f"{coeff_str}{variable}²" if power == 2 else f"{coeff_str}{variable}^{power}"
            else:
                term = f"{coeff_str}{variable}"
        else:
            term = f"{coeff_str}"
        return f"{sign}{term}" if not first else term

    def _create_problem_description(self) -> str:
        """
        Формирует строку с постановкой задачи в зависимости от типа уравнения и коэффициентов.
        """
        if self.equation_type == "linear":
            # Ожидаются коэффициенты a, b, c для уравнения a*x + b = c.
            a, b, c = self.coeffs
            left = self._format_term(a, "x", first=True) + self._format_term(b)
            return f"Решите линейное уравнение: {left} = {c}"
        elif self.equation_type == "quadratic":
            # Ожидаются коэффициенты a, b, c для уравнения a*x² + b*x + c = 0.
            a, b, c = self.coeffs
            left = (self._format_term(a, "x", power=2, first=True) +
                    self._format_term(b, "x") +
                    self._format_term(c, first=False))
            return f"Решите квадратное уравнение: {left} = 0"
        elif self.equation_type == "cubic":
            # Ожидаются коэффициенты a, b, c, d для уравнения a*x³ + b*x² + c*x + d = 0.
            a, b, c, d = self.coeffs
            left = (self._format_term(a, "x", power=3, first=True) +
                    self._format_term(b, "x", power=2) +
                    self._format_term(c, "x") +
                    self._format_term(d, first=False))
            return f"Решите кубическое уравнение: {left} = 0"
        elif self.equation_type == "exponential":
            # Ожидаются коэффициенты a, b, c, d для уравнения a*exp(b*x) + c = d.
            a, b, c, d = self.coeffs
            # Форматирование: если a=1, не пишем; если b=1, пишем просто exp(x)
            a_str = "" if abs(a) == 1 else f"{abs(a)}"
            b_str = "" if abs(b) == 1 else f"{abs(b)}"
            sign_a = "" if a > 0 else "-"
            left = f"{sign_a}{a_str}exp({b_str}*x)"
            # Добавляем член c
            left += self._format_term(c)
            return f"Решите экспоненциальное уравнение: {left} = {d}"
        elif self.equation_type == "logarithmic":
            # Ожидаются коэффициенты a, b, c, d для уравнения a*log(b*x) + c = d.
            a, b, c, d = self.coeffs
            a_str = "" if abs(a) == 1 else f"{abs(a)}"
            sign_a = "" if a > 0 else "-"
            left = f"{sign_a}{a_str}log({b}*x)"
            left += self._format_term(c)
            return f"Решите логарифмическое уравнение: {left} = {d}"
        else:
            raise ValueError("Неподдерживаемый тип уравнения.")

    def generate_prompt(self) -> str:
        """
        Генерирует промт с постановкой задачи.
        """
        return f"Задача: {self.problem}\n Пожалуйста, решите задачу пошагово."

    def solve(self):
        """
        Определяет, какой метод решения вызывать, в зависимости от типа уравнения.
        """
        if self.equation_type == "linear":
            self._solve_linear()
        elif self.equation_type == "quadratic":
            self._solve_quadratic()
        elif self.equation_type == "cubic":
            self._solve_cubic()
        elif self.equation_type == "exponential":
            self._solve_exponential()
        elif self.equation_type == "logarithmic":
            self._solve_logarithmic()
        else:
            raise ValueError("Неподдерживаемый тип уравнения.")

    def _solve_linear(self):
        # Решаем линейное уравнение: a*x + b = c.
        a, b, c = self.coeffs
        x = sp.symbols('x')
        equation = sp.Eq(a*x + b, c)
        eq_pretty = sp.pretty(equation)
        self.solution_steps.append(f"Шаг 1: Запишем уравнение: {eq_pretty}.")
        right_side = c - b
        self.solution_steps.append(f"Шаг 2: Переносим {b} на правую сторону: {a}x = {c} - {b} = {right_side}.")
        solution = sp.solve(equation, x)
        self.solution_steps.append(f"Шаг 3: Делим обе части на {a}: x = {right_side} / {a} = {solution[0]}.")
        self.final_answer = str(solution[0])

    def _solve_quadratic(self):
        # Решаем квадратное уравнение: a*x² + b*x + c = 0.
        a, b, c = self.coeffs
        x = sp.symbols('x')
        equation = sp.Eq(a*x**2 + b*x + c, 0)
        eq_pretty = sp.pretty(equation)
        self.solution_steps.append(f"Шаг 1: Запишем уравнение: {eq_pretty}.")
        discriminant = b**2 - 4*a*c
        self.solution_steps.append(f"Шаг 2: Вычисляем дискриминант: D = {b}² - 4*{a}*{c} = {discriminant}.")
        roots = sp.solve(equation, x)
        self.solution_steps.append(f"Шаг 3: Находим корни уравнения: x = {roots}.")
        self.final_answer = str(roots)

    def _solve_cubic(self):
        # Решаем кубическое уравнение: a*x³ + b*x² + c*x + d = 0.
        a, b, c, d = self.coeffs
        x = sp.symbols('x')
        equation = sp.Eq(a*x**3 + b*x**2 + c*x + d, 0)
        eq_pretty = sp.pretty(equation)
        self.solution_steps.append(f"Шаг 1: Запишем уравнение: {eq_pretty}.")
        roots = sp.solve(equation, x)
        self.solution_steps.append(f"Шаг 2: Находим корни уравнения: x = {roots}.")
        self.final_answer = str(roots)

    def _solve_exponential(self):
        # Решаем экспоненциальное уравнение: a*exp(b*x) + c = d.
        a, b, c, d = self.coeffs
        x = sp.symbols('x')
        equation = sp.Eq(a * sp.exp(b*x) + c, d)
        eq_pretty = sp.pretty(equation)
        self.solution_steps.append(f"Шаг 1: Запишем уравнение: {eq_pretty}.")
        self.solution_steps.append(f"Шаг 2: Переносим {c} на правую сторону: {a}*exp({b}*x) = {d} - {c}.")
        right_side = d - c
        self.solution_steps.append(f"Шаг 3: Делим обе части на {a}: exp({b}*x) = {right_side} / {a}.")
        
        ratio = right_side / a
        if ratio <= 0:
            self.solution_steps.append("Шаг 4: Нет решений, так как аргумент логарифма не положительный.")
            self.final_answer = "Нет решений"
        else:
            sol_val = sp.log(ratio) / b
            self.solution_steps.append(f"Шаг 4: Применяем натуральный логарифм: x = log({ratio}) / {b} = {sol_val}.")
            self.final_answer = str(sol_val)


    def _solve_logarithmic(self):
        # Решаем логарифмическое уравнение: a*log(b*x) + c = d.
        a, b, c, d = self.coeffs
        x = sp.symbols('x', positive=True)
        equation = sp.Eq(a * sp.log(b * x) + c, d)
        eq_pretty = sp.pretty(equation)
        self.solution_steps.append(f"Шаг 1: Запишем уравнение: {eq_pretty}.")
        self.solution_steps.append(f"Шаг 2: Переносим {c} на правую сторону: a*log(b*x) = {d} - {c}.")
        self.solution_steps.append(f"Шаг 3: Делим обе части на {a}: log(b*x) = ({d} - {c}) / {a}.")
        
        # Вычисляем решение вручную:
        sol_val = sp.exp((d - c) / a) / b
        self.solution_steps.append(f"Шаг 4: Вычисляем x = exp(({d} - {c})/{a})/{b} = {sol_val}.")
        self.final_answer = str(sol_val)



    def get_result(self) -> dict:
        """
        Возвращает словарь с постановкой задачи, промтом, пошаговым решением и итоговым ответом.
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
    def generate_random_task(cls, only_valid: bool = False, max_attempts: int = 10):
        """
        Генерирует случайную задачу.
        Если only_valid=True, повторяет генерацию до тех пор, пока не будет получена задача,
        у которой final_answer != "Нет решений", или пока не исчерпается max_attempts.
        """
        attempts = 0
        while True:
            attempts += 1
            types = ["linear", "quadratic", "cubic", "exponential", "logarithmic"]
            eq_type = random.choice(types)
            if eq_type == "linear":
                a = random.choice([i for i in range(-10, 11) if i != 0])
                b = random.randint(-10, 10)
                c = random.randint(-10, 10)
                task = cls("linear", a, b, c)
            elif eq_type == "quadratic":
                a = random.choice([i for i in range(-10, 11) if i != 0])
                b = random.randint(-10, 10)
                c = random.randint(-10, 10)
                task = cls("quadratic", a, b, c)
            elif eq_type == "cubic":
                a = random.choice([i for i in range(-10, 11) if i != 0])
                b = random.randint(-10, 10)
                c = random.randint(-10, 10)
                d = random.randint(-10, 10)
                task = cls("cubic", a, b, c, d)
            elif eq_type == "exponential":
                a = random.choice([i for i in range(-5, 6) if i != 0])
                b = random.choice([i for i in range(-5, 6) if i != 0])
                c = random.randint(-10, 10)
                d = random.randint(-10, 10)
                task = cls("exponential", a, b, c, d)
            elif eq_type == "logarithmic":
                a = random.choice([i for i in range(-5, 6) if i != 0])
                b = random.choice([i for i in range(1, 11)])  # b > 0
                c = random.randint(-10, 10)
                d = random.randint(-10, 10)
                task = cls("logarithmic", a, b, c, d)
            else:
                raise ValueError("Неподдерживаемый тип уравнения.")

            # Если не требуется фильтрация, возвращаем задачу сразу.
            if not only_valid:
                return task

            # Проверяем, что задача решаемая.
            result = task.get_result()
            if result["final_answer"] != "Нет решений":
                return task

            # Если превысили максимум попыток, можно вернуть последнюю с предупреждением.
            if attempts >= max_attempts:
                print("Предупреждение: не удалось сгенерировать решаемую задачу за", max_attempts, "попыток.")
                return task
        
# Пример использования
if __name__ == "__main__":
    # Генерация случайной задачи
    task = MathTask.generate_random_task()
    result = task.get_result()
    
    print("Постановка задачи:")
    print(result["problem"])
    print("\nПромт:")
    print(result["prompt"])
    print("\nПошаговое решение:")
    for step in result["solution_steps"]:
        print(step)
    print("\nИтоговый ответ:")
    print(result["final_answer"])
