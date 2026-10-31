"""Small finite-domain solvers recording supports, conflicts and backtracking."""
from fractions import Fraction
from itertools import permutations, product
from math import prod
from re_rl.tasks.math.logic.grid_search_traces import solve_lines


def kakuro_solutions(s1,s2,v1,v2,events=None,limit=None):
    solutions = []
    for a in range(1,10):
        b = s1-a
        c = v1-a
        d = v2-b
        e = s2-c-d
        values = (a,b,c,d,e)
        in_range = all(1 <= value <= 9 for value in values)
        distinct = a != b and len({c,d,e}) == 3 and a != c and b != d
        valid = in_range and distinct
        if events is not None:
            events.append(dict(operation='kakuro_candidate',values=list(values),s1=s1,s2=s2,v1=v1,v2=v2,
                               in_range=in_range,distinct=distinct,valid=valid))
        if valid:
            solutions.append(values)
            if limit is not None and len(solutions) >= limit: break
    return solutions


def queens(n,count_all,events):
    if n < 0: raise ValueError('invalid_size')
    full = (1 << n)-1
    count = 0
    first = None
    def search(placement,columns,down,up):
        nonlocal count,first
        row = len(placement)
        if row == n:
            count += 1
            if first is None: first = list(placement)
            events.append(dict(operation='queens_solution',placement=list(placement),count=count))
            return not count_all
        available = full & ~(columns|down|up)
        events.append(dict(operation='queens_domain',row=row,columns=columns,down=down,up=up,
                           available=[col for col in range(n) if available & (1 << col)]))
        if not available:
            events.append(dict(operation='queens_dead_end',row=row,placement=list(placement)))
        while available:
            bit = available & -available
            available ^= bit
            col = bit.bit_length()-1
            events.append(dict(operation='queens_place',row=row,col=col))
            if search(placement+(col,),columns|bit,((down|bit) << 1)&full,(up|bit) >> 1): return True
            events.append(dict(operation='queens_remove',row=row,col=col))
        return False
    search((),0,0,0)
    events.append(dict(operation='queens_result',n=n,count=count,complete=count_all))
    return count,first


def finite_csp(initial,tables,distinct_groups,events):
    """Generalized arc consistency for explicit tables plus singleton all-different."""
    for index,domain in enumerate(initial):
        events.append(dict(operation='csp_domain',index=index,values=sorted(domain)))
    for table,(cells,allowed) in enumerate(tables):
        events.append(dict(operation='csp_table_init',table=table,cells=list(cells),tuples=[list(values) for values in allowed]))
    def search(domains,depth):
        while True:
            changed = False
            if any(not domain for domain in domains):
                events.append(dict(operation='csp_conflict',depth=depth,reason='empty_domain',cells=[cell for cell,domain in enumerate(domains) if not domain]))
                return None
            for group,cells in enumerate(distinct_groups):
                used = {}
                for cell in cells:
                    if len(domains[cell]) == 1:
                        value = next(iter(domains[cell]))
                        if value in used:
                            events.append(dict(operation='csp_conflict',depth=depth,reason='duplicate',cells=[used[value],cell],value=value))
                            return None
                        used[value] = cell
                for cell in cells:
                    if len(domains[cell]) == 1: continue
                    removed = sorted(domains[cell]&used.keys())
                    if removed:
                        domains[cell] -= set(removed)
                        events.append(dict(operation='csp_filter',depth=depth,index=cell,reason='distinct',constraint=group,
                                           removed=removed,supports={str(value):used[value] for value in removed},remaining=sorted(domains[cell])))
                        changed = True
            for table,(cells,allowed) in enumerate(tables):
                supported = [values for values in allowed if all(value in domains[cell] for cell,value in zip(cells,values))]
                if not supported:
                    events.append(dict(operation='csp_conflict',depth=depth,reason='unsupported_table',table=table,
                                       domains={str(cell):sorted(domains[cell]) for cell in cells}))
                    return None
                for offset,cell in enumerate(cells):
                    values = {row[offset] for row in supported}
                    removed = sorted(domains[cell]-values)
                    if removed:
                        domains[cell] &= values
                        events.append(dict(operation='csp_filter',depth=depth,index=cell,reason='table',constraint=table,
                                           removed=removed,supports=sorted(values),remaining=sorted(domains[cell])))
                        changed = True
            if not changed: break
        undecided = [(len(domain),cell) for cell,domain in enumerate(domains) if len(domain) > 1]
        if not undecided:
            result = [next(iter(domain)) for domain in domains]
            events.append(dict(operation='csp_solution',values=result[:]))
            return result
        _,cell = min(undecided)
        for value in sorted(domains[cell]):
            events.append(dict(operation='csp_branch',depth=depth,index=cell,value=value))
            branch = [set(domain) for domain in domains]
            branch[cell] = {value}
            result = search(branch,depth+1)
            if result is not None: return result
            events.append(dict(operation='csp_backtrack',depth=depth,index=cell,value=value))
        return None
    return search([set(domain) for domain in initial],0)


def magic_square(given,events):
    domains = [set(range(1,10)) for _ in range(9)]
    for cell,value in given.items():
        if cell not in range(9) or value not in range(1,10): return None
        domains[cell] = {value}
    triples = tuple(values for values in permutations(range(1,10),3) if sum(values) == 15)
    lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    return finite_csp(domains,[(line,triples) for line in lines],[tuple(range(9))],events)


def cage_value(values,operation):
    if operation == '=': return values[0] if len(values) == 1 else None
    if operation == '+': return sum(values)
    if operation == '*': return prod(values)
    if len(values) != 2: return None
    if operation == '-': return abs(values[0]-values[1])
    if operation == '/': return Fraction(max(values),min(values))
    raise ValueError(operation)


def kenken(n,cages,clues,events):
    if len(cages) != len(clues): raise ValueError('invalid_cages')
    covered = [r*n+c for cage in cages for r,c in cage]
    if any(not 0 <= r < n or not 0 <= c < n for cage in cages for r,c in cage) or sorted(covered) != list(range(n*n)):
        raise ValueError('invalid_cages')
    tables = []
    for index,(cage,(operation,target)) in enumerate(zip(cages,clues)):
        allowed = []
        checks = []
        for values in product(range(1,n+1),repeat=len(cage)):
            actual = cage_value(values,operation)
            matches = actual == target
            checks.append(dict(values=list(values),result=str(actual),matches=matches))
            if matches: allowed.append(values)
        events.append(dict(operation='cage_candidates',cage=index,cells=cage,operator=operation,target=target,checks=checks))
        tables.append(([r*n+c for r,c in cage],tuple(allowed)))
    groups = [tuple(r*n+c for c in range(n)) for r in range(n)] + [tuple(r*n+c for r in range(n)) for c in range(n)]
    flat = finite_csp([set(range(1,n+1)) for _ in range(n*n)],tables,groups,events)
    return [flat[r*n:(r+1)*n] for r in range(n)] if flat is not None else None


def visible(values):
    maximum = 0
    count = 0
    steps = []
    for value in values:
        seen = value > maximum
        if seen:
            maximum = value
            count += 1
        steps.append(dict(height=value,visible=seen,maximum=maximum,count=count))
    return count,steps


def skyscrapers(n,clues,events):
    patterns = tuple(permutations(range(1,n+1)))
    domains = []
    for axis,sides in enumerate((('left','right'),('top','bottom'))):
        side_domains = []
        for index in range(n):
            candidates = []
            checks = []
            for pattern in patterns:
                forward,forward_steps = visible(pattern)
                backward,backward_steps = visible(pattern[::-1])
                matches = forward == clues[sides[0]][index] and backward == clues[sides[1]][index]
                checks.append(dict(pattern=list(pattern),forward=forward,backward=backward,
                                   forward_steps=forward_steps,backward_steps=backward_steps,matches=matches))
                if matches: candidates.append(pattern)
            events.append(dict(operation='sky_candidates',axis=axis,index=index,
                               forward=clues[sides[0]][index],backward=clues[sides[1]][index],checks=checks))
            side_domains.append(candidates)
        domains.append(side_domains)
    return solve_lines(domains[0],domains[1],False,events)
