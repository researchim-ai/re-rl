"""Evaluate repository-owned arithmetic expressions with an event per operation."""
import ast
from fractions import Fraction
import math
import operator
from re_rl.tasks.execution_trace import snapshot

def rational_power(base, exponent):
    base, exponent = Fraction(base), Fraction(exponent)
    degree = exponent.denominator
    def root(value):
        lo, hi = 0, max(1, value)
        while lo < hi:
            mid = (lo + hi) // 2
            if mid ** degree < value:
                lo = mid + 1
            else:
                hi = mid
        return lo
    numerator, denominator = root(base.numerator), root(base.denominator)
    if numerator ** degree == base.numerator and denominator ** degree == base.denominator:
        return Fraction(numerator, denominator) ** exponent.numerator
    return float(base) ** float(exponent)


_BINARY = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
           ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
           ast.Mod: operator.mod, ast.Pow: rational_power, ast.BitXor: operator.xor,
           ast.RShift: operator.rshift, ast.LShift: operator.lshift}
_FUNCTIONS = {'abs': abs, 'min': min, 'max': max, 'sum': sum, 'len': len,
              'gcd': math.gcd, 'sqrt': lambda value: rational_power(value, Fraction(1,2)), 'isqrt': math.isqrt,
              'round': round, 'int': int, 'Fraction': Fraction}


def evaluate(expression, variables, events):
    """No arbitrary Python execution: only the arithmetic AST below is accepted."""
    def visit(node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            value = variables[node.id]
            result = Fraction(value) if isinstance(value, int) and not isinstance(value, bool) else value
            events.append(dict(operation='expression', expression=node.id, operands=[snapshot(result)], result=snapshot(result)))
            return result
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, (ast.BitXor, ast.LShift, ast.RShift)):
                left, right = int(left), int(right)
            result = _BINARY[type(node.op)](left, right)
            operands = [left, right]
        elif isinstance(node, ast.UnaryOp):
            operand = visit(node.operand)
            result = -operand if isinstance(node.op, ast.USub) else +operand
            operands = [operand]
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCTIONS:
            operands = [visit(arg) for arg in node.args]
            if node.func.id in ('gcd', 'isqrt', 'int'):
                operands = [int(value) for value in operands]
            result = _FUNCTIONS[node.func.id](*operands)
        else:
            raise ValueError(ast.dump(node))
        events.append(dict(operation='expression', expression=ast.unparse(node),
                           operands=snapshot(operands), result=snapshot(result)))
        return result
    return visit(ast.parse(expression, mode='eval').body)
