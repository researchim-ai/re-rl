# re_rl/tasks/generators.py

import random
import sympy
from typing import Optional

# ============================================================================
# ИМПОРТЫ МАТЕМАТИЧЕСКИХ ЗАДАЧ
# ============================================================================

# Алгебра
from re_rl.tasks.math.algebra.linear_task import LinearTask
from re_rl.tasks.math.algebra.quadratic_task import QuadraticTask
from re_rl.tasks.math.algebra.cubic_task import CubicTask
from re_rl.tasks.math.algebra.system_linear_task import SystemLinearTask
from re_rl.tasks.math.algebra.exponential_task import ExponentialTask
from re_rl.tasks.math.algebra.logarithmic_task import LogarithmicTask
from re_rl.tasks.math.algebra.inequality_task import InequalityTask

# Анализ
from re_rl.tasks.math.analysis.calculus_task import CalculusTask
from re_rl.tasks.math.analysis.limits_task import LimitsTask
from re_rl.tasks.math.analysis.integral_task import IntegralTask
from re_rl.tasks.math.analysis.differential_equation_task import DifferentialEquationTask
from re_rl.tasks.math.analysis.series_task import SeriesTask
from re_rl.tasks.math.analysis.optimization_task import OptimizationTask

# Геометрия
from re_rl.tasks.math.geometry.geometry_task import GeometryTask
from re_rl.tasks.math.geometry.trigonometry_task import TrigonometryTask
from re_rl.tasks.math.geometry.vector_3d_task import Vector3DTask

# Линейная алгебра
from re_rl.tasks.math.linear_algebra.matrix_task import MatrixTask
from re_rl.tasks.math.linear_algebra.complex_number_task import ComplexNumberTask

# Дискретная математика
from re_rl.tasks.math.discrete.number_theory_task import NumberTheoryTask
from re_rl.tasks.math.discrete.combinatorics_task import CombinatoricsTask
from re_rl.tasks.math.discrete.sequence_task import SequenceTask
from re_rl.tasks.math.discrete.set_logic_task import SetLogicTask
from re_rl.tasks.math.discrete.graph_task import GraphTask

# Абстрактная алгебра
from re_rl.tasks.math.abstract_algebra.group_theory_task import GroupTheoryTask
from re_rl.tasks.math.abstract_algebra.category_theory_task import CategoryTheoryTask

# Вероятность и статистика
from re_rl.tasks.math.probability.urn_probability_task import UrnProbabilityTask
from re_rl.tasks.math.probability.statistics_task import StatisticsTask

# Прикладная математика
from re_rl.tasks.math.applied.financial_math_task import FinancialMathTask
from re_rl.tasks.math.applied.arithmetic_task import ArithmeticTask

# Логика
from re_rl.tasks.math.logic.contradiction_task import ContradictionTask
from re_rl.tasks.math.logic.knights_knaves_task import KnightsKnavesTask
from re_rl.tasks.math.logic.futoshiki_task import FutoshikiTask
from re_rl.tasks.math.logic.analogical_task import AnalogicalTask
from re_rl.tasks.math.logic.text_stats_task import TextStatsTask
from re_rl.tasks.math.logic.sudoku_task import SudokuTask
from re_rl.tasks.math.logic.zebra_puzzle_task import ZebraPuzzleTask

# Планирование
from re_rl.tasks.math.planning.river_crossing_task import RiverCrossingTask
from re_rl.tasks.math.planning.tower_of_hanoi_task import TowerOfHanoiTask
from re_rl.tasks.math.planning.water_jug_task import WaterJugTask

# Теория игр
from re_rl.tasks.math.discrete.nim_game_task import NimGameTask

# Физические задачи (импортируем все генераторы)
from re_rl.tasks.physics.generators import ALL_PHYSICS_TASK_GENERATORS


##################################################
# 0. Арифметические задачи (цепочки операций)
##################################################

def generate_random_arithmetic_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    augment: bool = True,
    **kwargs
) -> ArithmeticTask:
    """
    Генерирует случайную арифметическую задачу с цепочками операций.
    
    :param language: 'ru' или 'en'
    :param detail_level: сколько шагов решения показывать
    :param difficulty: уровень сложности (1-10)
    :param augment: если True — использует случайные варианты формулировок
    :return: экземпляр ArithmeticTask
    """
    return ArithmeticTask(
        difficulty=difficulty,
        language=language,
        detail_level=detail_level,
        augment=augment,
        **kwargs
    )


##################################################
# 1. Линейное уравнение: a*x + b = c
##################################################

def generate_random_linear_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    output_format: str = "text",
    augment: bool = True,
    a_range=(-10, 10),
    b_range=(-10, 10),
    c_range=(-10, 10),
    **kwargs
) -> LinearTask:
    """
    Генерирует случайную линейную задачу вида a*x + b = c.
    
    Args:
        language: Язык ("ru" или "en")
        detail_level: Сколько шагов решения показывать
        difficulty: Уровень сложности (1-10)
        output_format: Формат вывода ("text" или "latex")
        augment: Если True — использует случайные варианты формулировок
    """
    return LinearTask(
        difficulty=difficulty,
        language=language,
        detail_level=detail_level,
        output_format=output_format,
        augment=augment,
        **kwargs
    )


##################################################
# 2. Квадратное уравнение: a*x^2 + b*x + c = 0
##################################################

def generate_random_quadratic_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    output_format: str = "text",
    augment: bool = True,
    a_range=(-5, 5),
    b_range=(-10, 10),
    c_range=(-10, 10),
    **kwargs
) -> QuadraticTask:
    """
    Генерирует случайную квадратную задачу a*x^2 + b*x + c = 0, a!=0.
    
    Args:
        language: Язык ("ru" или "en")
        detail_level: Детализация решения
        difficulty: Уровень сложности (1-10)
        output_format: Формат вывода ("text" или "latex")
        augment: Если True — использует случайные варианты формулировок
    """
    return QuadraticTask(
        difficulty=difficulty,
        language=language,
        detail_level=detail_level,
        output_format=output_format,
        augment=augment,
        **kwargs
    )


##################################################
# 3. Кубическое уравнение: a*x^3 + b*x^2 + c*x + d
##################################################

def generate_random_cubic_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    output_format: str = "text"
,
    **kwargs
) -> CubicTask:
    return CubicTask(
        difficulty=difficulty,
        language=language,
        detail_level=detail_level,
        output_format=output_format
    )


##################################################
# 4. Экспоненциальное уравнение: a*exp(b*x) + c = d
##################################################

def generate_random_exponential_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    output_format: str = "text"
,
    **kwargs
) -> ExponentialTask:
    return ExponentialTask(
        difficulty=difficulty,
        language=language,
        detail_level=detail_level,
        output_format=output_format
    )


##################################################
# 5. Логарифмическое уравнение: a*log(b*x) + c = d
##################################################

def generate_random_logarithmic_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    output_format: str = "text"
,
    **kwargs
) -> LogarithmicTask:
    return LogarithmicTask(
        difficulty=difficulty,
        language=language,
        detail_level=detail_level,
        output_format=output_format
    )


##################################################
# 6. CalculusTask (дифференцирование / интегрирование)
##################################################

def generate_random_calculus_task(
    task_type="differentiation",
    language="ru",
    detail_level=3,
    difficulty: int = 5,
    output_format: str = "text"
,
    **kwargs
) -> CalculusTask:
    return CalculusTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty,
        output_format=output_format
    )


##################################################
# 7. ContradictionTask
##################################################

def generate_random_contradiction_task(
    language="ru",
    num_statements=10,
    reasoning_mode: bool = False,
    **kwargs  # игнорируем difficulty и другие
) -> ContradictionTask:
    return ContradictionTask(language=language, num_statements=num_statements, reasoning_mode=reasoning_mode)


##################################################
# 8. KnightsKnavesTask
##################################################

def generate_random_knights_knaves_task(
    language="ru",
    detail_level=5,
    reasoning_mode: bool = False,
    **kwargs
) -> KnightsKnavesTask:
    return KnightsKnavesTask(language=language, detail_level=detail_level, reasoning_mode=reasoning_mode)


##################################################
# 9. FutoshikiTask
##################################################

def generate_random_futoshiki_task(
    language="ru",
    detail_level=5,
    size_range=(4,5),
    ineq_factor=2,
    reasoning_mode: bool = False,
    **kwargs
) -> FutoshikiTask:
    """
    size_range=(4,5) => выбираем случайный size=4 или 5.
    num_inequalities ~ size*ineq_factor, 
    но можно сделать случайно.
    """
    import random
    size = random.randint(size_range[0], size_range[1])
    num_ineq = random.randint(size, size*ineq_factor)
    return FutoshikiTask(language=language, detail_level=detail_level, size=size, num_inequalities=num_ineq, reasoning_mode=reasoning_mode)


##################################################
# 10. UrnProbabilityTask
##################################################

def generate_random_urn_probability_task(
    language="ru",
    count_containers_range=(2,4),
    draws_range=(1,3),
    **kwargs
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
    text_gen_mode="mixed",
    reasoning_mode: bool = False,
    **kwargs
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
        reasoning_mode=reasoning_mode,
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
,
    **kwargs
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
    detail_level: int = 3,
    reasoning_mode: bool = False,
    **kwargs
) -> AnalogicalTask:
    """
    Генерирует случайную аналогическую задачу.
    
    :param language: 'ru' или 'en'
    :param detail_level: количество шагов в решении
    :param reasoning_mode: режим рассуждений
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
        detail_level=detail_level,
        reasoning_mode=reasoning_mode
    )


##################################################
# 15. GroupTheoryTask
##################################################

def generate_random_group_theory_task(
    language: str = "ru",
    detail_level: int = 3,
    task_type=None,
    group_type=None
,
    **kwargs
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
,
    **kwargs
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
,
    **kwargs
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
,
    **kwargs
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
,
    **kwargs
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
,
    **kwargs
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
,
    **kwargs
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
,
    **kwargs
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
,
    **kwargs
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
,
    **kwargs
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
,
    **kwargs
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
,
    **kwargs
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
# 18. Статистика
##################################################

def generate_random_statistics_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> StatisticsTask:
    """
    Генерирует случайную задачу по статистике.
    
    Типы задач:
    - mean: среднее арифметическое
    - median: медиана
    - mode: мода
    - variance: дисперсия
    - std_deviation: стандартное отклонение
    - correlation: корреляция Пирсона
    - linear_regression: линейная регрессия
    - percentile: перцентиль
    - quartiles: квартили
    - z_score: z-оценка
    """
    return StatisticsTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 19. Интегралы
##################################################

def generate_random_integral_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> IntegralTask:
    """
    Генерирует случайную задачу на интегрирование.
    
    Типы задач:
    - indefinite_polynomial: неопределённый интеграл от многочлена
    - definite_polynomial: определённый интеграл от многочлена
    - indefinite_trig: неопределённый интеграл от тригонометрии
    - definite_trig: определённый интеграл от тригонометрии
    - area: площадь под кривой
    """
    return IntegralTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 20. Дифференциальные уравнения
##################################################

def generate_random_differential_equation_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> DifferentialEquationTask:
    """
    Генерирует случайную задачу на дифференциальные уравнения.
    
    Типы задач:
    - separable: с разделяющимися переменными
    - linear_first_order: линейные первого порядка
    - homogeneous_second_order: однородные второго порядка
    - exponential_growth: экспоненциальный рост
    - cauchy_problem: задача Коши
    """
    return DifferentialEquationTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 21. Оптимизация
##################################################

def generate_random_optimization_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> OptimizationTask:
    """
    Генерирует случайную задачу на оптимизацию.
    
    Типы задач:
    - find_extremum: поиск экстремумов
    - max_min_interval: max/min на отрезке
    - linear_programming: линейное программирование
    """
    return OptimizationTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 22. Векторы 3D
##################################################

def generate_random_vector_3d_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> Vector3DTask:
    """
    Генерирует случайную задачу по векторам в 3D.
    
    Типы задач:
    - cross_product: векторное произведение
    - triple_scalar: смешанное произведение
    - plane_equation: уравнение плоскости
    - distance_point_plane: расстояние от точки до плоскости
    - angle_vectors: угол между векторами
    - projection: проекция вектора
    - parallelpiped_volume: объём параллелепипеда
    """
    return Vector3DTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 23. Финансовая математика
##################################################

def generate_random_financial_math_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> FinancialMathTask:
    """
    Генерирует случайную задачу по финансовой математике.
    
    Типы задач:
    - simple_interest: простые проценты
    - compound_interest: сложные проценты
    - present_value: текущая стоимость
    - annuity_pv: текущая стоимость аннуитета
    - annuity_fv: будущая стоимость аннуитета
    - loan_payment: платёж по кредиту
    - npv: чистая приведённая стоимость
    """
    return FinancialMathTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 24. Ряды и сходимость
##################################################

def generate_random_series_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> SeriesTask:
    """
    Генерирует случайную задачу на ряды.
    
    Типы задач:
    - geometric_sum: сумма геометрического ряда
    - convergence_test: исследование сходимости
    - partial_sum: частичная сумма
    - telescoping: телескопический ряд
    """
    return SeriesTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 25. SudokuTask - Судоку
##################################################

def generate_random_sudoku_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    reasoning_mode: bool = False,
    **kwargs
) -> SudokuTask:
    """Генерирует случайную задачу судоку."""
    return SudokuTask(
        language=language,
        detail_level=detail_level,
        difficulty=difficulty,
        reasoning_mode=reasoning_mode
    )


##################################################
# 26. ZebraPuzzleTask - Загадка Эйнштейна
##################################################

def generate_random_zebra_puzzle_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    reasoning_mode: bool = False,
    **kwargs
) -> ZebraPuzzleTask:
    """Генерирует случайную загадку Эйнштейна."""
    return ZebraPuzzleTask(
        language=language,
        detail_level=detail_level,
        difficulty=min(difficulty, 8),  # Ограничиваем для стабильности
        reasoning_mode=reasoning_mode
    )


##################################################
# 27. RiverCrossingTask - Задача о переправе
##################################################

def generate_random_river_crossing_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5
,
    **kwargs
) -> RiverCrossingTask:
    """Генерирует случайную задачу о переправе."""
    return RiverCrossingTask(
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 28. TowerOfHanoiTask - Ханойская башня
##################################################

def generate_random_tower_of_hanoi_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5
,
    **kwargs
) -> TowerOfHanoiTask:
    """Генерирует случайную задачу Ханойской башни."""
    return TowerOfHanoiTask(
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 29. WaterJugTask - Задача о кувшинах
##################################################

def generate_random_water_jug_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5
,
    **kwargs
) -> WaterJugTask:
    """Генерирует случайную задачу о кувшинах."""
    return WaterJugTask(
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 30. NimGameTask - Игра Ним
##################################################

def generate_random_nim_game_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5
,
    **kwargs
) -> NimGameTask:
    """Генерирует случайную задачу игры Ним."""
    return NimGameTask(
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
    # Новые задачи (вторая волна):
    "statistics": generate_random_statistics_task,
    "integral": generate_random_integral_task,
    "differential_equation": generate_random_differential_equation_task,
    "optimization": generate_random_optimization_task,
    "vector_3d": generate_random_vector_3d_task,
    "financial_math": generate_random_financial_math_task,
    "series": generate_random_series_task,
    # Новые reasoning задачи:
    "sudoku": generate_random_sudoku_task,
    "zebra_puzzle": generate_random_zebra_puzzle_task,
    "river_crossing": generate_random_river_crossing_task,
    "tower_of_hanoi": generate_random_tower_of_hanoi_task,
    "water_jug": generate_random_water_jug_task,
    "nim_game": generate_random_nim_game_task,
    # Физические задачи (добавляем все из physics):
    **ALL_PHYSICS_TASK_GENERATORS,
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
