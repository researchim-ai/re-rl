"""Independent validation of CSP supports, arithmetic cages and queen search."""
from itertools import permutations, product
from math import prod
import json
import random
import pytest
from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.visual.generators import ALL_VISUAL_TASK_GENERATORS
from re_rl.tasks.math.logic.csp_search_traces import kakuro_solutions,queens,kenken,magic_square,skyscrapers

NAMES = ('kakuro','kenken','magic_square','magic_square_image','n_queens','skyscrapers')


@pytest.mark.parametrize('name',NAMES)
@pytest.mark.parametrize('difficulty',range(1,11))
def test_solver_ignores_generation_solutions(name,difficulty):
    generators = {**ALL_TASK_GENERATORS,**ALL_VISUAL_TASK_GENERATORS}
    for seed in (0,8):
        random.seed(seed)
        task = generators[name](language='en',difficulty=difficulty)
        task.solution = None
        task._count = -999
        task.squares = []
        task.all_squares = []
        task.solve()
        assert task.verify('<answer>'+task.final_answer+'</answer>') == 1
        assert not {'solution','_count','squares','all_squares'} & task.computation_inputs.keys()
        json.dumps(task.get_result(),allow_nan=False)
        before = json.dumps(task.get_result(),sort_keys=True)
        task.solve()
        assert json.dumps(task.get_result(),sort_keys=True) == before


def brute_kakuro(s1,s2,v1,v2):
    return [values for values in product(range(1,10),repeat=5)
            if values[0]+values[1] == s1 and sum(values[2:]) == s2
            and values[0]+values[2] == v1 and values[1]+values[3] == v2
            and values[0] != values[1] and len(set(values[2:])) == 3
            and values[0] != values[2] and values[1] != values[3]]


def test_kakuro_reduction_matches_independent_enumeration():
    random.seed(3)
    for _ in range(15):
        clues = [random.randrange(2,19),random.randrange(3,25),random.randrange(2,19),random.randrange(2,19)]
        assert kakuro_solutions(*clues) == brute_kakuro(*clues)
    task = ALL_TASK_GENERATORS['kakuro'](language='en')
    task.s1,task.s2,task.v1,task.v2 = 6,13,9,9
    task.solve()
    assert task.verify('<answer>0 6 9 3 1</answer>') == 0
    assert task.verify('<answer>'+task.final_answer+'</answer>') == 1


def test_kakuro_generation_does_not_silently_drop_uniqueness(monkeypatch):
    from re_rl.tasks.math.logic.kakuro.task import KakuroTask
    monkeypatch.setattr(KakuroTask,'_count_solutions',lambda self:[(1,2,3,4,5),(2,1,3,4,5)])
    with pytest.raises(RuntimeError,match='generation_failed'): KakuroTask()


def valid_queens(columns):
    return len(set(columns)) == len(columns) and len({row-col for row,col in enumerate(columns)}) == len(columns) and len({row+col for row,col in enumerate(columns)}) == len(columns)


@pytest.mark.parametrize('n',range(9))
def test_queens_counts_match_permutation_enumeration(n):
    events = []
    count,first = queens(n,True,events)
    expected = sum(valid_queens(values) for values in permutations(range(n)))
    assert count == expected
    if count: assert first is not None and valid_queens(first)
    assert len([event for event in events if event['operation'] == 'queens_solution']) == expected


def test_queen_domains_and_rollbacks_replay():
    events = []
    count,_ = queens(6,True,events)
    stack = []
    found = 0
    for event in events:
        op = event['operation']
        if op == 'queens_domain':
            assert event['row'] == len(stack)
            allowed = [col for col in range(6) if col not in stack and all(abs(col-other) != len(stack)-row for row,other in enumerate(stack))]
            assert event['available'] == allowed
        elif op == 'queens_place':
            assert event['row'] == len(stack)
            stack.append(event['col'])
        elif op == 'queens_remove':
            assert stack.pop() == event['col'] and event['row'] == len(stack)
        elif op == 'queens_solution':
            found += 1
            assert event['placement'] == stack and valid_queens(stack)
            assert event['count'] == found
    assert not stack and found == count == 4


def test_kenken_all_cage_operations_from_public_clues():
    target_grid = [[1,2,3],[2,3,1],[3,1,2]]
    pair = [(0,0),(0,1)]
    singles = [[(r,c)] for r in range(3) for c in range(3) if (r,c) not in pair]
    for op,target in [('+',3),('*',2),('-',1),('/',2)]:
        clues = [(op,target)]+[('=',target_grid[r][c]) for [(r,c)] in singles]
        events = []
        actual = kenken(3,[pair]+singles,clues,events)
        assert actual == target_grid
        checks = next(e for e in events if e['operation'] == 'cage_candidates')['checks']
        for check in checks:
            a,b = check['values']
            expected = a+b if op == '+' else a*b if op == '*' else abs(a-b) if op == '-' else max(a,b)/min(a,b)
            assert check['matches'] == (expected == target)
    assert kenken(2,[[(0,0)],[(0,1)],[(1,0)],[(1,1)]],[('=',1)]*4,[]) is None


def test_magic_squares_against_full_permutation_oracle():
    lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    valid = [values for values in permutations(range(1,10)) if all(sum(values[cell] for cell in line) == 15 for line in lines)]
    assert len(valid) == 8
    for values in valid:
        for cells in ((0,1),(0,4),(1,7),(2,6),(3,5)):
            given = {cell:values[cell] for cell in cells}
            result = magic_square(given,[])
            assert tuple(result) in valid and all(result[cell] == value for cell,value in given.items())
    assert magic_square({0:1,1:1},[]) is None
    assert magic_square({0:99},[]) is None


def test_magic_verifier_checks_rules_and_givens_without_saved_answer():
    task = ALL_TASK_GENERATORS['magic_square'](language='en',difficulty=10)
    expected = task.final_answer
    task.solution = None
    assert task.verify('<answer>'+expected+'</answer>') == 1
    assert task.verify('<answer>1 2 3 4 5 6 7 8 9</answer>') == 0


def independent_visible(values):
    return sum(value == max(values[:index+1]) for index,value in enumerate(values))


def test_skyscrapers_against_small_latin_square_oracle():
    patterns = tuple(permutations((1,2,3)))
    for grid in product(patterns,repeat=3):
        if any(len({row[col] for row in grid}) != 3 for col in range(3)): continue
        columns = list(zip(*grid))
        clues = {'left':[independent_visible(row) for row in grid],
                 'right':[independent_visible(row[::-1]) for row in grid],
                 'top':[independent_visible(col) for col in columns],
                 'bottom':[independent_visible(col[::-1]) for col in columns]}
        events = []
        result = skyscrapers(3,clues,events)
        assert result is not None
        assert all(sorted(row) == [1,2,3] for row in result)
        assert all(sorted(col) == [1,2,3] for col in zip(*result))
        assert [independent_visible(row) for row in result] == clues['left']
        assert [independent_visible(tuple(col)[::-1]) for col in zip(*result)] == clues['bottom']
