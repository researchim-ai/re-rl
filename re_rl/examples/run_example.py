#!/usr/bin/env python3
"""
Примеры использования библиотеки re-rl для генерации задач.

Демонстрирует:
- Генерацию математических задач
- Генерацию физических задач
- Использование системы сложности (difficulty)
- Генерацию датасетов для SFT
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__, 'run_example_i18n.json')


from re_rl.tasks import (
    # Математические задачи
    ArithmeticTask,
    LinearTask,
    QuadraticTask,
    CombinatoricsTask,
    StatisticsTask,
    IntegralTask,
    # Физические задачи
    KinematicsTask,
    CircuitsTask,
    GasLawsTask,
    WavesTask,
    QuantumTask,
    NuclearTask,
    RelativityTask,
    # Генераторы
    ALL_TASK_GENERATORS,
    ALL_PHYSICS_TASK_GENERATORS,
    generate_random_physics_task,
    # Утилиты физики
    PHYSICS_CONSTANTS,
)
from re_rl.dataset_generator import DatasetGenerator


def example_math_tasks():
    """Примеры математических задач."""
    print("=" * 60)
    print(texts.literal('literals.s0'))
    print("=" * 60)
    
    # Арифметика
    print(texts.literal('literals.s1'))
    task = ArithmeticTask(difficulty=5, language="ru")
    result = task.get_result()
    print(texts.t('s2', 'ru', v0=result['problem']))
    print(texts.t('s3', 'ru', v0=result['final_answer']))
    
    # Линейные уравнения
    print(texts.literal('literals.s4'))
    task = LinearTask.from_difficulty(7, language="ru")
    result = task.get_result()
    print(texts.t('s5', 'ru', v0=result['problem']))
    print(texts.t('s6', 'ru', v0=result['final_answer']))
    
    # Комбинаторика
    print(texts.literal('literals.s7'))
    task = CombinatoricsTask(task_type="permutations", difficulty=5, language="ru")
    task.solve()
    print(texts.t('s8', 'ru', v0=task.description))
    print(texts.t('s9', 'ru', v0=task.final_answer))
    
    # Статистика
    print(texts.literal('literals.s10'))
    task = StatisticsTask(task_type="mean", difficulty=5, language="ru")
    task.solve()
    print(texts.t('s11', 'ru', v0=task.description))
    print(texts.t('s12', 'ru', v0=task.final_answer))
    
    # Интеграл
    print(texts.literal('literals.s13'))
    task = IntegralTask(task_type="indefinite_polynomial", difficulty=3, language="ru", detail_level=5)
    task.solve()
    print(texts.t('s14', 'ru', v0=task.description))
    print(texts.t('s15', 'ru', v0=task.final_answer))


def example_physics_tasks():
    """Примеры физических задач."""
    print("\n" + "=" * 60)
    print(texts.literal('literals.s16'))
    print("=" * 60)
    
    # Кинематика
    print(texts.literal('literals.s17'))
    task = KinematicsTask(task_type="uniform_motion", v=15, t=10, language="ru")
    task.solve()
    print(texts.t('s18', 'ru', v0=task.description))
    print(texts.literal('literals.s19'))
    for step in task.solution_steps:
        print(f"  {step}")
    print(texts.t('s20', 'ru', v0=task.final_answer))
    
    # Электрические цепи
    print(texts.literal('literals.s21'))
    task = CircuitsTask(task_type="ohms_law", R=100, I=0.5, language="ru")
    task.solve()
    print(texts.t('s22', 'ru', v0=task.description))
    print(texts.t('s23', 'ru', v0=task.final_answer))
    
    # Газовые законы
    print(texts.literal('literals.s24'))
    task = GasLawsTask(task_type="ideal_gas", n=2, T=300, V=10, language="ru")
    task.solve()
    print(texts.t('s25', 'ru', v0=task.description))
    print(texts.t('s26', 'ru', v0=task.final_answer))
    
    # Волны
    print(texts.literal('literals.s27'))
    task = WavesTask(task_type="wavelength", f=440, v=340, language="ru")
    task.solve()
    print(texts.t('s28', 'ru', v0=task.description))
    print(texts.t('s29', 'ru', v0=task.final_answer))
    
    # Квантовая механика
    print(texts.literal('literals.s30'))
    task = QuantumTask(task_type="photoelectric", freq=1e15, work_function=2.0, 
                       language="ru", detail_level=5)
    task.solve()
    print(texts.t('s31', 'ru', v0=task.description))
    print(texts.literal('literals.s32'))
    for step in task.solution_steps:
        print(f"  {step}")
    print(texts.t('s33', 'ru', v0=task.final_answer))
    
    # Ядерная физика
    print(texts.literal('literals.s34'))
    task = NuclearTask(task_type="binding_energy", nucleus="He-4", 
                       language="ru", detail_level=10)
    task.solve()
    print(texts.t('s35', 'ru', v0=task.description))
    print(texts.t('s36', 'ru', v0=task.final_answer))
    
    # СТО
    print(texts.literal('literals.s37'))
    task = RelativityTask(task_type="time_dilation", beta=0.8, t0=10, 
                          language="ru", detail_level=5)
    task.solve()
    print(texts.t('s38', 'ru', v0=task.description))
    print(texts.t('s39', 'ru', v0=task.final_answer))


def example_random_generation():
    """Примеры случайной генерации задач."""
    print("\n" + "=" * 60)
    print(texts.literal('literals.s40'))
    print("=" * 60)
    
    print(texts.literal('literals.s41'))
    from re_rl.tasks.generators import generate_random_quadratic_task
    task = generate_random_quadratic_task(language="ru")
    result = task.get_result()
    print(texts.t('s42', 'ru', v0=result['problem']))
    print(texts.t('s43', 'ru', v0=result['final_answer']))
    
    print(texts.literal('literals.s44'))
    task = generate_random_physics_task(language="ru", difficulty=5)
    task.solve()
    print(texts.t('s45', 'ru', v0=task.get_task_type()))
    print(texts.t('s46', 'ru', v0=task.description))
    print(texts.t('s47', 'ru', v0=task.final_answer))


def example_physics_constants():
    """Примеры использования физических констант."""
    print("\n" + "=" * 60)
    print(texts.literal('literals.s48'))
    print("=" * 60)
    
    constants_to_show = ["g", "c", "R", "k_e", "h", "N_A", "G"]
    
    for const_name in constants_to_show:
        const = PHYSICS_CONSTANTS[const_name]
        print(f"  {const['name_ru']}: {const['value']} {const['unit']}")


def example_all_task_types():
    """Вывод всех доступных типов задач."""
    print("\n" + "=" * 60)
    print(texts.literal('literals.s49'))
    print("=" * 60)
    
    print(texts.literal('literals.s50'))
    for i, name in enumerate(sorted(ALL_TASK_GENERATORS.keys()), 1):
        print(f"  {i:2}. {name}")
    
    print(texts.t('s51', 'ru', v0=len(ALL_TASK_GENERATORS)))
    
    print(texts.literal('literals.s52'))
    for i, name in enumerate(ALL_PHYSICS_TASK_GENERATORS.keys(), 1):
        print(f"  {i:2}. {name}")
    
    print(texts.t('s53', 'ru', v0=len(ALL_PHYSICS_TASK_GENERATORS)))
    print(texts.t('s54', 'ru', v0=len(ALL_TASK_GENERATORS) + len(ALL_PHYSICS_TASK_GENERATORS)))


def example_bilingual():
    """Пример двуязычной генерации."""
    print("\n" + "=" * 60)
    print(texts.literal('literals.s55'))
    print("=" * 60)
    
    # Русский
    print(texts.literal('literals.s56'))
    task = KinematicsTask(task_type="projectile_max_height", v0=20, language="ru")
    task.solve()
    print(texts.t('s57', 'ru', v0=task.description))
    print(texts.t('s58', 'ru', v0=task.final_answer))
    
    # English
    print("\n--- Kinematics (EN) ---")
    task = KinematicsTask(task_type="projectile_max_height", v0=20, language="en")
    task.solve()
    print(f"Problem: {task.description}")
    print(f"Answer: {task.final_answer}")


def example_sft_dataset():
    """Пример генерации SFT датасета."""
    print("\n" + "=" * 60)
    print(texts.literal('literals.s59'))
    print("=" * 60)
    
    generator = DatasetGenerator()
    
    dataset = generator.generate_sft_dataset(
        task_types=["quadratic", "kinematics", "quantum"],
        num_samples=10,
        language="ru",
        difficulties=[5],
    )
    
    print(texts.t('s60', 'ru', v0=len(dataset)))
    print(texts.literal('literals.s61'))
    ex = dataset[0]
    print(f"  instruction: {ex['instruction']}")
    print(f"  input: {ex['input'][:60]}...")
    print(f"  output: {ex['output'][:100]}...")


def main():
    """Запуск всех примеров."""
    example_math_tasks()
    example_physics_tasks()
    example_random_generation()
    example_physics_constants()
    example_all_task_types()
    example_bilingual()
    example_sft_dataset()
    
    print("\n" + "=" * 60)
    print(texts.literal('literals.s62'))
    print("=" * 60)


if __name__ == "__main__":
    main()
