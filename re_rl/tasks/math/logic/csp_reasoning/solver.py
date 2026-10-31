"""Public finite-domain models; first solution is sufficient, uniqueness is not required."""
from re_rl.tasks.math.logic.csp_search_traces import finite_csp


def latin(puzzle, events):
    n = len(puzzle)
    if not 2 <= n <= 9 or any(len(row) != n for row in puzzle):
        raise ValueError('invalid_grid')
    domains = []
    for row in puzzle:
        for value in row:
            if type(value) is not int or not 0 <= value <= n:
                raise ValueError('invalid_cell')
            domains.append({value} if value else set(range(1,n+1)))
    groups = [[r*n+c for c in range(n)] for r in range(n)]
    groups += [[r*n+c for r in range(n)] for c in range(n)]
    result = finite_csp(domains,[],groups,events)
    if result is None:
        raise ValueError('unsatisfiable')
    return [result[r*n:(r+1)*n] for r in range(n)]


def mini_kakuro(sums, events):
    if set(sums) != {'S1','S2','S3','S4'} or any(type(v) is not int for v in sums.values()):
        raise ValueError('invalid_sums')
    tables = []
    for cells,key in [((0,1),'S1'),((2,3),'S2'),((0,2),'S3'),((1,3),'S4')]:
        allowed = [(a,b) for a in range(1,10) for b in range(1,10) if a+b==sums[key]]
        tables.append((cells,allowed))
    # Only the two row inequalities stated in this task's public contract.
    result = finite_csp([set(range(1,10)) for _ in range(4)],tables,[(0,1),(2,3)],events)
    if result is None:
        raise ValueError('unsatisfiable')
    return result
