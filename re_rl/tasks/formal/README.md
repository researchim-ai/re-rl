# Formal Math: генерация данных для Theorem Proving (LeanNavigator)

Воспроизведение pipeline из [LeanNavigator](https://arxiv.org/abs/2503.04772) (Yin & Gao, 2025) — генерация **миллионов** training pairs из формальных доказательств Lean 4 через BFS-обход графа состояний.

## Идея

В Lean 4 доказательство — последовательность **переходов между состояниями**. Тактика трансформирует текущее состояние (гипотезы + цель) в новое, пока не достигнуто `ProofFinished`. LeanNavigator рассматривает это как **граф** и обходит его через BFS:

```
State₀ (goal теоремы)
  ├── omega       → ProofFinished ✓   ← training pair (distance=0)
  ├── norm_cast   → ProofFinished ✓   ← training pair (distance=0)
  ├── induction a → SubGoal₁, SubGoal₂ ← training pair (distance=2)
  │     └── simp  → ProofFinished ✓
  └── congr       → сложные подцели   ← training pair (branch)
```

Каждый успешный переход `(state, tactic) → next_state` записывается как **training pair**. Из одной теоремы получаются десятки пар — модель учится не только "как доказать", но и "какие тактики вообще применимы".

## Как BERT + FAISS помогает в BFS

Главная проблема BFS — **огромное пространство поиска**. В Mathlib 200+ встроенных тактик, тысячи лемм, а каждая тактика может принимать разные аргументы. Перебирать всё подряд — невозможно (одна тактика в Lean проверяется ~0.12с).

BERT + FAISS решают эту задачу: для каждого proof state система находит **200 наиболее релевантных шаблонов тактик** за миллисекунды, вместо перебора всех 60K+.

### Алгоритм одной итерации BFS

```
┌─────────────────────────────────────────────────────────────────┐
│  Текущее состояние из очереди (PriorityQueue):                  │
│                                                                 │
│    α : Type u_1                                                 │
│    inst✝ : Fintype α                                            │
│    s : Finset α                                                 │
│    ⊢ s.card ≤ Fintype.card α                                    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. КЛАССИФИКАЦИЯ СОСТОЯНИЯ                                     │
│     classify_lean_elements(state.pp) →                           │
│       α       → type                                            │
│       inst✝   → unknown                                         │
│       s       → variable                                        │
│       Гипотезы, переменные, типы → словарь type_of_item         │
│                                                                 │
│  2. RAG RETRIEVAL (BERT + FAISS)                                │
│     query = theorem_code + ' # ' + state.pp                     │
│     BERT encode(query) → embedding [768 dim]                    │
│     FAISS L2 search → top-200 ближайших шаблонов:               │
│       "exact {hypothesis}"          (similarity=0.92)           │
│       "simp [{hypothesis}]"         (similarity=0.87)           │
│       "apply Finset.card_le_univ"   (similarity=0.85)           │
│       "rw [{hypothesis}]"           (similarity=0.81)           │
│       ...ещё 196 шаблонов                                       │
│                                                                 │
│  3. ИНСТАНЦИАЦИЯ ШАБЛОНОВ                                       │
│     Подставляем переменные из type_of_item:                     │
│       "exact {hypothesis}" → ["exact inst✝"]                    │
│       "simp [{hypothesis}]" → ["simp [inst✝]"]                  │
│       "apply Finset.card_le_univ" → ["apply Finset.card_le_univ"]│
│       ...до MAX_TACTIC_FROM_TEMPLATE=50 на шаблон               │
│     + обратные rw: "rw [← ...]" для каждой "rw [...]"           │
│                                                                 │
│  4. ПРИМЕНЕНИЕ ТАКТИК (через Pantograph)                        │
│     Для каждой конкретной тактики:                               │
│       goal_tactic(state, "apply Finset.card_le_univ")           │
│         → ProofFinished ✓  (записываем пару, distance=0)        │
│       goal_tactic(state, "simp [inst✝]")                        │
│         → новое состояние  (добавляем в очередь)                │
│       goal_tactic(state, "exact inst✝")                         │
│         → ошибка типов     (пропускаем)                         │
│                                                                 │
│  5. ПРИОРИТЕТ НОВЫХ СОСТОЯНИЙ                                   │
│     complexity = длина цели + штраф за повторные подцели         │
│     state_queue.push(new_state, complexity + random(0,4))        │
│     → простые состояния обрабатываются первыми                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Почему это работает

**Без RAG**: нужно перебирать ~60K шаблонов × N аргументов = миллионы вариантов на одно состояние. BFS практически стоит на месте.

**С RAG**: BERT+FAISS за ~1мс выдаёт 200 релевантных шаблонов → ~2000 конкретных тактик. Из них ~5-50 проходят type-checking в Lean. Скорость: **~2000 состояний/мин** (оригинал) vs **~20 состояний/мин** (ReProver с генеративной моделью).

### Обучение vs Pretrained

| | Pretrained (sentence-transformers) | Обученный BERT (triplet loss) |
|---|---|---|
| Как ищет | Косинусная близость текстов | L2 расстояние в пространстве "state→tactic" |
| Знает ли Lean | Нет — `simp` и `simple` будут рядом | Да — учился на реальных (state, tactic) парах |
| Качество | Находит текстово похожие шаблоны | Находит **семантически подходящие** шаблоны |
| Результат на 50 теоремах | ~11 доказано | Ожидаемо больше (после обучения) |

## Масштаб оригинала

| Метрика | LeanNavigator |
|---|---|
| Репозиторий | Mathlib4 (100K+ теорем) |
| Результат | 4.7M теорем, 1B токенов |
| RAG модель | GPTNeo-350M + FAISS L2 (contrastive learning) |
| Prover модель | Flan-T5 (350M) → превосходит ReProver |
| Ресурсы | 24 процесса × 28 дней (RAY) |

## Наша реализация

| Компонент | Оригинал (LeanNavigator) | Наша реализация |
|---|---|---|
| Lean interaction | LeanDojo (Lean4Repl) | **Pantograph** (pypantograph) |
| Трейсинг | lean-dojo trace() | **scripts/fast_trace.py** (ExtractData.lean) |
| RAG embedding | Custom BERT (contrastive) | **BERT + triplet loss** (обучаемый) |
| FAISS | IndexFlatL2 | **IndexFlatL2** (идентично) |
| BFS | ExploreStates + PriorityQueue | **LeanNavigatorExplorer** (идентично) |
| Шаблоны тактик | parse_lean_state_and_tactic | **parse_lean_state_and_tactic** (идентично) |

---

## Пошаговое воспроизведение

### Шаг 0: Системные зависимости

```bash
# Lean 4 toolchain (elan)
curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh
source ~/.profile  # или перезапустите терминал

# Проверка
elan --version   # elan 4.x
lake --version   # должен быть доступен

# Python зависимости
pip install -e .
# Или напрямую из requirements.txt:
pip install -r requirements.txt
```

Основные Python-пакеты: `pantograph`, `faiss-cpu`, `sentence-transformers`, `torch`, `transformers`, `tqdm`, `loguru`, `nest-asyncio`.

### Шаг 1: Трейсинг Mathlib4

Компилируем Mathlib4 и извлекаем AST-данные (тактики, состояния, позиции). Это нужно сделать **один раз**, результат кэшируется в `~/.cache/re_rl/`.

```bash
python scripts/fast_trace.py --version v4.26.0
```

Что происходит:
1. `git clone --depth 1 --branch v4.26.0` Mathlib4
2. `lake exe cache get` — скачивание бинарных кэшей из Reservoir
3. `lake build` — компиляция (~15-30 мин)
4. Копирование `ExtractData.lean` в Mathlib
5. `lake build ExtractData` — извлечение `.ast.json` файлов с тактиками

Результат: `~/.cache/re_rl/mathlib4-v4.26.0/mathlib4/.lake/build/ir/**/*.ast.json`

**Время**: ~30-60 мин (первый раз), потом мгновенно (кэш).

### Шаг 2: Извлечение шаблонов тактик

Из `.ast.json` + `.lean` исходников извлекаются шаблоны тактик. Каждая конкретная тактика (например `rw [mul_comm a b]`) преобразуется в шаблон (`rw [mul_comm {variable} {variable}]`).

Это можно сделать через скрипт BFS (шаг 4) или отдельно:

```python
from re_rl.tasks.formal import TacticTemplateExtractor

extractor = TacticTemplateExtractor()
extractor.extract_from_ast_dir("~/.cache/re_rl/mathlib4-v4.26.0/mathlib4")
extractor.save("tactic_templates.json")

print(f"Шаблонов: {len(extractor.templates)}")  # ~60K+ уникальных
for tmpl, freq in extractor.get_top_templates(10):
    print(f"  [{freq}] {tmpl}")
```

**Время**: ~2-5 мин.

### Шаг 3: Обучение RAG retriever (BERT + triplet loss)

Ключевой компонент — embedding модель, которая по proof state находит релевантные шаблоны тактик. Авторы используют contrastive learning с triplet loss.

```bash
# Полное обучение (~30-60 мин на GPU, несколько часов на CPU)
python examples/train_rag.py

# Быстрый тест (для проверки что всё работает)
python examples/train_rag.py --max-files 100 --num-epochs 1 --batch-size 32

# С hard negative mining (лучше качество, дольше)
python examples/train_rag.py --hard-negatives 1

# Маленькая модель (быстрее, менее точно)
python examples/train_rag.py --model-name prajjwal1/bert-tiny
```

Что происходит:
1. **Генерация triplets**: для каждой тактики в traced данных создаётся тройка
   - query = `theorem_code + ' # ' + state_before`
   - positive = шаблон тактики, которая была реально применена
   - negative = случайный шаблон (или hard negative из FAISS)
2. **Обучение BERT**: `bert-base-uncased` + TripletLoss(margin=1.0), Adam lr=1e-5
3. **Построение FAISS L2 index** из обученных embeddings

Результат: `~/.cache/re_rl/mathlib4-v4.26.0/navigator_data/trained_rag/`

> **Примечание**: Можно пропустить этот шаг — BFS будет работать с pretrained `all-MiniLM-L6-v2` (sentence-transformers), но качество retrieval будет ниже.

### Шаг 4: BFS exploration (генерация training pairs)

Основной шаг — обход графа состояний через Pantograph:

```bash
# С обученным RAG (после шага 3)
python examples/run_bfs.py --rag-model trained --max-theorems 50

# С pretrained RAG (без шага 3)
python examples/run_bfs.py --max-theorems 50

# Быстрый тест (5 теорем)
python examples/run_bfs.py --max-theorems 5 --max-steps 3000 --max-time 15 --verbose

# Полный прогон (может занять часы)
python examples/run_bfs.py --max-theorems 500 --max-steps 50000 --max-time 300
```

Что происходит:
1. Загрузка теорем из Lean окружения через `env_catalog` + `env_inspect`
2. Для каждой теоремы запускается BFS:
   - `goal_start(theorem_type)` → начальное состояние
   - RAG retrieval → top-200 шаблонов тактик
   - Инстанциация шаблонов переменными из состояния
   - `goal_tactic(state, tactic)` → новое состояние
   - Приоритетная очередь по сложности состояния
   - Остановка при `ProofFinished` или лимите
3. Все пары `(state, tactic, next_state, distance_to_proof)` сохраняются

Результат: `datasets/formal_math_data/lean_data_*.jsonl`

**Время**: ~1-5 мин на 50 теорем; часы-дни для полного Mathlib.

### Шаг 5 (опционально): Обучение prover-модели

Используя сгенерированный датасет, можно дообучить LLM:

```python
from datasets import load_dataset

dataset = load_dataset("json", data_files="datasets/formal_math_data/lean_data_*.jsonl")
# Формат: {"state": "...", "tactic": "...", "next_state": "...", "distance_to_proof": N}
```

Авторы обучали Flan-T5 (350M) и получили SOTA на MIL и MiniF2F бенчмарках.

---

## Ноутбук

Все шаги 1-4 также доступны в интерактивном режиме:

[`examples/Formal_Math_Generation.ipynb`](../../examples/Formal_Math_Generation.ipynb)

---

## Архитектура модулей

```
re_rl/tasks/formal/
├── __init__.py                # Общий init + реэкспорт из lean_navigator
├── lean_proof_task.py         # Общий: шаблонные задачи на доказательство
├── theorem_templates.py       # Общий: 24+ шаблонов теорем
├── tactic_generator.py        # Общий: rule-based генерация тактик
├── lean_utils.py              # Общий: парсинг Lean состояний
├── setup_lean_repos.py        # Общий: скачивание и настройка Lean репо
├── ExtractData.lean           # Lean скрипт извлечения AST
│
└── lean_navigator/            # ═══ Подход LeanNavigator ═══
    ├── __init__.py                # Реэкспорт всех компонентов
    ├── core.py                    # Основной pipeline (~1900 строк)
    │   ├── TacticTemplateExtractor    # Извлечение шаблонов из .ast.json
    │   ├── TacticRAG                  # Pretrained SBERT + FAISS IP
    │   ├── PantographDojo             # Обёртка Pantograph Server (per-file + shared)
    │   ├── LeanNavigatorExplorer      # BFS exploration с per-file fallback
    │   └── load_theorems_from_env     # Загрузка теорем из Lean environment
    ├── rag_trainer.py             # Обучение BERT retriever
    │   ├── TripletDataGenerator       # Генерация обучающих троек
    │   ├── TacticBERTTrainer          # BERT + TripletLoss обучение
    │   └── TrainedTacticRAG           # Drop-in замена TacticRAG
    ├── state_explorer.py          # BFS по графу состояний
    ├── dataset_generator.py       # Оркестрация генерации
    ├── lean_utils.py              # Парсинг Lean состояний
    └── ml_tactic_generator.py     # ML-ускорение (HF, API)

scripts/
└── fast_trace.py              # Трейсинг Mathlib4 (шаг 1)

examples/
├── Formal_Math_Generation.ipynb   # Интерактивный notebook
├── run_bfs.py                     # BFS скрипт (шаг 4)
└── train_rag.py                   # Обучение RAG (шаг 3)
```

> Будущие подходы добавляются как `re_rl/tasks/formal/<approach_name>/`

## Ключевые параметры (из оригинальной статьи)

| Параметр | Значение | Описание |
|---|---|---|
| `MAX_STEPS` | 200,000 | Макс переходов BFS на теорему |
| `MAX_TACTIC_FROM_TEMPLATE` | 50 | Макс тактик из одного шаблона |
| `MAX_DISTANCE` | 8 | Макс расстояние до ProofFinished |
| `MAX_NUM_OUTPUT_PER_STATE` | 50 | Макс новых состояний из одного |
| RAG top-k | 200 | Шаблонов из FAISS на запрос |
| Triplet margin | 1.0 | Margin для contrastive loss |
| BERT lr | 1e-5 | Learning rate обучения retriever |

## Training Pair формат

```json
{
  "state": "a b c : Nat\n⊢ a + b + c = a + c + b",
  "tactic": "omega",
  "next_state": "ProofFinished",
  "distance_to_proof": 0,
  "theorem_name": "Nat.add_right_comm"
}
```

## Форматы экспорта

### JSONL (для обучения)

```jsonl
{"state": "a b c : Nat\n⊢ a + b + c = a + c + b", "tactic": "omega", "distance_to_proof": 0}
{"state": "a : Nat\n⊢ a + 1 = Nat.succ a", "tactic": "rfl", "distance_to_proof": 0}
```

### SFT формат

```json
{
  "instruction": "You are a Lean 4 theorem prover. Given the current proof state, suggest the next tactic.",
  "input": "Current proof state:\na b c : Nat\n⊢ a + b + c = a + c + b",
  "output": "omega"
}
```

### Chat формат

```json
{
  "messages": [
    {"role": "system", "content": "You are an expert Lean 4 theorem prover."},
    {"role": "user", "content": "Prove this goal:\n```\na b c : Nat\n⊢ a + b + c = a + c + b\n```"},
    {"role": "assistant", "content": "omega"}
  ]
}
```

## Ссылки

- [LeanNavigator Paper](https://arxiv.org/abs/2503.04772) — оригинальная статья
- [Pantograph](https://github.com/stanford-centaur/PyPantograph) — Lean 4 machine-to-machine API
- [Mathlib4](https://github.com/leanprover-community/mathlib4) — библиотека математики Lean 4