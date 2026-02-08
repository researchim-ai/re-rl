# Formal Math Generation (Lean 4 + Mathlib4)

Инструменты для генерации данных для theorem proving.

## Файлы

| Файл | Описание |
|------|----------|
| `Formal_Math_Generation.ipynb` | **Главный notebook** — полный pipeline |
| `extract_mathlib_proofs.py` | Извлечение готовых доказательств из Mathlib |
| `run_bfs.py` | BFS exploration (последовательный) |
| `run_bfs_parallel.py` | BFS exploration (параллельный, Ray) |
| `train_rag.py` | Обучение кастомного BERT RAG |

## Быстрый старт

### 1. Трейсинг Mathlib (один раз, ~60 мин)

```bash
python scripts/fast_trace.py --version v4.26.0
```

### 2. Генерация данных

**Вариант A: Jupyter notebook (рекомендуется)**
```bash
cd examples/formal
jupyter notebook Formal_Math_Generation.ipynb
```

**Вариант B: Командная строка**

```bash
# Извлечение из Mathlib (быстро, ~100k+ pairs)
python examples/formal/extract_mathlib_proofs.py \
    --min-proof-length 2 \
    --max-theorems 50000

# BFS exploration (новые пути, медленнее)
python examples/formal/run_bfs.py \
    --max-theorems 100 \
    --max-steps 10000 \
    --decompose-auto

# BFS параллельно (быстрее)
python examples/formal/run_bfs_parallel.py \
    --max-theorems 1000 \
    --workers 8
```

## Два источника данных

### Mathlib Extraction
- **Что**: Готовые доказательства из Mathlib
- **Плюсы**: Быстро, много данных, реальные человеческие доказательства
- **Минусы**: Только один путь на теорему

### BFS LeanNavigator
- **Что**: Исследование альтернативных путей через BFS
- **Плюсы**: Новые данные, которых нет в Mathlib; data augmentation
- **Минусы**: Медленнее

**Рекомендация**: Комбинировать оба источника.

## Параметры BFS

| Параметр | Описание |
|----------|----------|
| `--max-theorems` | Сколько теорем исследовать |
| `--max-steps` | Шагов BFS на теорему |
| `--max-time` | Секунд на теорему |
| `--no-auto` | Запретить simp/aesop (для длинных путей) |
| `--decompose-auto` | Раскладывать simp на отдельные шаги |
| `--min-proof-length` | Фильтр пар по длине пути |
| `--rag-model` | `sbert` (default) или `trained` |

## Форматы вывода

| Формат | Использование |
|--------|---------------|
| `jsonl` | Streaming, большие датасеты |
| `sft` | Supervised fine-tuning |
| `chat` | Chat fine-tuning |
