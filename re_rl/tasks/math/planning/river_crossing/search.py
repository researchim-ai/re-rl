"""Breadth-first search over labeled couples; safety applies to both banks and boat."""
from collections import deque
from itertools import combinations


def jealous(couples, capacity, events=None):
    if not isinstance(couples,int) or couples < 1 or not isinstance(capacity,int) or capacity < 1:
        raise ValueError('invalid_river_parameters')
    if events is None:
        events = []
    # Person 2*i is husband i; person 2*i+1 is wife i.
    full = (1 << (2*couples))-1

    def safe(mask):
        husbands = [i for i in range(couples) if mask & (1 << (2*i))]
        return not husbands or all(not (mask & (1 << (2*i+1))) or i in husbands
                                   for i in range(couples))

    initial,goal = (0,0),(full,1)
    queue = deque([initial])
    parents = {initial:None}
    while queue:
        state = queue.popleft()
        events.append(dict(operation='river_pop',state=list(state),frontier=len(queue)))
        if state == goal:
            path = []
            while state is not None:
                previous = parents[state]
                path.append((state,None if previous is None else previous[1]))
                state = None if previous is None else previous[0]
            path.reverse()
            events.append(dict(operation='river_path',path=path,crossings=len(path)-1))
            return path
        right,boat = state
        available = right if boat else full ^ right
        people = [p for p in range(2*couples) if available & (1 << p)]
        for count in range(1,min(capacity,len(people))+1):
            for passengers in combinations(people,count):
                mask = sum(1 << p for p in passengers)
                new_right = right ^ mask
                neighbor = (new_right,1-boat)
                boat_safe = safe(mask)
                left_safe,right_safe = safe(full ^ new_right),safe(new_right)
                visited = neighbor in parents
                accepted = boat_safe and left_safe and right_safe and not visited
                events.append(dict(operation='river_edge',state=list(state),passengers=list(passengers),
                                   neighbor=list(neighbor),boat_safe=boat_safe,left_safe=left_safe,
                                   right_safe=right_safe,visited=visited,accepted=accepted))
                if accepted:
                    parents[neighbor] = (state,passengers)
                    queue.append(neighbor)
    events.append(dict(operation='river_path',path=[],crossings=-1))
    return []
