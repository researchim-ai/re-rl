# re_rl/tasks/math/discrete/__init__.py

"""Задачи дискретной математики."""

from re_rl.tasks.math.discrete.number_theory_task import NumberTheoryTask
from re_rl.tasks.math.discrete.combinatorics_task import CombinatoricsTask
from re_rl.tasks.math.discrete.sequence_task import SequenceTask
from re_rl.tasks.math.discrete.set_logic_task import SetLogicTask
from re_rl.tasks.math.discrete.graph_task import GraphTask
from re_rl.tasks.math.discrete.nim_game_task import NimGameTask
from re_rl.tasks.math.discrete.graph_justification_task import GraphJustificationTask
from re_rl.tasks.math.discrete.combinatorial_optimization_task import CombinatorialOptimizationTask

__all__ = [
    "NumberTheoryTask",
    "CombinatoricsTask",
    "SequenceTask",
    "SetLogicTask",
    "GraphTask",
    "NimGameTask",
    "GraphJustificationTask",
    "CombinatorialOptimizationTask",
]
