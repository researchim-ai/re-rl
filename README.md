# re-rl

Библиотека для тренировки LLM моделей размышлениям с искусственными данным

re-rl
re-rl (Reasoning RL) – это универсальный фреймворк для генерации искусственных задач интеграции с обучением языковых моделей посредством reinforcement learning.

Особенности
Генерация математических задач

Поддержка различных типов уравнений: линейные, квадратные, кубические, экспоненциальные и логарифмические.
Возможность генерировать только решаемые задачи с помощью параметра only_valid.
Детализированные пошаговые решения для каждого уравнения.
Reward Shaping

Набор функций наград для проверки формата ответа, корректности решения и других критериев.
Интеграция с обучающими фреймворками

Примеры использования с GRPO, unsloth и другими инструментами для тренировки LLM.
Расширяемость

Проектирование библиотеки с учетом дальнейшего добавления новых типов задач, методов reward shaping и дополнительных модулей для обучения языковых моделей.
Установка
Для установки библиотеки в режиме разработки выполните из корневой директории проекта:

```bash
pip install -e .
```
Также убедитесь, что установлены все зависимости, указанные в файле requirements.txt.

Использование
Генерация математических задач
Пример использования генератора математических задач:

```python
from re_rl.tasks.math_task import MathTask
```

# Генерация случайной задачи с решаемым решением
```python
task = MathTask.generate_random_task(only_valid=True)
result = task.get_result()
print("Постановка задачи:", result["problem"])
print("Пошаговое решение:")
for step in result["solution_steps"]:
    print(step)
print("Итоговый ответ:", result["final_answer"])
```
