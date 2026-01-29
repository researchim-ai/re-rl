# re_rl/examples/run_example.py
"""
Примеры использования библиотеки re-rl для генерации задач.

Демонстрирует:
- Генерацию математических задач
- Генерацию физических задач
- Использование системы сложности (difficulty)
- Генерацию датасетов
"""

from re_rl.tasks import (
    # Математические задачи
    ArithmeticTask,
    LinearTask,
    QuadraticTask,
    NumberTheoryTask,
    StatisticsTask,
    # Физические задачи
    KinematicsTask,
    CircuitsTask,
    GasLawsTask,
    WavesTask,
    # Генераторы
    generate_random_task,
    generate_random_physics_task,
    ALL_TASK_GENERATORS,
    ALL_PHYSICS_TASK_GENERATORS,
    # Утилиты физики
    PHYSICS_CONSTANTS,
    get_constant,
)
from re_rl.dataset_generator import DatasetGenerator


def example_math_tasks():
    """Примеры математических задач."""
    print("=" * 60)
    print("Пример 1: Математические задачи")
    print("=" * 60)
    
    # Арифметика
    print("\n--- Арифметика (difficulty=5) ---")
    task = ArithmeticTask(difficulty=5, language="ru")
    result = task.get_result()
    print(f"Задача: {result['problem']}")
    print(f"Ответ: {result['final_answer']}")
    
    # Линейные уравнения
    print("\n--- Линейные уравнения ---")
    task = LinearTask.from_difficulty(7, language="ru")
    result = task.get_result()
    print(f"Задача: {result['problem']}")
    print(f"Ответ: {result['final_answer']}")
    
    # Теория чисел
    print("\n--- Теория чисел ---")
    task = NumberTheoryTask(task_type="gcd", language="ru", difficulty=5)
    task.solve()
    print(f"Задача: {task.description}")
    print(f"Ответ: {task.final_answer}")
    
    # Статистика
    print("\n--- Статистика ---")
    task = StatisticsTask(task_type="mean", language="ru", difficulty=5)
    task.solve()
    print(f"Задача: {task.description}")
    print(f"Ответ: {task.final_answer}")


def example_physics_tasks():
    """Примеры физических задач."""
    print("\n" + "=" * 60)
    print("Пример 2: Физические задачи")
    print("=" * 60)
    
    # Кинематика
    print("\n--- Кинематика (равномерное движение) ---")
    task = KinematicsTask(task_type="uniform_motion", v=15, t=10, language="ru")
    task.solve()
    print(f"Задача: {task.description}")
    print(f"Шаги решения:")
    for step in task.solution_steps:
        print(f"  {step}")
    print(f"Ответ: {task.final_answer}")
    
    # Электрические цепи
    print("\n--- Электрические цепи (закон Ома) ---")
    task = CircuitsTask(task_type="ohms_law", R=100, I=0.5, language="ru")
    task.solve()
    print(f"Задача: {task.description}")
    print(f"Ответ: {task.final_answer}")
    
    # Газовые законы
    print("\n--- Газовые законы (идеальный газ) ---")
    task = GasLawsTask(task_type="ideal_gas", n=2, T=300, V=10, language="ru")
    task.solve()
    print(f"Задача: {task.description}")
    print(f"Ответ: {task.final_answer}")
    
    # Волны
    print("\n--- Волны ---")
    task = WavesTask(task_type="wavelength", f=440, v=340, language="ru")
    task.solve()
    print(f"Задача: {task.description}")
    print(f"Ответ: {task.final_answer}")


def example_random_generation():
    """Примеры случайной генерации задач."""
    print("\n" + "=" * 60)
    print("Пример 3: Случайная генерация задач")
    print("=" * 60)
    
    print("\n--- Случайная математическая задача (квадратное уравнение) ---")
    from re_rl.tasks.generators import generate_random_quadratic_task
    task = generate_random_quadratic_task(language="ru")
    result = task.get_result()
    print(f"Задача: {result['problem']}")
    print(f"Ответ: {result['final_answer']}")
    
    print("\n--- Случайная физическая задача ---")
    task = generate_random_physics_task(language="ru", difficulty=5)
    task.solve()
    print(f"Тип: {task.get_task_type()}")
    print(f"Задача: {task.description}")
    print(f"Ответ: {task.final_answer}")


def example_physics_constants():
    """Примеры использования физических констант."""
    print("\n" + "=" * 60)
    print("Пример 4: Физические константы")
    print("=" * 60)
    
    constants_to_show = ["g", "c", "R", "k_e", "h", "N_A"]
    
    for const_name in constants_to_show:
        const = PHYSICS_CONSTANTS[const_name]
        print(f"  {const['name_ru']}: {const['value']} {const['unit']}")


def example_all_task_types():
    """Вывод всех доступных типов задач."""
    print("\n" + "=" * 60)
    print("Пример 5: Все доступные типы задач")
    print("=" * 60)
    
    print("\nМатематические задачи:")
    for i, name in enumerate(ALL_TASK_GENERATORS.keys(), 1):
        print(f"  {i:2}. {name}")
    
    print(f"\nВсего математических типов: {len(ALL_TASK_GENERATORS)}")
    
    print("\nФизические задачи:")
    for i, name in enumerate(ALL_PHYSICS_TASK_GENERATORS.keys(), 1):
        print(f"  {i:2}. {name}")
    
    print(f"\nВсего физических типов: {len(ALL_PHYSICS_TASK_GENERATORS)}")
    print(f"\nОБЩЕЕ КОЛИЧЕСТВО: {len(ALL_TASK_GENERATORS) + len(ALL_PHYSICS_TASK_GENERATORS)} типов задач")


def example_bilingual():
    """Пример двуязычной генерации."""
    print("\n" + "=" * 60)
    print("Пример 6: Двуязычная генерация (RU/EN)")
    print("=" * 60)
    
    # Русский
    print("\n--- Кинематика (RU) ---")
    task = KinematicsTask(task_type="projectile_max_height", v0=20, language="ru")
    task.solve()
    print(f"Задача: {task.description}")
    print(f"Ответ: {task.final_answer}")
    
    # English
    print("\n--- Kinematics (EN) ---")
    task = KinematicsTask(task_type="projectile_max_height", v0=20, language="en")
    task.solve()
    print(f"Problem: {task.description}")
    print(f"Answer: {task.final_answer}")


def main():
    """Запуск всех примеров."""
    example_math_tasks()
    example_physics_tasks()
    example_random_generation()
    example_physics_constants()
    example_all_task_types()
    example_bilingual()
    
    print("\n" + "=" * 60)
    print("Все примеры выполнены успешно!")
    print("=" * 60)


if __name__ == "__main__":
    main()
