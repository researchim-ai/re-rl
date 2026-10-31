"""Execution traces for Boolean gates and deterministic automata."""
from itertools import product
from re_rl.tasks.computation_trace import ExactTrace
from re_rl.tasks.i18n import TaskTexts

texts = TaskTexts(__file__)
TRACED_AUTOMATA_TASKS = ('boolean_circuit', 'boolean_circuit_image', 'dfa_simulation', 'dfa_image')


def solve_circuit(task):
    trace = ExactTrace()
    inputs = {'gates': task.gates, 'input_count': task.k, 'subtype': task.subtype}
    assignments = [task.inputs] if task.subtype == 'evaluate' else product((0, 1), repeat=task.k)
    if task.subtype == 'evaluate':
        inputs['inputs'] = task.inputs
    count = 0
    for bits in assignments:
        label = ''.join(map(str, bits))
        values = [trace.calc(f'{label}:x{i+1}', 'add', bit, 0) for i, bit in enumerate(bits)]
        for i, (op, a, b) in enumerate(task.gates):
            gate = f'{label}:g{i+1}={op}({a},{b})'
            if op == 'NOT':
                value = trace.calc(gate, 'sub', 1, values[a])
            else:
                operation = {'AND': 'min', 'OR': 'max', 'XOR': 'ne'}[op]
                value = trace.calc(gate, operation, values[a], values[b])
            values.append(value)
        count = trace.calc(f'count_{label}', 'add', count, values[-1])
    task._answer = int(count)
    trace.finish(task, task._answer, inputs)


def solve_dfa(task):
    state = 0
    events = [dict(operation='initial', state=state)]
    steps = [texts.t('initial', task.language, state=state)]
    for index, symbol in enumerate(task.word):
        destination = task.delta[state][symbol]
        events.append(dict(operation='transition', index=index, symbol=symbol, source=state, destination=destination))
        steps.append(texts.t('transition', task.language, index=index+1, symbol=symbol, source=state, destination=destination))
        state = destination
    task._answer = state in task.accepting
    events.append(dict(operation='accept', state=state, accepting=sorted(task.accepting), result=task._answer))
    answer = texts.t('yes' if task._answer else 'no', task.language)
    steps.append(texts.t('accept', task.language, state=state, accepting=sorted(task.accepting), answer=answer))
    task.algorithm_trace = events
    task.computation_inputs = {'start': 0, 'word': task.word, 'delta': {str(k): v for k,v in task.delta.items()}, 'accepting': sorted(task.accepting)}
    task.final_answer = answer
    task.solution_steps = steps + [texts.common('answer_line', task.language, answer=answer)]
