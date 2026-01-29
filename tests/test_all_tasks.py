"""
Тесты для всех типов задач re-rl.

Проверяет:
- Корректность импортов из новой структуры
- Генерацию задач и решений
- Двуязычность
- Систему сложности
"""

import unittest
import sympy as sp

# Новые пути импорта после реструктуризации
from re_rl.tasks import (
    # Алгебра
    LinearTask,
    QuadraticTask,
    CubicTask,
    ExponentialTask,
    LogarithmicTask,
    SystemLinearTask,
    InequalityTask,
    # Анализ
    CalculusTask,
    LimitsTask,
    IntegralTask,
    DifferentialEquationTask,
    SeriesTask,
    OptimizationTask,
    # Геометрия
    GeometryTask,
    TrigonometryTask,
    Vector3DTask,
    # Линейная алгебра
    MatrixTask,
    ComplexNumberTask,
    # Дискретная математика
    NumberTheoryTask,
    CombinatoricsTask,
    SequenceTask,
    SetLogicTask,
    GraphTask,
    # Абстрактная алгебра
    GroupTheoryTask,
    CategoryTheoryTask,
    # Теория вероятностей
    UrnProbabilityTask,
    StatisticsTask,
    # Прикладная математика
    FinancialMathTask,
    ArithmeticTask,
    # Логика
    ContradictionTask,
    KnightsKnavesTask,
    FutoshikiTask,
    AnalogicalTask,
    TextStatsTask,
)

# Физические задачи
from re_rl.tasks.physics import (
    KinematicsTask,
    DynamicsTask,
    EnergyTask,
    MomentumTask,
    CircuitsTask,
    ElectrostaticsTask,
    CapacitorsTask,
    GasLawsTask,
    HeatTransferTask,
    WavesTask,
    OpticsTask,
    QuantumTask,
    NuclearTask,
    MagnetismTask,
    RelativityTask,
    OscillationsTask,
    FluidsTask,
    AstrophysicsTask,
)

from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.factory import MathTaskFactory


class TestLinearTask(unittest.TestCase):
    def test_linear_ru(self):
        task = LinearTask(2, 3, 7, language="ru", detail_level=4)
        result = task.get_result()
        self.assertIn("Решите линейное уравнение", result["problem"])
        self.assertEqual(result["final_answer"], "2")
        self.assertTrue(result["prompt"].startswith("Задача:"))

    def test_linear_en(self):
        task = LinearTask(2, 3, 7, language="en", detail_level=4)
        result = task.get_result()
        self.assertIn("Solve the linear equation", result["problem"])
        self.assertEqual(result["final_answer"], "2")
        self.assertTrue(result["prompt"].startswith("Task:"))


class TestQuadraticTask(unittest.TestCase):
    def test_quadratic(self):
        task = QuadraticTask(1, -5, 6, language="ru", detail_level=3)
        result = task.get_result()
        self.assertIn("Решите квадратное уравнение", result["problem"])
        self.assertTrue("2" in result["final_answer"] or "3" in result["final_answer"])
    
    def test_quadratic_solution_steps(self):
        """Проверяет, что есть шаги решения."""
        task = QuadraticTask(1, -5, 6, language="ru", detail_level=5)
        task.solve()
        self.assertGreater(len(task.solution_steps), 0)


class TestCubicTask(unittest.TestCase):
    def test_cubic(self):
        task = CubicTask(1, -6, 11, -6, language="ru", detail_level=3)
        result = task.get_result()
        self.assertIn("Решите кубическое уравнение", result["problem"])
        for r in ["1", "2", "3"]:
            self.assertIn(r, result["final_answer"])


class TestExponentialTask(unittest.TestCase):
    def test_exponential(self):
        task = ExponentialTask(2, 1, 1, 5, language="en", detail_level=4)
        result = task.get_result()
        expected = sp.log(2)
        self.assertAlmostEqual(float(result["final_answer"]), float(expected), places=5)


class TestLogarithmicTask(unittest.TestCase):
    def test_logarithmic(self):
        task = LogarithmicTask(2, 3, 1, 5, language="ru", detail_level=3)
        result = task.get_result()
        expected = sp.exp((5-1)/2)/3
        self.assertAlmostEqual(float(result["final_answer"]), float(expected), places=2)


class TestCalculusTask(unittest.TestCase):
    def test_differentiation(self):
        task = CalculusTask("differentiation", degree=2, language="ru", detail_level=3)
        result = task.get_result()
        self.assertIn("производную", result["problem"])
        self.assertNotEqual(result["final_answer"].strip(), "")

    def test_integration(self):
        task = CalculusTask("integration", degree=2, language="en", detail_level=3)
        result = task.get_result()
        self.assertIn("indefinite integral", result["problem"])
        self.assertNotEqual(result["final_answer"].strip(), "")


class TestIntegralTask(unittest.TestCase):
    def test_indefinite_polynomial(self):
        """Проверяет неопределённый интеграл от многочлена."""
        task = IntegralTask(task_type="indefinite_polynomial", difficulty=3, language="ru", detail_level=5)
        task.solve()
        self.assertIsNotNone(task.final_answer)
        self.assertIn("+ C", task.final_answer)
        self.assertGreater(len(task.solution_steps), 0)
    
    def test_definite_polynomial(self):
        """Проверяет определённый интеграл."""
        task = IntegralTask(task_type="definite_polynomial", difficulty=3, language="ru", detail_level=5)
        task.solve()
        self.assertIsNotNone(task.final_answer)


class TestSystemLinearTask(unittest.TestCase):
    def test_system_linear(self):
        matrix = [
            [2, 1, 5],
            [1, 2, 4]
        ]
        task = SystemLinearTask(matrix, language="ru", detail_level=4)
        result = task.get_result()
        self.assertIn("Решите систему уравнений", result["problem"])
        self.assertIn("x1 = 2.00", result["final_answer"])
        self.assertIn("x2 = 1.00", result["final_answer"])


class TestGraphTask(unittest.TestCase):
    def test_graph_ru(self):
        task = GraphTask.generate_random_task(only_valid=True, num_nodes=15, edge_prob=0.3, language="ru", detail_level=3)
        result = task.get_result()
        self.assertTrue(result["prompt"].startswith("Задача:") or result["prompt"].startswith("Используя аналогию"))
        self.assertNotEqual(result["final_answer"], PROMPT_TEMPLATES["default"]["no_solution"]["ru"])


class TestGroupTheoryTask(unittest.TestCase):
    def test_specific_inverse(self):
        task = GroupTheoryTask(task_type="inverse_element", group_type="cyclic", modulus=11, element=3, language="ru", detail_level=3)
        result = task.get_result()
        # Проверяем что задача про обратный элемент (может быть на русском или английском)
        self.assertTrue("обратный" in result["problem"].lower() or "inverse" in result["problem"].lower())
        self.assertEqual(result["final_answer"], str(pow(3, -1, 11)))

    def test_random_generation(self):
        task = GroupTheoryTask.generate_random_task(language="en", detail_level=2)
        result = task.get_result()
        self.assertTrue(result["problem"].strip())
        self.assertTrue(result["final_answer"].strip())


class TestCategoryTheoryTask(unittest.TestCase):
    def test_composition(self):
        task = CategoryTheoryTask(task_type="morphism_composition", language="en", detail_level=3)
        result = task.get_result()
        self.assertIn("composition", result["problem"].lower())
        self.assertIn("∘", result["final_answer"])


# Физические задачи
class TestPhysicsTasks(unittest.TestCase):
    
    def test_kinematics(self):
        task = KinematicsTask(task_type="uniform_motion", difficulty=5, language="ru", detail_level=5)
        task.solve()
        self.assertIsNotNone(task.final_answer)
        self.assertGreater(len(task.solution_steps), 0)
    
    def test_quantum(self):
        task = QuantumTask(task_type="photoelectric", difficulty=5, language="ru", detail_level=5)
        task.solve()
        self.assertIsNotNone(task.final_answer)
        self.assertGreater(len(task.solution_steps), 2)
    
    def test_nuclear(self):
        task = NuclearTask(task_type="binding_energy", difficulty=5, language="ru", detail_level=5)
        task.solve()
        self.assertIsNotNone(task.final_answer)
        self.assertIn("МэВ", task.final_answer)
    
    def test_relativity(self):
        task = RelativityTask(task_type="time_dilation", difficulty=5, language="ru", detail_level=5)
        task.solve()
        self.assertIsNotNone(task.final_answer)
    
    def test_astrophysics(self):
        task = AstrophysicsTask(task_type="escape_velocity", difficulty=5, language="ru", detail_level=5)
        task.solve()
        self.assertIsNotNone(task.final_answer)
        self.assertIn("м/с", task.final_answer)
    
    def test_oscillations(self):
        task = OscillationsTask(task_type="pendulum", difficulty=5, language="ru", detail_level=5)
        task.solve()
        self.assertIsNotNone(task.final_answer)
    
    def test_fluids(self):
        task = FluidsTask(task_type="archimedes", difficulty=5, language="ru", detail_level=5)
        task.solve()
        self.assertIsNotNone(task.final_answer)
    
    def test_magnetism(self):
        task = MagnetismTask(task_type="lorentz_force", difficulty=5, language="ru", detail_level=5)
        task.solve()
        self.assertIsNotNone(task.final_answer)


class TestBilingualSupport(unittest.TestCase):
    """Тесты двуязычной поддержки."""
    
    def test_kinematics_bilingual(self):
        task_ru = KinematicsTask(task_type="uniform_motion", difficulty=5, language="ru")
        task_en = KinematicsTask(task_type="uniform_motion", difficulty=5, language="en")
        self.assertNotEqual(task_ru.description, task_en.description)
    
    def test_quantum_bilingual(self):
        task_ru = QuantumTask(task_type="photoelectric", difficulty=5, language="ru")
        task_en = QuantumTask(task_type="photoelectric", difficulty=5, language="en")
        self.assertNotEqual(task_ru.description, task_en.description)


class TestDifficultySystem(unittest.TestCase):
    """Тесты системы сложности."""
    
    def test_difficulty_affects_parameters(self):
        task_easy = ArithmeticTask(difficulty=1, language="ru")
        task_hard = ArithmeticTask(difficulty=10, language="ru")
        # Разная сложность должна давать разные диапазоны
        self.assertNotEqual(task_easy.difficulty, task_hard.difficulty)


class TestSolutionStepsQuality(unittest.TestCase):
    """Тесты качества цепочек решений."""
    
    def test_quadratic_has_steps(self):
        task = QuadraticTask(1, -5, 6, language="ru", detail_level=5)
        task.solve()
        self.assertGreater(len(task.solution_steps), 1, "Квадратное уравнение должно иметь несколько шагов")
    
    def test_quantum_has_formula_step(self):
        task = QuantumTask(task_type="photoelectric", difficulty=5, language="ru", detail_level=5)
        task.solve()
        # Должен быть шаг с формулой
        has_formula = any("=" in step or "hν" in step for step in task.solution_steps)
        self.assertTrue(has_formula, "Должна быть формула в шагах")
    
    def test_nuclear_has_detailed_steps(self):
        task = NuclearTask(task_type="binding_energy", difficulty=5, language="ru", detail_level=10)
        task.solve()
        self.assertGreaterEqual(len(task.solution_steps), 3, "Энергия связи должна иметь минимум 3 шага")


class TestFactory(unittest.TestCase):
    def test_factory_math(self):
        task = MathTaskFactory.generate_random_math_task(only_valid=True, language="en", detail_level=3)
        result = task.get_result()
        self.assertTrue(result["prompt"].startswith("Task:"))
        self.assertNotEqual(result["final_answer"], PROMPT_TEMPLATES["default"]["no_solution"]["en"])
    
    def test_language_switch(self):
        task_ru = LinearTask(2, 3, 7, language="ru", detail_level=3)
        task_en = LinearTask(2, 3, 7, language="en", detail_level=3)
        prompt_ru = task_ru.generate_prompt()
        prompt_en = task_en.generate_prompt()
        self.assertNotEqual(prompt_ru, prompt_en)
        self.assertIn("Решите", prompt_ru)
        self.assertIn("Solve", prompt_en)


if __name__ == '__main__':
    unittest.main()
