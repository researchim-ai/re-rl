"""Explicit dispatch for reviewed legacy tasks; cached answers are not solver inputs."""
from importlib import import_module
from re_rl.tasks.execution_trace import ExecutionTrace
from re_rl.tasks.reviewed_coverage import REVIEWED_TASKS


def solve_reviewed(task):
    name = task.TASK_TYPE
    module_name,domain = REVIEWED_TASKS[name]
    trace = ExecutionTrace()
    if domain == 'physics':
        from re_rl.tasks.physics.reviewed_solvers import solve_physics
        result = solve_physics(task,name,trace)
    elif domain == 'visual' and name not in ('convex_hull_image','game_of_life_image','arc_grid_image','magic_square_image','sudoku_image','sliding_puzzle_image','grid_navigation_image','grid_color_count','queens_check_image','hanoi_disk','minesweeper_image','mastermind_image'):
        from re_rl.tasks.visual.reviewed_solvers import solve_visual
        result = solve_visual(task,name,trace)
    else:
        from re_rl.tasks.math.reviewed_solvers import solve_math
        result = solve_math(task,name,import_module(module_name),trace)
    inputs,already_formatted = result if isinstance(result,tuple) else (result,False)
    if not already_formatted:
        task._solve_before_trace()
    if not trace.events:
        raise RuntimeError(name)
    trace.finish(task,inputs)
