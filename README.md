# re-rl

Библиотека для генерации математических и физических задач с пошаговыми решениями для обучения LLM навыкам reasoning (Chain-of-Thought).

## Особенности

- **52 типа задач**: 34 математических + 18 физических
- **Языки**: русский и английский
- **Система сложности**: 10 уровней для каждого типа задач
- **Пошаговые решения**: детальные цепочки рассуждений для SFT/RL обучения
- **Форматы экспорта**: JSON, JSONL, SFT-формат, Chat-формат

## Быстрый старт

```bash
pip install -e .
```

### Генерация SFT датасета

```python
from re_rl.dataset_generator import DatasetGenerator

generator = DatasetGenerator()

# Генерация 10000 примеров для SFT
dataset = generator.generate_sft_dataset(
    task_types=["quadratic", "kinematics", "quantum", "circuits"],
    num_samples=10000,
    language="ru",
    difficulties=[3, 5, 7, 9],  # Средняя и высокая сложность
)

# Разделение на train/eval
train, eval = generator.split_dataset(dataset, train_ratio=0.9)

# Сохранение в JSONL (для transformers/trl)
generator.save_jsonl(train, "train.jsonl")
generator.save_jsonl(eval, "eval.jsonl")
```

### Формат SFT данных

```json
{
  "instruction": "Решите задачу пошагово, объясняя каждый шаг рассуждения.",
  "input": "Фотон с частотой 1e15 Гц падает на металл с работой выхода 2 эВ. Найдите кинетическую энергию фотоэлектрона.",
  "output": "Шаг 1: Уравнение Эйнштейна для фотоэффекта: hν = A + Eₖ\nE_фотона = hν = 6.626e-34 × 1e15 = 6.626e-19 Дж = 4.14 эВ\nEₖ = hν - A = 4.14 - 2.0 = 2.14 эВ\n\nОтвет: 2.14 эВ",
  "metadata": {"task_type": "quantum", "difficulty": 5, "language": "ru"}
}
```

### Chat-формат (для Llama/ChatML)

```python
chat_dataset = generator.generate_chat_dataset(
    task_types=["quadratic", "quantum"],
    num_samples=5000,
    language="ru"
)
# Формат: {"messages": [{"role": "user", ...}, {"role": "assistant", ...}]}
```

## Типы задач

### Математика (34 типа)

| Категория | Задачи |
|-----------|--------|
| **Алгебра** | linear, quadratic, cubic, system_linear, exponential, logarithmic, inequality |
| **Анализ** | calculus, limits, integral, differential_equation, series, optimization |
| **Геометрия** | geometry, trigonometry, vector_3d |
| **Линейная алгебра** | matrix, complex_number |
| **Дискретная математика** | number_theory, combinatorics, sequence, set_logic, graph |
| **Абстрактная алгебра** | group_theory, category_theory |
| **Теория вероятностей** | urn_probability, statistics |
| **Прикладная** | financial_math, arithmetic |
| **Логика** | contradiction, knights_knaves, futoshiki, analogical, text_stats |

### Физика (18 типов)

| Категория | Задачи |
|-----------|--------|
| **Механика** | kinematics, dynamics, energy, momentum |
| **Электричество** | circuits, electrostatics, capacitors, magnetism |
| **Термодинамика** | gas_laws, heat_transfer |
| **Волны и оптика** | waves, optics |
| **Современная физика** | quantum, nuclear, relativity |
| **Колебания** | oscillations |
| **Гидростатика** | fluids |
| **Астрофизика** | astrophysics |

## Примеры использования

### Генерация отдельных задач

```python
from re_rl.tasks.physics import QuantumTask, generate_random_physics_task
from re_rl.tasks import QuadraticTask

# Квантовая механика
task = QuantumTask(task_type="photoelectric", difficulty=5, language="ru")
task.solve()
print(task.description)
print(task.solution_steps)
print(task.final_answer)

# Случайная физическая задача
task = generate_random_physics_task(difficulty=7, language="en")
task.solve()
print(task.get_result())

# Квадратное уравнение
task = QuadraticTask(a=1, b=-5, c=6, language="ru")
result = task.get_result()
print(result["problem"])
print(result["solution_steps"])
print(result["final_answer"])
```

### Список всех задач

```python
from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.physics.generators import ALL_PHYSICS_TASK_GENERATORS

print("Математика:", list(ALL_TASK_GENERATORS.keys()))
print("Физика:", list(ALL_PHYSICS_TASK_GENERATORS.keys()))
```

### Физические константы

```python
from re_rl.tasks.physics import PHYSICS_CONSTANTS, get_constant

print(get_constant("c"))  # Скорость света: 299792458
print(get_constant("h"))  # Постоянная Планка: 6.62607015e-34
print(PHYSICS_CONSTANTS["G"])  # Гравитационная постоянная с описанием
```

## Использование для SFT обучения

### С Hugging Face transformers + trl

```python
from datasets import load_dataset
from trl import SFTTrainer

# Загрузка сгенерированного датасета
dataset = load_dataset("json", data_files={"train": "train.jsonl", "eval": "eval.jsonl"})

# Форматирование для SFT
def format_prompt(example):
    return f"""### Instruction:
{example['instruction']}

### Input:
{example['input']}

### Response:
{example['output']}"""

# Обучение
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset["train"],
    formatting_func=format_prompt,
    max_seq_length=2048,
)
trainer.train()
```

### С Axolotl

```yaml
# axolotl config
datasets:
  - path: train.jsonl
    type: alpaca
    
# Формат уже совместим с alpaca (instruction/input/output)
```

## Formal Math: Theorem Proving в Lean 4

Помимо текстовых задач, RE-RL воспроизводит pipeline генерации training data из формальных доказательств Lean 4 по подходу [LeanNavigator](https://arxiv.org/abs/2502.10000) (Yin & Gao, 2025) — BFS-обход графа состояний Mathlib4 через Pantograph с BERT+FAISS retrieval тактик.

### Два источника данных

| Источник | Описание | Скорость |
|----------|----------|----------|
| **Mathlib Extraction** | Готовые доказательства из traced Mathlib | Быстро (~100k pairs/мин) |
| **BFS LeanNavigator** | Новые альтернативные пути через BFS | Медленнее, но уникальные данные |

**Рекомендация**: комбинировать оба источника для максимального разнообразия.

### Быстрый старт

```bash
# 1. Трейсинг Mathlib4 (один раз, ~60 мин, результат кэшируется)
python scripts/fast_trace.py --version v4.26.0

# 2a. Извлечение готовых доказательств (быстро)
python examples/formal/extract_mathlib_proofs.py --min-proof-length 2 --max-theorems 50000

# 2b. BFS exploration (новые пути)
python examples/formal/run_bfs.py --max-theorems 100 --decompose-auto

# 3. (Опционально) Обучение BERT RAG для лучшего retrieval
python examples/formal/train_rag.py
```

### Jupyter Notebook (полный pipeline)

Интерактивный notebook с пошаговым объяснением:

```bash
cd examples/formal
jupyter notebook Formal_Math_Generation.ipynb
```

Подробная документация: [`re_rl/tasks/formal/README.md`](re_rl/tasks/formal/README.md) и [`examples/formal/README.md`](examples/formal/README.md)

## Структура проекта

```
re_rl/
├── tasks/
│   ├── math/              # Математические задачи (34 типа)
│   ├── physics/           # Физические задачи (18 типов)
│   └── formal/            # Formal Math — см. formal/README.md
│       ├── lean_navigator/    # Подход LeanNavigator (BFS + Pantograph + RAG)
│       │   ├── core.py            # BFS exploration + PantographDojo + TacticRAG
│       │   ├── rag_trainer.py     # Обучение BERT retriever (triplet loss)
│       │   └── ...
│       ├── lean_proof_task.py # Шаблонные задачи (без зависимостей)
│       └── ...
├── dataset_generator.py   # Генератор датасетов
├── environments/          # RL окружения
scripts/
└── fast_trace.py          # Трейсинг Mathlib4
examples/
├── formal/                    # ← Formal Math примеры и скрипты
│   ├── Formal_Math_Generation.ipynb  # Полный pipeline (notebook)
│   ├── extract_mathlib_proofs.py     # Извлечение из Mathlib
│   ├── run_bfs.py                    # BFS генерация (последовательный)
│   ├── run_bfs_parallel.py           # BFS генерация (Ray, параллельный)
│   └── train_rag.py                  # Обучение BERT RAG
├── Генерация_датасета.ipynb      # Генерация math/physics задач
└── test_all_tasks.py             # Тест всех 52 типов задач
```

## Подходит ли для SFT?

**Да!** Данные генерируются в формате, оптимальном для SFT обучения:

1. **Chain-of-Thought**: Каждая задача содержит пошаговое решение
2. **Стандартные форматы**: instruction/input/output (Alpaca), messages (ChatML)
3. **Контроль сложности**: 10 уровней для curriculum learning
4. **Двуязычность**: Можно обучать мультиязычные модели
5. **Верифицируемые ответы**: Все решения математически корректны

### Пример цепочки рассуждений

```
Задача: Найдите энергию связи ядра He-4 (A=4, Z=2).

Шаг 1: Eсв = Δm·c² = [Z·m_p + (A-Z)·m_n - M]·931.5 МэВ
Шаг 2: m_теор = 2×1.007276 + 2×1.008665 = 4.031882 а.е.м.
Шаг 3: Δm = 4.031882 - 4.002603 = 0.029279 а.е.м.
Шаг 4: Eсв = 0.029279 × 931.5 = 27.27 МэВ
Шаг 5: Eсв/A = 27.27/4 = 6.82 МэВ/нуклон

Ответ: Eсв = 27.27 МэВ (6.82 МэВ/нуклон)
```

## Тестирование и бенчмарки

### Быстрая проверка (все задачи)

```bash
# Запуск всех unit-тестов (~1 мин)
pytest tests/

# Тест всех 52 типов задач (math + physics)
python examples/test_all_tasks.py
```

### Formal Math бенчмарк (LeanNavigator)

Требует: `elan` (Lean toolchain), `pantograph`, `faiss-cpu`, `sentence-transformers`.

#### Установка и подготовка

```bash
# Установка Python-пакета
pip install -e .

# Трейсинг Mathlib4 (один раз, ~30-60 мин, результат кэшируется)
python scripts/fast_trace.py --version v4.26.0
```

#### Извлечение данных из Mathlib (быстрый способ)

Напрямую извлекает (state, tactic) пары из traced Mathlib — без BFS.

```bash
# Все теоремы с доказательствами ≥2 шагов
python examples/formal/extract_mathlib_proofs.py --min-proof-length 2

# Только определённый модуль
python examples/formal/extract_mathlib_proofs.py --module-prefix Mathlib.Algebra --max-theorems 10000

# SFT формат для обучения
python examples/formal/extract_mathlib_proofs.py --output-format sft
```

#### BFS Exploration (новые пути)

Генерирует альтернативные доказательства через BFS — данные, которых нет в Mathlib.

```bash
# Базовый запуск
python examples/formal/run_bfs.py --max-theorems 100 --decompose-auto

# С запретом автоматизаторов (для длинных путей)
python examples/formal/run_bfs.py --max-theorems 50 --no-auto --min-proof-length 3

# Параллельно (Ray, быстрее)
python examples/formal/run_bfs_parallel.py --workers 8 --max-theorems 500 --decompose-auto
```

#### Бенчмарк: Pretrained SBERT vs Обученный BERT

```bash
# Прогон 1: Pretrained SBERT
python examples/formal/run_bfs.py --seed 42 --max-theorems 50 --rag-model sbert

# Обучение BERT retriever
python examples/formal/train_rag.py

# Прогон 2: Обученный BERT (те же теоремы)
python examples/formal/run_bfs.py --seed 42 --max-theorems 50 --rag-model trained
```

Результаты сохраняются в `datasets/formal_math_data/`.

Подробная документация: [`re_rl/tasks/formal/README.md`](re_rl/tasks/formal/README.md) и [`examples/formal/README.md`](examples/formal/README.md)

## Лицензия

MIT License
