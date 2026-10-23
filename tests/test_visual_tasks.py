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


def test_picture_chains():
    from re_rl.tasks.math.logic.domino_chain.task import first_break
    from re_rl.tasks.visual.abacus_read.task import AbacusReadTask
    from re_rl.tasks.visual.block_tower.task import BlockTowerTask
    from re_rl.tasks.visual.domino_image.task import DominoImageTask, pip_sum

    random.seed(2)
    low = BlockTowerTask.generate_random_task(task_type="total", difficulty=1)
    high = BlockTowerTask.generate_random_task(task_type="height", difficulty=10)
    assert high.n > low.n
    assert low.answer == sum(low.heights)
    assert high.column == high.heights[high.k - 1]
    assert len(high.solution_steps) >= high.n
    assert high.render_image().size[0] > low.render_image().size[0]

    random.seed(3)
    abacus = AbacusReadTask.generate_random_task(task_type="value", difficulty=8)
    rebuilt = 0
    for digit in abacus.digits:
        rebuilt = rebuilt * 10 + digit
    assert abacus.value == rebuilt
    assert abacus.digits[0] != 0
    assert abacus.render_image().size[0] > 10
    assert len(abacus.solution_steps) >= abacus.n

    random.seed(4)
    tiles = DominoImageTask.generate_random_task(task_type="break", difficulty=9)
    assert tiles.pips == pip_sum(tiles.dominoes)
    assert tiles.break_at == first_break(tiles.dominoes)[0]
    assert len(tiles.solution_steps) >= tiles.n
    assert "{" not in tiles.description and "}" not in tiles.description


def test_picture_geometry():
    from re_rl.tasks.visual.arrow_path.task import ArrowPathTask, count_turns
    from re_rl.tasks.visual.clock_row.task import ClockRowTask, hand_tip, hour_degrees, minute_degrees
    from re_rl.tasks.visual.grid_squares.task import GridSquaresTask, square_counts

    random.seed(5)
    low = GridSquaresTask.generate_random_task(task_type="all", difficulty=1)
    high = GridSquaresTask.generate_random_task(task_type="size_k", difficulty=10)
    assert high.n > low.n
    assert low.total == sum(square_counts(low.rows, low.cols))
    assert high.at_k == square_counts(high.rows, high.cols)[high.k - 1]
    assert len(high.solution_steps) >= high.n

    random.seed(6)
    path = ArrowPathTask.generate_random_task(task_type="turns", difficulty=8)
    assert len(path.points) == path.n + 1
    assert path.turns == count_turns(path.points)
    for start, end in zip(path.points, path.points[1:]):
        assert abs(start[0] - end[0]) + abs(start[1] - end[1]) == 1
    assert path.render_image().size[0] > 10

    tip_x, tip_y = hand_tip(0, 0, 10, hour_degrees(3, 0))
    assert abs(tip_x - 10) < 1e-6 and abs(tip_y) < 1e-6
    tip_x, tip_y = hand_tip(0, 0, 10, minute_degrees(0))
    assert abs(tip_x) < 1e-6 and abs(tip_y + 10) < 1e-6
    random.seed(7)
    clocks = ClockRowTask.generate_random_task(task_type="hour_sum", difficulty=6)
    assert clocks.hour_sum == sum(hour for hour, _minute in clocks.clocks)
    assert clocks.minute_sum == sum(minute for _hour, minute in clocks.clocks)
    assert len(clocks.solution_steps) >= clocks.n
    assert clocks.render_image().size[0] > clocks.render_image().size[1]


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


def test_balance_and_slope_formulas():
    from re_rl.tasks.visual import BalanceScaleTask, SlopeReadTask, NumberLineTask
    _seed("bal", 1)
    arm = BalanceScaleTask.generate_random_task(task_type="equal_arm", difficulty=8)
    assert arm.answer == sum(arm.left) - sum(arm.right)
    assert arm.answer > 0
    lever = BalanceScaleTask.generate_random_task(task_type="lever", difficulty=6)
    assert lever.m_l * lever.d_l == lever.answer * lever.d_r
    slope = SlopeReadTask.generate_random_task(task_type="slope", difficulty=7)
    assert slope.answer == slope.m
    inter = SlopeReadTask.generate_random_task(task_type="intercept", difficulty=4)
    assert inter.answer == inter.b
    mid = NumberLineTask.generate_random_task(task_type="midpoint", difficulty=9)
    assert (mid.a + mid.b) % 2 == 0
    assert mid.answer == (mid.a + mid.b) // 2


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
