#!/usr/bin/env python3
"""
Обучение BERT-based RAG retriever для тактик Lean 4.

Воспроизводит подход из LeanNavigator (tactic_proximity.ipynb):
  1. Генерирует triplet data из traced Mathlib4
  2. Обучает BERT с triplet loss (contrastive learning)
  3. Строит FAISS L2 индекс для поиска тактик
  4. Сохраняет модель для использования в BFS

Использование:
    # Полное обучение (первый раз ~30-60 мин на GPU)
    python examples/train_rag.py

    # Быстрый тест (ограниченные данные)
    python examples/train_rag.py --max-files 100 --num-epochs 1 --batch-size 32

    # С hard negative mining (дольше, но лучше качество)
    python examples/train_rag.py --hard-negatives 1

    # Использовать меньшую модель (быстрее, менее точно)
    python examples/train_rag.py --model-name prajjwal1/bert-tiny

Предварительно нужен трейсинг Mathlib:
    python scripts/fast_trace.py --version v4.26.0

После обучения — запуск BFS с обученным RAG:
    python examples/run_bfs.py --rag-model trained
"""

import argparse
import os
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Обучение BERT RAG retriever для тактик Lean 4",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python examples/train_rag.py                              # полное обучение
  python examples/train_rag.py --max-files 100              # быстрый тест
  python examples/train_rag.py --hard-negatives 1           # с hard negatives
  python examples/train_rag.py --model-name prajjwal1/bert-tiny  # маленькая модель
        """,
    )
    parser.add_argument("--mathlib-version", default="v4.26.0",
                        help="Версия Mathlib4 (default: v4.26.0)")
    parser.add_argument("--model-name", default="bert-base-uncased",
                        help="HuggingFace модель (default: bert-base-uncased)")
    parser.add_argument("--num-epochs", type=int, default=1,
                        help="Число эпох (default: 1)")
    parser.add_argument("--batch-size", type=int, default=64,
                        help="Размер батча (default: 64)")
    parser.add_argument("--lr", type=float, default=1e-5,
                        help="Learning rate (default: 1e-5)")
    parser.add_argument("--margin", type=float, default=1.0,
                        help="Triplet loss margin (default: 1.0)")
    parser.add_argument("--min-template-freq", type=int, default=3,
                        help="Мин частота шаблона (default: 3)")
    parser.add_argument("--max-files", type=int, default=0,
                        help="Макс AST файлов для triplet генерации (0=все, default: 0)")
    parser.add_argument("--hard-negatives", type=int, default=0,
                        help="Раундов hard negative mining (default: 0)")
    parser.add_argument("--output-dir", default=None,
                        help="Директория для модели (default: auto)")
    parser.add_argument("--device", default=None,
                        help="cuda/cpu (default: auto)")
    return parser.parse_args()


def main():
    args = parse_args()

    # Пути
    CACHE_BASE = Path.home() / ".cache" / "re_rl"
    REPO_DIR = CACHE_BASE / f"mathlib4-{args.mathlib_version}" / "mathlib4"
    NAV_DATA = CACHE_BASE / f"mathlib4-{args.mathlib_version}" / "navigator_data"

    if args.output_dir:
        OUTPUT_DIR = Path(args.output_dir)
    else:
        OUTPUT_DIR = NAV_DATA / "trained_rag"

    # Проверка трейсинга
    if not (REPO_DIR.parent / ".step_5_done").exists():
        print(f"ОШИБКА: Трейсинг не выполнен для {args.mathlib_version}")
        print(f"  Запустите: python scripts/fast_trace.py --version {args.mathlib_version}")
        sys.exit(1)

    # Проверка зависимостей
    try:
        import torch
        print(f"PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}")
    except ImportError:
        print("ОШИБКА: pip install torch")
        sys.exit(1)

    try:
        import transformers
        print(f"Transformers: {transformers.__version__}")
    except ImportError:
        print("ОШИБКА: pip install transformers")
        sys.exit(1)

    try:
        import faiss
        print(f"FAISS: OK")
    except ImportError:
        print("ОШИБКА: pip install faiss-cpu")
        sys.exit(1)

    print()
    print(f"КОНФИГУРАЦИЯ")
    print(f"{'=' * 60}")
    print(f"  Mathlib:          {args.mathlib_version}")
    print(f"  Модель:           {args.model_name}")
    print(f"  Эпохи:            {args.num_epochs}")
    print(f"  Batch size:       {args.batch_size}")
    print(f"  LR:               {args.lr}")
    print(f"  Margin:           {args.margin}")
    print(f"  Max files:        {args.max_files if args.max_files > 0 else 'все'}")
    print(f"  Hard negatives:   {args.hard_negatives}")
    print(f"  Output:           {OUTPUT_DIR}")
    print()

    # Кэшированные шаблоны
    templates_path = str(NAV_DATA / "tactic_templates.json")
    if not Path(templates_path).exists():
        templates_path = None

    # Кэшированные тройки
    triplets_path = str(OUTPUT_DIR / "triplets.json")
    if not Path(triplets_path).exists():
        triplets_path = None

    # Импорт и запуск
    # Добавляем проект в PATH
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from re_rl.tasks.formal.lean_navigator import train_tactic_rag

    model_path = train_tactic_rag(
        repo_dir=str(REPO_DIR),
        output_dir=str(OUTPUT_DIR),
        templates_path=templates_path,
        triplets_path=triplets_path,
        model_name=args.model_name,
        num_epochs=args.num_epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        margin=args.margin,
        min_template_freq=args.min_template_freq,
        max_files=args.max_files,
        hard_negative_rounds=args.hard_negatives,
        device=args.device,
    )

    print(f"\nМодель сохранена: {model_path}")
    print(f"\nДля использования в BFS:")
    print(f"  python examples/run_bfs.py --rag-model {model_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
