#!/usr/bin/env python3
"""
Скрипт для скачивания и tracing Lean репозиториев.

Использование:
    # Быстрый тест (1-2 минуты)
    python setup_lean_repos.py --repo lean4-example
    
    # MiniF2F - 493 олимпиадные теоремы (30-60 минут)
    python setup_lean_repos.py --repo minif2f
    
    # Mathlib4 - полная библиотека (2-4 часа)
    python setup_lean_repos.py --repo mathlib4
    
    # Все репозитории
    python setup_lean_repos.py --repo all
    
    # Только проверить что уже скачано
    python setup_lean_repos.py --check

Требования:
    pip install lean-dojo
    curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh
"""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Проверяем установку lean-dojo
try:
    from lean_dojo import LeanGitRepo, trace
    from lean_dojo.data_extraction.trace import get_traced_repo_path
    import lean_dojo.data_extraction.trace as _trace_module
    LEANDOJO_AVAILABLE = True
except ImportError:
    LEANDOJO_AVAILABLE = False
    print("⚠ LeanDojo не установлен. Установите: pip install lean-dojo")


# ============================================================================
# ИСПРАВЛЕННЫЙ ExtractData.lean
# ============================================================================
# lean-dojo 4.20.0 содержит ExtractData.lean с типом TSyntax, который
# несовместим с Lean ≥ v4.7.0. LeanDojo-v2 исправляет это, используя Syntax.
# Мы храним исправленную версию у себя и подставляем её перед tracing.
# Формат выхода (JSON: commandASTs, tactics, premises) идентичен.
#
# Подробнее: https://github.com/lean-dojo/LeanDojo-v2

_OUR_EXTRACT_DATA = Path(__file__).parent / "ExtractData.lean"


def _apply_extractor_fix():
    """Подставляет наш ExtractData.lean вместо стандартного lean-dojo."""
    if not LEANDOJO_AVAILABLE:
        return
    if _OUR_EXTRACT_DATA.exists():
        _trace_module.LEAN4_DATA_EXTRACTOR_PATH = _OUR_EXTRACT_DATA


# ============================================================================
# КОНФИГУРАЦИЯ РЕПОЗИТОРИЕВ
# ============================================================================

REPOS = {
    # === Быстрый тест ===
    "lean4-example": {
        "url": "https://github.com/yangky11/lean4-example",
        "commit": "7b6ecb9ad4829e4e73600a3329baeb3b5df8d23f",
        "description": "Минимальный пример (2 теоремы) — для проверки pipeline",
        "estimated_time": "1-2 минуты",
        "theorems_count": 2,
    },

    # === Бенчмарки ===
    "minif2f": {
        "url": "https://github.com/facebookresearch/miniF2F",
        "commit": "5271ddec788677c815cf818a06f368ef6498a106",
        "description": "Олимпиадные задачи (IMO, AIME) — бенчмарк",
        "estimated_time": "30-60 минут",
        "theorems_count": 493,
    },

    # === Mathlib4 — основная библиотека математики ===
    # Совместимость с Lean до v4.30.0 обеспечивается нашим ExtractData.lean
    # (взят из LeanDojo-v2). Можно использовать любой тег Mathlib4.
    "mathlib4": {
        "url": "https://github.com/leanprover-community/mathlib4",
        "commit": "v4.19.0",
        "description": "Mathlib4 v4.19.0 — 100K+ теорем",
        "estimated_time": "3-6 часов",
        "theorems_count": "100K+",
    },

    # === Учебники ===
    "mathematics-in-lean": {
        "url": "https://github.com/leanprover-community/mathematics_in_lean",
        "commit": "master",
        "description": "Mathematics in Lean (учебник) — бенчмарк MIL",
        "estimated_time": "30-60 минут",
        "theorems_count": "~500",
    },
}


def add_custom_mathlib4(version: str) -> str:
    """
    Добавляет произвольную версию Mathlib4 в REPOS и возвращает ключ.

    Пример:
        key = add_custom_mathlib4("v4.25.0")
        trace_repo(key)
    """
    key = f"mathlib4-{version}"
    if key not in REPOS:
        REPOS[key] = {
            "url": "https://github.com/leanprover-community/mathlib4",
            "commit": version,
            "description": f"Mathlib4 {version}",
            "estimated_time": "3-6 часов",
            "theorems_count": "100K+",
        }
    return key


def get_cache_dir() -> Path:
    """Возвращает директорию кэша LeanDojo."""
    return Path.home() / ".cache" / "lean_dojo"


def list_cached_repos() -> List[str]:
    """Возвращает список закэшированных репозиториев."""
    cache_dir = get_cache_dir()
    if not cache_dir.exists():
        return []
    
    repos = []
    for item in cache_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            repos.append(item.name)
    return repos


def check_elan_installed() -> bool:
    """Проверяет установлен ли elan."""
    elan_path = Path.home() / ".elan" / "bin" / "elan"
    return elan_path.exists()


def print_status():
    """Выводит текущий статус установки."""
    print("=" * 60)
    print("СТАТУС УСТАНОВКИ")
    print("=" * 60)
    print()
    
    # LeanDojo
    if LEANDOJO_AVAILABLE:
        import lean_dojo
        version = getattr(lean_dojo, '__version__', 'unknown')
        print(f"✓ LeanDojo: {version}")
    else:
        print("✗ LeanDojo: не установлен")
        print("  Установите: pip install lean-dojo")
    
    # elan
    if check_elan_installed():
        print("✓ elan: установлен")
    else:
        print("✗ elan: не установлен")
        print("  Установите: curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh")
    
    print()
    
    # Кэшированные репозитории
    cached = list_cached_repos()
    print(f"ЗАКЭШИРОВАННЫЕ РЕПОЗИТОРИИ ({len(cached)}):")
    if cached:
        for repo in cached[:10]:
            print(f"  - {repo}")
        if len(cached) > 10:
            print(f"  ... и ещё {len(cached) - 10}")
    else:
        print("  (пусто)")
    
    print()


def print_available_repos():
    """Выводит список доступных репозиториев."""
    print("=" * 60)
    print("ДОСТУПНЫЕ РЕПОЗИТОРИИ")
    print("=" * 60)
    print()
    
    for name, info in REPOS.items():
        print(f"  {name}")
        print(f"    {info['description']}")
        print(f"    Теорем: {info['theorems_count']}")
        print(f"    Время: {info['estimated_time']}")
        print()


def trace_repo(repo_name: str, verbose: bool = True) -> Optional[str]:
    """
    Скачивает и трейсит репозиторий.
    
    Returns:
        Путь к traced репозиторию или None при ошибке
    """
    if not LEANDOJO_AVAILABLE:
        print("✗ LeanDojo не установлен")
        return None
    
    if repo_name not in REPOS:
        print(f"✗ Неизвестный репозиторий: {repo_name}")
        print(f"  Доступные: {', '.join(REPOS.keys())}")
        return None
    
    info = REPOS[repo_name]
    
    print(f"{'=' * 60}")
    print(f"TRACING: {repo_name}")
    print(f"{'=' * 60}")
    print(f"  URL: {info['url']}")
    print(f"  Commit: {info['commit']}")
    print(f"  Описание: {info['description']}")
    print(f"  Ожидаемое время: {info['estimated_time']}")
    print()
    
    try:
        _apply_extractor_fix()
        repo = LeanGitRepo(info['url'], info['commit'])
        
        print("Запускаем tracing...")
        print("(при первом запуске скачивается Lean toolchain и зависимости)")
        print()
        
        start_time = time.time()
        traced_repo = trace(repo)
        elapsed = time.time() - start_time
        
        print()
        print(f"✓ Tracing завершён за {elapsed:.1f} секунд ({elapsed/60:.1f} минут)")
        print(f"  Файлов: {len(traced_repo.traced_files)}")
        
        # Путь к кэшу
        cache_path = get_traced_repo_path(repo, build_deps=False)
        print(f"  Кэш: {cache_path}")
        
        return str(cache_path)
        
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return None


def trace_all_repos(repos: List[str], verbose: bool = True):
    """Трейсит несколько репозиториев."""
    results = {}
    
    for repo_name in repos:
        print()
        result = trace_repo(repo_name, verbose)
        results[repo_name] = result
        print()
    
    # Итоги
    print("=" * 60)
    print("ИТОГИ")
    print("=" * 60)
    
    for name, path in results.items():
        status = "✓" if path else "✗"
        print(f"  {status} {name}")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Скачивание и tracing Lean репозиториев для LeanDojo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
    %(prog)s --check                    # Проверить статус
    %(prog)s --list                     # Список доступных репозиториев
    %(prog)s --repo lean4-example       # Быстрый тест (1-2 мин)
    %(prog)s --repo minif2f             # MiniF2F (30-60 мин)
    %(prog)s --repo mathlib4            # Mathlib4 (2-4 часа)
    %(prog)s --repo all                 # Все репозитории
        """
    )
    
    parser.add_argument(
        "--repo", "-r",
        type=str,
        choices=list(REPOS.keys()) + ["all"],
        help="Репозиторий для tracing"
    )
    
    parser.add_argument(
        "--check", "-c",
        action="store_true",
        help="Проверить статус установки"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="Показать доступные репозитории"
    )
    
    parser.add_argument(
        "--mathlib-version",
        type=str,
        help="Произвольная версия Mathlib4 (tag), например: v4.25.0, v4.28.0-rc1"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=True,
        help="Подробный вывод"
    )
    
    args = parser.parse_args()
    
    # Если нет аргументов - показываем справку
    if len(sys.argv) == 1:
        parser.print_help()
        print()
        print_status()
        return
    
    if args.check:
        print_status()
        return
    
    if args.list:
        print_available_repos()
        return
    
    # Если указана произвольная версия mathlib4
    if args.mathlib_version:
        version = args.mathlib_version
        if not version.startswith("v"):
            version = f"v{version}"
        key = add_custom_mathlib4(version)
        trace_repo(key, args.verbose)
        return
    
    if args.repo:
        if args.repo == "all":
            # Трейсим в порядке от быстрого к медленному
            repos_order = ["lean4-example", "minif2f", "mathlib4"]
            trace_all_repos(repos_order, args.verbose)
        else:
            trace_repo(args.repo, args.verbose)


if __name__ == "__main__":
    main()
