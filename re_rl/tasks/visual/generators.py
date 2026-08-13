"""Реестр генераторов визуальных (VLM) задач.

Держится отдельно от ``ALL_TASK_GENERATORS`` (текстовый конвейер), чтобы не смешивать
текстовые и мультимодальные задачи. Классы всё равно попадают в общий ``registry``
через метакласс.
"""

from re_rl.tasks.visual.function_plot_task import FunctionPlotReadTask
from re_rl.tasks.visual.bar_chart_task import BarChartReadTask
from re_rl.tasks.visual.grid_color_task import GridColorCountTask
from re_rl.tasks.visual.geometry_figure_task import GeometryFigureTask
from re_rl.tasks.visual.line_plot_task import LinePlotReadTask
from re_rl.tasks.visual.pie_chart_task import PieChartReadTask
from re_rl.tasks.visual.clock_task import ClockReadTask
from re_rl.tasks.visual.dice_task import DiceReadTask
from re_rl.tasks.visual.chessboard_task import ChessboardCountTask
from re_rl.tasks.visual.puzzle_visual_task import (
    SudokuVisualTask, SlidingPuzzleVisualTask, ARCGridVisualTask,
)
from re_rl.tasks.visual.graph_task import (
    ShortestPathVisualTask, MSTVisualTask, GraphColoringVisualTask,
    TopoSortVisualTask, MaxFlowVisualTask,
)
from re_rl.tasks.visual.venn_task import VennDiagramTask
from re_rl.tasks.visual.area_task import AreaReadTask
from re_rl.tasks.visual.stats_task import StatsHistogramTask
from re_rl.tasks.visual.motion_task import KinematicsGraphTask, ProjectileGraphTask
from re_rl.tasks.visual.puzzle_visual2_task import (
    GameOfLifeVisualTask, MagicSquareVisualTask, GridNavigationVisualTask,
)
from re_rl.tasks.visual.dfa_task import DFAVisualTask
from re_rl.tasks.visual.logic_circuit_task import BooleanCircuitVisualTask
from re_rl.tasks.visual.minesweeper_task import MinesweeperVisualTask
from re_rl.tasks.visual.queens_task import QueensCheckVisualTask
from re_rl.tasks.visual.mastermind_task import MastermindVisualTask
from re_rl.tasks.visual.pv_cycle_task import PVCycleVisualTask
from re_rl.tasks.visual.shoelace_task import ShoelaceAreaVisualTask


def _mk(task_cls):
    def _gen(task_type=None, language="ru", detail_level=3, difficulty=5,
             reasoning_mode=False, **kwargs):
        return task_cls.generate_random_task(
            task_type=task_type, language=language, detail_level=detail_level,
            difficulty=difficulty, reasoning_mode=reasoning_mode, **kwargs)
    return _gen


VISUAL_TASK_CLASSES = [
    FunctionPlotReadTask, BarChartReadTask, GridColorCountTask,
    GeometryFigureTask, LinePlotReadTask, PieChartReadTask,
    ClockReadTask, DiceReadTask, ChessboardCountTask,
    SudokuVisualTask, SlidingPuzzleVisualTask, ARCGridVisualTask,
    ShortestPathVisualTask, MSTVisualTask, DFAVisualTask, BooleanCircuitVisualTask,
    MinesweeperVisualTask, QueensCheckVisualTask, MastermindVisualTask,
    PVCycleVisualTask, ShoelaceAreaVisualTask,
    GraphColoringVisualTask, TopoSortVisualTask, MaxFlowVisualTask,
    VennDiagramTask, AreaReadTask, StatsHistogramTask,
    KinematicsGraphTask, ProjectileGraphTask,
    GameOfLifeVisualTask, MagicSquareVisualTask, GridNavigationVisualTask,
]

ALL_VISUAL_TASK_GENERATORS = {cls.TASK_TYPE: _mk(cls) for cls in VISUAL_TASK_CLASSES}

__all__ = ["ALL_VISUAL_TASK_GENERATORS", "VISUAL_TASK_CLASSES"]
