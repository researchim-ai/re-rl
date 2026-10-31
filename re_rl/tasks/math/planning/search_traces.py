"""Public-input planners with parent links and actual state-transition certificates."""
from collections import deque
from functools import reduce
from math import gcd


def bfs(initial, goal, successors, events):
    queue = deque([initial])
    parents = {initial:None}
    distances = {initial:0}
    while queue:
        state = queue.popleft()
        distance = distances[state]
        events.append(dict(operation='plan_pop',state=list(state),distance=distance,frontier=len(queue)))
        if goal(state):
            path = []
            while state is not None:
                link = parents[state]
                path.append((state,None if link is None else link[1]))
                state = None if link is None else link[0]
            path.reverse()
            events.append(dict(operation='plan_path',path=[(list(s),a) for s,a in path],distance=distance))
            return path
        for neighbor,action in successors(state):
            visited = neighbor in parents
            events.append(dict(operation='plan_edge',state=list(state),action=list(action),
                               neighbor=list(neighbor),visited=visited,distance=distance+1))
            if not visited:
                parents[neighbor] = (state,action)
                distances[neighbor] = distance+1
                queue.append(neighbor)
    events.append(dict(operation='plan_exhausted',visited=len(parents)))
    return []


def jug_successors(state,capacities):
    for i,capacity in enumerate(capacities):
        if state[i] < capacity:
            other = list(state);other[i] = capacity
            yield tuple(other),('fill',i)
        if state[i] > 0:
            other = list(state);other[i] = 0
            yield tuple(other),('empty',i)
        for j in range(len(state)):
            if i == j or state[i] == 0 or state[j] == capacities[j]:
                continue
            amount = min(state[i],capacities[j]-state[j])
            other = list(state);other[i] -= amount;other[j] += amount
            yield tuple(other),('pour',i,j)


def water_jug(capacities,target,events):
    divisor = reduce(gcd,capacities)
    possible = target <= max(capacities) and target % divisor == 0
    events.append(dict(operation='plan_jug_gcd',capacities=list(capacities),target=target,gcd=divisor,possible=possible))
    if not possible:
        return []
    return bfs((0,)*len(capacities),lambda s:target in s,
               lambda s:jug_successors(s,capacities),events)


def validate_blocks(blocks,state):
    if set(state) != set(blocks):
        raise ValueError('invalid_blocks')
    occupied = set()
    for block in blocks:
        support = state[block]
        if support != 'table':
            if support not in blocks or support in occupied:
                raise ValueError('invalid_blocks')
            occupied.add(support)
        seen = {block}
        while support != 'table':
            if support in seen:
                raise ValueError('cyclic_blocks')
            seen.add(support)
            support = state[support]


def blocks_world(blocks,initial,goal,events):
    validate_blocks(blocks,initial);validate_blocks(blocks,goal)
    def encoded(state):
        return tuple(-1 if state[b] == 'table' else blocks.index(state[b]) for b in blocks)
    def successors(state):
        clear = [i for i in range(len(blocks)) if i not in state]
        events.append(dict(operation='plan_clear',state=list(state),clear=clear))
        for block in clear:
            for target in [-1]+clear:
                if target == block or state[block] == target:
                    continue
                other = list(state);other[block] = target
                yield tuple(other),(block,target)
    target = encoded(goal)
    return bfs(encoded(initial),lambda s:s == target,successors,events)


def hanoi(n,source,target,auxiliary,events):
    pegs = {p:[] for p in (source,target,auxiliary)}
    pegs[source] = list(range(n,0,-1))
    moves = []
    def transfer(count,start,end,spare,depth):
        events.append(dict(operation='plan_hanoi_call',n=count,source=start,target=end,auxiliary=spare,depth=depth))
        if count == 0:
            events.append(dict(operation='plan_hanoi_return',n=count,depth=depth))
            return
        transfer(count-1,start,spare,end,depth+1)
        before = {p:list(v) for p,v in pegs.items()}
        disk = pegs[start].pop()
        if disk != count or (pegs[end] and pegs[end][-1] < disk):
            raise RuntimeError('illegal_hanoi_move')
        pegs[end].append(disk)
        moves.append((disk,start,end))
        events.append(dict(operation='plan_hanoi_move',disk=disk,source=start,target=end,
                           before=before,after={p:list(v) for p,v in pegs.items()}))
        transfer(count-1,spare,end,start,depth+1)
        events.append(dict(operation='plan_hanoi_return',n=count,depth=depth))
    transfer(n,source,target,auxiliary,0)
    return moves
