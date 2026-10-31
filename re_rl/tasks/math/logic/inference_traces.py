"""Infer answers from formulas, clauses and examples, never generation secrets."""
from itertools import product
from re_rl.tasks.math.logic.formal_logic2_shared.base import _eval


def classify_formula(variables, formula):
    rows = []
    true_count = 0
    for bits in product((False, True), repeat=len(variables)):
        assignment = dict(zip(variables,bits))
        value = _eval(formula,assignment)
        rows.append((assignment,value))
        true_count += int(value)
    total = len(rows)
    classification = 'tautology' if true_count == total else 'contradiction' if true_count == 0 else 'contingent'
    return classification, true_count, rows


def solve_cnf(variable_count, clauses):
    """DPLL with deterministic unit propagation, branching and backtracking."""
    def search(assignment):
        while True:
            pending = []
            for clause in clauses:
                unresolved = []
                satisfied = False
                for variable, positive in clause:
                    if variable in assignment:
                        literal = bool(assignment[variable]) == positive
                        if literal:
                            satisfied = True
                            break
                    else:
                        unresolved.append((variable,positive))
                if satisfied:
                    continue
                if not unresolved:
                    return None
                pending.append(unresolved)
            if not pending:
                return [assignment.get(i,0) for i in range(variable_count)]
            unit = next((clause[0] for clause in pending if len(clause) == 1),None)
            if unit is None:
                break
            variable,positive = unit
            assignment[variable] = int(positive)
        variable = min(v for clause in pending for v,_ in clause)
        for value in (0,1):
            branch = dict(assignment)
            branch[variable] = value
            solution = search(branch)
            if solution is not None:
                return solution
        return None
    return search({})


def rule_candidates(rows,colors):
    candidates = [(name,()) for name in ('reflect_h','reflect_v','rotate180','transpose','tile2','gravity_down')]
    candidates += [('roll_rows',(shift,)) for shift in range(1,rows)]
    candidates += [('color_swap',(a,b)) for a in range(1,colors) for b in range(a,colors)]
    candidates += [('recolor',(a,b)) for a in range(1,colors) for b in range(1,colors)]
    candidates += [('border',(color,)) for color in range(1,colors)]
    return candidates


def apply_rule(grid,name,parameters):
    if name == 'reflect_h': return [row[::-1] for row in grid]
    if name == 'reflect_v': return [row[:] for row in grid[::-1]]
    if name == 'rotate180': return [row[::-1] for row in grid[::-1]]
    if name == 'transpose': return [list(col) for col in zip(*grid)]
    if name == 'tile2':
        top = [row+row for row in grid]
        return top + [row[:] for row in top]
    if name == 'gravity_down':
        rows,cols = len(grid),len(grid[0])
        out = [[0]*cols for _ in range(rows)]
        for col in range(cols):
            values = [grid[row][col] for row in range(rows) if grid[row][col] != 0]
            for offset,value in enumerate(values):
                out[rows-len(values)+offset][col] = value
        return out
    if name == 'roll_rows':
        shift = parameters[0] % len(grid)
        return [row[:] for row in grid[-shift:]+grid[:-shift]] if shift else [row[:] for row in grid]
    if name == 'color_swap':
        a,b = parameters
        return [[b if value == a else a if value == b else value for value in row] for row in grid]
    if name == 'recolor':
        source,destination = parameters
        return [[destination if value == source else value for value in row] for row in grid]
    if name == 'border':
        color = parameters[0]
        width = len(grid[0])+2
        return [[color]*width] + [[color]+row[:]+[color] for row in grid] + [[color]*width]
    raise ValueError(name)


def matching_rules(train, colors):
    return [(name,parameters) for name,parameters in rule_candidates(len(train[0][0]),colors)
            if all(apply_rule(gin,name,parameters) == gout for gin,gout in train)]


def unique_prediction(train,test_grid,colors):
    fits = matching_rules(train,colors)
    predictions = [apply_rule(test_grid,name,parameters) for name,parameters in fits]
    if not predictions or any(value != predictions[0] for value in predictions[1:]):
        raise ValueError('ambiguous_examples')
    return predictions[0]


def infer_arc(train,test_grid,colors,trace):
    fits = []
    for name,parameters in rule_candidates(len(train[0][0]),colors):
        checks = []
        for example,(gin,gout) in enumerate(train):
            actual = apply_rule(gin,name,parameters)
            matches = actual == gout
            checks.append(dict(example=example,matches=matches,actual=actual))
            if not matches:
                break
        trace.events.append(dict(operation='arc_candidate',rule=name,parameters=list(parameters),checks=checks,
                                 fits=len(checks) == len(train) and all(check['matches'] for check in checks)))
        if len(checks) == len(train) and all(check['matches'] for check in checks):
            fits.append((name,parameters))
    predictions = []
    for name,parameters in fits:
        prediction = apply_rule(test_grid,name,parameters)
        predictions.append(prediction)
        trace.events.append(dict(operation='arc_prediction',rule=name,parameters=list(parameters),result=prediction))
    if not predictions or any(value != predictions[0] for value in predictions[1:]):
        raise ValueError('ambiguous_examples')
    selected_name,selected_parameters = fits[0]
    return trace.call(apply_rule,test_grid,selected_name,selected_parameters)
