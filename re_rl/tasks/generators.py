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

# Новые задачи:
from re_rl.tasks.number_theory_task import NumberTheoryTask
from re_rl.tasks.combinatorics_task import CombinatoricsTask
from re_rl.tasks.sequence_task import SequenceTask
from re_rl.tasks.geometry_task import GeometryTask
from re_rl.tasks.matrix_task import MatrixTask
from re_rl.tasks.trigonometry_task import TrigonometryTask
from re_rl.tasks.inequality_task import InequalityTask
from re_rl.tasks.complex_number_task import ComplexNumberTask
from re_rl.tasks.limits_task import LimitsTask
from re_rl.tasks.set_logic_task import SetLogicTask


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


##################################################
# 17. NumberTheoryTask - Теория чисел
##################################################

def generate_random_number_theory_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
) -> NumberTheoryTask:
    """
    Генерирует случайную задачу по теории чисел.
    
    Типы задач:
    - gcd_lcm: НОД и НОК
    - prime_factorization: разложение на простые множители
    - modular_arithmetic: вычисления по модулю
    - chinese_remainder: китайская теорема об остатках
    - divisibility: делимость
    - diophantine: диофантовы уравнения
    - euler_totient: функция Эйлера
    """
    return NumberTheoryTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 18. CombinatoricsTask - Комбинаторика
##################################################

def generate_random_combinatorics_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
) -> CombinatoricsTask:
    """
    Генерирует случайную комбинаторную задачу.
    
    Типы задач:
    - permutations: перестановки
    - combinations: сочетания
    - binomial: биномиальные коэффициенты
    - pigeonhole: принцип Дирихле
    - inclusion_exclusion: формула включения-исключения
    - derangements: беспорядки
    - stars_and_bars: шары и перегородки
    - circular_permutation: круговые перестановки
    """
    return CombinatoricsTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 19. SequenceTask - Последовательности
##################################################

def generate_random_sequence_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
) -> SequenceTask:
    """
    Генерирует случайную задачу на последовательности.
    
    Типы задач:
    - arithmetic_nth: n-й член арифметической прогрессии
    - arithmetic_sum: сумма арифметической прогрессии
    - geometric_nth: n-й член геометрической прогрессии
    - geometric_sum: сумма геометрической прогрессии
    - fibonacci_nth: числа Фибоначчи
    - recurrence: рекуррентные соотношения
    - pattern: найти закономерность
    """
    return SequenceTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 20. GeometryTask - Геометрия
##################################################

def generate_random_geometry_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
) -> GeometryTask:
    """
    Генерирует случайную геометрическую задачу.
    
    Типы задач:
    - triangle_area_coords: площадь треугольника по координатам
    - triangle_area_sides: площадь по формуле Герона
    - distance_2d/3d: расстояние между точками
    - circle_area, circle_circumference: площадь/окружность
    - sphere_volume, cylinder_volume, cone_volume: объёмы тел
    - angle_between_vectors: угол между векторами
    - dot_product, cross_product: произведения векторов
    - line_equation: уравнение прямой
    - midpoint: середина отрезка
    """
    return GeometryTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 21. MatrixTask - Матрицы
##################################################

def generate_random_matrix_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
) -> MatrixTask:
    """
    Генерирует случайную задачу с матрицами.
    
    Типы задач:
    - determinant: вычисление определителя
    - inverse: обратная матрица
    - multiplication: умножение матриц
    - transpose: транспонирование
    - rank: ранг матрицы
    - eigenvalues: собственные значения
    - trace: след матрицы
    - add: сложение матриц
    - scalar_mult: умножение на скаляр
    """
    return MatrixTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 22. TrigonometryTask - Тригонометрия
##################################################

def generate_random_trigonometry_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
) -> TrigonometryTask:
    """
    Генерирует случайную тригонометрическую задачу.
    
    Типы задач:
    - basic_value: значения тригонометрических функций
    - equation: тригонометрические уравнения
    - identity: упрощение тождеств
    - triangle_solve: решение треугольников
    - inverse: обратные тригонометрические функции
    """
    return TrigonometryTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 23. InequalityTask - Неравенства
##################################################

def generate_random_inequality_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
) -> InequalityTask:
    """
    Генерирует случайную задачу на неравенства.
    
    Типы задач:
    - linear: линейные неравенства
    - quadratic: квадратные неравенства
    - rational: дробно-рациональные
    - absolute: с модулем
    - system: системы неравенств
    """
    return InequalityTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 24. ComplexNumberTask - Комплексные числа
##################################################

def generate_random_complex_number_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
) -> ComplexNumberTask:
    """
    Генерирует случайную задачу с комплексными числами.
    
    Типы задач:
    - arithmetic: арифметические операции
    - modulus: модуль
    - argument: аргумент
    - polar_form: тригонометрическая форма
    - power: возведение в степень (формула Муавра)
    - roots: корни n-й степени
    - conjugate: сопряжённое число
    - equation: уравнения
    """
    return ComplexNumberTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 25. LimitsTask - Пределы
##################################################

def generate_random_limits_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
) -> LimitsTask:
    """
    Генерирует случайную задачу на пределы.
    
    Типы задач:
    - polynomial: пределы полиномов
    - rational: пределы рациональных функций
    - infinity: пределы на бесконечности
    - indeterminate: неопределённости (0/0, ∞/∞)
    - sequence: пределы последовательностей
    - special: замечательные пределы
    """
    return LimitsTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 26. SetLogicTask - Множества и логика
##################################################

def generate_random_set_logic_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
) -> SetLogicTask:
    """
    Генерирует случайную задачу на множества и логику.
    
    Типы задач:
    - union: объединение множеств
    - intersection: пересечение
    - difference: разность
    - symmetric_difference: симметрическая разность
    - complement: дополнение
    - cardinality: мощность объединения
    - power_set: степень множества
    - cartesian_product: декартово произведение
    - boolean_simplify: упрощение логических выражений
    - truth_table: таблица истинности
    - venn_problem: задачи на диаграммы Венна
    """
    return SetLogicTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# Универсальный генератор всех типов задач
##################################################

ALL_TASK_GENERATORS = {
    "arithmetic": generate_random_arithmetic_task,
    "linear": generate_random_linear_task,
    "quadratic": generate_random_quadratic_task,
    "cubic": generate_random_cubic_task,
    "exponential": generate_random_exponential_task,
    "logarithmic": generate_random_logarithmic_task,
    "calculus": generate_random_calculus_task,
    "contradiction": generate_random_contradiction_task,
    "knights_knaves": generate_random_knights_knaves_task,
    "futoshiki": generate_random_futoshiki_task,
    "urn_probability": generate_random_urn_probability_task,
    "text_stats": generate_random_text_stats_task,
    "graph": generate_random_graph_task,
    "system_linear": generate_random_system_linear_task,
    "analogical": generate_random_analogical_task,
    "group_theory": generate_random_group_theory_task,
    "category_theory": generate_random_category_theory_task,
    # Новые задачи:
    "number_theory": generate_random_number_theory_task,
    "combinatorics": generate_random_combinatorics_task,
    "sequence": generate_random_sequence_task,
    "geometry": generate_random_geometry_task,
    "matrix": generate_random_matrix_task,
    "trigonometry": generate_random_trigonometry_task,
    "inequality": generate_random_inequality_task,
    "complex_number": generate_random_complex_number_task,
    "limits": generate_random_limits_task,
    "set_logic": generate_random_set_logic_task,
}


def generate_random_task(
    task_type: str = None,
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    **kwargs
):
    """
    Универсальный генератор случайной задачи.
    
    Если task_type не указан, выбирается случайный тип.
    
    :param task_type: тип задачи (см. ALL_TASK_GENERATORS.keys())
    :param language: 'ru' или 'en'
    :param detail_level: уровень детализации решения
    :param difficulty: уровень сложности (1-10)
    :param kwargs: дополнительные параметры для конкретного генератора
    :return: экземпляр задачи
    """
    if task_type is None:
        task_type = random.choice(list(ALL_TASK_GENERATORS.keys()))
    
    generator = ALL_TASK_GENERATORS.get(task_type)
    if generator is None:
        raise ValueError(f"Неизвестный тип задачи: {task_type}. Доступные: {list(ALL_TASK_GENERATORS.keys())}")
    
    # Передаём параметры, которые поддерживает генератор
    return generator(language=language, detail_level=detail_level, **kwargs)
