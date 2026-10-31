"""Constraint search from clues, with domain filtering and explicit backtracking."""
from functools import lru_cache
from itertools import product


@lru_cache(maxsize=None)
def binary_lines(length):
    return tuple(bits for bits in product((0,1),repeat=length)
                 if sum(bits) == length//2
                 and all(not bits[i] == bits[i+1] == bits[i+2] for i in range(length-2)))


def runs(bits):
    result = []
    current = 0
    for bit in bits:
        if bit:
            current += 1
        elif current:
            result.append(current)
            current = 0
    if current: result.append(current)
    return tuple(result)


@lru_cache(maxsize=None)
def run_lines(length,clues):
    return tuple(bits for bits in product((0,1),repeat=length) if runs(bits) == clues)


def solve_lines(row_domains,col_domains,distinct,events):
    rows,cols = len(row_domains),len(col_domains)
    def search(domains,depth):
        while True:
            changed = False
            for axis in (0,1):
                opposite = domains[1-axis]
                for index,candidates in enumerate(domains[axis]):
                    allowed = [set(pattern[index] for pattern in choices) for choices in opposite]
                    removed = []
                    remaining = []
                    for pattern in candidates:
                        bad = next((cell for cell,value in enumerate(pattern) if value not in allowed[cell]),None)
                        if bad is None: remaining.append(pattern)
                        else: removed.append(dict(pattern=list(pattern),cell=bad,value=pattern[bad],allowed=sorted(allowed[bad])))
                    if removed:
                        events.append(dict(operation='grid_filter',depth=depth,axis=axis,index=index,
                                           reason='crossing',removed=removed,remaining=[list(p) for p in remaining]))
                        domains[axis][index] = remaining
                        changed = True
                    if not remaining:
                        events.append(dict(operation='grid_conflict',depth=depth,axis=axis,index=index,reason='empty_domain'))
                        return None
                if distinct:
                    singletons = {}
                    for index,choices in enumerate(domains[axis]):
                        if len(choices) == 1:
                            pattern = choices[0]
                            if pattern in singletons:
                                events.append(dict(operation='grid_conflict',depth=depth,axis=axis,index=index,reason='duplicate_line'))
                                return None
                            singletons[pattern] = index
                    for index,choices in enumerate(domains[axis]):
                        if len(choices) <= 1: continue
                        removed = [dict(pattern=list(p),witness=singletons[p]) for p in choices if p in singletons]
                        if removed:
                            remaining = [p for p in choices if p not in singletons]
                            events.append(dict(operation='grid_filter',depth=depth,axis=axis,index=index,
                                               reason='distinct',removed=removed,remaining=[list(p) for p in remaining]))
                            domains[axis][index] = remaining
                            changed = True
                            if not remaining:
                                events.append(dict(operation='grid_conflict',depth=depth,axis=axis,index=index,reason='empty_domain'))
                                return None
            if not changed: break
        choices = [(len(patterns),axis,index) for axis in (0,1)
                   for index,patterns in enumerate(domains[axis]) if len(patterns) > 1]
        if not choices:
            grid = [list(patterns[0]) for patterns in domains[0]]
            events.append(dict(operation='grid_solution',grid=[row[:] for row in grid]))
            return grid
        _,axis,index = min(choices)
        for pattern in domains[axis][index]:
            events.append(dict(operation='grid_branch',depth=depth,axis=axis,index=index,pattern=list(pattern)))
            branch = [[patterns[:] for patterns in side] for side in domains]
            branch[axis][index] = [pattern]
            result = search(branch,depth+1)
            if result is not None: return result
            events.append(dict(operation='grid_backtrack',depth=depth,axis=axis,index=index,pattern=list(pattern)))
        return None
    initial = [[list(patterns) for patterns in row_domains],[list(patterns) for patterns in col_domains]]
    for axis,side in enumerate(initial):
        for index,patterns in enumerate(side):
            events.append(dict(operation='grid_domain',axis=axis,index=index,patterns=[list(p) for p in patterns]))
            if not patterns:
                events.append(dict(operation='grid_conflict',depth=0,axis=axis,index=index,reason='empty_domain'))
                return None
    return search(initial,0)


def takuzu(n,given,events):
    if n <= 0 or n % 2:
        raise ValueError('invalid_size')
    patterns = binary_lines(n)
    row_domains = [[p for p in patterns if all(p[c] == value for (r,c),value in given.items() if r == row)] for row in range(n)]
    col_domains = [[p for p in patterns if all(p[r] == value for (r,c),value in given.items() if c == col)] for col in range(n)]
    return solve_lines(row_domains,col_domains,True,events)


def nonogram(row_clues,col_clues,events):
    row_domains = [run_lines(len(col_clues),tuple(clues)) for clues in row_clues]
    col_domains = [run_lines(len(row_clues),tuple(clues)) for clues in col_clues]
    return solve_lines(row_domains,col_domains,False,events)


def battleship(row_counts,col_counts,fleet,events):
    n = len(row_counts)
    if n <= 0 or any(length <= 0 for length in fleet):
        return None
    if len(col_counts) != n or sum(row_counts) != sum(col_counts) or sum(row_counts) != sum(fleet):
        return None
    pools = {}
    for length in sorted(set(fleet),reverse=True):
        candidates = []
        for row in range(n):
            for col in range(n):
                for dr,dc in ((0,1),(1,0)) if length > 1 else ((0,1),):
                    cells = [(row+dr*i,col+dc*i) for i in range(length)]
                    if any(r >= n or c >= n for r,c in cells): continue
                    row_use = [sum(r == index for r,c in cells) for index in range(n)]
                    col_use = [sum(c == index for r,c in cells) for index in range(n)]
                    if any(a > b for a,b in zip(row_use,row_counts)) or any(a > b for a,b in zip(col_use,col_counts)): continue
                    mask = sum(1 << (r*n+c) for r,c in cells)
                    halo = 0
                    for r,c in cells:
                        for rr in range(max(0,r-1),min(n,r+2)):
                            for cc in range(max(0,c-1),min(n,c+2)):
                                halo |= 1 << (rr*n+cc)
                    candidates.append((cells,mask,halo,row_use,col_use))
        pools[length] = candidates
        events.append(dict(operation='fleet_domain',length=length,placements=[cells for cells,_,_,_,_ in candidates]))
    def search(ships,occupied,blocked,rows,cols,minimum,depth):
        if not ships:
            if any(rows) or any(cols): return None
            grid = [[int(bool(occupied & (1 << (r*n+c)))) for c in range(n)] for r in range(n)]
            events.append(dict(operation='grid_solution',grid=[row[:] for row in grid]))
            return grid
        # Long ships first; identical ships use increasing placement indices.
        length = ships[0]
        for index in range(minimum.get(length,0),len(pools[length])):
            cells,mask,halo,row_use,col_use = pools[length][index]
            reason = 'touching' if mask & blocked else 'row_quota' if any(a > b for a,b in zip(row_use,rows)) else 'col_quota' if any(a > b for a,b in zip(col_use,cols)) else None
            if reason:
                events.append(dict(operation='fleet_reject',depth=depth,length=length,cells=cells,reason=reason))
                continue
            remaining_rows = [a-b for a,b in zip(rows,row_use)]
            remaining_cols = [a-b for a,b in zip(cols,col_use)]
            next_blocked = blocked | halo
            row_free = [sum(not bool(next_blocked & (1 << (r*n+c))) for c in range(n)) for r in range(n)]
            col_free = [sum(not bool(next_blocked & (1 << (r*n+c))) for r in range(n)) for c in range(n)]
            if any(a > b for a,b in zip(remaining_rows,row_free)) or any(a > b for a,b in zip(remaining_cols,col_free)):
                events.append(dict(operation='fleet_reject',depth=depth,length=length,cells=cells,reason='free_capacity'))
                continue
            events.append(dict(operation='fleet_place',depth=depth,length=length,cells=cells,rows=remaining_rows,cols=remaining_cols))
            next_minimum = dict(minimum)
            next_minimum[length] = index+1
            result = search(ships[1:],occupied|mask,next_blocked,remaining_rows,remaining_cols,next_minimum,depth+1)
            if result is not None: return result
            events.append(dict(operation='fleet_backtrack',depth=depth,length=length,cells=cells))
        return None
    return search(sorted(fleet,reverse=True),0,0,list(row_counts),list(col_counts),{},0)
