"""Recorded connectivity, tree and degree-sequence algorithms."""
from collections import deque
from fractions import Fraction

from .traces import traversal_trace


def scc_trace(n, edges):
    adj, reverse = [[] for _ in range(n)], [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        reverse[b].append(a)
    seen, order, events = set(), [], []
    def visit(v):
        seen.add(v)
        events.append(dict(event='enter', vertex=v))
        for w in sorted(adj[v]):
            events.append(dict(event='edge', a=v, b=w, seen=int(w in seen)))
            if w not in seen:
                visit(w)
        order.append(v)
        events.append(dict(event='finish', vertex=v, order=order.copy()))
    for v in range(n):
        if v not in seen:
            visit(v)
    events.append(dict(event='reverse', order=list(reversed(order))))
    seen, groups = set(), []
    for v in reversed(order):
        if v in seen:
            continue
        group, queue = [], deque([v])
        seen.add(v)
        while queue:
            a = queue.popleft()
            group.append(a)
            added = [b for b in sorted(reverse[a]) if b not in seen]
            seen.update(added)
            queue.extend(added)
            events.append(dict(event='collect', vertex=a, added=added, queue=list(queue), group=group.copy()))
        groups.append(sorted(group))
        events.append(dict(event='group', group=sorted(group), count=len(groups)))
    events.append(dict(event='done', groups=groups, answer=len(groups)))
    return len(groups), events


def lowlink_trace(n, edges, mode):
    adjacency = [set() for _ in range(n)]
    for a, b in edges:
        adjacency[a].add(b); adjacency[b].add(a)
    disc, low, points, bridges, events = [-1] * n, [-1] * n, set(), [], []
    clock = 0
    def visit(v, parent):
        nonlocal clock
        disc[v] = low[v] = clock; clock += 1
        children = 0
        events.append(dict(event='enter', vertex=v, parent=parent, disc=disc[v], low=low[v]))
        for w in sorted(adjacency[v]):
            if w == parent:
                continue
            if disc[w] == -1:
                children += 1
                events.append(dict(event='tree', a=v, b=w))
                visit(w, v)
                old = low[v]; low[v] = min(low[v], low[w])
                bridge = low[w] > disc[v]
                point = parent != -1 and low[w] >= disc[v]
                if bridge: bridges.append([min(v, w), max(v, w)])
                if point: points.add(v)
                events.append(dict(event='return', a=v, b=w, old=old, child_low=low[w], low=low[v],
                                   disc=disc[v], bridge=int(bridge), point=int(point)))
            else:
                old = low[v]; low[v] = min(low[v], disc[w])
                events.append(dict(event='back', a=v, b=w, old=old, disc=disc[w], low=low[v]))
        if parent == -1:
            point = children > 1
            if point: points.add(v)
            events.append(dict(event='root', vertex=v, children=children, point=int(point)))
    for v in range(n):
        if disc[v] == -1: visit(v, -1)
    answer = len(points) if mode == 'articulation_points' else len(bridges)
    events.append(dict(event='done', points=sorted(points), bridges=sorted(bridges), answer=answer))
    return answer, events


def negative_cycle_trace(n, edges):
    distances, parents, events = [0] * n, [None] * n, [dict(event='init', n=n)]
    last = None
    for phase in range(1, n + 1):
        last = None
        events.append(dict(event='phase', phase=phase))
        for a, b, weight in edges:
            old, candidate = distances[b], distances[a] + weight
            improved = candidate < old
            if improved:
                distances[b], parents[b], last = candidate, a, b
            events.append(dict(event='relax', a=a, b=b, weight=weight, old=old, candidate=candidate,
                               improved=int(improved), distances=distances.copy()))
        if last is None:
            events.append(dict(event='stable', phase=phase))
            return False, events
    vertex = last
    for _ in range(n): vertex = parents[vertex]
    reverse = [vertex]
    current = parents[vertex]
    while current != vertex:
        reverse.append(current); current = parents[current]
    reverse.append(vertex)
    path = list(reversed(reverse))
    weights = {(a, b): w for a, b, w in edges}
    total = sum(weights[a, b] for a, b in zip(path, path[1:]))
    events.append(dict(event='cycle', path=path, weight=total))
    return True, events


def tree_query_trace(n, edges, mode, a=None, b=None):
    """Tree vertices in this function are numbered 1..n."""
    adjacency = [[] for _ in range(n + 1)]
    for v, w in edges: adjacency[v].append(w); adjacency[w].append(v)
    events = []
    if mode == 'leaves':
        leaves = []
        for v in range(1, n + 1):
            if len(adjacency[v]) == 1: leaves.append(v)
            events.append(dict(event='degree', vertex=v, degree=len(adjacency[v]), count=len(leaves)))
        events.append(dict(event='leaves', leaves=leaves, answer=len(leaves)))
        return len(leaves), events
    parent, depth, queue = {1: None}, {1: 0}, deque([1])
    while queue:
        v = queue.popleft()
        for w in sorted(adjacency[v]):
            if w in parent: continue
            parent[w], depth[w] = v, depth[v] + 1
            queue.append(w)
            events.append(dict(event='parent', vertex=w, parent=v, depth=depth[w]))
    if mode == 'height':
        answer = max(depth.values())
        events.append(dict(event='height', depths=sorted(depth.items()), answer=answer))
    elif mode == 'lca':
        while depth[a] > depth[b]:
            events.append(dict(event='lift', vertex=a, parent=parent[a], depth=depth[a]))
            a = parent[a]
        while depth[b] > depth[a]:
            events.append(dict(event='lift', vertex=b, parent=parent[b], depth=depth[b]))
            b = parent[b]
        while a != b:
            events.append(dict(event='pair', a=a, b=b, pa=parent[a], pb=parent[b]))
            a, b = parent[a], parent[b]
        answer = a
        events.append(dict(event='lca', answer=answer))
    else:
        eccentricities = []
        for source in range(n):
            ecc, walk = traversal_trace(n, [(v - 1, w - 1) for v, w in edges], 'all_distances', source)
            # Store 0-based events with explicit rendering offset for this nested traversal.
            events.extend(dict(e, algorithm='walk', vertex_offset=1) for e in walk)
            eccentricities.append(ecc)
        answer = max(eccentricities)
        events.append(dict(event='diameter', values=eccentricities, answer=answer))
    return answer, events


def tree_mis_trace(n, edges):
    adjacency = [[] for _ in range(n)]
    for a, b in edges: adjacency[a].append(b); adjacency[b].append(a)
    events, table = [], {}
    def visit(v, parent):
        skip, take = 0, 1
        events.append(dict(event='enter', vertex=v, parent=parent, skip=skip, take=take))
        for w in sorted(adjacency[v]):
            if w == parent: continue
            cs, ct = visit(w, v)
            skip += max(cs, ct); take += cs
            events.append(dict(event='merge', vertex=v, child=w, child_skip=cs, child_take=ct, skip=skip, take=take))
        table[v] = (skip, take)
        return skip, take
    skip, take = visit(0, -1)
    chosen = []
    def recover(v, parent, parent_taken):
        selected = not parent_taken and table[v][1] > table[v][0]
        if selected: chosen.append(v)
        for w in sorted(adjacency[v]):
            if w != parent: recover(w, v, selected)
    recover(0, -1, False)
    events.append(dict(event='done', skip=skip, take=take, chosen=chosen, answer=max(skip, take)))
    return max(skip, take), events


def tree_times_trace(parents):
    children = [[] for _ in parents]
    for v in range(2, len(parents)): children[parents[v]].append(v)
    enter, sizes, events, clock = [0] * len(parents), [0] * len(parents), [], 0
    def visit(v):
        nonlocal clock
        clock += 1; enter[v] = clock; sizes[v] = 1
        events.append(dict(event='enter', vertex=v, clock=clock, size=1))
        for w in children[v]:
            visit(w); old = sizes[v]; sizes[v] += sizes[w]
            events.append(dict(event='merge', vertex=v, child=w, old=old, child_size=sizes[w], size=sizes[v]))
        events.append(dict(event='exit', vertex=v, enter=enter[v], size=sizes[v]))
    visit(1)
    return enter, sizes, events


def degree_trace(sequence):
    values, events = list(sequence), []
    while True:
        values.sort(reverse=True)
        events.append(dict(event='sort', values=values.copy()))
        if any(v < 0 for v in values):
            events.append(dict(event='negative', values=values.copy())); return False, events
        if not values or values[0] == 0:
            events.append(dict(event='success')); return True, events
        degree = values.pop(0)
        if degree > len(values):
            events.append(dict(event='oversize', degree=degree, remaining=len(values))); return False, events
        events.append(dict(event='remove', degree=degree, values=values.copy()))
        for i in range(degree):
            old = values[i]; values[i] -= 1
            events.append(dict(event='subtract', index=i, old=old, value=values[i], values=values.copy()))


def spanning_trace(n, edges):
    laplacian = [[0] * n for _ in range(n)]
    events = []
    for a, b in edges:
        laplacian[a][a] += 1; laplacian[b][b] += 1
        laplacian[a][b] -= 1; laplacian[b][a] -= 1
        events.append(dict(event='edge', a=a, b=b, matrix=[r.copy() for r in laplacian]))
    matrix = [[Fraction(v) for v in row[:-1]] for row in laplacian[:-1]]
    shown = lambda: [[str(v) for v in row] for row in matrix]
    events.append(dict(event='minor', matrix=shown()))
    sign = 1
    for col in range(n - 1):
        pivot = next((r for r in range(col, n - 1) if matrix[r][col]), None)
        if pivot is None:
            events.append(dict(event='zero', col=col, answer=0)); return 0, events
        if pivot != col:
            matrix[pivot], matrix[col] = matrix[col], matrix[pivot]; sign *= -1
            events.append(dict(event='swap', row=pivot, col=col, sign=sign, matrix=shown()))
        events.append(dict(event='pivot', col=col, value=str(matrix[col][col])))
        for row in range(col + 1, n - 1):
            factor = matrix[row][col] / matrix[col][col]
            for k in range(col, n - 1): matrix[row][k] -= factor * matrix[col][k]
            events.append(dict(event='eliminate', row=row, col=col, factor=str(factor), matrix=shown()))
    determinant = Fraction(sign)
    diagonal = [matrix[i][i] for i in range(n - 1)]
    for value in diagonal: determinant *= value
    answer = int(determinant)
    events.append(dict(event='done', sign=sign, diagonal=[str(v) for v in diagonal], answer=answer))
    return answer, events


def minimax_trace(branches):
    best, choice, events = None, 1, []
    for action, leaves in enumerate(branches, 1):
        minimum = None
        for index, value in enumerate(leaves, 1):
            old = minimum
            minimum = value if minimum is None else min(minimum, value)
            events.append(dict(event='leaf', action=action, index=index, value=value, old=old, minimum=minimum))
        old = best
        if best is None or minimum > best: best, choice = minimum, action
        events.append(dict(event='root', action=action, minimum=minimum, old=old, best=best, choice=choice))
    events.append(dict(event='done', value=best, choice=choice))
    return best, choice, events


def triangle_girth_trace(n, edges, mode):
    from itertools import combinations
    allowed = {tuple(sorted((a, b))) for a, b in edges}
    events, total = [], 0
    if mode == 'triangles':
        for a, b, c in combinations(range(1, n + 1), 3):
            present = [int(edge in allowed) for edge in ((a, b), (a, c), (b, c))]
            total += int(all(present))
            events.append(dict(event='triple', a=a, b=b, c=c, present=present, total=total))
        events.append(dict(event='triangles', answer=total))
        return total, events
    best = None
    for a, b in sorted(allowed):
        remaining = [(u - 1, v - 1) for u, v in sorted(allowed) if (u, v) != (a, b)]
        events.append(dict(event='remove', a=a, b=b))
        distance, walk = traversal_trace(n, remaining, 'bfs', a - 1, b - 1)
        events.extend(dict(e, algorithm='walk', vertex_offset=1) for e in walk)
        candidate = distance + 1 if distance >= 0 else None
        if candidate is not None and (best is None or candidate < best): best = candidate
        events.append(dict(event='candidate', a=a, b=b, distance=distance, candidate=candidate, best=best))
    events.append(dict(event='girth', answer=best or 0))
    return best or 0, events


def wiener_trace(n, edges):
    total, events = 0, []
    for source in range(n):
        _, walk = traversal_trace(n, [(a - 1, b - 1) for a, b in edges], 'all_distances', source)
        events.extend(dict(e, algorithm='walk', vertex_offset=1) for e in walk)
        distances = walk[-1]['distances']
        for target in range(source + 1, n):
            total += distances[target]
            events.append(dict(event='pair', source=source + 1, target=target + 1, distance=distances[target], total=total))
    events.append(dict(event='done', answer=total))
    return total, events


def path_counts_trace(n, edges, source, directed=False):
    adjacency = [[] for _ in range(n)]
    for a, b in edges:
        adjacency[a].append(b)
        if not directed: adjacency[b].append(a)
    distances, ways, events = [-1] * n, [0] * n, []
    distances[source], ways[source] = 0, 1
    if directed:
        from .traces import kahn_trace
        order, cycle, topology = kahn_trace(n, edges)
        if cycle: raise ValueError(edges)
        events.extend(dict(e, algorithm='kahn', vertex_offset=1) for e in topology)
        queue = deque(order)
    else:
        queue = deque([source])
    events.append(dict(event='init', source=source + 1, ways=ways.copy()))
    while queue:
        v = queue.popleft()
        events.append(dict(event='visit', vertex=v + 1, ways=ways[v], distance=distances[v], queue=[w + 1 for w in queue]))
        for w in sorted(adjacency[v]):
            if not directed and distances[w] == -1:
                distances[w] = distances[v] + 1
                queue.append(w)
                events.append(dict(event='discover', a=v + 1, b=w + 1, distance=distances[w], queue=[u + 1 for u in queue]))
            eligible = directed or distances[w] == distances[v] + 1
            old = ways[w]
            if eligible: ways[w] += ways[v]
            events.append(dict(event='edge', a=v + 1, b=w + 1, old=old, addition=ways[v], eligible=int(eligible), value=ways[w]))
    events.append(dict(event='done', distances=distances, ways=ways.copy()))
    return distances, ways, events


def prufer_trace(n, edges):
    adjacency = [set() for _ in range(n + 1)]
    for a, b in edges: adjacency[a].add(b); adjacency[b].add(a)
    events, code = [], []
    for _ in range(n - 2):
        leaves = [v for v in range(1, n + 1) if len(adjacency[v]) == 1]
        leaf = min(leaves); neighbor = next(iter(adjacency[leaf]))
        code.append(neighbor)
        adjacency[leaf].remove(neighbor); adjacency[neighbor].remove(leaf)
        events.append(dict(event='leaf', leaves=leaves, leaf=leaf, neighbor=neighbor, code=code.copy(), degree=len(adjacency[neighbor])))
    events.append(dict(event='done', code=code.copy()))
    return code, events


def expectimax_trace(actions):
    events, best, choice = [], None, 1
    for action, outcomes in enumerate(actions, 1):
        value = Fraction(0)
        for index, (prob, utility) in enumerate(outcomes, 1):
            contribution = prob * utility; value += contribution
            events.append(dict(event='outcome', action=action, index=index, probability=str(prob), utility=utility,
                               contribution=str(contribution), value=str(value)))
        old = best
        if best is None or value > best: best, choice = value, action
        events.append(dict(event='choose', action=action, value=str(value), old=str(old) if old is not None else None, best=str(best), choice=choice))
    events.append(dict(event='done', value=str(best), choice=choice))
    return best, choice, events
