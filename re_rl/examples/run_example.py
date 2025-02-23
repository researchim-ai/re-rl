from re_rl.environments.textual_math_env import TextualMathEnv

def main():
    env = TextualMathEnv()
    task_result = env.get_task()
    print("Постановка задачи:", task_result["problem"])
    print("Промт:", task_result["prompt"])
    print("Пошаговое решение:")
    for step in task_result["solution_steps"]:
        print(step)
    print("Итоговый ответ:", task_result["final_answer"])

if __name__ == "__main__":
    main()
