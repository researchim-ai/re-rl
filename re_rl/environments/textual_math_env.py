from re_rl.tasks.composer import TaskComposer

class TextualMathEnv:
    """
    Интерфейс для выдачи задач в процессе тренировки LLM.
    В данном примере возвращается математическая задача.
    """
    def __init__(self):
        self.composer = TaskComposer()

    def get_task(self):
        # Пример: создаем математическую задачу 2x + 3 = 7
        math_task = self.composer.compose_math_task(2, 3, 7)
        return math_task.get_result()

# Пример использования интерфейса
if __name__ == "__main__":
    env = TextualMathEnv()
    result = env.get_task()
    print("Постановка задачи:")
    print(result["problem"])
    print("\n Промт:")
    print(result["prompt"])
    print("\n Пошаговое решение:")
    for step in result["solution_steps"]:
        print(step)
    print("\n Итоговый ответ:")
    print(result["final_answer"])
