# re_rl/tasks/generators.py

import random
import sympy
from typing import Optional

# Импорты классов задач:
from re_rl.tasks.arithmetic_task import ArithmeticTask
from re_rl.tasks.linear_task import LinearTask
from re_rl.tasks.quadratic_task import QuadraticTask
from re_rl.tasks.cubic_task import CubicTask
from re_rl.tasks.exponential_task import ExponentialTask
from re_rl.tasks.logarithmic_task import LogarithmicTask
from re_rl.tasks.calculus_task import CalculusTask
from re_rl.tasks.contradiction_task import ContradictionTask
from re_rl.tasks.knights_knaves_task import KnightsKnavesTask
from re_rl.tasks.futoshiki_task import FutoshikiTask
from re_rl.tasks.urn_probability_task import UrnProbabilityTask
from re_rl.tasks.text_stats_task import TextStatsTask
from re_rl.tasks.graph_task import GraphTask
from re_rl.tasks.system_linear_task import SystemLinearTask
from re_rl.tasks.analogical_task import AnalogicalTask
from re_rl.tasks.group_theory_task import GroupTheoryTask
from re_rl.tasks.category_theory_task import CategoryTheoryTask


##################################################
# 0. Арифметические задачи (цепочки операций)
##################################################

def generate_random_arithmetic_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5
) -> ArithmeticTask:
    """
    Генерирует случайную арифметическую задачу с цепочками операций.
    
    :param language: 'ru' или 'en'
    :param detail_level: сколько шагов решения показывать
    :param difficulty: уровень сложности (1-10)
    :return: экземпляр ArithmeticTask
    """
    return ArithmeticTask(
        difficulty=difficulty,
        language=language,
        detail_level=detail_level
    )


##################################################
# 1. Линейное уравнение: a*x + b = c
##################################################

def generate_random_linear_task(
    language: str = "ru",
    detail_level: int = 3,
    a_range=(-10, 10),
    b_range=(-10, 10),
    c_range=(-10, 10)
) -> LinearTask:
    """
    Генерирует случайную линейную задачу вида a*x + b = c, 
    где a != 0 и a, b, c - целые из заданных диапазонов.

    :param language: 'ru' или 'en'
    :param detail_level: сколько шагов решения показывать
    :param a_range, b_range, c_range: диапазоны для a, b, c (кортежи (min, max))
    :return: экземпляр LinearTask
    """
    while True:
        a = random.randint(a_range[0], a_range[1])
        if a == 0:
            continue
        b = random.randint(b_range[0], b_range[1])
        c = random.randint(c_range[0], c_range[1])
        # Окей, у нас есть a!=0 => задача "валидна"
        return LinearTask(a, b, c, language=language, detail_level=detail_level)


##################################################
# 2. Квадратное уравнение: a*x^2 + b*x + c = 0
##################################################

def generate_random_quadratic_task(
    language: str = "ru",
    detail_level: int = 3,
    a_range=(-5, 5),
    b_range=(-10, 10),
    c_range=(-10, 10)
) -> QuadraticTask:
    """
    Генерирует случайную квадратную задачу a*x^2 + b*x + c = 0, a!=0.
    """
    while True:
        a = random.randint(a_range[0], a_range[1])
        if a == 0:
            continue
        b = random.randint(b_range[0], b_range[1])
        c = random.randint(c_range[0], c_range[1])
        return QuadraticTask(a, b, c, language=language, detail_level=detail_level)


##################################################
# 3. Кубическое уравнение: a*x^3 + b*x^2 + c*x + d
##################################################

def generate_random_cubic_task(
    language: str = "ru",
    detail_level: int = 3,
    a_range=(-5,5),
    b_range=(-10,10),
    c_range=(-10,10),
    d_range=(-10,10)
) -> CubicTask:
    while True:
        a = random.randint(a_range[0], a_range[1])
        if a == 0:
            continue
        b = random.randint(b_range[0], b_range[1])
        c = random.randint(c_range[0], c_range[1])
        d = random.randint(d_range[0], d_range[1])
        return CubicTask(a, b, c, d, language=language, detail_level=detail_level)


##################################################
# 4. Экспоненциальное уравнение: a*exp(b*x) + c = d
##################################################

def generate_random_exponential_task(
    language: str = "ru",
    detail_level: int = 3,
    a_range=(-5,5),
    b_range=(-5,5),
    c_range=(-10,10),
    d_range=(-10,10)
) -> ExponentialTask:
    while True:
        a = random.choice([i for i in range(a_range[0], a_range[1]+1) if i != 0])
        b = random.choice([i for i in range(b_range[0], b_range[1]+1) if i != 0])
        c = random.randint(c_range[0], c_range[1])
        d = random.randint(d_range[0], d_range[1])
        return ExponentialTask(a, b, c, d, language=language, detail_level=detail_level)


##################################################
# 5. Логарифмическое уравнение: a*log(b*x) + c = d
##################################################

def generate_random_logarithmic_task(
    language: str = "ru",
    detail_level: int = 3,
    a_range=(-5,5),
    b_range=(1,10),
    c_range=(-10,10),
    d_range=(-10,10)
) -> LogarithmicTask:
    """
    b>0
    """
    while True:
        a = random.choice([i for i in range(a_range[0], a_range[1]+1) if i != 0])
        b = random.randint(b_range[0], b_range[1])
        if b == 0:
            continue
        c = random.randint(c_range[0], c_range[1])
        d = random.randint(d_range[0], d_range[1])
        return LogarithmicTask(a, b, c, d, language=language, detail_level=detail_level)


##################################################
# 6. CalculusTask (дифференцирование / интегрирование)
##################################################

def generate_random_calculus_task(
    task_type="differentiation",
    degree_range=(1,3),
    language="ru",
    detail_level=3
) -> CalculusTask:
    """
    Генерирует случайную функцию, степень от 1..3, затем 
    создаёт CalculusTask (либо differentiation, либо integration).
    """
    import random
    deg = random.randint(degree_range[0], degree_range[1])
    return CalculusTask(task_type=task_type, degree=deg, language=language, detail_level=detail_level)


##################################################
# 7. ContradictionTask
##################################################

def generate_random_contradiction_task(
    language="ru",
    num_statements=10
) -> ContradictionTask:
    return ContradictionTask(language=language, num_statements=num_statements)


##################################################
# 8. KnightsKnavesTask
##################################################

def generate_random_knights_knaves_task(
    language="ru",
    detail_level=5
) -> KnightsKnavesTask:
    return KnightsKnavesTask(language=language, detail_level=detail_level)


##################################################
# 9. FutoshikiTask
##################################################

def generate_random_futoshiki_task(
    language="ru",
    detail_level=5,
    size_range=(4,5),
    ineq_factor=2
) -> FutoshikiTask:
    """
    size_range=(4,5) => выбираем случайный size=4 или 5.
    num_inequalities ~ size*ineq_factor, 
    но можно сделать случайно.
    """
    import random
    size = random.randint(size_range[0], size_range[1])
    num_ineq = random.randint(size, size*ineq_factor)
    return FutoshikiTask(language=language, detail_level=detail_level, size=size, num_inequalities=num_ineq)


##################################################
# 10. UrnProbabilityTask
##################################################

def generate_random_urn_probability_task(
    language="ru",
    count_containers_range=(2,4),
    draws_range=(1,3)
) -> UrnProbabilityTask:
    count_containers = random.randint(count_containers_range[0], count_containers_range[1])
    draws = random.randint(draws_range[0], draws_range[1])
    return UrnProbabilityTask(language=language, count_containers=count_containers, draws=draws)


##################################################
# 11. TextStatsTask
##################################################

def generate_random_text_stats_task(
    language="ru",
    detail_level=3,
    allow_overlapping=None,
    text_gen_mode="mixed"
) -> TextStatsTask:
    """
    Генерируем случайную задачу на поиск подстроки в тексте.
    allow_overlapping - можно random либо bool
    text_gen_mode = "words", "letters", "mixed"
    """
    import random
    if allow_overlapping is None:
        allow_overlapping = bool(random.getrandbits(1))

    return TextStatsTask(
        language=language,
        detail_level=detail_level,
        allow_overlapping=allow_overlapping,
        text_gen_mode=text_gen_mode,
    )


##################################################
# 12. GraphTask
##################################################

def generate_random_graph_task(
    task_type="shortest_path",
    num_nodes=8,
    edge_prob=0.4,
    language="ru",
    detail_level=3
) -> GraphTask:
    return GraphTask(
        task_type=task_type,
        num_nodes=num_nodes,
        edge_prob=edge_prob,
        language=language,
        detail_level=detail_level
    )


##################################################
# 13. SystemLinearTask
##################################################

def generate_random_system_linear_task(
    language="ru",
    detail_level=3,
    size=2
):
    """
    Генерируем систему линейных уравнений размером size x size.
    Матрица shape = (size, size+1).
    Метод Крамера, a!=0 => суммарный дет!=0 (не всегда гарантирован).
    """
    import numpy as np

    while True:
        # Генерируем случайную матрицу (size x (size+1))
        # Например, коэф из -5..5, ensure not all zero
        mat = np.random.randint(-5, 6, size=(size, size+1))
        # Проверим, что A есть invertible
        A = mat[:, :-1]
        detA = round(np.linalg.det(A), 5)
        if abs(detA) < 1e-3:
            continue
        return SystemLinearTask(mat.tolist(), language=language, detail_level=detail_level)


##################################################
# 14. AnalogicalTask
##################################################

def generate_random_analogical_task(
    language: str = "ru",
    detail_level: int = 3
) -> AnalogicalTask:
    """
    Генерирует случайную аналогическую задачу.
    
    :param language: 'ru' или 'en'
    :param detail_level: количество шагов в решении
    :return: экземпляр AnalogicalTask
    """
    # Список предопределенных аналогий
    analogies = [
        # Математические аналогии
        "2 * 3 = 6 -> 3 * 4 = 12",
        "2^3 = 8 -> 3^2 = 9",
        "5 + 3 = 8 -> 7 + 4 = 11",
        
        # Логические аналогии
        "круг -> круглый -> квадрат -> квадратный",
        "бежать -> бег -> плыть -> плавание",
        "горячий -> холодный -> светлый -> темный",
        
        # Геометрические аналогии
        "треугольник -> 3 стороны -> квадрат -> 4 стороны",
        "круг -> 0 углов -> треугольник -> 3 угла",
        
        # Числовые аналогии
        "2 -> 4 -> 3 -> 6",  # умножение на 2
        "3 -> 9 -> 4 -> 16",  # возведение в квадрат
        "2 -> 8 -> 3 -> 27",  # возведение в куб
    ]
    
    # Выбираем случайную аналогию
    analogy = random.choice(analogies)
    
    return AnalogicalTask(
        description=analogy,
        language=language,
        detail_level=detail_level
    )


##################################################
# 15. GroupTheoryTask
##################################################

def generate_random_group_theory_task(
    language: str = "ru",
    detail_level: int = 3,
    task_type=None,
    group_type=None
) -> GroupTheoryTask:
    """Генерируем случайную задачу по теории групп."""
    return GroupTheoryTask.generate_random_task(
        task_type=task_type,
        group_type=group_type,
        language=language,
        detail_level=detail_level
    )

##################################################
# 16. CategoryTheoryTask
##################################################

def generate_random_category_theory_task(
    language: str = "ru",
    detail_level: int = 3,
    task_type=None
) -> CategoryTheoryTask:
    """Генерируем случайную задачу по теории категорий."""
    return CategoryTheoryTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level
    )
