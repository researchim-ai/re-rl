# re-rl

Библиотека для генерации искусственных задач и тренировочных примеров для обучения LLM навыкам reasoning (цепочкам рассуждений) с использованием подхода RL.

## Возможности

- **Мультиязычность**  
  Все текстовые строки (описания, шаблоны, шаги решения) хранятся в централизованном модуле `prompts.py` и подставляются в зависимости от выбранного языка (например, `ru` или `en`).

- **Генерация математических задач**  
  1. **LinearTask** — решение линейного уравнения $\( a x + b = c \)$.  
  2. **QuadraticTask** — квадратное уравнение $\( a x^2 + b x + c = 0 \)$.  
  3. **CubicTask** — кубическое уравнение $\( a x^3 + b x^2 + c x + d = 0 \)$.  
  4. **ExponentialTask** — задачи вида $\( a \exp(b x) + c = d \)$.  
  5. **LogarithmicTask** — задачи вида $\( a \log(b x) + c = d \)$.  
  6. **CalculusTask** — задачи по дифференцированию и интегрированию полиномиальных функций.  
  7. **SystemLinearTask** — решение систем линейных уравнений (метод Крамера).

- **Генерация логических задач**  
  1. **ContradictionTask** — задача на поиск ложного утверждения в списке фактов (генерация случайных истинных/ложных фактов).  
  2. **KnightsKnavesTask** — классические задачи о «рыцарях и лжецах» (knights and knaves) с высокой вариативностью:
     - Случайный выбор имён персонажей.  
     - Различные сценарии и синонимы ролей (напр. «рыцарь», «лжец» или «честный», «обманщик»).  
     - Пошаговое решение (chain-of-thought).

- **Генерация графовых задач** (GraphTask)  
  1. **shortest_path** — поиск кратчайшего пути в случайном графе.  
  2. **minimum_spanning_tree** — построение минимального остовного дерева.  
  3. **diameter** — вычисление диаметра графа.  
  4. **clustering_coefficient** — средний коэффициент кластеризации.

- **Генерация задач на аналогии** (AnalogicalTask)  
  Сценарии, где нужно применить аналогическое мышление — модель получает описание аналогии и должна перенести решение на новую ситуацию.

- **Фабрика случайных задач**  
  В файле `factory.py` реализован класс (например, `MathTaskFactory`), который позволяет вызвать метод `generate_random_task(...)` и получить задачу случайного типа. Внутри фабрики учитываются все вышеперечисленные классы задач (математика, графы, аналогии, knights & knaves и т. д.).

- **Поддержка мультиязычности**
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
