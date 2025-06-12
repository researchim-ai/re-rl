# re-rl

Библиотека для генерации искусственных задач и тренировочных примеров для обучения LLM навыкам reasoning (цепочкам рассуждений) с использованием подхода RL.

## Возможности

### 1. Математические задачи
- **LinearTask** — линейные уравнения \(a x + b = c\)
- **QuadraticTask** — квадратные уравнения \(a x^2 + b x + c = 0\)
- **CubicTask** — кубические уравнения \(a x^3 + b x^2 + c x + d = 0\)
- **ExponentialTask** — уравнения вида \(a \exp(b x) + c = d\)
- **LogarithmicTask** — задачи вида \(a \log(b x) + c = d\)
- **CalculusTask** — задачи на дифференцирование и интегрирование
- **SystemLinearTask** — системы линейных уравнений

### 2. Логические задачи
- **ContradictionTask** — поиск ложного утверждения
- **KnightsKnavesTask** — классические "рыцари и лжецы"
- **FutoshikiTask** — головоломка с неравенствами
- **TextStatsTask** — анализ текстовых данных

### 3. Вероятностные задачи
- **UrnProbabilityTask** — задачи с вероятностями и выбором предметов
- **GraphTask** — задачи на графах:
  - Кратчайший путь
  - Минимальное остовное дерево
  - Диаметр графа
  - Коэффициент кластеризации

## Системные возможности
- **Мультиязычность** — поддержка русского и английского языков
- **Генерация датасетов** — создание обучающих и тестовых наборов
- **Система наград** — оценка качества решений
- **Валидация** — проверка корректности ответов
- **Логирование** — отслеживание процесса обучения

## Установка

```bash
pip install -e .
```

## Примеры использования

### 1. Генерация математической задачи
```python
from re_rl.tasks.math_task import MathTask

task = MathTask.generate_random_task(only_valid=True)
result = task.get_result()
print("Задача:", result["problem"])
print("Решение:")
for step in result["solution_steps"]:
    print(step)
print("Ответ:", result["final_answer"])
```

### 2. Генерация логической задачи
```python
from re_rl.tasks.knights_knaves_task import KnightsKnavesTask

task = KnightsKnavesTask.generate_random_task(language="ru")
result = task.get_result()
print("Задача:", result["problem"])
print("Решение:")
for step in result["solution_steps"]:
    print(step)
print("Ответ:", result["final_answer"])
```


### 4. Обучение модели
```python
from re_rl.trainer import GRPOTrainer
from re_rl.dataset_generator import DatasetGenerator

# Генерация датасета
generator = DatasetGenerator()
train_data, eval_data = generator.generate_dataset(
    num_train=1000,
    num_eval=100,
    task_types=["linear", "quadratic", "knights_knaves"]
)

# Настройка и запуск обучения
trainer = GRPOTrainer(
    model_name="Qwen/Qwen2.5-1.5B-Instruct",
    train_data=train_data,
    eval_data=eval_data
)
trainer.train()
```

## Структура проекта

```
re_rl/
├── tasks/              # Генераторы задач
│   ├── math_task.py
│   ├── logical_task.py
│   └── ...
├── rewards.py         # Система наград
├── dataset_generator.py # Генератор датасетов
└── prompts.py         # Шаблоны промптов
```

## Лицензия

MIT License
