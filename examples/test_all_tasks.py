#!/usr/bin/env python3
"""
Тестирование всех типов задач в re-rl.

Демонстрирует:
- Генерацию всех математических задач
- Генерацию всех физических задач
- Использование системы сложности (difficulty)
- Проверку корректности генерации
"""

import sys
import os

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.physics.generators import ALL_PHYSICS_TASK_GENERATORS


def test_task(task_generator, task_name, num_tests=3, language="ru", **kwargs):
    """
    Тестирует генератор задач и выводит результаты.
    """
    print(f"\n{'='*50}")
    print(f"Тестирование: {task_name}")
    print(f"{'='*50}")
    
    success = 0
    failed = 0
    
    for i in range(num_tests):
        try:
            task = task_generator(language=language, **kwargs)
            
            # Для BaseMathTask используем solve()
            if hasattr(task, 'solve'):
                task.solve()
                problem = task.description
                answer = task.final_answer
                steps = task.solution_steps
            else:
                # Для старых задач используем get_result()
                result = task.get_result()
                problem = result["problem"]
                answer = result["final_answer"]
                steps = result.get("solution_steps", [])
            
            print(f"\n  Тест {i+1}: ✓")
            problem_preview = str(problem)[:70].replace('\n', ' ')
            print(f"    Задача: {problem_preview}...")
            print(f"    Ответ: {answer}")
            success += 1
            
        except Exception as e:
            print(f"\n  Тест {i+1}: ✗ - {str(e)[:50]}")
            failed += 1
    
    return success, failed


def test_all_math_tasks(num_tests=2):
    """Тестирует все математические задачи."""
    print("\n" + "#" * 60)
    print("# МАТЕМАТИЧЕСКИЕ ЗАДАЧИ")
    print("#" * 60)
    
    total_success = 0
    total_failed = 0
    
    for name, generator in ALL_TASK_GENERATORS.items():
        try:
            success, failed = test_task(generator, name, num_tests=num_tests)
            total_success += success
            total_failed += failed
        except Exception as e:
            print(f"\nОшибка при тестировании {name}: {str(e)}")
            total_failed += num_tests
    
    return total_success, total_failed


def test_all_physics_tasks(num_tests=2):
    """Тестирует все физические задачи."""
    print("\n" + "#" * 60)
    print("# ФИЗИЧЕСКИЕ ЗАДАЧИ")
    print("#" * 60)
    
    total_success = 0
    total_failed = 0
    
    for name, generator in ALL_PHYSICS_TASK_GENERATORS.items():
        try:
            success, failed = test_task(generator, name, num_tests=num_tests)
            total_success += success
            total_failed += failed
        except Exception as e:
            print(f"\nОшибка при тестировании {name}: {str(e)}")
            total_failed += num_tests
    
    return total_success, total_failed


def test_difficulty_levels():
    """Тестирует систему сложности."""
    print("\n" + "#" * 60)
    print("# ТЕСТИРОВАНИЕ СИСТЕМЫ СЛОЖНОСТИ")
    print("#" * 60)
    
    from re_rl.tasks import ArithmeticTask, KinematicsTask, CircuitsTask
    
    tasks_to_test = [
        (ArithmeticTask, "ArithmeticTask", {"language": "ru"}),
        (KinematicsTask, "KinematicsTask", {"task_type": "uniform_motion", "language": "ru"}),
        (CircuitsTask, "CircuitsTask", {"task_type": "ohms_law", "language": "ru"}),
    ]
    
    for task_class, name, kwargs in tasks_to_test:
        print(f"\n--- {name} ---")
        for difficulty in [1, 5, 10]:
            try:
                task = task_class(difficulty=difficulty, **kwargs)
                if hasattr(task, 'solve'):
                    task.solve()
                    answer = task.final_answer
                else:
                    result = task.get_result()
                    answer = result['final_answer']
                print(f"  Difficulty {difficulty:2}: ✓ ({answer})")
            except Exception as e:
                print(f"  Difficulty {difficulty:2}: ✗ ({str(e)[:30]})")


def test_bilingual():
    """Тестирует двуязычную генерацию."""
    print("\n" + "#" * 60)
    print("# ТЕСТИРОВАНИЕ ДВУЯЗЫЧНОСТИ (RU/EN)")
    print("#" * 60)
    
    from re_rl.tasks import KinematicsTask, GasLawsTask
    
    for TaskClass, name in [(KinematicsTask, "Kinematics"), (GasLawsTask, "GasLaws")]:
        print(f"\n--- {name} ---")
        for lang in ["ru", "en"]:
            try:
                task = TaskClass(language=lang, difficulty=5)
                task.solve()
                desc_preview = task.description[:50] + "..."
                print(f"  {lang.upper()}: {desc_preview}")
            except Exception as e:
                print(f"  {lang.upper()}: ✗ ({str(e)[:30]})")


def main():
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ВСЕХ ЗАДАЧ RE-RL")
    print("=" * 60)
    
    # Тест математических задач
    math_success, math_failed = test_all_math_tasks(num_tests=1)
    
    # Тест физических задач  
    physics_success, physics_failed = test_all_physics_tasks(num_tests=1)
    
    # Тест сложности
    test_difficulty_levels()
    
    # Тест двуязычности
    test_bilingual()
    
    # Итоговая статистика
    print("\n" + "=" * 60)
    print("ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 60)
    
    total_math = len(ALL_TASK_GENERATORS)
    total_physics = len(ALL_PHYSICS_TASK_GENERATORS)
    
    print(f"\nМатематические задачи: {math_success} успешно, {math_failed} ошибок (из {total_math} типов)")
    print(f"Физические задачи: {physics_success} успешно, {physics_failed} ошибок (из {total_physics} типов)")
    print(f"\nВСЕГО ТИПОВ ЗАДАЧ: {total_math + total_physics}")
    
    total_success = math_success + physics_success
    total_failed = math_failed + physics_failed
    
    if total_failed == 0:
        print("\n✓ Все тесты пройдены успешно!")
    else:
        print(f"\n✗ Обнаружены ошибки: {total_failed}")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
