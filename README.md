# re-rl

Библиотека для генерации математических и физических задач с пошаговыми решениями для обучения LLM навыкам reasoning (Chain-of-Thought).

## Особенности

- **232 типов задач**: 162 математических (включая формальную математику Lean 4 и логические/ризонинг-головоломки) + 70 физических
- **Визуальные (VLM) задачи**: 32 типа с генерацией изображений — графики функций, столбчатые/круговые/линейные диаграммы, гистограммы, диаграммы Венна, площадь по графику, графики движения (v–t и траектории), геометрия, аналоговые часы, кости, шахматная доска, цветная сетка, взвешенные/ориентированные графы (кратчайший путь, MST, раскраска, топ-сортировка, макс. поток), диаграммы ДКА, схемы логических вентилей, «Сапёр», «Мастермайнд», ферзи, «Жизнь» Конвея, магический квадрат, лабиринт, P–V диаграммы, многоугольники, а также картиночные варианты судоку/пятнашек/ARC — картинка + текстовый ответ, плюс аугментации изображений
- **Языки**: русский и английский
- **Система сложности**: 10 уровней для каждого типа задач
- **Пошаговые решения**: детальные цепочки рассуждений для SFT/RL обучения
- **Форматы экспорта**: JSON, JSONL, SFT-формат, Chat-формат, мультимодальный (`generate_vlm_dataset`)

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

### Математика (162 типов)

| Категория | Задачи |
|-----------|--------|
| **Алгебра** | linear, quadratic, cubic, system_linear, exponential, logarithmic, inequality, symbolic_simplification, polynomial_factorization, vieta |
| **Анализ** | calculus, limits, integral, differential_equation, series, optimization, taylor_series, partial_fractions, partial_derivatives, area_between_curves, lhopital, symbolic_regression |
| **Геометрия** | geometry, trigonometry, vector_3d, coordinate_geometry, shoelace_area, triangle_solving, conic_sections |
| **Линейная алгебра** | matrix, complex_number, matrix_reasoning, gaussian_elimination, matrix_multiplication, gram_schmidt, least_squares, roots_of_unity |
| **Дискретная математика** | number_theory, combinatorics, sequence, set_logic, graph, dynamic_programming, base_conversion, modular_arithmetic, recurrence, prime_factorization, diophantine, modular_inverse, continued_fraction, generating_function |
| **Абстрактная алгебра** | group_theory, category_theory |
| **Теория вероятностей** | urn_probability, statistics, bayesian_reasoning, expected_value, markov_chain, conditional_probability, hypothesis_testing |
| **Прикладная** | financial_math, arithmetic |
| **Логика и планирование** | contradiction, knights_knaves, futoshiki, analogical, text_stats, sudoku, zebra_puzzle, csp_reasoning, sat_smt_mini, propositional_logic, regex_dfa, find_the_error, cryptarithmetic, inequality_proof, river_crossing, tower_of_hanoi, water_jug, blocks_world, nim_game |
| **Ризонинг и дедукция** | graph_reasoning, ordering_puzzle, state_tracking, grid_navigation, interval_scheduling, set_reasoning, pattern_induction, syllogism, logical_entailment, boolean_circuit, mastermind, countdown_24, game_theory_optimal, family_tree, minesweeper_deduction |
| **CSP-головоломки (сетки)** | n_queens, magic_square, skyscrapers, kenken, kakuro, nonogram, binary_puzzle, hitori, star_battle, battleship |
| **Графы и оптимизация** | weighted_shortest_path, topological_sort, graph_coloring, mst_weight, eulerian_path, hamiltonian_path, bipartite_matching, tsp, max_flow, dag_longest_path, knapsack, subset_sum |
| **Формальная логика и вычисления** | truth_table, model_counting, three_sat, logical_equivalence, qbf, dfa_simulation, turing_machine, game_of_life, elementary_ca, rpn_eval, balanced_brackets, sorting_trace |
| **Дедукция и игры** | logic_grid, seating_circular, tournament, combinatorial_games, tic_tac_toe |
| **Пространственное мышление и прочее** | cube_net, dice_reasoning, rotation_reflection, paper_folding, cipher_decode, pigeonhole, monty_hall, allen_relations |
| **Продвинутый ризонинг** | arc_grid_induction, program_trace, sprague_grundy, natural_deduction, edit_distance, calendar_reasoning, word_ladder, cfg_membership |
| **Логика, вывод и алгоритмы** | datalog_inference, unification, lambda_calculus, resolution, lis_dp, kmp_matching, sliding_puzzle |

### Физика (70 типов)

| Категория | Задачи |
|-----------|--------|
| **Механика** | kinematics, dynamics, energy, momentum, projectile_motion, rotational_dynamics, center_of_mass, atwood_machine, inclined_plane, statics_equilibrium, circular_dynamics, rolling_motion, elasticity, terminal_velocity, elastic_chain, composite_inertia |
| **Электричество и магнетизм** | circuits, electrostatics, capacitors, electromagnetic_induction, ac_circuits, rc_circuits, magnetism, magnetic_force, kirchhoff_laws, rl_circuits, gauss_law, transformer, wheatstone_bridge |
| **Термодинамика** | gas_laws, heat_transfer, thermodynamic_cycles, entropy, phase_transitions, kinetic_theory, thermal_expansion, blackbody_radiation, gas_work, mean_free_path, pv_cycle, calorimetry_mix |
| **Волны, оптика и звук** | waves, optics, doppler_effect, interference, diffraction, polarization, standing_waves, sound_intensity, beats, abcd_optics |
| **Квантовая физика** | quantum, bohr_model, de_broglie, uncertainty_principle, radioactive_decay, radiation_pressure, pair_production |
| **Ядерная физика** | nuclear |
| **Теория относительности** | relativity, relativistic_energy, velocity_addition |
| **Колебания** | oscillations |
| **Гидростатика и гидродинамика** | fluids, surface_tension |
| **Астрофизика** | astrophysics |
| **Измерения и анализ** | dimensional_analysis, error_propagation, unit_conversion |
| **Масштабируемые сети** | series_parallel_network (резисторы/конденсаторы/пружины/тепловые сопротивления) |

### Визуальные (VLM) задачи

Мультимодальные задачи: изображение + вопрос → текстовый ответ (проверка `verify` без изменений). Реестр — `ALL_VISUAL_TASK_GENERATORS` (отдельно от текстового `ALL_TASK_GENERATORS`).

| Тип | Бэкенд | Подтипы |
|---|---|---|
| `function_plot_read` | matplotlib | count_roots, y_intercept |
| `bar_chart_read` | matplotlib | max_category, min_category, difference, total |
| `grid_color_count` | PIL | count_color, most_color |
| `geometry_figure` | matplotlib | right_triangle_area, perimeter, missing_angle |
| `line_plot_read` | matplotlib | value_at, max_x, num_increases |
| `pie_chart_read` | matplotlib | largest, smallest |
| `clock_read` | PIL | чтение времени по циферблату (Ч:ММ) |
| `dice_read` | PIL | sum, count_value |
| `chessboard_count` | PIL | total, on_dark, on_light |
| `sudoku_image` | PIL | судоку-картинка: число в выделенной клетке |
| `sliding_puzzle_image` | PIL | пятнашки-картинка: solvable, min_moves |
| `arc_grid_image` | PIL | ARC-индукция на цветных сетках |
| `shortest_path_image` | networkx | взвешенный граф: вес кратчайшего пути |
| `mst_image` | networkx | взвешенный граф: вес минимального остовного дерева |
| `dfa_image` | matplotlib | диаграмма ДКА: принимает ли строку |
| `boolean_circuit_image` | matplotlib | схема вентилей: evaluate, count |
| `minesweeper_image` | PIL | поле «Сапёра»: мина/безопасно |
| `queens_check_image` | PIL | ферзи на доске: корректна ли расстановка |
| `mastermind_image` | PIL | доска «Мастермайнда»: восстановить код |
| `pv_cycle_image` | matplotlib | P–V диаграмма: работа за цикл (площадь) |
| `shoelace_image` | matplotlib | многоугольник по вершинам: площадь |
| `venn_diagram` | matplotlib | диаграмма Венна: intersection, union, only_a, sym_diff |
| `area_read` | matplotlib | площадь по графику: under_curve, between_curves |
| `stats_histogram` | matplotlib | гистограмма: mode, median, range |
| `kinematics_graph` | matplotlib | график v(t): displacement, acceleration |
| `projectile_graph` | matplotlib | траектория-парабола: range, max_height |
| `graph_coloring_image` | networkx | граф: хроматическое число / k-раскрашиваемость |
| `topological_sort_image` | networkx | орграф: топ-порядок / наличие цикла |
| `max_flow_image` | networkx | сеть с пропускными: максимальный поток |
| `game_of_life_image` | PIL | «Жизнь» Конвея: поле через k шагов |
| `magic_square_image` | PIL | магический квадрат 3×3 с пропусками |
| `grid_navigation_image` | PIL | лабиринт: длина кратчайшего пути |

Дополнительно доступна лёгкая аугментация изображений `augment_image(img, seed=...)` (небольшой поворот на белом фоне) — верификация текстовая, поэтому корректность ответа не меняется.

```python
from re_rl.tasks.visual.generators import ALL_VISUAL_TASK_GENERATORS

task = ALL_VISUAL_TASK_GENERATORS["bar_chart_read"](language="ru", difficulty=6)
task.render_image().save("chart.png")   # PIL.Image
print(task.description, "→", task.final_answer)

# Мультимодальный датасет (PNG на диск + JSONL с путём и токеном <image>)
from re_rl.dataset_generator import DatasetGenerator
gen = DatasetGenerator(output_dir="datasets_vlm")
vlm = gen.generate_vlm_dataset(num_samples=100, language="ru", difficulties=[3, 5, 7])
gen.save_jsonl(vlm, "vlm.jsonl", validate=False)
```

Подробности и инлайн-картинки — в `examples/Визуальные_задачи.ipynb`.

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

Помимо текстовых задач, RE-RL воспроизводит pipeline генерации training data из формальных доказательств Lean 4 по подходу [LeanNavigator](https://arxiv.org/abs/2503.04772) (Yin & Gao, 2025) — BFS-обход графа состояний Mathlib4 через Pantograph с BERT+FAISS retrieval тактик.

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
