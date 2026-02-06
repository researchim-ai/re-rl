# RE-RL Formal Math: Генерация данных для обучения theorem provers

Модуль для генерации обучающих данных из формальных доказательств Lean 4.
Реализует подход из статьи **LeanNavigator** — систематическое исследование графов переходов состояний.

## Обзор

```
┌─────────────────────────────────────────────────────────────────────┐
│                         RE-RL Formal Math                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Теорема (Lean)  ──►  StateExplorer (BFS)  ──►  Training Pairs    │
│                              │                                      │
│                              ▼                                      │
│                    ┌─────────────────┐                              │
│                    │  TacticGenerator │                              │
│                    │  (rule-based)    │                              │
│                    └─────────────────┘                              │
│                              │                                      │
│                              ▼                                      │
│                    ┌─────────────────┐                              │
│                    │    LeanDojo     │                              │
│                    │  (Lean 4 API)   │                              │
│                    └─────────────────┘                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Как это работает

### 1. Граф переходов состояний

В Lean доказательство — это последовательность **состояний** (proof states), 
соединённых **тактиками** (tactics):

```
State₀ ──tactic₁──► State₁ ──tactic₂──► State₂ ──tactic₃──► ProofFinished
```

Пример:
```
Начальное состояние:          После "omega":
a b c : Nat                   ProofFinished
⊢ a + b + c = a + c + b       (доказательство завершено)
```

### 2. BFS исследование

Алгоритм `StateExplorer` использует поиск в ширину (BFS) с приоритетной очередью:

1. **Инициализация**: Берём начальное состояние теоремы
2. **Генерация тактик**: Для текущего состояния генерируем кандидаты тактик
3. **Применение**: Применяем каждую тактику через LeanDojo
4. **Расширение**: Успешные новые состояния добавляем в очередь
5. **Сбор данных**: Все пары `(state, tactic)` сохраняем как training data
6. **Завершение**: Достигаем `ProofFinished` или лимитов

### 3. Training Pairs

Результат — пары для обучения LLM:

```json
{
  "state": "a b c : Nat\n⊢ a + b + c = a + c + b",
  "tactic": "omega",
  "next_state": "ProofFinished",
  "distance_to_proof": 0,
  "theorem_name": "hello_world"
}
```

## Быстрый старт

### Установка зависимостей

```bash
# LeanDojo для взаимодействия с Lean
pip install lean-dojo

# Lean version manager (elan)
curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh
```

### Скачивание репозиториев (tracing)

Используйте скрипт `setup_lean_repos.py`:

```bash
# Проверить статус
python -m re_rl.tasks.formal.setup_lean_repos --check

# Список доступных репозиториев
python -m re_rl.tasks.formal.setup_lean_repos --list

# Быстрый тест (1-2 минуты, 2 теоремы)
python -m re_rl.tasks.formal.setup_lean_repos --repo lean4-example

# MiniF2F - олимпиадные задачи (30-60 минут, 493 теоремы)
python -m re_rl.tasks.formal.setup_lean_repos --repo minif2f

# Mathlib4 - полная библиотека (2-4 часа, 100K+ теорем)
python -m re_rl.tasks.formal.setup_lean_repos --repo mathlib4

# Все репозитории
python -m re_rl.tasks.formal.setup_lean_repos --repo all
```

**Важно**: Tracing делается один раз и кэшируется в `~/.cache/lean_dojo/`.

### Базовый пример

```python
from lean_dojo import LeanGitRepo, Theorem, Dojo
from re_rl.tasks.formal import StateExplorer

# Репозиторий с теоремами
repo = LeanGitRepo(
    "https://github.com/yangky11/lean4-example",
    "7b6ecb9ad4829e4e73600a3329baeb3b5df8d23f"
)

# Теорема для исследования
theorem = Theorem(repo, "Lean4Example.lean", "hello_world")

# Создаём explorer
explorer = StateExplorer(
    max_steps=1000,    # Макс. применений тактик
    max_time=120,      # Макс. время (секунды)
    max_depth=10,      # Макс. глубина поиска
    verbose=True,
)

# Запускаем исследование
with Dojo(theorem) as (dojo, state_0):
    result, training_pairs, stats = explorer.explore(
        dojo, 
        state_0, 
        theorem_name=theorem.full_name
    )

print(f"Найдено {len(training_pairs)} training pairs")
print(f"Доказательство: {'найдено' if stats.proof_found else 'не найдено'}")
```

### Генерация датасета

```python
from re_rl.tasks.formal import LeanDatasetGenerator, DatasetConfig

config = DatasetConfig(
    max_theorems=100,
    max_steps_per_theorem=5000,
    max_time_per_theorem=300,
)

generator = LeanDatasetGenerator(config)

# Генерация из репозитория
pairs = generator.generate_from_repo(repo, theorem_list)

# Сохранение
generator.save(pairs, "lean_dataset.jsonl", format="jsonl")
```

## Архитектура модуля

### Основные компоненты

| Файл | Описание |
|------|----------|
| `state_explorer.py` | BFS исследование графа состояний |
| `tactic_generator.py` | Rule-based генерация тактик |
| `lean_utils.py` | Утилиты парсинга Lean состояний |
| `dataset_generator.py` | Оркестрация генерации датасетов |
| `ml_tactic_generator.py` | ML-ускоренная генерация (опционально) |

### StateExplorer

```python
class StateExplorer:
    """BFS исследователь графа состояний."""
    
    def explore(
        self,
        dojo: Dojo,           # LeanDojo instance
        state_0: TacticState, # Начальное состояние
        theorem_name: str,    # Имя теоремы
        exit_on_proof: bool,  # Остановиться после первого доказательства?
    ) -> Tuple[ExplorationResult, List[TrainingPair], ExplorationStats]:
        ...
```

### TacticGenerator

```python
class TacticGenerator:
    """Rule-based генератор тактик."""
    
    def generate(self, state_pp: str, max_count: int = 100) -> List[str]:
        """
        Генерирует тактики для состояния.
        
        Использует:
        - Базовые тактики (rfl, ring, simp, omega, ...)
        - Шаблоны с гипотезами (apply {h}, rw [{h}], ...)
        - Структурные тактики (cases, induction, ...)
        """
        ...
```

### TrainingPair

```python
@dataclass
class TrainingPair:
    state: str              # Состояние перед тактикой
    tactic: str             # Применённая тактика
    next_state: str         # Результирующее состояние
    distance_to_proof: int  # Расстояние до ProofFinished (-1 если неизвестно)
    theorem_name: str       # Исходная теорема
```

## Сравнение с LeanNavigator

| Компонент | LeanNavigator | RE-RL |
|-----------|---------------|-------|
| LeanDojo взаимодействие | ✓ | ✓ |
| BFS по графу состояний | ✓ | ✓ |
| Приоритетная очередь | ✓ | ✓ |
| Rule-based тактики | ✓ | ✓ |
| Сбор training pairs | ✓ | ✓ |
| Embedding retrieval (BERT+FAISS) | ✓ | ⚠️ Опционально |
| Ray параллелизация | ✓ | ❌ Планируется |
| Mathlib4 поддержка | ✓ | ✓ (требует tracing) |

## Форматы вывода

### JSONL (для обучения)

```jsonl
{"state": "a b c : Nat\n⊢ a + b + c = a + c + b", "tactic": "omega"}
{"state": "a : Nat\n⊢ a + 1 = Nat.succ a", "tactic": "rfl"}
```

### SFT формат

```json
{
  "instruction": "Prove the following Lean 4 goal",
  "input": "a b c : Nat\n⊢ a + b + c = a + c + b",
  "output": "omega"
}
```

### Chat формат

```json
{
  "messages": [
    {"role": "system", "content": "You are a Lean 4 theorem prover..."},
    {"role": "user", "content": "State: a b c : Nat\n⊢ a + b + c = a + c + b"},
    {"role": "assistant", "content": "omega"}
  ]
}
```

## Важные замечания

### Первый запуск

При первом использовании репозитория LeanDojo выполняет **tracing** — 
компиляцию и анализ всего Lean кода. Это занимает время:

- `lean4-example`: ~1 минута
- `mathlib4`: несколько часов

После первого раза результат кэшируется в `~/.cache/lean_dojo/`.

### Генерация тактик

Текущая реализация использует **rule-based** генерацию тактик.
Для ускорения (как в LeanNavigator) можно добавить **embedding retrieval**:

```python
from re_rl.tasks.formal import create_ml_generator, StateExplorer

# ML генератор тактик (опционально)
ml_gen = create_ml_generator("embedding", 
    model_name="bert-base-uncased",
    tactics_db="tactics.faiss"
)

explorer = StateExplorer(ml_generator=ml_gen)
```

## Ссылки

- [LeanNavigator Paper](https://arxiv.org/abs/...) — оригинальная статья
- [LeanDojo](https://github.com/lean-dojo/LeanDojo) — API для Lean
- [Mathlib4](https://github.com/leanprover-community/mathlib4) — библиотека математики
- [RE-RL](https://github.com/...) — основной репозиторий

## Пример результатов

```
======================================================================
RE-RL: ПОЛНЫЙ BFS КАК В LEANNAVIGATOR
======================================================================

Теорема: hello_world

РЕЗУЛЬТАТЫ ИССЛЕДОВАНИЯ:
  Результат: success
  Время: 39.42с
  Всего состояний: 47
  Тактик попробовано: 556
  Успешных тактик: 47
  Training pairs: 56
  Доказательство найдено: True
  Максимальная глубина: 3

Пары на пути к ProofFinished:
  [0] "omega" : a b c : Nat ⊢ a + b + c = a + c + b
  [1] "norm_cast" : a b c : Nat ⊢ a + b + c = a + c + b
```
