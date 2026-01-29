# tests/test_new_physics_tasks.py
"""
Тесты для новых физических задач.
"""

import unittest
import math

# Механика
from re_rl.tasks.physics.mechanics import (
    ProjectileMotionTask, RotationalDynamicsTask, CenterOfMassTask,
    AtwoodMachineTask, InclinedPlaneTask
)

# Электричество
from re_rl.tasks.physics.electricity import (
    ElectromagneticInductionTask, ACCircuitsTask, RCCircuitsTask
)

# Магнетизм
from re_rl.tasks.physics.magnetism import MagneticForceTask

# Термодинамика
from re_rl.tasks.physics.thermodynamics import (
    ThermodynamicCyclesTask, EntropyTask, PhaseTransitionsTask
)

# Волны и оптика
from re_rl.tasks.physics.waves import (
    DopplerEffectTask, InterferenceTask, DiffractionTask, PolarizationTask
)

# Квантовая механика
from re_rl.tasks.physics.quantum import (
    BohrModelTask, DeBroglieTask, UncertaintyPrincipleTask, RadioactiveDecayTask
)

# Измерения
from re_rl.tasks.physics.measurements import (
    DimensionalAnalysisTask, ErrorPropagationTask, UnitConversionTask
)


class TestProjectileMotionTask(unittest.TestCase):
    """Тесты для задач на баллистику."""
    
    def test_creation_ru(self):
        task = ProjectileMotionTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)
        self.assertIn("solution_steps", result)
        self.assertIn("final_answer", result)
    
    def test_creation_en(self):
        task = ProjectileMotionTask(language="en", difficulty=5)
        result = task.get_result()
        self.assertIn("thrown", result["problem"].lower())
    
    def test_task_types(self):
        for task_type in ProjectileMotionTask.TASK_TYPES:
            task = ProjectileMotionTask(task_type=task_type, language="ru")
            result = task.get_result()
            self.assertIsNotNone(result["final_answer"])
    
    def test_difficulty_scaling(self):
        task_easy = ProjectileMotionTask(difficulty=1)
        task_hard = ProjectileMotionTask(difficulty=10)
        self.assertLessEqual(task_easy.v0, 15)
        self.assertGreaterEqual(task_hard.v0, 100)


class TestRotationalDynamicsTask(unittest.TestCase):
    """Тесты для задач на вращательное движение."""
    
    def test_creation(self):
        task = RotationalDynamicsTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)
    
    def test_all_task_types(self):
        for task_type in RotationalDynamicsTask.TASK_TYPES:
            task = RotationalDynamicsTask(task_type=task_type)
            result = task.get_result()
            self.assertIsNotNone(result["final_answer"])


class TestCenterOfMassTask(unittest.TestCase):
    """Тесты для задач на центр масс."""
    
    def test_creation(self):
        task = CenterOfMassTask(language="ru", difficulty=3)
        result = task.get_result()
        self.assertIn("problem", result)
    
    def test_calculation_simple(self):
        task = CenterOfMassTask(
            masses=[1, 1],
            positions=[(0, 0), (2, 0)]
        )
        self.assertAlmostEqual(task.x_cm, 1.0, places=2)
        self.assertAlmostEqual(task.y_cm, 0.0, places=2)


class TestAtwoodMachineTask(unittest.TestCase):
    """Тесты для машины Атвуда."""
    
    def test_creation(self):
        task = AtwoodMachineTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)
    
    def test_physics_correct(self):
        task = AtwoodMachineTask(m1=10, m2=5)
        g = 9.8
        expected_a = (10 - 5) * g / (10 + 5)
        self.assertAlmostEqual(task.acceleration, expected_a, places=2)


class TestInclinedPlaneTask(unittest.TestCase):
    """Тесты для наклонной плоскости."""
    
    def test_creation(self):
        task = InclinedPlaneTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)
    
    def test_all_task_types(self):
        for task_type in InclinedPlaneTask.TASK_TYPES:
            task = InclinedPlaneTask(task_type=task_type)
            result = task.get_result()
            self.assertIsNotNone(result["final_answer"])


class TestElectromagneticInductionTask(unittest.TestCase):
    """Тесты для электромагнитной индукции."""
    
    def test_creation(self):
        task = ElectromagneticInductionTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)
    
    def test_all_task_types(self):
        for task_type in ElectromagneticInductionTask.TASK_TYPES:
            task = ElectromagneticInductionTask(task_type=task_type)
            result = task.get_result()
            self.assertIsNotNone(result["final_answer"])


class TestACCircuitsTask(unittest.TestCase):
    """Тесты для цепей переменного тока."""
    
    def test_creation(self):
        task = ACCircuitsTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)
    
    def test_resonance_calculation(self):
        # Просто проверяем, что задача на резонанс создаётся
        task = ACCircuitsTask(task_type="resonance")
        result = task.get_result()
        self.assertIn("Гц", result["final_answer"])


class TestRCCircuitsTask(unittest.TestCase):
    """Тесты для RC-цепей."""
    
    def test_creation(self):
        task = RCCircuitsTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)


class TestMagneticForceTask(unittest.TestCase):
    """Тесты для силы Лоренца."""
    
    def test_creation(self):
        task = MagneticForceTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)
    
    def test_all_particles(self):
        for particle in MagneticForceTask.PARTICLES.keys():
            task = MagneticForceTask(particle=particle)
            result = task.get_result()
            self.assertIsNotNone(result["final_answer"])


class TestThermodynamicCyclesTask(unittest.TestCase):
    """Тесты для термодинамических циклов."""
    
    def test_creation(self):
        task = ThermodynamicCyclesTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)
    
    def test_carnot_efficiency(self):
        task = ThermodynamicCyclesTask(task_type="carnot_efficiency")
        result = task.get_result()
        # Проверяем, что в ответе есть процент
        self.assertIn("%", result["final_answer"])


class TestEntropyTask(unittest.TestCase):
    """Тесты для энтропии."""
    
    def test_creation(self):
        task = EntropyTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)


class TestPhaseTransitionsTask(unittest.TestCase):
    """Тесты для фазовых переходов."""
    
    def test_creation(self):
        task = PhaseTransitionsTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)


class TestDopplerEffectTask(unittest.TestCase):
    """Тесты для эффекта Доплера."""
    
    def test_creation(self):
        task = DopplerEffectTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)
    
    def test_all_task_types(self):
        for task_type in DopplerEffectTask.TASK_TYPES:
            task = DopplerEffectTask(task_type=task_type)
            result = task.get_result()
            self.assertIsNotNone(result["final_answer"])


class TestInterferenceTask(unittest.TestCase):
    """Тесты для интерференции."""
    
    def test_creation(self):
        task = InterferenceTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)


class TestDiffractionTask(unittest.TestCase):
    """Тесты для дифракции."""
    
    def test_creation(self):
        task = DiffractionTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)


class TestPolarizationTask(unittest.TestCase):
    """Тесты для поляризации."""
    
    def test_creation(self):
        task = PolarizationTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)
    
    def test_brewster_angle(self):
        task = PolarizationTask(task_type="brewster")
        result = task.get_result()
        # Проверяем, что в ответе есть градусы
        self.assertIn("°", result["final_answer"])


class TestBohrModelTask(unittest.TestCase):
    """Тесты для модели Бора."""
    
    def test_creation(self):
        task = BohrModelTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)
    
    def test_ground_state_energy(self):
        task = BohrModelTask(task_type="energy_level")
        task.n = 1
        task.solve()
        # E_1 = -13.6 эВ
        self.assertIn("-13.6", task.final_answer)


class TestDeBroglieTask(unittest.TestCase):
    """Тесты для волн де Бройля."""
    
    def test_creation(self):
        task = DeBroglieTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)


class TestUncertaintyPrincipleTask(unittest.TestCase):
    """Тесты для принципа неопределённости."""
    
    def test_creation(self):
        task = UncertaintyPrincipleTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)


class TestRadioactiveDecayTask(unittest.TestCase):
    """Тесты для радиоактивного распада."""
    
    def test_creation(self):
        task = RadioactiveDecayTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)
    
    def test_half_life_remaining(self):
        task = RadioactiveDecayTask(task_type="remaining")
        task.T = 10
        task.t = 10  # один период полураспада
        task.solve()
        # Должно остаться 50%
        self.assertIn("50", task.final_answer)


class TestDimensionalAnalysisTask(unittest.TestCase):
    """Тесты для анализа размерностей."""
    
    def test_creation(self):
        task = DimensionalAnalysisTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)


class TestErrorPropagationTask(unittest.TestCase):
    """Тесты для распространения погрешностей."""
    
    def test_creation(self):
        task = ErrorPropagationTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)


class TestUnitConversionTask(unittest.TestCase):
    """Тесты для перевода единиц."""
    
    def test_creation(self):
        task = UnitConversionTask(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)


class TestAllTasksLanguages(unittest.TestCase):
    """Проверка поддержки языков для всех задач."""
    
    TASK_CLASSES = [
        ProjectileMotionTask, RotationalDynamicsTask, CenterOfMassTask,
        AtwoodMachineTask, InclinedPlaneTask, ElectromagneticInductionTask,
        ACCircuitsTask, RCCircuitsTask, MagneticForceTask,
        ThermodynamicCyclesTask, EntropyTask, PhaseTransitionsTask,
        DopplerEffectTask, InterferenceTask, DiffractionTask, PolarizationTask,
        BohrModelTask, DeBroglieTask, UncertaintyPrincipleTask, RadioactiveDecayTask,
        DimensionalAnalysisTask, ErrorPropagationTask, UnitConversionTask
    ]
    
    def test_russian_language(self):
        for TaskClass in self.TASK_CLASSES:
            task = TaskClass(language="ru")
            result = task.get_result()
            self.assertIsNotNone(result["problem"])
    
    def test_english_language(self):
        for TaskClass in self.TASK_CLASSES:
            task = TaskClass(language="en")
            result = task.get_result()
            self.assertIsNotNone(result["problem"])


if __name__ == "__main__":
    unittest.main()
