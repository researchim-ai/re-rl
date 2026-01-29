# re_rl/tasks/math/logic/__init__.py

"""Логические задачи."""

from re_rl.tasks.math.logic.contradiction_task import ContradictionTask
from re_rl.tasks.math.logic.knights_knaves_task import KnightsKnavesTask
from re_rl.tasks.math.logic.futoshiki_task import FutoshikiTask
from re_rl.tasks.math.logic.analogical_task import AnalogicalTask
from re_rl.tasks.math.logic.text_stats_task import TextStatsTask
from re_rl.tasks.math.logic.sudoku_task import SudokuTask
from re_rl.tasks.math.logic.zebra_puzzle_task import ZebraPuzzleTask

__all__ = [
    "ContradictionTask",
    "KnightsKnavesTask",
    "FutoshikiTask",
    "AnalogicalTask",
    "TextStatsTask",
    "SudokuTask",
    "ZebraPuzzleTask",
]
