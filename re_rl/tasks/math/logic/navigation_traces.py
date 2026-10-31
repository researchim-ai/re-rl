"""Deterministic searches from public boards, with bounded per-event snapshots."""
from collections import deque
from heapq import heappop, heappush


def sliding(board, n, kind, events):
    board = tuple(board)
    if n < 2 or len(board) != n*n or sorted(board) != list(range(n*n)):
        raise ValueError('invalid_board')
    if kind not in ('solvable', 'min_moves'):
        raise ValueError('invalid_subtype')
    inversions = 0
    for i, a in enumerate(board):
        if not a:
            continue
        for j in range(i+1, len(board)):
            b = board[j]
            if not b:
                continue
            inverted = a > b
            inversions += inverted
            events.append(dict(operation='nav_inversion', i=i, j=j, a=a, b=b,
                               inverted=inverted, total=inversions))
    blank_row = n-board.index(0)//n
    solvable = inversions % 2 == 0 if n % 2 else (inversions+blank_row) % 2 == 1
    events.append(dict(operation='nav_parity', n=n, inversions=inversions,
                       blank_row=blank_row, solvable=solvable))
    if kind == 'solvable':
        return solvable
    if not solvable:
        return -1
    goal = tuple(range(1,n*n))+(0,)

    def heuristic(state):
        return sum(abs(i//n-(v-1)//n)+abs(i%n-(v-1)%n)
                   for i,v in enumerate(state) if v)

    queue = [(heuristic(board), 0, board)]
    best = {board: 0}
    parent = {board: None}
    while queue:
        f,g,state = heappop(queue)
        stale = g != best[state]
        events.append(dict(operation='nav_astar_pop', state=list(state), g=g,
                           h=f-g, f=f, stale=stale, frontier=len(queue)))
        if stale:
            continue
        if state == goal:
            path = []
            while state is not None:
                path.append(list(state))
                state = parent[state]
            events.append(dict(operation='nav_path', path=path[::-1], distance=g))
            return g
        zero = state.index(0)
        r,c = divmod(zero,n)
        for dr,dc in ((-1,0),(1,0),(0,-1),(0,1)):
            nr,nc = r+dr,c+dc
            if not (0 <= nr < n and 0 <= nc < n):
                continue
            neighbor = list(state)
            k = nr*n+nc
            neighbor[zero],neighbor[k] = neighbor[k],neighbor[zero]
            neighbor = tuple(neighbor)
            old = best.get(neighbor)
            candidate = g+1
            accepted = old is None or candidate < old
            h = heuristic(neighbor)
            events.append(dict(operation='nav_astar_edge', state=list(state),
                               neighbor=list(neighbor), g=candidate, h=h, f=candidate+h,
                               old=old, accepted=accepted))
            if accepted:
                best[neighbor] = candidate
                parent[neighbor] = state
                heappush(queue,(candidate+h,candidate,neighbor))
    return -1


def maze(grid, events):
    n = len(grid)
    if not n or any(len(row) != n or any(v not in (0,1) for v in row) for row in grid):
        raise ValueError('invalid_grid')
    start,goal = (0,0),(n-1,n-1)
    if grid[0][0] or grid[-1][-1]:
        events.append(dict(operation='nav_blocked', start=grid[0][0], goal=grid[-1][-1]))
        return -1
    queue = deque([start])
    distance = {start:0}
    parent = {start:None}
    while queue:
        current = queue.popleft()
        d = distance[current]
        events.append(dict(operation='nav_bfs_pop', cell=list(current), distance=d, frontier=len(queue)))
        if current == goal:
            path = []
            while current is not None:
                path.append(list(current))
                current = parent[current]
            events.append(dict(operation='nav_path', path=path[::-1], distance=d))
            return d
        x,y = current
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx,ny = x+dx,y+dy
            neighbor = (nx,ny)
            inside = 0 <= nx < n and 0 <= ny < n
            wall = bool(grid[ny][nx]) if inside else None
            visited = neighbor in distance
            accepted = inside and not wall and not visited
            events.append(dict(operation='nav_bfs_edge', cell=list(current), neighbor=list(neighbor),
                               inside=inside, wall=wall, visited=visited, accepted=accepted, distance=d+1))
            if accepted:
                distance[neighbor] = d+1
                parent[neighbor] = current
                queue.append(neighbor)
    events.append(dict(operation='nav_exhausted', visited=len(distance), distance=-1))
    return -1


def commands(start_dir, commands, events):
    if start_dir not in range(4):
        raise ValueError('invalid_direction')
    x = y = 0
    d = start_dir
    directions = ((0,1),(1,0),(0,-1),(-1,0))
    for index,(kind,k) in enumerate(commands):
        before = [x,y,d]
        if kind == 'fwd':
            if not isinstance(k,int) or k < 0:
                raise ValueError('invalid_distance')
            dx,dy = directions[d]
            x,y = x+dx*k,y+dy*k
        elif kind == 'left':
            d = (d-1)%4
        elif kind == 'right':
            d = (d+1)%4
        else:
            raise ValueError('invalid_command')
        events.append(dict(operation='nav_command', index=index, kind=kind, amount=k,
                           before=before, after=[x,y,d]))
    events.append(dict(operation='nav_position', position=[x,y,d]))
    return x,y,d
