"""Independent puzzle checks, answer ambiguity and malformed-coordinate grading."""
from itertools import product, permutations
from collections import deque
import json
import random
import pytest
from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.visual.generators import ALL_VISUAL_TASK_GENERATORS
from re_rl.tasks.math.logic.board_search_traces import hitori,star_battle,sudoku


@pytest.mark.parametrize('name',['hitori','star_battle','sudoku','sudoku_image'])
@pytest.mark.parametrize('difficulty',range(1,11))
def test_board_solver_uses_only_public_input(name,difficulty):
    generators = {**ALL_TASK_GENERATORS,**ALL_VISUAL_TASK_GENERATORS}
    for seed in (0,7):
        random.seed(seed)
        task = generators[name](language='en',difficulty=difficulty)
        task.solution = None
        task.shaded = None
        task.stars = None
        task.target_value = 999
        task.solve()
        assert task.verify('<answer>'+task.final_answer+'</answer>') == 1
        assert not {'solution','shaded','stars','target_value'} & task.computation_inputs.keys()
        json.dumps(task.get_result(),allow_nan=False)
        before = json.dumps(task.get_result(),sort_keys=True)
        task.solve()
        assert json.dumps(task.get_result(),sort_keys=True) == before


def valid_shading(grid,shaded):
    n = len(grid)
    if any((r+dr,c+dc) in shaded for r,c in shaded for dr,dc in ((-1,0),(1,0),(0,-1),(0,1))): return False
    for index in range(n):
        row = [grid[index][c] for c in range(n) if (index,c) not in shaded]
        col = [grid[r][index] for r in range(n) if (r,index) not in shaded]
        if len(set(row)) != len(row) or len(set(col)) != len(col): return False
    free = {(r,c) for r in range(n) for c in range(n)}-shaded
    if not free: return False
    seen = {min(free)}
    queue = list(seen)
    while queue:
        r,c = queue.pop()
        for other in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
            if other in free and other not in seen: seen.add(other);queue.append(other)
    return seen == free


def test_hitori_all_two_by_two_inputs_against_exhaustive_shadings():
    cells = [(0,0),(0,1),(1,0),(1,1)]
    for values in product((1,2),repeat=4):
        grid = [list(values[:2]),list(values[2:])]
        valid = [{cell for cell,bit in zip(cells,mask) if bit} for mask in product((0,1),repeat=4)]
        valid = [shaded for shaded in valid if valid_shading(grid,shaded)]
        result = hitori(grid,[])
        assert (result is None) == (not valid)
        if result is not None: assert result in valid


def test_star_battle_matches_permutation_oracle():
    random.seed(4)
    for _ in range(30):
        labels = [random.randrange(4) for _ in range(16)]
        labels[:4] = [0,1,2,3]
        region = [labels[i:i+4] for i in range(0,16,4)]
        valid = [cols for cols in permutations(range(4)) if all(abs(cols[r]-cols[r+1]) > 1 for r in range(3))
                 and len({region[r][col] for r,col in enumerate(cols)}) == 4]
        result = star_battle(region,[])
        assert (result is None) == (not valid)
        if result is not None: assert tuple(c for _,c in result) in valid


@pytest.mark.parametrize('name',['hitori','star_battle'])
def test_coordinate_grading_rejects_truncated_and_duplicate_lists(name):
    task = ALL_TASK_GENERATORS[name](language='en',difficulty=4)
    answer = task.final_answer
    assert task.verify('<answer>'+answer+'</answer>') == 1
    assert task.verify('<answer>'+answer+' 99</answer>') == 0
    assert task.verify('<answer>'+answer+', '+answer+'</answer>') == 0
    if name == 'hitori':
        task.grid = [[1,2],[2,1]];task.n = 2
        assert task.verify('<answer>none</answer>') == 1
        assert task.verify('<answer>none.</answer>') == 1
        assert task.verify('<answer>[ ]</answer>') == 1
        assert task.verify('<answer>nonsense</answer>') == 0


def test_star_generator_fallback_is_valid_even_if_shuffle_never_changes():
    from re_rl.tasks.math.logic.star_battle.task import StarBattleTask
    from unittest.mock import patch
    task = StarBattleTask(difficulty=1)
    with patch('random.shuffle',lambda values:None): stars = task._gen_stars()
    assert len({c for r,c in stars}) == 4
    assert all(abs(stars[r][1]-stars[r+1][1]) > 1 for r in range(3))


def latin_sudoku4():
    lines = tuple(permutations((1,2,3,4)))
    for grid in product(lines,repeat=4):
        if any(len({row[c] for row in grid}) != 4 for c in range(4)): continue
        if any(len({grid[r][c] for r in range(br,br+2) for c in range(bc,bc+2)}) != 4 for br in (0,2) for bc in (0,2)): continue
        yield [list(row) for row in grid]


def test_sudoku_solution_count_and_forbidden_target_against_full_oracle():
    all_solutions = list(latin_sudoku4())
    assert len(all_solutions) == 288
    random.seed(2)
    for _ in range(12):
        source = random.choice(all_solutions)
        puzzle = [[value if random.random() < .4 else None for value in row] for row in source]
        expected = [grid for grid in all_solutions if all(value is None or grid[r][c] == value for r,row in enumerate(puzzle) for c,value in enumerate(row))]
        actual = sudoku(puzzle,limit=2)
        assert len(actual) == min(2,len(expected))
        assert all(grid in expected for grid in actual)
        forbidden = (0,0,source[0][0])
        other = sudoku(puzzle,forbidden=forbidden)
        assert bool(other) == any(grid[0][0] != source[0][0] for grid in expected)
    assert sudoku([[1,1,None,None]]+[[None]*4 for _ in range(3)]) == []


def test_sudoku_verifier_accepts_alternatives_but_checks_givens_and_blocks():
    from re_rl.tasks.math.logic.sudoku.task import SudokuTask
    task = SudokuTask(size=4,hints_ratio=.5)
    task.puzzle = [[None]*4 for _ in range(4)]
    candidates = list(latin_sudoku4())[:2]
    for grid in candidates:
        assert task.verify('<answer>'+' '.join(str(v) for row in grid for v in row)+'</answer>') == 1
    task.puzzle[0][0] = 4 if candidates[0][0][0] != 4 else 3
    assert task.verify(' '.join(str(v) for row in candidates[0] for v in row)) == 0
    task.puzzle = [[None]*4 for _ in range(4)]
    latin = [[1,2,3,4],[2,3,4,1],[3,4,1,2],[4,1,2,3]]
    assert task.verify(' '.join(str(v) for row in latin for v in row)) == 0
    assert not task._has_unique_solution(task.puzzle)
    task.puzzle = candidates[0]
    assert task._has_unique_solution(task.puzzle)


def test_visual_sudoku_ambiguity_and_proof_cache_invalidation():
    task = ALL_VISUAL_TASK_GENERATORS['sudoku_image'](language='en',difficulty=2)
    expected = task.final_answer
    task.target_value = 999
    assert task.verify('<answer>'+expected+'</answer>') == 1
    task.puzzle = [[None]*4 for _ in range(4)]
    task.target = (0,0)
    with pytest.raises(ValueError,match='ambiguous_target'): task.solve()
    assert task.verify('<answer>1</answer>') == 0


def test_full_visual_grid_gets_a_real_blank_and_unique_answer():
    from re_rl.tasks.visual.sudoku_image.task import SudokuVisualTask
    task = SudokuVisualTask(language='en',size=4,hints_ratio=1,difficulty=1)
    r,c = task.target
    assert task.puzzle[r][c] is None
    task.solve()
    assert task.verify('<answer>'+task.final_answer+'</answer>') == 1
    assert not sudoku(task.puzzle,forbidden=(r,c,int(task.final_answer)))


def test_hitori_connectivity_queue_replays():
    random.seed(8)
    task = ALL_TASK_GENERATORS['hitori'](language='en',difficulty=6)
    n = task.n
    queue=[];seen=set();blocked=set()
    for event in task.algorithm_trace:
        if event['operation'] == 'hitori_walk_start':
            blocked=set(event['blocked']);queue=[event['start']];seen={event['start']}
        elif event['operation'] == 'hitori_visit':
            cell=queue.pop(0)
            assert cell == event['cell']
            r,c=divmod(cell,n)
            discovered=[]
            for rr,cc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
                other=rr*n+cc
                if 0 <= rr < n and 0 <= cc < n and other not in blocked and other not in seen:
                    seen.add(other);queue.append(other);discovered.append(other)
            assert event['discovered'] == discovered and event['queue'] == queue
        elif event['operation'] == 'hitori_connect' and event['start'] is not None:
            assert set(event['reached']) == seen and not queue


def test_sudoku_domains_replay_from_actual_assignments():
    puzzle=[[None]*4 for _ in range(4)]
    events=[]
    results=sudoku(puzzle,limit=2,events=events)
    assert len(results) == 2
    working=[row[:] for row in puzzle]
    for event in events:
        op=event['operation']
        if op == 'sudoku_scan':
            for candidate in event['candidates']:
                r,c=candidate['row'],candidate['col']
                used=set(working[r])|{row[c] for row in working}
                used|={working[rr][cc] for rr in range(r//2*2,r//2*2+2) for cc in range(c//2*2,c//2*2+2)}
                assert candidate['values'] == [value for value in range(1,5) if value not in used]
        elif op == 'sudoku_place':
            r,c=event['row'],event['col']
            assert working[r][c] is None
            working[r][c]=event['value']
        elif op == 'sudoku_backtrack':
            r,c=event['row'],event['col']
            assert working[r][c] == event['value']
            working[r][c]=None
        elif op == 'sudoku_solution':
            assert event['grid'] == working


def test_sudoku_explicit_zero_hints_is_not_replaced_by_default():
    from re_rl.tasks.math.logic.sudoku.task import SudokuTask
    task = SudokuTask(size=9,hints_ratio=0)
    assert task.hints_ratio == 0 and all(value is None for row in task.puzzle for value in row)
    task.solve()
    assert task.verify('<answer>'+task.final_answer+'</answer>') == 1


@pytest.mark.parametrize('kwargs',[{'size':0},{'size':6},{'size':4.0},{'hints_ratio':-0.1},{'hints_ratio':1.1}])
def test_sudoku_invalid_parameters_fail_explicitly(kwargs):
    from re_rl.tasks.math.logic.sudoku.task import SudokuTask
    with pytest.raises(ValueError): SudokuTask(**kwargs)


def test_audit_catches_cached_coordinates_and_partial_sudoku_solver():
    from scripts.audit_task_traces import static_indicators
    class Coordinates:
        def solve(self):
            self.final_answer = ', '.join(str(cell) for cell in sorted(self.stars))
    class PartialSolver:
        def solve(self):
            for row in range(4):
                self.solution_steps.append(str(row))
            self.final_answer = self._format_grid(self.solution)
    assert static_indicators(Coordinates)['rendered_cached_grid']
    partial = static_indicators(PartialSolver)
    assert partial['has_iteration'] and partial['cached_final_grid'] and partial['candidate']
