# re_rl/tasks/math/__init__.py

"""
Математические задачи.

Категории:
- algebra: алгебра (линейные, квадратные, кубические уравнения и т.д.)
- analysis: анализ (пределы, производные, интегралы, ДУ)
- geometry: геометрия и тригонометрия
- linear_algebra: линейная алгебра (матрицы, комплексные числа)
- discrete: дискретная математика (теория чисел, комбинаторика, графы)
- abstract_algebra: абстрактная алгебра (теория групп, категорий)
- probability: вероятность и статистика
- applied: прикладная математика (финансы, арифметика)
- logic: логические задачи
"""

# Алгебра
from re_rl.tasks.math.algebra import (
    LinearTask,
    QuadraticTask,
    CubicTask,
    SystemLinearTask,
    ExponentialTask,
    LogarithmicTask,
    InequalityTask,
)

# Анализ
from re_rl.tasks.math.analysis import (
    CalculusTask,
    LimitsTask,
    IntegralTask,
    DifferentialEquationTask,
    SeriesTask,
    OptimizationTask,
)

# Геометрия
from re_rl.tasks.math.geometry import (
    GeometryTask,
    TrigonometryTask,
    Vector3DTask,
)

# Линейная алгебра
from re_rl.tasks.math.linear_algebra import (
    MatrixTask,
    ComplexNumberTask,
)

# Дискретная математика
from re_rl.tasks.math.discrete import (
    NumberTheoryTask,
    CombinatoricsTask,
    SequenceTask,
    SetLogicTask,
    GraphTask,
)

# Абстрактная алгебра
from re_rl.tasks.math.abstract_algebra import (
    GroupTheoryTask,
    CategoryTheoryTask,
)

# Вероятность и статистика
from re_rl.tasks.math.probability import (
    UrnProbabilityTask,
    StatisticsTask,
)

# Прикладная математика
from re_rl.tasks.math.applied import (
    FinancialMathTask,
    ArithmeticTask,
)

# Логика
from re_rl.tasks.math.logic import (
    ContradictionTask,
    KnightsKnavesTask,
    FutoshikiTask,
    AnalogicalTask,
    TextStatsTask,
)

__all__ = [
    # Алгебра
    "LinearTask",
    "QuadraticTask", 
    "CubicTask",
    "SystemLinearTask",
    "ExponentialTask",
    "LogarithmicTask",
    "InequalityTask",
    # Анализ
    "CalculusTask",
    "LimitsTask",
    "IntegralTask",
    "DifferentialEquationTask",
    "SeriesTask",
    "OptimizationTask",
    # Геометрия
    "GeometryTask",
    "TrigonometryTask",
    "Vector3DTask",
    # Линейная алгебра
    "MatrixTask",
    "ComplexNumberTask",
    # Дискретная математика
    "NumberTheoryTask",
    "CombinatoricsTask",
    "SequenceTask",
    "SetLogicTask",
    "GraphTask",
    # Абстрактная алгебра
    "GroupTheoryTask",
    "CategoryTheoryTask",
    # Вероятность
    "UrnProbabilityTask",
    "StatisticsTask",
    # Прикладная
    "FinancialMathTask",
    "ArithmeticTask",
    # Логика
    "ContradictionTask",
    "KnightsKnavesTask",
    "FutoshikiTask",
    "AnalogicalTask",
    "TextStatsTask",
]
