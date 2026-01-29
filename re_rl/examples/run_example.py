# re_rl/examples/run_example.py
"""
Примеры использования библиотеки re-rl для генерации задач.

Демонстрирует:
- Базовое использование TextualMathEnv
- Использование ArithmeticTask с разными уровнями сложности
- Генерацию задач через from_difficulty()
- Использование DatasetGenerator с параметром difficulties
"""

from re_rl.environments.textual_math_env import TextualMathEnv
from re_rl.tasks.arithmetic_task import ArithmeticTask
from re_rl.tasks.linear_task import LinearTask
from re_rl.tasks.quadratic_task import QuadraticTask
from re_rl.dataset_generator import DatasetGenerator


def example_basic_env():
    """Базовый пример использования TextualMathEnv."""
    print("=" * 60)
    print("Пример 1: Базовое использование TextualMathEnv")
    print("=" * 60)
    
    env = TextualMathEnv()
    task_result = env.get_task()
    
    print("Постановка задачи:", task_result["problem"])
    print("Промт:", task_result["prompt"])
    print("\nПошаговое решение:")
    for step in task_result["solution_steps"]:
        print(" ", step)
    print("\nИтоговый ответ:", task_result["final_answer"])


def example_arithmetic_difficulty():
    """Пример ArithmeticTask с разными уровнями сложности."""
    print("\n" + "=" * 60)
    print("Пример 2: ArithmeticTask с разными уровнями сложности")
    print("=" * 60)
    
    for difficulty in [1, 5, 10]:
        print(f"\n--- Сложность {difficulty} ---")
        task = ArithmeticTask(difficulty=difficulty, language="ru")
        result = task.get_result()
        
        print(f"Задача: {result['problem']}")
        print(f"Ответ: {result['final_answer']}")


def example_from_difficulty():
    """Пример использования from_difficulty() для разных задач."""
    print("\n" + "=" * 60)
    print("Пример 3: Использование from_difficulty()")
    print("=" * 60)
    
    # LinearTask с difficulty
    print("\n--- LinearTask (difficulty=7) ---")
    task = LinearTask.from_difficulty(7, language="ru")
    result = task.get_result()
    print(f"Задача: {result['problem']}")
    print(f"Ответ: {result['final_answer']}")
    
    # QuadraticTask с difficulty
    print("\n--- QuadraticTask (difficulty=5) ---")
    task = QuadraticTask.from_difficulty(5, language="en")
    result = task.get_result()
    print(f"Problem: {result['problem']}")
    print(f"Answer: {result['final_answer']}")
    
    # ArithmeticTask с переопределением параметров
    print("\n--- ArithmeticTask (difficulty=3, num_operations=5) ---")
    task = ArithmeticTask.from_difficulty(3, language="ru", num_operations=5)
    result = task.get_result()
    print(f"Задача: {result['problem']}")
    print(f"Ответ: {result['final_answer']}")


def example_dataset_with_difficulties():
    """Пример генерации датасета с разными уровнями сложности."""
    print("\n" + "=" * 60)
    print("Пример 4: DatasetGenerator с difficulties")
    print("=" * 60)
    
    generator = DatasetGenerator()
    
    # Генерируем датасет с разными уровнями сложности
    dataset = generator.generate_dataset(
        task_types=["arithmetic", "linear"],
        languages=["ru"],
        difficulties=[1, 5, 10],
        detail_levels=[2],
        tasks_per_type=1,
        use_difficulty=True
    )
    
    print(f"\nСгенерировано {len(dataset)} задач:")
    for i, task in enumerate(dataset, 1):
        print(f"\n{i}. {task['task_type']} (difficulty={task['difficulty']})")
        print(f"   Задача: {task['result']['problem'][:60]}...")
        print(f"   Ответ: {task['result']['final_answer']}")


def main():
    """Запуск всех примеров."""
    example_basic_env()
    example_arithmetic_difficulty()
    example_from_difficulty()
    example_dataset_with_difficulties()
    
    print("\n" + "=" * 60)
    print("Все примеры выполнены успешно!")
    print("=" * 60)


if __name__ == "__main__":
    main()
