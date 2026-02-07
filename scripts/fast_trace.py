#!/usr/bin/env python3
"""
Быстрый трейсинг Mathlib4 с кэшированием каждого этапа.

Все данные хранятся в ~/.cache/re_rl/mathlib4-<version>/.
При повторном запуске пропускает уже выполненные этапы.

Использование:
    python scripts/fast_trace.py                           # v4.26.0
    python scripts/fast_trace.py --version v4.22.0         # другая версия
    python scripts/fast_trace.py --archive ~/Downloads/mathlib4-4.26.0.tar.gz
    python scripts/fast_trace.py --force-step 5            # перезапустить с этапа 5
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path


# ============================================================================
# Пути
# ============================================================================
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
OUR_EXTRACT_DATA = PROJECT_DIR / "re_rl" / "tasks" / "formal" / "ExtractData.lean"
MATHLIB4_URL = "https://github.com/leanprover-community/mathlib4"
DEFAULT_VERSION = "v4.26.0"

# Постоянный кэш
CACHE_BASE = Path.home() / ".cache" / "re_rl"


def get_repo_dir(version: str) -> Path:
    """Постоянная директория для конкретной версии."""
    return CACHE_BASE / f"mathlib4-{version}" / "mathlib4"


def find_lean4_repl() -> Path:
    """Находит Lean4Repl.lean (опционально)."""
    try:
        import lean_dojo
        pkg = Path(lean_dojo.__file__).parent
        for sub in ["interaction", "data_extraction", ""]:
            p = (pkg / sub / "Lean4Repl.lean") if sub else (pkg / "Lean4Repl.lean")
            if p.exists():
                return p
    except ImportError:
        pass
    local = PROJECT_DIR / "re_rl" / "tasks" / "formal" / "Lean4Repl.lean"
    return local if local.exists() else None


def run_cmd(cmd: str, cwd: str, desc: str) -> int:
    """Запускает команду с полным выводом."""
    print(f"\n{'='*60}")
    print(f"  {desc}")
    print(f"{'='*60}")
    print(f"  $ {cmd}\n", flush=True)

    start = time.time()
    result = subprocess.run(
        cmd, shell=True, cwd=cwd,
        env={**os.environ, "PATH": f"{Path.home()}/.elan/bin:{os.environ.get('PATH', '')}"},
    )
    elapsed = time.time() - start
    status = "OK" if result.returncode == 0 else f"ОШИБКА (code {result.returncode})"
    print(f"\n  [{status}] {elapsed:.1f}с ({elapsed/60:.1f} мин)", flush=True)
    return result.returncode


def step_done(repo_dir: Path, step: int) -> bool:
    """Проверяет выполнен ли этап."""
    marker = repo_dir.parent / f".step_{step}_done"
    return marker.exists()


def mark_done(repo_dir: Path, step: int):
    """Отмечает этап как выполненный."""
    marker = repo_dir.parent / f".step_{step}_done"
    marker.write_text(time.strftime("%Y-%m-%d %H:%M:%S"))


def clear_from_step(repo_dir: Path, step: int):
    """Сбрасывает маркеры начиная с этапа."""
    for s in range(step, 8):
        marker = repo_dir.parent / f".step_{s}_done"
        if marker.exists():
            marker.unlink()


def main():
    parser = argparse.ArgumentParser(description="Быстрый трейсинг Mathlib4")
    parser.add_argument("--version", "-v", default=DEFAULT_VERSION, help="Версия Mathlib4")
    parser.add_argument("--archive", "-a", help="Путь к .tar.gz архиву")
    parser.add_argument("--jobs", "-j", type=int, default=os.cpu_count(), help="Потоки")
    parser.add_argument("--force-step", type=int, default=0,
                        help="Принудительно перезапустить с этого этапа")
    args = parser.parse_args()

    version = args.version
    if not version.startswith("v"):
        version = f"v{version}"

    # Пути
    repo_dir = get_repo_dir(version)
    repo_dir.parent.mkdir(parents=True, exist_ok=True)

    elan = Path.home() / ".elan" / "bin"
    if not elan.exists():
        print("ОШИБКА: elan не установлен"); sys.exit(1)
    os.environ["PATH"] = f"{elan}:{os.environ.get('PATH', '')}"

    if not OUR_EXTRACT_DATA.exists():
        print(f"ОШИБКА: {OUR_EXTRACT_DATA} не найден"); sys.exit(1)

    lean4_repl = find_lean4_repl()

    # Сброс маркеров если --force-step
    if args.force_step > 0:
        clear_from_step(repo_dir, args.force_step)

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  Быстрый трейсинг Mathlib4 {version:>10s}                        ║
║  Кэш: {str(repo_dir.parent)[-50:]:>50s}  ║
║  Потоков: {args.jobs:<4d}                                            ║
╚══════════════════════════════════════════════════════════════╝
""")

    total_start = time.time()

    # ================================================================
    # ЭТАП 1: Исходники Mathlib4
    # ================================================================
    if step_done(repo_dir, 1):
        print(f"  ЭТАП 1: Исходники — уже есть, пропускаем")
    else:
        if args.archive:
            archive = Path(args.archive)
            if not archive.exists():
                print(f"ОШИБКА: {archive} не найден"); sys.exit(1)
            print(f"\n{'='*60}")
            print(f"  ЭТАП 1: Распаковка архива {archive.name}")
            print(f"{'='*60}", flush=True)

            if repo_dir.exists():
                shutil.rmtree(repo_dir)
            repo_dir.parent.mkdir(parents=True, exist_ok=True)

            subprocess.run(f"tar xzf {archive}", shell=True,
                           cwd=str(repo_dir.parent), check=True)
            # Переименуем распакованную папку
            for d in repo_dir.parent.iterdir():
                if d.is_dir() and d.name.startswith("mathlib4") and d.name != "mathlib4":
                    d.rename(repo_dir)
                    break
            print(f"  Распаковано: {repo_dir}")
        else:
            if repo_dir.exists():
                shutil.rmtree(repo_dir)
            rc = run_cmd(
                f"git clone --depth 1 --branch {version} --single-branch "
                f"{MATHLIB4_URL} mathlib4",
                cwd=str(repo_dir.parent),
                desc=f"ЭТАП 1: git clone --depth 1 Mathlib4 {version}",
            )
            if rc != 0:
                sys.exit(1)

        # git init если нужно (для lake)
        if not (repo_dir / ".git").exists():
            print("  Инициализируем git...", flush=True)
            subprocess.run("git init -q", shell=True, cwd=repo_dir, check=True)
            subprocess.run("git add -A", shell=True, cwd=repo_dir, check=True)
            subprocess.run('git commit -q -m "init"', shell=True, cwd=repo_dir, check=True)

        mark_done(repo_dir, 1)

    print(f"  Toolchain: {(repo_dir / 'lean-toolchain').read_text().strip()}")

    # ================================================================
    # ЭТАП 2: lake exe cache get
    # ================================================================
    if step_done(repo_dir, 2):
        print(f"  ЭТАП 2: lake exe cache get — уже есть, пропускаем")
    else:
        rc = run_cmd("lake exe cache get", cwd=str(repo_dir),
                      desc="ЭТАП 2: lake exe cache get (скачивание .olean)")
        if rc != 0:
            print("  WARNING: cache get не удался, lake build соберёт с нуля")
        mark_done(repo_dir, 2)

    # ================================================================
    # ЭТАП 3: lake build
    # ================================================================
    if step_done(repo_dir, 3):
        print(f"  ЭТАП 3: lake build — уже есть, пропускаем")
    else:
        rc = run_cmd("lake build", cwd=str(repo_dir),
                      desc="ЭТАП 3: lake build")
        if rc != 0:
            print("ОШИБКА: lake build упал"); sys.exit(1)
        mark_done(repo_dir, 3)

    # ================================================================
    # ЭТАП 4: Копирование Lean 4 stdlib
    # ================================================================
    if step_done(repo_dir, 4):
        print(f"  ЭТАП 4: Lean 4 stdlib — уже есть, пропускаем")
    else:
        print(f"\n{'='*60}")
        print(f"  ЭТАП 4: Копирование Lean 4 stdlib")
        print(f"{'='*60}", flush=True)

        lean_prefix_raw = subprocess.check_output(
            "lake env lean --print-prefix", shell=True, cwd=str(repo_dir), text=True
        )
        lean_prefix = [l.strip() for l in lean_prefix_raw.strip().split('\n')
                       if l.strip() and not l.strip().startswith('warning')][-1]
        dest = repo_dir / ".lake" / "packages" / "lean4"
        if not dest.exists():
            print(f"  {lean_prefix} → {dest}")
            shutil.copytree(lean_prefix, str(dest))
        print("  Готово", flush=True)
        mark_done(repo_dir, 4)

    # ================================================================
    # ЭТАП 5: ExtractData.lean
    # ================================================================
    if step_done(repo_dir, 5):
        print(f"  ЭТАП 5: ExtractData — уже есть, пропускаем")
    else:
        shutil.copyfile(OUR_EXTRACT_DATA, repo_dir / "ExtractData.lean")

        build_ir = repo_dir / ".lake" / "build" / "ir"
        # Грубая оценка
        total_olean = sum(1 for _ in (repo_dir / ".lake" / "build" / "lib").rglob("*.olean"))
        expected = max(total_olean, 5000)

        print(f"\n{'='*60}")
        print(f"  ЭТАП 5: ExtractData — извлечение тактик ({args.jobs} потоков)")
        print(f"  Ожидается ~{expected} файлов")
        print(f"{'='*60}")
        print(f"  $ lake env lean --threads {args.jobs} --run ExtractData.lean noDeps\n", flush=True)

        stop_monitor = threading.Event()

        def monitor_progress():
            start = time.time()
            while not stop_monitor.is_set():
                stop_monitor.wait(15)
                if stop_monitor.is_set():
                    break
                done = sum(1 for _ in build_ir.rglob("*.ast.json")) if build_ir.exists() else 0
                elapsed = time.time() - start
                pct = done / expected * 100 if expected > 0 else 0
                speed = done / elapsed * 60 if elapsed > 0 else 0
                eta = (expected - done) / (done / elapsed) / 60 if done > 0 else 0
                print(f"  [{elapsed/60:5.1f} мин] {done}/{expected} ({pct:.0f}%) "
                      f"| {speed:.0f} ф/мин | ETA: {eta:.0f} мин", flush=True)

        monitor = threading.Thread(target=monitor_progress, daemon=True)
        monitor.start()

        result = subprocess.run(
            f"lake env lean --threads {args.jobs} --run ExtractData.lean noDeps",
            shell=True, cwd=str(repo_dir),
            env={**os.environ, "PATH": f"{elan}:{os.environ.get('PATH', '')}"},
        )
        stop_monitor.set()
        monitor.join(timeout=2)

        done = sum(1 for _ in build_ir.rglob("*.ast.json")) if build_ir.exists() else 0
        print(f"\n  Обработано: {done} файлов", flush=True)

        if result.returncode != 0:
            print(f"  ОШИБКА: ExtractData упал! (code {result.returncode})")
            print(f"  Данные сохранены в {repo_dir} — исправьте и перезапустите с --force-step 5")
            sys.exit(1)

        (repo_dir / "ExtractData.lean").unlink(missing_ok=True)
        mark_done(repo_dir, 5)

    # ================================================================
    # ЭТАП 6: Lean4Repl (опционально)
    # ================================================================
    if step_done(repo_dir, 6):
        print(f"  ЭТАП 6: Lean4Repl — уже есть, пропускаем")
    elif lean4_repl:
        shutil.copyfile(lean4_repl, repo_dir / "Lean4Repl.lean")
        lakefile = repo_dir / "lakefile.lean"
        if lakefile.exists():
            content = lakefile.read_text()
            if "Lean4Repl" not in content:
                with open(lakefile, "a") as f:
                    f.write("\nlean_lib Lean4Repl {\n\n}\n")
        rc = run_cmd("lake build Lean4Repl", cwd=str(repo_dir),
                      desc="ЭТАП 6: Сборка Lean4Repl (опционально)")
        if rc != 0:
            print("  Пропускаем — Pantograph работает без него")
        mark_done(repo_dir, 6)
    else:
        print(f"  ЭТАП 6: Lean4Repl — пропущен (Pantograph работает без него)")
        mark_done(repo_dir, 6)

    # ================================================================
    # ЭТАП 7: Подсчёт статистики
    # ================================================================
    print(f"\n{'='*60}")
    print(f"  ЭТАП 7: Подсчёт статистики")
    print(f"{'='*60}", flush=True)

    build_ir = repo_dir / ".lake" / "build" / "ir"
    n_ast = sum(1 for _ in build_ir.rglob("*.ast.json")) if build_ir.exists() else 0
    n_dep = sum(1 for _ in build_ir.rglob("*.dep_paths")) if build_ir.exists() else 0

    total_tactics = 0
    total_premises = 0
    for f in build_ir.rglob("*.ast.json"):
        try:
            with open(f) as fh:
                data = json.load(fh)
            total_tactics += len(data.get("tactics", []))
            total_premises += len(data.get("premises", []))
        except Exception:
            pass

    total_elapsed = time.time() - total_start

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  ГОТОВО! Mathlib4 {version:>10s}                                 ║
║  Время: {total_elapsed/60:5.1f} мин                                      ║
║                                                               ║
║  ast.json:  {n_ast:<6d}    dep_paths: {n_dep:<6d}                     ║
║  Тактик:    {total_tactics:<8d}  Посылок:   {total_premises:<8d}               ║
║                                                               ║
║  Данные: {str(repo_dir)[-52:]:>52s}  ║
║                                                               ║
║  При повторном запуске этапы будут пропущены.                 ║
║  Для перезапуска этапа: --force-step N                        ║
╚══════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
