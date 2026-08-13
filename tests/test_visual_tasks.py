"""Тесты визуальных (VLM) задач: рендер изображения, самосогласованность ответа,
отклонение неверных ответов и генерация мультимодального датасета."""

import random

import pytest
from PIL import Image

from re_rl.tasks.visual.generators import ALL_VISUAL_TASK_GENERATORS, VISUAL_TASK_CLASSES
from re_rl.tasks.registry import registry

VISUAL_TYPES = list(ALL_VISUAL_TASK_GENERATORS.keys())


def _seed(*p):
    random.seed("|".join(map(str, p)))


@pytest.mark.parametrize("task_type", VISUAL_TYPES)
def test_registered(task_type):
    assert task_type in registry


@pytest.mark.parametrize("task_type", VISUAL_TYPES)
@pytest.mark.parametrize("language", ["ru", "en"])
@pytest.mark.parametrize("difficulty", [1, 4, 7, 10])
def test_self_consistent_and_renders(task_type, language, difficulty):
    gen = ALL_VISUAL_TASK_GENERATORS[task_type]
    cls = registry[task_type]
    for sub in getattr(cls, "TASK_TYPES", [None]):
        for i in range(3):
            _seed(task_type, sub, language, difficulty, i)
            kwargs = {"task_type": sub} if sub else {}
            task = gen(language=language, difficulty=difficulty, **kwargs)
            # изображение рендерится и непустое
            img = task.render_image()
            assert isinstance(img, Image.Image)
            assert img.size[0] > 10 and img.size[1] > 10
            # текст без незаполненных плейсхолдеров, ответ проходит verify
            assert "{" not in task.description and "}" not in task.description
            assert task.final_answer is not None
            assert task.verify(f"<answer>{task.final_answer}</answer>") == 1.0


@pytest.mark.parametrize("task_type", VISUAL_TYPES)
def test_wrong_answer_rejected(task_type):
    gen = ALL_VISUAL_TASK_GENERATORS[task_type]
    cls = registry[task_type]
    for sub in getattr(cls, "TASK_TYPES", [None]):
        for i in range(4):
            _seed("wrong", task_type, sub, i)
            kwargs = {"task_type": sub} if sub else {}
            task = gen(language="ru", difficulty=6, **kwargs)
            fa = str(task.final_answer).strip()
            if fa.lstrip("-").isdigit():
                wrong = str(int(fa) + 5)
            else:  # ответ-метка (буква категории или цвет)
                wrong = "zzqqx"
            assert task.verify(f"<answer>{wrong}</answer>") < 1.0


def test_save_image(tmp_path):
    gen = ALL_VISUAL_TASK_GENERATORS["grid_color_count"]
    task = gen(language="ru", difficulty=5)
    path = tmp_path / "grid.png"
    out = task.save_image(str(path))
    assert path.exists() and path.stat().st_size > 0
    with Image.open(out) as im:
        assert im.size[0] > 10


def test_clock_time_formats():
    from re_rl.tasks.visual import ClockReadTask
    _seed("clock", 1)
    t = ClockReadTask.generate_random_task(difficulty=5)
    h, m = t.hour, t.minute
    # разные записи одного и того же времени принимаются
    assert t.verify(f"<answer>{h}:{m:02d}</answer>") == 1.0
    assert t.verify(f"<answer>{h}.{m:02d}</answer>") == 1.0
    assert t.verify(f"<answer>{(h % 12) + 12 if h != 12 else 12}:{m:02d}</answer>") == 1.0
    # неверная минута отвергается
    assert t.verify(f"<answer>{h}:{(m + 5) % 60:02d}</answer>") < 1.0


def test_geometry_formulas():
    from re_rl.tasks.visual import GeometryFigureTask
    _seed("geom", 2)
    area = GeometryFigureTask.generate_random_task(task_type="right_triangle_area", difficulty=5)
    assert abs(area.answer - area.a * area.b / 2) < 1e-9
    peri = GeometryFigureTask.generate_random_task(task_type="perimeter", difficulty=5)
    assert peri.answer == sum(peri.sides)
    ang = GeometryFigureTask.generate_random_task(task_type="missing_angle", difficulty=5)
    assert ang.answer == 180 - ang.alpha - ang.beta and ang.answer > 0


def test_puzzle_visual_inherits_logic():
    """Визуальные варианты должны совпадать по ответу с текстовыми головоломками."""
    from re_rl.tasks.visual import ARCGridVisualTask, SlidingPuzzleVisualTask
    _seed("arc", 3)
    arc = ARCGridVisualTask.generate_random_task(difficulty=5)
    flat = " ".join(str(v) for row in arc.test_out for v in row)
    assert arc.verify(f"<answer>{flat}</answer>") == 1.0
    _seed("slide", 4)
    sp = SlidingPuzzleVisualTask.generate_random_task(task_type="min_moves", difficulty=5)
    assert sp.verify(f"<answer>{sp.answer_int}</answer>") == 1.0


def test_generate_vlm_dataset(tmp_path):
    from re_rl.dataset_generator import DatasetGenerator

    gen = DatasetGenerator(output_dir=str(tmp_path))
    ds = gen.generate_vlm_dataset(num_samples=9, language="ru",
                                  difficulties=[3, 5, 7], show_progress=False)
    assert len(ds) == 9
    for rec in ds:
        assert rec["image"].endswith(".png")
        assert (tmp_path / rec["image"]).exists()
        assert rec["input"].startswith("<image>")
        assert "<answer>" in rec["output"]
        assert rec["metadata"]["task_type"] in VISUAL_TYPES
