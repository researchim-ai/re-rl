"""Визуальные (мультимодальные / VLM) задачи: изображение + текстовый ответ."""

from re_rl.tasks.visual._visual_utils import (
    VisualTaskMixin, fig_to_image, augment_image,
    render_number_grid, render_color_grid,
)
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
from re_rl.tasks.visual.graph_task import ShortestPathVisualTask, MSTVisualTask
from re_rl.tasks.visual.dfa_task import DFAVisualTask
from re_rl.tasks.visual.logic_circuit_task import BooleanCircuitVisualTask
from re_rl.tasks.visual.minesweeper_task import MinesweeperVisualTask
from re_rl.tasks.visual.queens_task import QueensCheckVisualTask
from re_rl.tasks.visual.mastermind_task import MastermindVisualTask
from re_rl.tasks.visual.pv_cycle_task import PVCycleVisualTask
from re_rl.tasks.visual.shoelace_task import ShoelaceAreaVisualTask

__all__ = [
    "VisualTaskMixin",
    "fig_to_image",
    "augment_image",
    "render_number_grid",
    "render_color_grid",
    "FunctionPlotReadTask",
    "BarChartReadTask",
    "GridColorCountTask",
    "GeometryFigureTask",
    "LinePlotReadTask",
    "PieChartReadTask",
    "ClockReadTask",
    "DiceReadTask",
    "ChessboardCountTask",
    "SudokuVisualTask",
    "SlidingPuzzleVisualTask",
    "ARCGridVisualTask",
    "ShortestPathVisualTask",
    "MSTVisualTask",
    "DFAVisualTask",
    "BooleanCircuitVisualTask",
    "MinesweeperVisualTask",
    "QueensCheckVisualTask",
    "MastermindVisualTask",
    "PVCycleVisualTask",
    "ShoelaceAreaVisualTask",
]
