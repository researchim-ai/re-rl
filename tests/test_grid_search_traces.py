"""Independent enumeration and state replay for grid reasoning tasks."""
from itertools import product
import json
import random
import pytest
from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.math.logic.grid_search_traces import takuzu,nonogram,battleship


NAMES = ('binary_puzzle','nonogram','battleship')


@pytest.mark.parametrize('name',NAMES)
@pytest.mark.parametrize('difficulty',range(1,11))
def test_search_uses_clues_not_saved_grid(name,difficulty):
    for seed in (0,8,39):
        random.seed(seed)
        task = ALL_TASK_GENERATORS[name](language='en',difficulty=difficulty)
        task.sol = [[9]*len(task.sol[0]) for _ in task.sol]
        task.solve()
        assert task.verify('<answer>'+task.final_answer+'</answer>') == 1
        assert 'sol' not in task.computation_inputs
        assert task.algorithm_trace[-1]['operation'] == 'grid_solution'
        assert task.algorithm_trace[-1]['grid'] == task.sol
        json.dumps(task.get_result(),allow_nan=False)
        before = task.get_result()
        task.solve()
        assert task.get_result() == before


def independent_runs(bits):
    # Group positions of 1s instead of using the solver's run construction.
    positions = [index for index,value in enumerate(bits) if value]
    if not positions: return []
    groups = [[positions[0]]]
    for index in positions[1:]:
        if index == groups[-1][-1]+1: groups[-1].append(index)
        else: groups.append([index])
    return [len(group) for group in groups]


def test_nonogram_all_two_by_three_boards():
    for values in product((0,1),repeat=6):
        original = [list(values[:3]),list(values[3:])]
        rows = [independent_runs(row) for row in original]
        cols = [independent_runs([original[r][c] for r in range(2)]) for c in range(3)]
        events = []
        result = nonogram(rows,cols,events)
        assert result is not None
        assert [independent_runs(row) for row in result] == rows
        assert [independent_runs([result[r][c] for r in range(2)]) for c in range(3)] == cols
    assert nonogram([[3]],[[1],[1]],[]) is None
    assert nonogram([[],[]],[[],[],[]],[]) == [[0,0,0],[0,0,0]]


def valid_takuzu(board):
    n = len(board)
    lines = board + [list(col) for col in zip(*board)]
    return all(sum(line) == n//2 and all(len(set(line[i:i+3])) > 1 for i in range(n-2)) for line in lines) and len({tuple(row) for row in board}) == n and len(set(zip(*board))) == n


def test_takuzu_against_all_two_by_two_partial_instances():
    solutions = [[[0,1],[1,0]],[[1,0],[0,1]]]
    for values in product((-1,0,1),repeat=4):
        given = {divmod(index,2):value for index,value in enumerate(values) if value != -1}
        expected = [grid for grid in solutions if all(grid[r][c] == value for (r,c),value in given.items())]
        result = takuzu(2,given,[])
        assert (result is None) == (not expected)
        if result is not None:
            assert result in expected and valid_takuzu(result)
    with pytest.raises(ValueError,match='invalid_size'): takuzu(3,{},[])


def independent_fleet(board):
    occupied = {(r,c) for r,row in enumerate(board) for c,value in enumerate(row) if value}
    remaining = set(occupied)
    components = []
    while remaining:
        component = {remaining.pop()}
        frontier = list(component)
        while frontier:
            r,c = frontier.pop()
            for neighbor in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
                if neighbor in remaining:
                    remaining.remove(neighbor);component.add(neighbor);frontier.append(neighbor)
        if len({r for r,c in component}) != 1 and len({c for r,c in component}) != 1: return None
        for r,c in component:
            if any(abs(r-rr) <= 1 and abs(c-cc) <= 1 for rr,cc in occupied-component): return None
        components.append(len(component))
    return sorted(components)


def test_battleship_all_three_by_three_clue_sets():
    instances = {}
    for values in product((0,1),repeat=9):
        board = [list(values[i:i+3]) for i in (0,3,6)]
        fleet = independent_fleet(board)
        if fleet is None: continue
        rows = tuple(map(sum,board))
        cols = tuple(sum(row[c] for row in board) for c in range(3))
        instances[(rows,cols,tuple(fleet))] = True
    for rows,cols,fleet in instances:
        result = battleship(rows,cols,fleet,[])
        assert result is not None
        assert tuple(map(sum,result)) == rows
        assert tuple(map(sum,zip(*result))) == cols
        assert independent_fleet(result) == list(fleet)
    assert battleship([1,1],[1,1],[1,1],[]) is None  # Two ships would touch.
    assert battleship([0,0],[0,0],[1],[]) is None


def test_domain_eliminations_have_checkable_witnesses():
    events = []
    nonogram([[2],[]],[[1],[1]],events)
    filtered = [e for e in events if e['operation'] == 'grid_filter']
    assert filtered
    for event in filtered:
        if event['reason'] == 'crossing':
            for item in event['removed']:
                assert item['pattern'][item['cell']] == item['value']
                assert item['value'] not in item['allowed']


def test_generators_never_return_an_invalid_fallback(monkeypatch):
    from re_rl.tasks.math.logic.binary_puzzle.task import BinaryPuzzleTask
    from re_rl.tasks.math.logic.battleship.task import BattleshipTask
    monkeypatch.setattr(BinaryPuzzleTask,'_fill',lambda *args:False)
    monkeypatch.setattr(BattleshipTask,'_place_all',lambda *args:False)
    for cls in (BinaryPuzzleTask,BattleshipTask):
        with pytest.raises(RuntimeError,match='generation_failed'): cls(difficulty=1)


def test_solution_events_do_not_alias_mutable_board():
    for solver,args in [(nonogram,([[1]],[[1]])), (takuzu,(2,{})), (battleship,([1],[1],[1]))]:
        events = []
        result = solver(*args,events)
        before = json.dumps(events)
        result[0][0] = 9
        assert json.dumps(events) == before


def test_trace_records_failed_branches_and_backtracking():
    for name,seed,operation in [('binary_puzzle',17,'grid_backtrack'),('nonogram',24,'grid_backtrack'),('battleship',1,'fleet_backtrack')]:
        random.seed(seed)
        task = ALL_TASK_GENERATORS[name](language='en',difficulty=10)
        assert any(event['operation'] == operation for event in task.algorithm_trace)
        assert task.verify('<answer>'+task.final_answer+'</answer>') == 1


def test_audit_does_not_mistake_printing_grid_for_algorithm():
    from scripts.audit_task_traces import static_indicators
    class CachedGrid:
        def solve(self):
            self.final_answer = ' '.join(str(self.sol[row][col]) for row in range(2) for col in range(2))
    indicator = static_indicators(CachedGrid)
    assert indicator['has_iteration']
    assert indicator['rendered_cached_grid']
    assert indicator['candidate']
