import sys
import os
import traceback

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from re_rl.tasks.generators import (
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

def test_task(task_generator, task_name, num_tests=5, language="ru"):
    """
    Тестирует генератор задач и выводит результаты
    """
    print(f"\n{'='*50}")
    print(f"Тестирование {task_name}")
    print(f"{'='*50}\n")
    
    for i in range(num_tests):
        print(f"\nТест {i+1}:")
        print("-" * 30)
        
        try:
            # Генерация задачи
            task = task_generator(language=language)
            result = task.get_result()
            
            # Вывод задачи
            print("Задача:")
            print(result["problem"])
            print("\nРешение:")
            for step in result["solution_steps"]:
                print(step)
            print("\nОтвет:", result["final_answer"])
            
            # Здесь можно добавить собственные проверки (например, формат),
            # но для быстрого smoke-теста просто выводим задачу и решение.
            
        except Exception as e:
            print(f"Ошибка при генерации задачи: {str(e)}")
            print("Трассировка ошибки:")
            print(traceback.format_exc())
        
        print("-" * 30)

def main():
    # Список всех задач для тестирования
    tasks = [
        (generate_random_linear_task, "Линейные уравнения"),
        (generate_random_quadratic_task, "Квадратные уравнения"),
        (generate_random_cubic_task, "Кубические уравнения"),
        (generate_random_exponential_task, "Экспоненциальные уравнения"),
        (generate_random_logarithmic_task, "Логарифмические уравнения"),
        (generate_random_calculus_task, "Дифференциальные уравнения"),
        (generate_random_system_linear_task, "Системы линейных уравнений"),
        (generate_random_contradiction_task, "Задачи на противоречия"),
        (generate_random_knights_knaves_task, "Рыцари и лжецы"),
        (generate_random_futoshiki_task, "Футошики"),
        (generate_random_text_stats_task, "Анализ текста"),
        (generate_random_urn_probability_task, "Вероятности с урнами"),
        (generate_random_graph_task, "Графовые задачи"),
        (generate_random_analogical_task, "Аналогические задачи"),
        (generate_random_group_theory_task, "Теория групп"),
        (generate_random_category_theory_task, "Теория категорий")
    ]
    
    # Тестирование каждой задачи
    for task_generator, task_name in tasks:
        try:
            test_task(task_generator, task_name)
        except Exception as e:
            print(f"Ошибка при тестировании {task_name}: {str(e)}")
            print("Трассировка ошибки:")
            print(traceback.format_exc())
            continue

if __name__ == "__main__":
    main() 