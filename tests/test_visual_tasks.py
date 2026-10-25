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


def test_picture_reasoning():
    from re_rl.tasks.visual.blob_count.task import BlobCountTask, blob_trace
    from re_rl.tasks.visual.ink_spread.task import InkSpreadTask, ink_trace
    from re_rl.tasks.visual.mirror_fault.task import MirrorFaultTask, mirror_trace
    from re_rl.tasks.visual.mirror_ray.task import MirrorRayTask, ray_trace, turn
    from re_rl.tasks.visual.paint_order.task import PaintOrderTask, paint_trace
    from re_rl.tasks.visual.shape_match.task import ShapeMatchTask, same_turn

    assert mirror_trace([[1, 0, 1], [0, 1, 0], [1, 1, 0]]) == [(0, 0, 0), (0, 0, 0), (1, 1, 1)]
    assert blob_trace([[1, 0], [0, 1]]) == [(1, 1), (2, 1)]
    assert blob_trace([[1, 1], [1, 0]]) == [(1, 2), (1, 3)]
    assert ink_trace([[0, 1], [0, 0]], (0, 0)) == [(1, 0), (3, 0)]
    assert turn(0, 1, 1) == (1, 0)
    assert turn(0, 1, 2) == (-1, 0)
    trace, hits, side = ray_trace([[0, 0], [0, 0]], 0)
    assert hits == 0 and side == 2 and trace == [(1, 1, 0), (1, 2, 0)]
    trace, hits, side = ray_trace([[1, 0], [0, 0]], 0)
    assert hits == 1 and side == 4
    straight = [(0, 0), (0, 1), (0, 2), (0, 3)]
    upright = [(0, 0), (1, 0), (2, 0), (3, 0)]
    bend_s = [(0, 0), (0, 1), (1, 1), (1, 2)]
    bend_z = [(0, 1), (0, 2), (1, 0), (1, 1)]
    assert same_turn(straight, upright)
    assert not same_turn(bend_s, bend_z)
    assert paint_trace(2, 2, [(0, 0, 2, 2), (0, 0, 2, 1)]) == [(4, 4), (4, 2)]

    random.seed(8)
    low = MirrorFaultTask.generate_random_task(task_type="pairs", difficulty=1)
    high = MirrorFaultTask.generate_random_task(task_type="rows", difficulty=10)
    assert high.n > low.n
    assert low.pairs == mirror_trace(low.grid)[-1][1]
    assert high.render_image().size[0] > low.render_image().size[0]

    random.seed(9)
    blobs = BlobCountTask.generate_random_task(task_type="parts", difficulty=7)
    assert blobs.parts == blob_trace(blobs.grid)[-1][0]
    assert blobs.largest == blob_trace(blobs.grid)[-1][1]
    assert blobs.largest >= 1

    random.seed(10)
    ink = InkSpreadTask.generate_random_task(task_type="missed", difficulty=8)
    assert (ink.reached, ink.missed) == tuple(ink_trace(ink.grid, ink.source)[-1])
    assert ink.grid[ink.source[0]][ink.source[1]] == 0

    random.seed(11)
    ray = MirrorRayTask.generate_random_task(task_type="side", difficulty=9)
    again, hits, side = ray_trace(ray.grid, ray.start)
    assert again == ray.trace and hits == ray.hits and side == ray.side
    assert ray.render_image().size[0] > ray.render_image().size[1]

    random.seed(12)
    shapes = ShapeMatchTask.generate_random_task(task_type="matches", difficulty=6)
    assert shapes.matches == sum(1 for cand in shapes.candidates if same_turn(shapes.target, cand))
    assert len(shapes.candidates) == shapes.n

    random.seed(13)
    paint = PaintOrderTask.generate_random_task(task_type="first", difficulty=8)
    assert (paint.cover, paint.first) == tuple(paint_trace(paint.side, paint.side, paint.rects)[-1])
    assert len(paint.solution_steps) >= paint.n
    assert paint.render_image().size[0] > 10


def test_picture_structures():
    from re_rl.tasks.visual.arrow_turn.task import ArrowTurnTask, arrow_trace
    from re_rl.tasks.visual.edge_flip.task import EdgeFlipTask, edge_trace
    from re_rl.tasks.visual.hanoi_disk.task import HanoiDiskTask, hanoi_trace
    from re_rl.tasks.visual.nest_box.task import NestBoxTask, contains, nest_trace
    from re_rl.tasks.visual.skyline_see.task import SkylineSeeTask, skyline_trace
    from re_rl.tasks.visual.solid_block.task import SolidBlockTask, solid_trace

    trace, moves = hanoi_trace([0, 1, 1])
    assert moves == 3 and trace[-1][3] == 3
    trace, moves = hanoi_trace([0, 3, 3])
    assert moves == 0 and trace == [(1, 3, 0, 0), (2, 3, 0, 0)]
    assert skyline_trace([1, 3, 2, 4, 4])[-1] == (3, 4, 4)
    rows, side = solid_trace([[1, 1], [1, 1]])
    assert side == 2 and rows[-1][1] == 1
    rows, side = solid_trace([[1, 1], [1, 0]])
    assert side == 1 and rows[-1][1] == 0
    assert edge_trace([[0, 1], [0, 0]]) == [(1, 1, 0, 0), (0, 1, 1, 1)]
    assert arrow_trace([1, 0, 0]) == [(2, 0, 0), (1, 1, 1), (1, 0, 1)]
    assert contains((0, 0, 6, 6), (1, 1, 2, 2))
    assert not contains((0, 0, 6, 6), (0, 1, 2, 2))
    assert nest_trace([(0, 0, 6, 6), (1, 1, 2, 2)]) == [(1, 1, 1), (0, 1, 1)]

    random.seed(14)
    low = HanoiDiskTask.generate_random_task(task_type="moves", difficulty=1)
    high = HanoiDiskTask.generate_random_task(task_type="home", difficulty=10)
    assert high.n > low.n
    assert low.moves == hanoi_trace(low.pegs)[1]
    assert high.home == sum(peg == 3 for peg in high.pegs[1:])
    assert len(high.solution_steps) >= high.n

    random.seed(15)
    sky = SkylineSeeTask.generate_random_task(task_type="visible", difficulty=8)
    assert (sky.visible, sky.last) == tuple(skyline_trace(sky.heights)[-1][:2])
    assert sky.render_image().size[0] > 10

    random.seed(16)
    block = SolidBlockTask.generate_random_task(task_type="twos", difficulty=7)
    rows, side = solid_trace(block.grid)
    assert block.side == side and block.twos == rows[-1][1]

    random.seed(17)
    edges = EdgeFlipTask.generate_random_task(task_type="flat", difficulty=6)
    trace = edge_trace(edges.grid)
    assert edges.flat == trace[-1][1] and edges.rise == trace[-1][3]

    random.seed(18)
    arrows = ArrowTurnTask.generate_random_task(task_type="lefts", difficulty=9)
    trace = arrow_trace(arrows.directions)
    assert arrows.lefts == trace[-1][2] and arrows.last == trace[-1][0]
    assert arrows.render_image().size[0] > arrows.render_image().size[1]

    random.seed(19)
    boxes = NestBoxTask.generate_random_task(task_type="pairs", difficulty=8)
    trace = nest_trace(boxes.rects)
    assert boxes.pairs == trace[-1][1] and boxes.outers == trace[-1][2]
    assert len(boxes.solution_steps) >= boxes.n


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
