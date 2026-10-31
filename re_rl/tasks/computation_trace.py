"""Exact arithmetic operations recorded as they execute, not reconstructed from answers."""
from fractions import Fraction
import operator

from re_rl.tasks.i18n import TaskTexts

texts = TaskTexts(__file__, 'computation_trace_i18n.json')


def json_value(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(v) for v in value]
    return value


class ExactTrace:
    OPERATIONS = {'add': operator.add, 'sub': operator.sub, 'mul': operator.mul,
                  'div': operator.truediv, 'abs': abs, 'square': lambda v: v * v,
                  'min': min, 'max': max, 'lt': lambda a, b: int(a < b),
                  'ge': lambda a, b: int(a >= b), 'eq': lambda a, b: int(a == b), 'ne': lambda a, b: int(a != b),
                  'floor': lambda v: v.numerator // v.denominator}
    SYMBOLS = {'add': '+', 'sub': '−', 'mul': '×', 'div': '/', 'lt': '<', 'ge': '≥', 'eq': '=', 'ne': '≠'}

    def __init__(self):
        self.events = []

    def calc(self, label, operation, *operands):
        operands = tuple(Fraction(v) for v in operands)
        result = Fraction(self.OPERATIONS[operation](*operands))
        self.events.append(dict(operation=operation, label=label,
                                operands=[str(v) for v in operands], result=str(result)))
        return result

    def accumulate(self, label, values):
        total = Fraction(0)
        for i, value in enumerate(values, 1):
            total = self.calc(f'{label}[1:{i}]', 'add', total, value)
        return total

    def finish(self, task, answer, inputs):
        task.algorithm_trace = self.events
        task.computation_inputs = json_value(inputs)
        task.solution_steps = []
        for event in self.events:
            op, args = event['operation'], event['operands']
            expression = f' {self.SYMBOLS[op]} '.join(f'({v})' for v in args) if op in self.SYMBOLS else f"{op}({', '.join(args)})"
            task.solution_steps.append(texts.t('operation', task.language, label=event['label'], expression=expression, result=event['result']))
        task.final_answer = str(answer)
        task.solution_steps.append(texts.common('answer_line', task.language, answer=task.final_answer))
