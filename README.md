# re-rl

Библиотека для генерации искусственных задач и тренировочных примеров для обучения LLM навыкам reasoning (цепочкам рассуждений) с использованием подхода RL.

## Возможности

- **Мультиязычность**  
  Все текстовые строки (описания, шаблоны, шаги решения) хранятся в централизованном модуле `prompts.py` и подставляются в зависимости от выбранного языка (например, `ru` или `en`).  

- **Генерация математических задач**  
  1. **LinearTask** — линейное уравнение \(a x + b = c\).  
  2. **QuadraticTask** — квадратное уравнение \(a x^2 + b x + c = 0\).  
  3. **CubicTask** — кубическое уравнение \(a x^3 + b x^2 + c x + d = 0\).  
  4. **ExponentialTask** — уравнения вида \(a \exp(b x) + c = d\).  
  5. **LogarithmicTask** — задачи вида \(a \log(b x) + c = d\).  
  6. **CalculusTask** — задачи на дифференцирование и интегрирование полиномиальных функций.  
  7. **SystemLinearTask** — решение систем линейных уравнений методом Крамера.

- **Генерация логических задач**  
  1. **ContradictionTask** — поиск ложного утверждения среди набора фактов (истинных и ложных).  
  2. **KnightsKnavesTask** — классические «рыцари и лжецы» с вариативными именами, сценариями, синонимами ролей.  
  3. **FutoshikiTask** — головоломка на \(N \times N\) поле, где каждую строку и столбец заполняем уникальными числами и учитываем неравенства между клетками (решается автоматически с помощью Z3).  

- **Генерация вероятностных/статистических задач**  
  1. **UrnProbabilityTask** — задачи с несколькими «коробками/ёмкостями», в которых распределены предметы разных цветов, а затем идёт случайный выбор ёмкости и извлечение предметов. Генерируются вопросы вида «вероятность, что все извлечённые предметы — красные» или «хотя бы один зелёный» и т. д.

- **Генерация графовых задач** (GraphTask)  
  1. **shortest_path** — кратчайший путь в случайном графе.  
  2. **minimum_spanning_tree** — минимальное остовное дерево.  
  3. **diameter** — диаметр графа.  
  4. **clustering_coefficient** — средний коэффициент кластеризации.

- **Генерация задач на аналогии** (AnalogicalTask)  
  Сценарии, требующие применить аналогическое мышление. Модель получает описание аналогии и должна перенести решение на новую ситуацию.

- **Фабрика случайных задач**  
  Класс (например, `MathTaskFactory` в `factory.py`), позволяющий вызвать `generate_random_task(...)` и получить задачу случайного типа (из всех перечисленных: математика, логика, графы, вероятности и т. д.). Фабрика подбирает случайную задачу нужного типа, генерирует её параметры и возвращает готовый объект, у которого можно вызвать `get_result()`.

- **Поддержка мультиязычности**  
  - Все текстовые строки (описания задач, шаги решения, пояснения) вынесены в шаблоны в `prompts.py`.  
  - Можно задавать язык, и промты автоматически подставятся.  
  - Добавление нового языка — расширение словаря шаблонов без изменения основной логики.

### Установка

```bash
pip install -e .
```

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
