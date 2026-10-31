"""Independent small-state oracles and replay of public search certificates."""
from collections import deque
from itertools import permutations, product, combinations
import json
import random
import pytest
from re_rl.tasks.math.logic.navigation_traces import sliding,maze,commands
from re_rl.tasks.math.planning.river_crossing.search import jealous
from re_rl.tasks.visual.generators import ALL_VISUAL_TASK_GENERATORS
from re_rl.tasks.registry import registry
from re_rl.tasks.math.planning.river_crossing.task import RiverCrossingTask


def puzzle_distances(n, depth=None):
    goal = tuple(range(1,n*n))+(0,)
    distances = {goal:0}
    queue = deque([goal])
    while queue:
        state = queue.popleft()
        if depth is not None and distances[state] == depth:
            continue
        z = state.index(0)
        for k in range(n*n):
            if abs(k//n-z//n)+abs(k%n-z%n) != 1:
                continue
            other = list(state)
            other[k],other[z] = other[z],other[k]
            other = tuple(other)
            if other not in distances:
                distances[other] = distances[state]+1
                queue.append(other)
    return distances


def test_every_two_by_two_puzzle():
    oracle = puzzle_distances(2)
    for state in permutations(range(4)):
        assert sliding(state,2,'solvable',[]) == (state in oracle)
        assert sliding(state,2,'min_moves',[]) == oracle.get(state,-1)


def test_astar_against_bfs_and_replay():
    for state,expected in puzzle_distances(3,7).items():
        events = []
        assert sliding(state,3,'min_moves',events) == expected
        best = {state:0}
        for event in events:
            if event['operation'] == 'nav_astar_edge':
                a,b = tuple(event['state']),tuple(event['neighbor'])
                za,zb = a.index(0),b.index(0)
                assert abs(za//3-zb//3)+abs(za%3-zb%3) == 1
                changed = list(a)
                changed[za],changed[zb] = changed[zb],changed[za]
                assert tuple(changed) == b
                assert event['old'] == best.get(b)
                assert event['g'] == best[a]+1
                h = sum(abs(i//3-(v-1)//3)+abs(i%3-(v-1)%3) for i,v in enumerate(b) if v)
                assert event['h'] == h
                assert event['f'] == event['g']+h
                assert event['accepted'] == (b not in best or event['g'] < best[b])
                if event['accepted']: best[b] = event['g']
        path = events[-1]['path']
        assert path[0] == list(state) and path[-1] == [1,2,3,4,5,6,7,8,0]
        assert len(path)-1 == expected


def test_all_three_by_three_mazes():
    # Independent repeated relaxation of all grid edges, no queue.
    for bits in product((0,1),repeat=9):
        grid = [list(bits[r*3:r*3+3]) for r in range(3)]
        distance = [100]*9
        if not bits[0]: distance[0] = 0
        for _ in range(9):
            for i in range(9):
                for j in range(9):
                    if not bits[i] and not bits[j] and abs(i//3-j//3)+abs(i%3-j%3) == 1:
                        distance[j] = min(distance[j],distance[i]+1)
        expected = distance[8] if distance[8] < 100 else -1
        events = []
        assert maze(grid,events) == expected
        if expected >= 0:
            path = events[-1]['path']
            assert path[0] == [0,0] and path[-1] == [2,2]
            assert len(path)-1 == expected
            assert all(grid[y][x] == 0 for x,y in path)
            assert all(abs(a[0]-b[0])+abs(a[1]-b[1]) == 1 for a,b in zip(path,path[1:]))
        queue = deque([[0,0]])
        for e in events:
            if e['operation'] == 'nav_bfs_pop':
                assert queue.popleft() == e['cell']
            elif e['operation'] == 'nav_bfs_edge' and e['accepted']:
                queue.append(e['neighbor'])


def test_command_sequences():
    # Complex coordinates rotate independently by multiplication with i.
    for heading in range(4):
        for kinds in product(('left','right','fwd'),repeat=5):
            seq = [(k,3 if k == 'fwd' else 0) for k in kinds]
            pos,orientation = 0j,1j*((-1j)**heading)
            for kind,k in seq:
                if kind == 'left': orientation *= 1j
                elif kind == 'right': orientation *= -1j
                else: pos += orientation*k
            events = []
            x,y,d = commands(heading,seq,events)
            assert (x,y) == (pos.real,pos.imag)
            assert 1j*((-1j)**d) == orientation
            assert len(events) == len(seq)+1


@pytest.mark.parametrize('name',['sliding_puzzle','sliding_puzzle_image','grid_navigation','grid_navigation_image'])
@pytest.mark.parametrize('level',range(1,11))
def test_all_navigation_subtypes_poison_cache(name,level):
    cls = registry[name]
    for kind in cls.TASK_TYPES:
        random.seed(level)
        task = cls(language='en',difficulty=level,task_type=kind)
        task.solve()
        expected = task.final_answer
        for field in ('answer_int','answer_bool','_answer_maze','end_x','end_y','end_dir'):
            if hasattr(task,field): setattr(task,field,'poison')
        task.final_answer = 'poison'
        task.solve()
        assert task.final_answer == expected
        assert task.verify(f'<answer>{expected}</answer>') == 1
        json.dumps(task.get_result(),allow_nan=False)


def river_oracle(n,capacity):
    initial = (frozenset(),0)
    goal = frozenset(range(2*n))
    levels = {initial:0}
    queue = deque([initial])
    def safe(people):
        for wife in range(1,2*n,2):
            if wife in people and wife-1 not in people:
                if any(h in people for h in range(0,2*n,2)):
                    return False
        return True
    while queue:
        right,side = queue.popleft()
        if right == goal: return levels[right,side]
        available = right if side else goal-right
        for k in range(1,min(capacity,len(available))+1):
            for crew in combinations(sorted(available),k):
                crew = frozenset(crew)
                new_right = right-crew if side else right|crew
                target = (new_right,1-side)
                if safe(crew) and safe(new_right) and safe(goal-new_right) and target not in levels:
                    levels[target] = levels[right,side]+1
                    queue.append(target)
    return -1


@pytest.mark.parametrize('n',range(1,5))
@pytest.mark.parametrize('capacity',range(1,4))
def test_labeled_couples_vs_set_oracle(n,capacity):
    events = []
    path = jealous(n,capacity,events)
    assert (len(path)-1 if path else -1) == river_oracle(n,capacity)
    for (a,_),(b,crew) in zip(path,path[1:]):
        assert 1 <= len(crew) <= capacity
        assert a[1] != b[1]
        assert a[0] ^ b[0] == sum(1 << p for p in crew)
        assert all(bool(a[0] & (1 << p)) == bool(a[1]) for p in crew)


@pytest.mark.parametrize('language',['ru','en'])
@pytest.mark.parametrize('level',range(1,11))
def test_river_all_levels_and_real_people(level,language):
    task = RiverCrossingTask(language=language,difficulty=level)
    task.solve()
    expected = task.final_answer
    task.solution_path = [('poison',None)]
    task.solve()
    assert task.final_answer == expected
    assert task.verify('<answer>'+expected+'</answer>') == 1
    json.dumps(task.get_result())
    if task.problem_type == 'jealous_husbands':
        assert ('husband' if language == 'en' else 'муж') in expected
        assert 'cannibal' not in expected
        assert task.solution_path[-1][0] == ((1 << (2*task.num_couples))-1,1)


@pytest.mark.parametrize('kind',['classic','missionaries','jealous_husbands'])
def test_explicit_river_kind(kind):
    task = RiverCrossingTask(problem_type=kind)
    task.solve()
    assert task.computation_inputs['problem_type'] == kind
