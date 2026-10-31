"""Deterministic graph algorithms with replayable, JSON-safe event traces."""
import heapq
from collections import deque


def dijkstra_trace(n, edges, source, target):
    adjacency = [[] for _ in range(n)]
    for a, b, weight in edges:
        if weight < 0:
            raise ValueError(weight)
        adjacency[a].append((b, weight))
        adjacency[b].append((a, weight))
    distances = [None] * n
    distances[source] = 0
    parents = [None] * n
    events = [dict(event='init', source=source, target=target, distances=distances.copy())]
    queue = [(0, source)]
    settled = set()
    while queue:
        distance, vertex = heapq.heappop(queue)
        if vertex in settled or distance != distances[vertex]:
            events.append(dict(event='stale', vertex=vertex, distance=distance))
            continue
        settled.add(vertex)
        events.append(dict(event='settle', vertex=vertex, distance=distance, distances=distances.copy()))
        if vertex == target:
            break
        for neighbor, weight in sorted(adjacency[vertex]):
            if neighbor in settled:
                continue
            candidate = distance + weight
            old = distances[neighbor]
            improved = old is None or candidate < old
            if improved:
                distances[neighbor] = candidate
                parents[neighbor] = vertex
                heapq.heappush(queue, (candidate, neighbor))
            events.append(dict(event='relax', vertex=vertex, neighbor=neighbor, weight=weight,
                               distance=distance, candidate=candidate, old=old,
                               improved=improved, distances=distances.copy()))
    path = []
    if distances[target] is not None:
        vertex = target
        while vertex is not None:
            path.append(vertex)
            vertex = parents[vertex]
        path.reverse()
    answer = distances[target] if path else -1
    weights = [min(w for v, w in adjacency[a] if v == b) for a, b in zip(path, path[1:])]
    if path:
        events.append(dict(event='path', path=path, weights=weights, answer=answer))
    else:
        events.append(dict(event='unreachable', source=source, target=target, path=[], answer=-1))
    return answer, events


def kruskal_trace(n, edges):
    parent = list(range(n))
    def root(vertex):
        while vertex != parent[vertex]:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex
    ordered = sorted(edges, key=lambda e: (e[2], min(e[0], e[1]), max(e[0], e[1])))
    events = [dict(event='init', edges=[list(e) for e in ordered])]
    total, selected = 0, []
    for a, b, weight in ordered:
        ra, rb = root(a), root(b)
        accepted = ra != rb
        if accepted:
            parent[ra] = rb
            total += weight
            selected.append([a, b, weight])
        events.append(dict(event='edge', a=a, b=b, weight=weight, accepted=accepted,
                           total=total, count=len(selected)))
        if len(selected) == n - 1:
            break
    events.append(dict(event='tree', edges=selected, total=total, count=len(selected)))
    return total, events


def kahn_trace(n, edges):
    adjacency = [[] for _ in range(n)]
    degrees = [0] * n
    for a, b in edges:
        adjacency[a].append(b)
        degrees[b] += 1
    queue = [v for v in range(n) if degrees[v] == 0]
    heapq.heapify(queue)
    events = [dict(event='init', degrees=degrees.copy(), queue=sorted(queue))]
    order = []
    while queue:
        vertex = heapq.heappop(queue)
        order.append(vertex)
        events.append(dict(event='take', vertex=vertex, order=order.copy(), queue=sorted(queue)))
        for neighbor in sorted(adjacency[vertex]):
            old = degrees[neighbor]
            degrees[neighbor] -= 1
            if degrees[neighbor] == 0:
                heapq.heappush(queue, neighbor)
            events.append(dict(event='remove', vertex=vertex, neighbor=neighbor, old=old,
                               degree=degrees[neighbor], queue=sorted(queue)))
    blocked = [v for v in range(n) if degrees[v] > 0]
    events.append(dict(event='done', order=order.copy(), blocked=blocked,
                       count=len(order), n=n, cycle=bool(blocked)))
    return order, bool(blocked), events


def flow_trace(n, edges, source, target):
    capacity = [[0] * n for _ in range(n)]
    for a, b, c in edges:
        capacity[a][b] += c
    residual = [row.copy() for row in capacity]
    total = 0
    events = [dict(event='init', source=source, target=target)]
    while True:
        parents = [None] * n
        parents[source] = source
        queue = deque([source])
        events.append(dict(event='bfs', queue=[source], total=total))
        while queue and parents[target] is None:
            vertex = queue.popleft()
            events.append(dict(event='visit', vertex=vertex, queue=list(queue)))
            for neighbor in range(n):
                if parents[neighbor] is None and residual[vertex][neighbor] > 0:
                    parents[neighbor] = vertex
                    queue.append(neighbor)
                    events.append(dict(event='discover', vertex=vertex, neighbor=neighbor,
                                       capacity=residual[vertex][neighbor], queue=list(queue)))
        if parents[target] is None:
            break
        path = [target]
        while path[-1] != source:
            path.append(parents[path[-1]])
        path.reverse()
        bottleneck = min(residual[a][b] for a, b in zip(path, path[1:]))
        total += bottleneck
        events.append(dict(event='augment', path=path, bottleneck=bottleneck, total=total))
        for a, b in zip(path, path[1:]):
            old_forward, old_reverse = residual[a][b], residual[b][a]
            residual[a][b] -= bottleneck
            residual[b][a] += bottleneck
            events.append(dict(event='residual', a=a, b=b, old_forward=old_forward,
                               forward=residual[a][b], old_reverse=old_reverse,
                               reverse=residual[b][a], bottleneck=bottleneck))
    reachable = {source}
    queue = deque([source])
    while queue:
        a = queue.popleft()
        for b in range(n):
            if b not in reachable and residual[a][b] > 0:
                reachable.add(b)
                queue.append(b)
    cut_edges = [[a, b, c] for a, b, c in edges if a in reachable and b not in reachable]
    cut = sum(e[2] for e in cut_edges)
    events.append(dict(event='cut', reachable=sorted(reachable), edges=cut_edges, capacity=cut, total=total))
    return total, events


def coloring_trace(n, edges, limit=None):
    adjacency = [set() for _ in range(n)]
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    events = [dict(event='init')]
    for k in (range(1, n + 1) if limit is None else [limit]):
        colors = [0] * n
        events.append(dict(event='try', k=k))
        def search(vertex, used):
            if vertex == n:
                return True
            # Permutations of unused color labels describe equivalent branches.
            for color in range(1, min(k, used + 1) + 1):
                conflicts = [u for u in sorted(adjacency[vertex]) if colors[u] == color]
                if conflicts:
                    events.append(dict(event='conflict', vertex=vertex, color=color, neighbors=conflicts))
                    continue
                colors[vertex] = color
                events.append(dict(event='assign', vertex=vertex, color=color, colors=colors.copy()))
                if search(vertex + 1, max(used, color)):
                    return True
                colors[vertex] = 0
                events.append(dict(event='backtrack', vertex=vertex, color=color, colors=colors.copy()))
            return False
        if search(0, 0):
            events.append(dict(event='success', k=k, colors=colors.copy()))
            return k, events
        events.append(dict(event='impossible', k=k))
    return None, events


def traversal_trace(n, edges, mode, source=0, target=None):
    """BFS distances, connected components or a two-coloring certificate."""
    adjacency = [set() for _ in range(n)]
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    seen, colors, distances, parents = set(), {}, {}, {}
    events = [dict(event='init', mode=mode, n=n)]
    components = 0
    for root in ([source] if mode in ('bfs', 'all_distances') else range(n)):
        if root in seen:
            continue
        components += 1
        queue = deque([root])
        seen.add(root)
        colors[root] = 0
        distances[root] = 0
        parents[root] = None
        events.append(dict(event='root', vertex=root, component=components, queue=list(queue)))
        while queue:
            vertex = queue.popleft()
            events.append(dict(event='visit', vertex=vertex, distance=distances[vertex],
                               color=colors[vertex], queue=list(queue)))
            for neighbor in sorted(adjacency[vertex]):
                if neighbor not in seen:
                    seen.add(neighbor)
                    parents[neighbor] = vertex
                    colors[neighbor] = 1 - colors[vertex]
                    distances[neighbor] = distances[vertex] + 1
                    queue.append(neighbor)
                    events.append(dict(event='discover', vertex=vertex, neighbor=neighbor,
                                       distance=distances[neighbor], color=colors[neighbor], queue=list(queue)))
                else:
                    conflict = colors[vertex] == colors[neighbor]
                    events.append(dict(event='check', vertex=vertex, neighbor=neighbor,
                                       left=colors[vertex], right=colors[neighbor]))
                    if mode == 'bipartite' and conflict:
                        events.append(dict(event='conflict', vertex=vertex, neighbor=neighbor, color=colors[vertex]))
                        return False, events
    if mode == 'all_distances':
        answer = max(distances.values(), default=0)
        events.append(dict(event='table', source=source, distances=[distances.get(v) for v in range(n)], answer=answer))
    elif mode == 'bfs':
        path = []
        vertex = target
        if vertex in seen:
            while vertex is not None:
                path.append(vertex)
                vertex = parents[vertex]
            path.reverse()
        answer = distances.get(target, -1)
        events.append(dict(event='distance', source=source, target=target, path=path, answer=answer))
    elif mode == 'components':
        answer = components
        events.append(dict(event='components', answer=answer, visited=sorted(seen)))
    else:
        answer = True
        events.append(dict(event='bipartite', colors=[colors[v] for v in range(n)]))
    return answer, events


def euler_trace(n, edges):
    degrees = [0] * n
    adjacency = [[] for _ in range(n)]
    events = [dict(event='init', n=n)]
    for index, (a, b) in enumerate(edges):
        degrees[a] += 1
        degrees[b] += 1
        adjacency[a].append((b, index))
        adjacency[b].append((a, index))
        events.append(dict(event='degree', a=a, b=b, degrees=degrees.copy()))
    active = [v for v in range(n) if degrees[v]]
    odd = [v for v in active if degrees[v] % 2]
    events.append(dict(event='parity', degrees=degrees.copy(), odd=odd))
    if not active:
        events.append(dict(event='empty'))
        return False, events
    seen, queue = {active[0]}, deque([active[0]])
    while queue:
        a = queue.popleft()
        discovered = sorted({b for b, _ in adjacency[a]} - seen)
        seen.update(discovered)
        queue.extend(discovered)
        events.append(dict(event='connect', vertex=a, discovered=discovered, queue=list(queue)))
    missing = sorted(set(active) - seen)
    events.append(dict(event='connected', missing=missing))
    if missing or len(odd) not in (0, 2):
        events.append(dict(event='impossible', missing=missing, odd=odd))
        return False, events
    start = odd[0] if odd else active[0]
    stack, route, used = [start], [], set()
    events.append(dict(event='start', vertex=start, stack=stack.copy()))
    while stack:
        vertex = stack[-1]
        while adjacency[vertex] and adjacency[vertex][-1][1] in used:
            adjacency[vertex].pop()
        if adjacency[vertex]:
            neighbor, edge = adjacency[vertex].pop()
            used.add(edge)
            stack.append(neighbor)
            events.append(dict(event='edge', a=vertex, b=neighbor, edge=edge, stack=stack.copy()))
        else:
            route.append(stack.pop())
            events.append(dict(event='pop', vertex=vertex, stack=stack.copy(), reverse_route=route.copy()))
    route.reverse()
    events.append(dict(event='path', path=route, count=len(used), total=len(edges)))
    return True, events


def hamilton_trace(n, edges):
    adjacency = [set() for _ in range(n)]
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    parents = {(1 << v, v): None for v in range(n)}
    events = [dict(event='init', starts=[[1 << v, v] for v in range(n)])]
    full = (1 << n) - 1
    for mask in range(1, full + 1):
        for vertex in range(n):
            if (mask, vertex) not in parents:
                continue
            choices = [w for w in sorted(adjacency[vertex]) if not mask & (1 << w)]
            events.append(dict(event='expand', mask=mask, vertex=vertex, choices=choices))
            if mask == full:
                path, current = [], (mask, vertex)
                while current is not None:
                    path.append(current[1])
                    current = parents[current]
                path.reverse()
                events.append(dict(event='path', path=path, mask=full))
                return True, events
            for neighbor in choices:
                new = (mask | (1 << neighbor), neighbor)
                fresh = new not in parents
                if fresh:
                    parents[new] = (mask, vertex)
                events.append(dict(event='transition', mask=mask, vertex=vertex, neighbor=neighbor,
                                   new_mask=new[0], fresh=int(fresh)))
    events.append(dict(event='impossible', mask=full, states=len(parents)))
    return False, events


def matching_trace(left_size, right_size, edges):
    adjacency = [[] for _ in range(left_size)]
    for left, right in edges:
        adjacency[left].append(right)
    match_l, match_r = {}, {}
    events = [dict(event='init', left_size=left_size, right_size=right_size)]
    for root in range(left_size):
        queue, seen_l, parent_r = deque([root]), {root}, {}
        events.append(dict(event='start', left=root, queue=list(queue)))
        free = None
        while queue and free is None:
            left = queue.popleft()
            events.append(dict(event='visit', left=left, queue=list(queue)))
            for right in sorted(adjacency[left]):
                if right in parent_r:
                    events.append(dict(event='seen', left=left, right=right))
                    continue
                parent_r[right] = left
                owner = match_r.get(right)
                events.append(dict(event='inspect', left=left, right=right, owner=owner))
                if owner is None:
                    free = right
                    break
                if owner not in seen_l:
                    seen_l.add(owner)
                    queue.append(owner)
                    events.append(dict(event='follow', right=right, left=owner, queue=list(queue)))
        if free is None:
            events.append(dict(event='failed', left=root, reached_left=sorted(seen_l), reached_right=sorted(parent_r)))
            continue
        path = []
        right = free
        while right is not None:
            left = parent_r[right]
            previous = match_l.get(left)
            path.append([left, right])
            match_l[left] = right
            match_r[right] = left
            right = previous
        path.reverse()
        events.append(dict(event='augment', assignments=path, matching=sorted([l, r] for l, r in match_l.items()), size=len(match_l)))
    events.append(dict(event='done', matching=sorted([l, r] for l, r in match_l.items()), size=len(match_l)))
    return len(match_l), events


def tsp_trace(matrix):
    """Held–Karp, rooted at 0; every candidate transition is recorded."""
    n = len(matrix)
    costs, parents = {(1, 0): 0}, {}
    events = [dict(event='init', n=n, mask=1, vertex=0, cost=0)]
    full = (1 << n) - 1
    for mask in range(1, full + 1, 2):
        for vertex in range(n):
            if (mask, vertex) not in costs:
                continue
            old_cost = costs[mask, vertex]
            for neighbor in range(1, n):
                if mask & (1 << neighbor):
                    continue
                new_mask = mask | (1 << neighbor)
                old = costs.get((new_mask, neighbor))
                candidate = old_cost + matrix[vertex][neighbor]
                improved = old is None or candidate < old
                if improved:
                    costs[new_mask, neighbor] = candidate
                    parents[new_mask, neighbor] = (mask, vertex)
                events.append(dict(event='transition', mask=mask, vertex=vertex, cost=old_cost,
                                   neighbor=neighbor, weight=matrix[vertex][neighbor], new_mask=new_mask,
                                   old=old, candidate=candidate, improved=int(improved)))
    best, last = None, None
    for vertex in range(1, n):
        candidate = costs[full, vertex] + matrix[vertex][0]
        improved = best is None or candidate < best
        if improved:
            best, last = candidate, vertex
        events.append(dict(event='close', vertex=vertex, cost=costs[full, vertex],
                           weight=matrix[vertex][0], candidate=candidate, best=best))
    current, path = (full, last), [0]
    reverse = []
    while current != (1, 0):
        reverse.append(current[1])
        current = parents[current]
    path.extend(reversed(reverse))
    path.append(0)
    weights = [matrix[a][b] for a, b in zip(path, path[1:])]
    events.append(dict(event='path', path=path, weights=weights, answer=best))
    return best, events


def dag_trace(n, edges):
    order, cycle, topology = kahn_trace(n, [(a, b) for a, b, _ in edges])
    if cycle:
        raise ValueError(edges)
    events = [dict(e, algorithm='kahn') for e in topology]
    values, parents = [0] * n, [None] * n
    events.append(dict(event='init', order=order, values=values.copy()))
    adjacency = [[] for _ in range(n)]
    for a, b, weight in edges:
        adjacency[a].append((b, weight))
    for vertex in order:
        events.append(dict(event='vertex', vertex=vertex, value=values[vertex]))
        for neighbor, weight in sorted(adjacency[vertex]):
            old, candidate = values[neighbor], values[vertex] + weight
            improved = candidate > old
            if improved:
                values[neighbor], parents[neighbor] = candidate, vertex
            events.append(dict(event='relax', vertex=vertex, neighbor=neighbor, weight=weight,
                               value=values[vertex], old=old, candidate=candidate,
                               improved=int(improved), values=values.copy()))
    last = max(range(n), key=lambda v: values[v])
    answer, path = values[last], []
    while last is not None:
        path.append(last)
        last = parents[last]
    path.reverse()
    events.append(dict(event='path', path=path, answer=answer, values=values.copy()))
    return answer, events


def floyd_trace(n, edges):
    distances = [[0 if a == b else None for b in range(n)] for a in range(n)]
    events = [dict(event='init', matrix=[r.copy() for r in distances])]
    for a, b, weight in edges:
        old = distances[a][b]
        if old is None or weight < old:
            distances[a][b] = weight
        events.append(dict(event='edge', a=a, b=b, weight=weight, old=old, value=distances[a][b]))
    for via in range(n):
        events.append(dict(event='via', via=via))
        for a in range(n):
            for b in range(n):
                left, right, old = distances[a][via], distances[via][b], distances[a][b]
                candidate = None if left is None or right is None else left + right
                improved = candidate is not None and (old is None or candidate < old)
                if improved:
                    distances[a][b] = candidate
                events.append(dict(event='compare', a=a, b=b, via=via, left=left, right=right,
                                   old=old, candidate=candidate, improved=int(improved), value=distances[a][b]))
    finite = [distances[a][b] for a in range(n) for b in range(n) if a != b and distances[a][b] is not None]
    total, diameter = sum(finite), max(finite, default=0)
    events.append(dict(event='done', matrix=[r.copy() for r in distances], total=total, diameter=diameter))
    return total, diameter, events


def clustering_trace(n, edges):
    from fractions import Fraction
    adjacency = [set() for _ in range(n)]
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    events = [dict(event='init', n=n)]
    coefficients = []
    for vertex in range(n):
        neighbors = sorted(adjacency[vertex])
        links = 0
        events.append(dict(event='neighbors', vertex=vertex, neighbors=neighbors, degree=len(neighbors)))
        for i, a in enumerate(neighbors):
            for b in neighbors[i + 1:]:
                present = b in adjacency[a]
                links += int(present)
                events.append(dict(event='pair', vertex=vertex, a=a, b=b, present=int(present), links=links))
        degree = len(neighbors)
        coefficient = Fraction(2 * links, degree * (degree - 1)) if degree > 1 else Fraction(0)
        coefficients.append(coefficient)
        events.append(dict(event='local', vertex=vertex, degree=degree, links=links, value=str(coefficient)))
    average = sum(coefficients) / n
    events.append(dict(event='done', coefficients=[str(c) for c in coefficients], n=n, value=str(average), answer=float(average)))
    return float(average), events
