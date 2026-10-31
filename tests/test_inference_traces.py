"""Independent checks for inference from public inputs, including ambiguous ARC."""
from itertools import product, combinations
import json
import random
import pytest
from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.visual.generators import ALL_VISUAL_TASK_GENERATORS
from re_rl.tasks.math.logic.inference_traces import solve_cnf, unique_prediction, apply_rule
from re_rl.tasks.execution_trace import ExecutionTrace


def satisfies(assignment, clauses):
    return all(any(bool(assignment[var]) == positive for var,positive in clause) for clause in clauses)


def test_dpll_matches_exhaustive_small_cnfs():
    pool = [[(0,True)],[(0,False)],[(1,True)],[(1,False)],
            [(0,True),(1,True)],[(0,False),(1,False)],
            [(0,True),(1,False)],[(0,False),(1,True)]]
    for size in range(len(pool)+1):
        for clauses in combinations(pool,size):
            solutions = [bits for bits in product((0,1),repeat=2) if satisfies(bits,clauses)]
            actual = solve_cnf(2,clauses)
            assert (actual is None) == (not solutions)
            if actual is not None: assert tuple(actual) in solutions


def test_dpll_trace_includes_failed_branch_and_unit_propagation():
    clauses = [[(0,True),(1,True)],[(0,True),(1,False)],[(0,False),(1,True)]]
    trace = ExecutionTrace()
    assert trace.call(solve_cnf,2,clauses) == [1,1]
    states = [e['inputs']['assignment'] for e in trace.events if e['operation'] == 'call' and e['function'] == 'search']
    assert {'0':0} in states and {'0':1} in states
    assert any(e['operation'] == 'return' and e.get('result','missing') is None for e in trace.events)
    assert any('assignment[variable]' in e.get('expression','') for e in trace.events)


def test_sat_does_not_read_hidden_assignment_and_can_report_unsat():
    task = ALL_TASK_GENERATORS['three_sat'](language='en')
    task.nv = 2
    task.clauses = [[(0,True)],[(1,False)]]
    task.hidden = [0,1]
    task.solve()
    assert task.final_answer == '1 0'
    assert task.verify('<answer>1 0</answer>') == 1
    assert 'hidden' not in task.computation_inputs
    task.clauses.append([(0,False)])
    task.solve()
    assert task.final_answer == 'unsatisfiable'
    assert task.verify('<answer>unsatisfiable</answer>') == 1
    assert task.verify('<answer>1 0</answer>') == 0


@pytest.mark.parametrize('formula,classification,count',[
    (('iff',('var','p'),('var','p')),'tautology',4),
    (('and',('var','p'),('not',('var','p'))),'contradiction',0),
    (('imp',('var','p'),('var','q')),'contingent',3),
])
def test_truth_table_recomputes_classification(formula,classification,count):
    task = ALL_TASK_GENERATORS['truth_table'](language='en')
    task.vars,task.formula,task.klass = ['p','q'],formula,'stale'
    task.solve()
    assert task.klass == classification and task.true_count == count
    assert len(task.truth_rows) == 4
    assert sum(value for _,value in task.truth_rows) == count


def test_ambiguous_arc_examples_are_rejected():
    initial = [[1,0],[0,1]]
    output = [[0,1],[1,0]]
    with pytest.raises(ValueError,match='ambiguous_examples'):
        unique_prediction([(initial,output)],[[1,1],[0,1]],2)


@pytest.mark.parametrize('name',['arc_grid_induction','arc_grid_image'])
@pytest.mark.parametrize('difficulty',range(1,11))
def test_arc_infers_unique_prediction_without_generation_secrets(name,difficulty):
    generators = {**ALL_TASK_GENERATORS,**ALL_VISUAL_TASK_GENERATORS}
    for seed in (0,7,29):
        random.seed(seed)
        task = generators[name](language='en',difficulty=difficulty)
        expected = [row[:] for row in task.test_out]
        task.fn = lambda _: (_ for _ in ()).throw(AssertionError('hidden_rule_used'))
        task.rule_name = 'stale'
        task.test_out = [[9]]
        task.colors = 999
        task.solve()
        assert task.test_out == expected
        predictions = [event['result'] for event in task.algorithm_trace if event['operation'] == 'arc_prediction']
        assert predictions and all(prediction == expected for prediction in predictions)
        assert 'fn' not in task.computation_inputs and 'test_out' not in task.computation_inputs
        assert task.verify('<answer>'+task.final_answer+'</answer>') == 1
        json.dumps(task.get_result(),allow_nan=False)


def test_arc_image_reserves_space_for_larger_output(tmp_path):
    task = ALL_VISUAL_TASK_GENERATORS['arc_grid_image'](language='en',difficulty=3)
    grid = [[1,2,0],[0,1,2]]
    output = apply_rule(grid,'tile2',())
    task.train = [(grid,output)]*3
    task.test_in,task.test_out = grid,output
    picture = task.render_image()
    # Four panels, each showing four output rows, plus labels and margins.
    assert picture.height == 526
    from re_rl.tasks.visual.arc_grid_image.task import texts
    from re_rl.tasks.visual._visual_utils import get_font
    box = get_font(16).getbbox(texts.t('s2','en'))
    assert picture.width >= box[2] - box[0] + 32
    picture.save(tmp_path/'arc-tile-preview.png')


def test_kmeans_tie_distances_counts_and_exact_centroid():
    task = ALL_TASK_GENERATORS['kmeans_step'](language='en')
    task.c1,task.c2 = (0,0),(4,0)
    task.query = (2,0)
    task.points = [(0,0),(2,0),(4,0),(1,2)]
    for kind,expected in [('nearest','1'),('count','3'),('mean_x','1')]:
        task.task_type = kind
        task.solve()
        assert task.final_answer == expected
        assert task.verify('<answer>'+expected+'</answer>') == 1
    task.points = [(4,0)]
    task.task_type = 'mean_x'
    with pytest.raises(ValueError,match='empty_cluster'):
        task.solve()


def test_audit_detects_hidden_grid_and_classification_caches():
    from scripts.audit_task_traces import static_indicators
    class Cached:
        def solve(self):
            self.final_answer = str(self.hidden) + str(self.test_out) + str(self.klass)
    class Formula:
        def solve(self):
            import math
            self.final_answer = str(math.pi * 2)
    assert set(static_indicators(Cached)['precomputed_reads']) == {'hidden','test_out','klass'}
    assert static_indicators(Cached)['candidate']
    assert not static_indicators(Formula)['candidate']
