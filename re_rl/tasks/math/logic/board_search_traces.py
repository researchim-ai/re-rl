"""Independent search for shading, region stars and Sudoku constraints."""
from collections import deque
from math import isqrt


def hitori(grid,events):
    n = len(grid)
    adjacent = []
    duplicates = []
    for r in range(n):
        for c in range(n):
            cell = r*n+c
            if r+1 < n: adjacent.append((cell,cell+n))
            if c+1 < n: adjacent.append((cell,cell+1))
            duplicates += [(cell,r*n+other) for other in range(c+1,n) if grid[r][other] == grid[r][c]]
            duplicates += [(cell,other*n+c) for other in range(r+1,n) if grid[other][c] == grid[r][c]]
    events.append(dict(operation='hitori_constraints',duplicates=[list(pair) for pair in duplicates],adjacent=[list(pair) for pair in adjacent]))
    def reachable(state,start,depth,final):
        events.append(dict(operation='hitori_walk_start',depth=depth,final=final,start=start,blocked=[cell for cell,value in enumerate(state) if value == 1]))
        seen = {start}
        queue = deque([start])
        while queue:
            cell = queue.popleft()
            row,col = divmod(cell,n)
            discovered = []
            for r,c in ((row-1,col),(row+1,col),(row,col-1),(row,col+1)):
                other = r*n+c
                if 0 <= r < n and 0 <= c < n and state[other] != 1 and other not in seen:
                    seen.add(other);queue.append(other);discovered.append(other)
            events.append(dict(operation='hitori_visit',depth=depth,final=final,cell=cell,discovered=discovered,queue=list(queue)))
        return seen
    def search(state,depth):
        while True:
            changed = False
            for pairs,trigger,forced,reason in ((duplicates,0,1,'duplicate'),(adjacent,1,0,'adjacent')):
                for a,b in pairs:
                    if state[a] == trigger and state[b] == trigger:
                        events.append(dict(operation='hitori_conflict',depth=depth,reason=reason,cells=[a,b]))
                        return None
                    for source,target in ((a,b),(b,a)):
                        if state[source] == trigger and state[target] == -1:
                            state[target] = forced
                            events.append(dict(operation='hitori_force',depth=depth,cell=target,value=forced,source=source,reason=reason))
                            changed = True
            if not changed: break
        whites = [cell for cell,value in enumerate(state) if value == 0]
        if whites:
            seen = reachable(state,whites[0],depth,False)
            possible = all(cell in seen for cell in whites)
            events.append(dict(operation='hitori_connect',depth=depth,start=whites[0],reached=sorted(seen),required=whites,possible=possible,final=False))
            if not possible: return None
        pending = [(a,b) for a,b in duplicates if state[a] != 1 and state[b] != 1]
        if not pending:
            # This is a completion trial, not a forced inference: leave unknown cells white.
            candidate = [0 if value == -1 else value for value in state]
            free = [cell for cell,value in enumerate(candidate) if value == 0]
            seen = reachable(candidate,free[0],depth,True) if free else set()
            connected = bool(free) and len(seen) == len(free)
            events.append(dict(operation='hitori_connect',depth=depth,start=free[0] if free else None,
                               reached=sorted(seen),required=free,possible=connected,final=True))
            if connected:
                shaded = [divmod(cell,n) for cell,value in enumerate(candidate) if value == 1]
                events.append(dict(operation='hitori_solution',shaded=[list(cell) for cell in shaded],completion=candidate))
                return set(shaded)
        unknown = [cell for cell,value in enumerate(state) if value == -1]
        if not unknown: return None
        degree = {cell:sum(cell in pair for pair in pending) for cell in unknown}
        cell = min(unknown,key=lambda value:(-degree[value],value))
        for value in (0,1):
            events.append(dict(operation='hitori_branch',depth=depth,cell=cell,value=value))
            branch = state[:];branch[cell] = value
            result = search(branch,depth+1)
            if result is not None: return result
            events.append(dict(operation='hitori_backtrack',depth=depth,cell=cell,value=value))
        return None
    return search([-1]*(n*n),0)


def star_battle(region,events=None):
    n = len(region)
    if not n or any(len(row) != n for row in region) or len({value for row in region for value in row}) != n:
        raise ValueError('invalid_regions')
    def emit(operation,**values):
        if events is not None: events.append(dict(operation=operation,**values))
    def search(placement,columns,regions):
        row = len(placement)
        if row == n:
            result = [(r,col) for r,col in enumerate(placement)]
            emit('star_solution',stars=[list(cell) for cell in result])
            return result
        checks = []
        available = []
        for col in range(n):
            reason = 'column' if col in columns else 'region' if region[row][col] in regions else 'touching' if row and abs(col-placement[-1]) <= 1 else None
            checks.append(dict(col=col,region=region[row][col],reason=reason))
            if reason is None: available.append(col)
        emit('star_domain',row=row,checks=checks,available=available)
        for col in available:
            emit('star_place',row=row,col=col,region=region[row][col])
            result = search(placement+(col,),columns|{col},regions|{region[row][col]})
            if result is not None: return result
            emit('star_backtrack',row=row,col=col)
        return None
    return search((),set(),set())


def sudoku(puzzle,limit=1,events=None,forbidden=None):
    """MRV search with exact row/column/block masks and a bounded solution count."""
    if limit < 1: raise ValueError('invalid_limit')
    n = len(puzzle)
    block = isqrt(n)
    if not n or block*block != n or any(len(row) != n for row in puzzle): raise ValueError('invalid_size')
    if forbidden is not None:
        forbidden = tuple(forbidden)
        if len(forbidden) != 3 or not 0 <= forbidden[0] < n or not 0 <= forbidden[1] < n or not 1 <= forbidden[2] <= n:
            raise ValueError('invalid_forbidden')
    grid = [row[:] for row in puzzle]
    rows,cols,blocks = [0]*n,[0]*n,[0]*n
    full = (1 << n)-1
    def emit(operation,**values):
        if events is not None: events.append(dict(operation=operation,**values))
    emit('sudoku_start',size=n,limit=limit,forbidden=list(forbidden) if forbidden else None)
    for r in range(n):
        for c in range(n):
            value = grid[r][c]
            if value is None: continue
            if not 1 <= value <= n:
                emit('sudoku_conflict',row=r,col=c,reason='range');return []
            mask = 1 << (value-1)
            b = (r//block)*block+c//block
            if rows[r]&mask or cols[c]&mask or blocks[b]&mask or forbidden == (r,c,value):
                emit('sudoku_conflict',row=r,col=c,reason='given');return []
            rows[r] |= mask;cols[c] |= mask;blocks[b] |= mask
    solutions = []
    def search(depth):
        best = None
        scans = []
        for r in range(n):
            for c in range(n):
                if grid[r][c] is not None: continue
                b = (r//block)*block+c//block
                allowed = full & ~(rows[r]|cols[c]|blocks[b])
                if forbidden is not None and forbidden[:2] == (r,c): allowed &= ~(1 << (forbidden[2]-1))
                if events is not None:
                    scans.append(dict(row=r,col=c,row_mask=rows[r],col_mask=cols[c],block_mask=blocks[b],
                                      values=[value+1 for value in range(n) if allowed & (1 << value)]))
                if not allowed:
                    emit('sudoku_scan',depth=depth,candidates=scans)
                    emit('sudoku_conflict',row=r,col=c,reason='empty_domain')
                    return False
                candidate = (allowed.bit_count(),r,c,b,allowed)
                if best is None or candidate[:3] < best[:3]: best = candidate
        emit('sudoku_scan',depth=depth,candidates=scans)
        if best is None:
            solution = [row[:] for row in grid]
            solutions.append(solution)
            emit('sudoku_solution',grid=[row[:] for row in solution],count=len(solutions))
            return len(solutions) >= limit
        _,r,c,b,allowed = best
        while allowed:
            mask = allowed & -allowed;allowed ^= mask
            value = mask.bit_length()
            grid[r][c] = value;rows[r] |= mask;cols[c] |= mask;blocks[b] |= mask
            emit('sudoku_place',depth=depth,row=r,col=c,value=value)
            stop = search(depth+1)
            grid[r][c] = None;rows[r] ^= mask;cols[c] ^= mask;blocks[b] ^= mask
            if stop: return True
            emit('sudoku_backtrack',depth=depth,row=r,col=c,value=value)
        return False
    search(0)
    emit('sudoku_done',count=len(solutions),limit_reached=len(solutions) >= limit)
    return solutions
