# re-rl

Библиотека для тренировки LLM моделей размышлениям с искусственными данным

re-rl (Reasoning RL) – это универсальный фреймворк для генерации искусственных задач интеграции с обучением языковых моделей посредством reinforcement learning.

Особенности
Генерация математических задач

Поддержка различных типов уравнений: линейные, квадратные, кубические, экспоненциальные и логарифмические.
Возможность генерировать только решаемые задачи с помощью параметра only_valid.
Детализированные пошаговые решения для каждого уравнения.

Набор функций наград для проверки формата ответа, корректности решения и других критериев.
Интеграция с обучающими фреймворками

Примеры использования с GRPO, unsloth и другими инструментами для тренировки LLM.
Расширяемость

- **Поддержка многоязычности**
  - Все текстовые строки (описания задач, шаги решения, пояснения) вынесены в централизованные шаблоны в файле `prompts.py`.
  - При создании каждой задачи можно задавать язык (например, `"ru"`, `"en"` и др.), и соответствующие промты подставляются автоматически.
  - Добавление нового языка сводится к расширению словаря шаблонов.

### Установка

Для установки библиотеки в режиме разработки выполните из корневой директории проекта:

```bash
pip install -e .
```
Также убедитесь, что установлены все зависимости, указанные в файле requirements.txt.

Генерация математических задач
Пример использования генератора математических задач:

```python
from re_rl.tasks.math_task import MathTask
task = MathTask.generate_random_task(only_valid=True)
result = task.get_result()
print("Постановка задачи:", result["problem"])
print("Пошаговое решение:")
for step in result["solution_steps"]:
    print(step)
print("Итоговый ответ:", result["final_answer"])
```

Пример использования генератора графовых задач:  
```python
from re_rl.tasks.graph_task import GraphTask

# Генерация случайной графовой задачи
graph_task = GraphTask.generate_random_task(only_valid=True, num_nodes=10, edge_prob=0.5)
result = graph_task.get_result()

print("Постановка задачи:", result["problem"])
print("Пошаговое решение:")
for step in result["solution_steps"]:
    print(step)
print("Итоговый ответ:", result["final_answer"])
```

Пример использования генератора задач по анализу:  
```python
from re_rl.tasks.calculus_task import CalculusTask

# Генерация задачи на дифференцирование
task_diff = CalculusTask.generate_random_task(task_type="differentiation", only_valid=True)
result_diff = task_diff.get_result()
print("Задача на дифференцирование:")
print("Постановка задачи:", result_diff["problem"])
for step in result_diff["solution_steps"]:
    print(step)
print("Итоговый ответ:", result_diff["final_answer"])

# Генерация задачи на интегрирование
task_int = CalculusTask.generate_random_task(task_type="integration", only_valid=True)
result_int = task_int.get_result()
print("\nЗадача на интегрирование:")
print("Постановка задачи:", result_int["problem"])
for step in result_int["solution_steps"]:
    print(step)
print("Итоговый ответ:", result_int["final_answer"])
```