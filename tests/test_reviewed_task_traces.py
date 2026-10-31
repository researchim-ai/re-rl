"""Exercise every reviewed subtype, level and language against constructor oracles."""
import inspect
import json
import random
import sys
from fractions import Fraction
import pytest
from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.visual.generators import ALL_VISUAL_TASK_GENERATORS
from re_rl.tasks.registry import registry
from re_rl.tasks.reviewed_coverage import REVIEWED_TASKS
from re_rl.tasks.execution_trace import ExecutionTrace
from re_rl.tasks.formula_trace import evaluate


def make_task(name,kind,language,difficulty):
    cls = registry[name]
    parameters = inspect.signature(cls).parameters
    kwargs = dict(language=language,difficulty=difficulty,task_type=kind)
    if name == "river_crossing":
        kwargs["problem_type"] = kind
    if not any(p.kind == inspect.Parameter.VAR_KEYWORD for p in parameters.values()):
        kwargs = {k:v for k,v in kwargs.items() if k in parameters}
    return cls(**kwargs)


@pytest.mark.parametrize('name', REVIEWED_TASKS)
@pytest.mark.parametrize('language', ['ru','en'])
@pytest.mark.parametrize('difficulty', range(1,11))
def test_all_reviewed_instances(name,language,difficulty):
    cls = registry[name]
    kinds = getattr(cls,'TASK_TYPES',[None])
    if name == 'modular_arithmetic': kinds = ['modexp','discrete_log']
    for kind in kinds:
        random.seed(31)
        task = make_task(name,kind,language,difficulty)
        task._solve_before_trace()
        expected = task.final_answer
        task.solve()
        if name not in ('three_sat','binary_puzzle','nonogram','battleship','kenken','skyscrapers','n_queens','hitori','star_battle','sudoku','futoshiki','cryptarithmetic','knights_knaves','zebra_puzzle'):
            assert task.final_answer == expected
        assert task.verify('<answer>'+str(task.final_answer)+'</answer>') == 1
        result = task.get_result()
        assert result['algorithm_trace'] and result['computation_inputs']
        assert len(result['solution_steps']) > 1
        json.dumps(result)
        before = json.dumps(result,sort_keys=True)
        task.solve()
        assert json.dumps(task.get_result(),sort_keys=True) == before
        if language == 'en':
            # Instance labels may legitimately be Russian only for legacy name lists;
            # code comments must never leak into instruction text.
            for event in task.algorithm_trace:
                if event['operation'] == 'statement': assert '#' not in event['expression']


@pytest.mark.parametrize('name', REVIEWED_TASKS)
def test_cached_answer_does_not_control_solver(name):
    task = make_task(name,None,'en',5)
    random.seed(17)
    task.solve()
    expected = task.final_answer
    for field in ('answer','_answer'):
        if hasattr(task,field): setattr(task,field,'stale')
    task.solve()
    assert task.final_answer == expected


def test_execution_hook_restoration_and_snapshot_copy():
    from re_rl.tasks.math.reviewed_solvers import sum_iter
    hook = sys.gettrace()
    trace = ExecutionTrace()
    values = [3,4,5]
    assert trace.call(sum_iter,values) == 12
    values[0] = 1000
    assert trace.events[0]['inputs']['values'] == [3,4,5]
    assert sys.gettrace() is hook
    def fail():
        raise ValueError('expected')
    with pytest.raises(ValueError): trace.call(fail)
    assert sys.gettrace() is hook


def test_exact_fractional_powers_and_inverse_formulas():
    events = []
    assert evaluate('sqrt(1 - (n / d) ** 2)',{'n':3,'d':5},events) == Fraction(4,5)
    assert evaluate('ratio ** Fraction(1,4)',{'ratio':81},events) == 3
    assert events and all('result' in e for e in events)


def test_statement_trace_contains_actual_mutations_and_branches():
    from re_rl.tasks.math.reviewed_solvers import rpn
    trace = ExecutionTrace()
    assert trace.call(rpn,['3','4','+','2','*']) == 14
    stacks = [e['changes']['stack'] for e in trace.events
              if e['operation'] == 'statement' and 'stack' in e['changes']]
    assert [3,4] in stacks and [7] in stacks and [14] in stacks
    assert any('if token' in e.get('expression','') for e in trace.events)


def test_hidden_mobile_mass_is_never_used_as_input():
    task = make_task('mobile_torque','hidden','en',10)
    task.solve()
    expected = task.final_answer
    def poison(node):
        if node['kind'] == 'rod':
            node['mass'] = 987654321
            poison(node['left']);poison(node['right'])
        elif node['id'] == task.k:
            node['mass'] = 987654321
    poison(task.root)
    task.solve()
    assert task.final_answer == expected
    assert '987654321' not in json.dumps(task.get_result()['computation_inputs'])
    assert '987654321' not in json.dumps(task.algorithm_trace)


def test_pattern_uses_visible_terms_not_generation_parameters():
    task = make_task('pattern_induction','quadratic','en',5)
    task.solve()
    expected = task.final_answer
    task.params = {'a':999,'b':999,'c':999}
    task.seq = [-999] * (len(task.given)+1)
    task.solve()
    assert task.final_answer == expected
    assert 'Rule family:' in task.description
    assert task.computation_inputs['given'] == task.given


def test_cellular_trace_replays_every_synchronous_cell():
    task = make_task('game_of_life',None,'en',1)
    task.r = task.c = 3
    task.k = 2
    task.grid0 = [[0,1,0],[0,1,0],[0,1,0]]
    task.grid = [[9]*3 for _ in range(3)]
    task.solve()
    generations = [e for e in task.algorithm_trace if e['operation'] == 'cellular_generation']
    assert generations[0]['result'] == [[0,0,0],[1,1,1],[0,0,0]]
    assert generations[1]['result'] == task.grid0
    cells = [e for e in task.algorithm_trace if e['operation'] == 'life_cell']
    assert len(cells) == 18
    for event in cells:
        assert event['count'] == sum(value for _,_,value in event['neighbors'])
        assert event['result'] == int(event['count'] == 3 or event['previous'] == 1 and event['count'] == 2)


def test_kmp_overlaps_and_binary_search_bounds():
    task = make_task('kmp_matching','occurrences','en',1)
    task.pattern,task.text,task.count = 'aaa','aaaaa',999
    task.solve()
    assert task.final_answer == '3'
    assert any('k = pi[k - 1]' in e.get('expression','') for e in task.algorithm_trace)
    task = make_task('binary_search','index','en',1)
    task.arr,task.target = [-9,-2,0,7,12],12
    task.solve()
    assert task.final_answer == '4'
    changes = [e['changes'] for e in task.algorithm_trace if e['operation'] == 'statement']
    assert any('lo' in change and change['lo'] == 3 for change in changes)
