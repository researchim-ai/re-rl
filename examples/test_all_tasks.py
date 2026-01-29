#!/usr/bin/env python3
"""
Тестирование всех типов задач в re-rl.

Демонстрирует:
- Генерацию всех типов задач
- Использование системы сложности (difficulty)
- Проверку корректности генерации
"""

import sys
import os
import traceback

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from re_rl.tasks.generators import (
    generate_random_arithmetic_task,
    generate_random_linear_task,
    generate_random_quadratic_task,
    generate_random_cubic_task,
    generate_random_exponential_task,
    generate_random_logarithmic_task,
    generate_random_calculus_task,
    generate_random_system_linear_task,
    generate_random_contradiction_task,
    generate_random_knights_knaves_task,
    generate_random_futoshiki_task,
    generate_random_text_stats_task,
    generate_random_urn_probability_task,
    generate_random_graph_task,
    generate_random_analogical_task,
    generate_random_group_theory_task,
    generate_random_category_theory_task
)

from re_rl.rewards import (
    reward_format_check,
    reward_cot_quality,
    reward_correctness,
)


def test_task(task_generator, task_name, num_tests=5, language="ru", **kwargs):
    """
    Тестирует генератор задач и выводит результаты.
    
    :param task_generator: функция-генератор задачи
    :param task_name: название задачи для вывода
    :param num_tests: количество тестов
    :param language: язык задачи
    :param kwargs: дополнительные параметры для генератора
    """
    print(f"\n{'='*50}")
    print(f"Тестирование {task_name}")
    print(f"{'='*50}\n")
    
    for i in range(num_tests):
        print(f"\nТест {i+1}:")
        print("-" * 30)
        
        try:
            # Генерация задачи
            task = task_generator(language=language, **kwargs)
            result = task.get_result()
            
            # Вывод задачи
            print("Задача:")
            print(result["problem"])
            print("\nРешение:")
            for step in result["solution_steps"]:
                print(step)
            print("\nОтвет:", result["final_answer"])
            
        except Exception as e:
            print(f"Ошибка при генерации задачи: {str(e)}")
            print("Трассировка ошибки:")
            print(traceback.format_exc())
        
        print("-" * 30)


def test_difficulty_levels(task_class, task_name, difficulties=[1, 5, 10], language="ru"):
    """
    Тестирует задачу с разными уровнями сложности.
    
    :param task_class: класс задачи с методом from_difficulty
    :param task_name: название задачи
    :param difficulties: список уровней сложности для тестирования
    :param language: язык задачи
    """
    print(f"\n{'='*50}")
    print(f"Тестирование {task_name} с разными уровнями сложности")
    print(f"{'='*50}\n")
    
    for difficulty in difficulties:
        print(f"\n--- Сложность {difficulty} ---")
        try:
            task = task_class.from_difficulty(difficulty, language=language)
            result = task.get_result()
            
            print(f"Задача: {result['problem'][:80]}...")
            print(f"Ответ: {result['final_answer']}")
            
        except Exception as e:
            print(f"Ошибка: {str(e)}")


def main():
    # Список всех задач для тестирования
    tasks = [
        (generate_random_arithmetic_task, "Арифметические задачи", {"difficulty": 5}),
        (generate_random_linear_task, "Линейные уравнения", {}),
        (generate_random_quadratic_task, "Квадратные уравнения", {}),
        (generate_random_cubic_task, "Кубические уравнения", {}),
        (generate_random_exponential_task, "Экспоненциальные уравнения", {}),
        (generate_random_logarithmic_task, "Логарифмические уравнения", {}),
        (generate_random_calculus_task, "Дифференциальные уравнения", {}),
        (generate_random_system_linear_task, "Системы линейных уравнений", {}),
        (generate_random_contradiction_task, "Задачи на противоречия", {}),
        (generate_random_knights_knaves_task, "Рыцари и лжецы", {}),
        (generate_random_futoshiki_task, "Футошики", {}),
        (generate_random_text_stats_task, "Анализ текста", {}),
        (generate_random_urn_probability_task, "Вероятности с урнами", {}),
        (generate_random_graph_task, "Графовые задачи", {}),
        (generate_random_analogical_task, "Аналогические задачи", {}),
        (generate_random_group_theory_task, "Теория групп", {}),
        (generate_random_category_theory_task, "Теория категорий", {})
    ]
    
    # Тестирование каждой задачи
    for task_generator, task_name, kwargs in tasks:
        try:
            test_task(task_generator, task_name, num_tests=2, **kwargs)
        except Exception as e:
            print(f"Ошибка при тестировании {task_name}: {str(e)}")
            print("Трассировка ошибки:")
            print(traceback.format_exc())
            continue
    
    # Тестирование системы сложности
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ СИСТЕМЫ СЛОЖНОСТИ (difficulty)")
    print("=" * 60)
    
    from re_rl.tasks.arithmetic_task import ArithmeticTask
    from re_rl.tasks.linear_task import LinearTask
    from re_rl.tasks.quadratic_task import QuadraticTask
    from re_rl.tasks.system_linear_task import SystemLinearTask
    from re_rl.tasks.graph_task import GraphTask
    
    difficulty_tasks = [
        (ArithmeticTask, "ArithmeticTask"),
        (LinearTask, "LinearTask"),
        (QuadraticTask, "QuadraticTask"),
        (SystemLinearTask, "SystemLinearTask"),
        (GraphTask, "GraphTask"),
    ]
    
    for task_class, task_name in difficulty_tasks:
        try:
            test_difficulty_levels(task_class, task_name)
        except Exception as e:
            print(f"Ошибка при тестировании {task_name}: {str(e)}")
            continue
    
    print("\n" + "=" * 60)
    print("Тестирование завершено!")
    print("=" * 60)


if __name__ == "__main__":
    main()
