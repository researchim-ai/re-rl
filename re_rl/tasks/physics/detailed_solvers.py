"""Evaluate circuit trees and retain every leaf and reduction operation."""
from re_rl.tasks.computation_trace import ExactTrace

TRACED_PHYSICS_TASKS = ('network_reduce', 'switch_net')


def solve_detailed(task):
    trace = ExactTrace()
    c = trace.calc
    inputs = {'tree': task.tree, 'task_type': task.task_type}

    def reduce(node, path, flip=None):
        if node[0] == 'leaf':
            value = node[1] if task.TASK_TYPE == 'network_reduce' else node[2]
            value = c(f'{path}:leaf', 'add', value, 0)
            if task.TASK_TYPE == 'switch_net' and node[1] == flip:
                value = c(f'{path}:flip_{flip}', 'sub', 1, value)
            return value
        left = reduce(node[1], path+'.L', flip)
        right = reduce(node[2], path+'.R', flip)
        if task.TASK_TYPE == 'switch_net':
            return c(f'{path}:{node[0]}', 'min' if node[0] == 'series' else 'max', left, right)
        if task.task_type == 'leaf_sum' or node[0] == 'series':
            return c(f'{path}:sum', 'add', left, right)
        numerator = c(f'{path}:R1*R2', 'mul', left, right)
        denominator = c(f'{path}:R1+R2', 'add', left, right)
        return c(f'{path}:parallel', 'div', numerator, denominator)

    value = reduce(task.tree, 'root')
    if task.TASK_TYPE == 'switch_net' and task.task_type == 'flip':
        inputs['switch'] = task.k
        after = reduce(task.tree, 'flipped', task.k)
        value = c('conductivity_changed', 'ne', value, after)
    answer = int(value) if value.denominator == 1 else value
    task.answer = answer
    trace.finish(task, answer, inputs)
