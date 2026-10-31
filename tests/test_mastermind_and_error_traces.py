"""Independent matching/permutation oracles and exact arithmetic replay."""
import itertools
import json
import operator
import random
from unittest.mock import patch
import pytest
from re_rl.tasks.math.logic.mastermind.task import MastermindTask
from re_rl.tasks.math.logic.mastermind.solver import deduce,feedback
from re_rl.tasks.math.logic.find_the_error.task import FindTheErrorTask
from re_rl.tasks.math.logic.find_the_error.solver import locate


def matching_feedback(guess,code):
    exact=sum(a==b for a,b in zip(guess,code))
    unmatched_guess=[a for a,b in zip(guess,code) if a!=b]
    unmatched_code=[b for a,b in zip(guess,code) if a!=b]
    partial=0
    for value in unmatched_guess:
        if value in unmatched_code:
            unmatched_code.remove(value);partial+=1
    return exact,partial


def candidates(length,colors,clues):
    return [code for code in itertools.product(range(1,colors+1),repeat=length)
            if all(matching_feedback(guess,code)==tuple(result) for guess,result in clues)]


def test_feedback_repeated_symbols_against_independent_one_to_one_matching():
    codes=list(itertools.product(range(1,4),repeat=3))
    for guess,code in itertools.product(codes,repeat=2):
        assert feedback(guess,code)==matching_feedback(guess,code)
    assert feedback((1,1,2,2),(2,2,1,1))==(0,4)
    assert feedback((1,1,1),(1,2,2))==(1,0)


def test_all_small_single_clues_and_pruning_soundness():
    codes=list(itertools.product((1,2),repeat=3))
    clues=[(guess,result) for guess in codes for result in itertools.product(range(4),repeat=2) if sum(result)<=3]
    for guess,result in clues:
        expected=candidates(3,2,[(guess,result)]);events=[]
        if len(expected)==1:assert deduce(3,2,[(guess,result)],events)==expected[0]
        else:
            with pytest.raises(ValueError,match='inconsistent_clues' if not expected else 'ambiguous_clues'):
                deduce(3,2,[(guess,result)],events)
        for event in events:
            if event['operation']=='code_prune':
                assert not any(code[:len(event['prefix'])]==tuple(event['prefix']) for code in expected)
            if event['operation']=='code_bound':
                prefix=event['prefix'];guess_counts={d:guess.count(d) for d in (1,2)}
                common=sum(min(prefix.count(d),guess_counts[d]) for d in (1,2))
                exact=sum(d==guess[i] for i,d in enumerate(prefix))
                assert event['exact_min']==exact and event['common_min']==common
                assert event['exact_max']==exact+3-len(prefix)
                suffixes=list(itertools.product((1,2),repeat=3-len(prefix)))
                actual_common=[sum(matching_feedback(guess,tuple(prefix)+suffix)) for suffix in suffixes]
                assert event['common_max']==max(actual_common)


def test_multiple_clues_against_exhaustive_code_oracle():
    codes=list(itertools.product((1,2),repeat=3))
    for secret in codes:
        clues=[(guess,matching_feedback(guess,secret)) for guess in codes if guess!=secret]
        assert candidates(3,2,clues)==[secret]
        events=[];assert deduce(3,2,clues,events)==secret
        assert events[-1]['complete'] and events[-1]['count']==1
    with pytest.raises(ValueError,match='ambiguous_clues'):deduce(2,2,[],[])
    with pytest.raises(ValueError,match='inconsistent_clues'):deduce(2,2,[((1,1),(2,0)),((1,1),(0,0))],[])


@pytest.mark.parametrize('language',['ru','en'])
def test_mastermind_all_levels_secret_poison_rng_and_bound_replay(language):
    for level in range(1,11):
        random.seed(level);task=MastermindTask(language=language,difficulty=level)
        expected=task.secret;description=task.description
        task.secret=(999,)*task.L
        state=random.getstate();task.solve()
        assert task.final_answer==' '.join(map(str,expected))
        assert random.getstate()==state and task.description==description
        saved=json.dumps(task.get_result(),sort_keys=True)
        task.solve();assert json.dumps(task.get_result(),sort_keys=True)==saved
        assert task.verify(task.final_answer)==1
        assert task.verify('junk '+task.final_answer)==0
        assert task.verify('999 '+task.final_answer)==0
        assert task.verify('-'+task.final_answer)==0
        assert 'secret' not in task.computation_inputs
        assert len(task.solution_steps)==len(task.algorithm_trace)+1
        for event in task.algorithm_trace:
            if event['operation']=='code_solution':
                assert all(matching_feedback(guess,event['code'])==tuple(result) for guess,result in task.guesses)
        assert task.algorithm_trace[-1]['complete']


def test_mastermind_parameters_fallback_and_inconsistent_public_clues():
    task=MastermindTask.generate_random_task(L=1,C=1)
    assert task.final_answer=='1' and not task.guesses
    task=MastermindTask.generate_random_task(L=3,C=3)
    assert (task.L,task.C)==(3,3)
    assert candidates(3,3,task.guesses)==[task.secret]
    assert all(tuple(guess)!=task.secret for guess,result in task.guesses)
    # A constant RNG prevents useful random guesses; deterministic fallback must still work.
    with patch('re_rl.tasks.math.logic.mastermind.task.random.randint',return_value=1):
        task=MastermindTask.generate_random_task(L=3,C=3)
    assert candidates(3,3,task.guesses)==[(1,1,1)]
    large=MastermindTask.generate_random_task(L=8,C=2)
    assert len(large.final_answer.split())==8 and large.verify(large.final_answer)==1
    ten=MastermindTask(L=1,C=10)
    ten.guesses=[((i,),(0,0)) for i in range(1,10)]
    ten.solve();assert ten.final_answer=='10' and ten.verify('10')==1
    task.guesses=[((1,1,1),(3,0)),((1,1,1),(0,0))]
    with pytest.raises(ValueError,match='inconsistent_clues'):task.solve()
    task.guesses=[]
    with pytest.raises(ValueError,match='ambiguous_clues'):task.solve()


@pytest.mark.parametrize('kwargs',[dict(L=0),dict(L=True),dict(L=9),dict(C=0),dict(C=True),dict(C=11),dict(L=8,C=8)])
def test_invalid_mastermind_parameters(kwargs):
    with pytest.raises(ValueError):MastermindTask(**kwargs)


@pytest.mark.parametrize('clues',[[((1,),(0,0))],[((1,3),(0,0))],[((True,1),(0,0))],[((1,1),(True,0))],[((1,1),(2,1))]])
def test_invalid_mastermind_clues(clues):
    with pytest.raises(ValueError):deduce(2,2,clues,[])


def test_every_small_arithmetic_row_recomputed_independently():
    functions={'+':operator.add,'-':operator.sub,'*':operator.mul}
    for a,b in itertools.product(range(-3,4),repeat=2):
        for op,compute in functions.items():
            actual=compute(a,b)
            for delta in (-1,1):
                steps=[[a,op,b,actual+delta],[2,'+',3,5]];events=[]
                assert locate(steps,events)==1
                assert events[0]['actual']==actual and events[0]['delta']==delta
                assert events[1]['equal']
    for steps in ([],[[1,'+',2,3]],[[1,'+',2,4],[2,'*',3,7]]):
        with pytest.raises(ValueError,match='expected_one_incorrect_step'):locate(steps,[])
    with pytest.raises(ValueError,match='invalid_operator'):locate([[2,'/',1,2]],[])
    with pytest.raises(ValueError,match='invalid_operand'):locate([[True,'+',1,3]],[])


@pytest.mark.parametrize('language',['ru','en'])
def test_error_task_all_levels_ignores_saved_correct_values_and_error_index(language):
    for level in range(1,11):
        random.seed(level);task=FindTheErrorTask(language=language,difficulty=level)
        expected=task._error_index
        task._steps=[tuple(row[:4])+(object(),) for row in task._steps]
        task._error_index=-999
        state=random.getstate();task.solve();assert random.getstate()==state
        assert task.final_answer==str(expected)
        saved=json.dumps(task.get_result(),sort_keys=True)
        task.solve();assert json.dumps(task.get_result(),sort_keys=True)==saved
        assert len([e for e in task.algorithm_trace if e['operation']=='error_check'])==task.num_steps
        assert task.verify('<answer>'+str(expected)+'</answer>')==1
        for label in ('Step','Шаг'):
            assert task.verify(f'{label} {expected}')==1
            assert task.verify(f'{label}: {expected}')==1
            assert task.verify(f'{label} {expected} junk')==0
        assert task.verify('junk '+str(expected))==0
        assert task.verify(str(expected+1))==0
        assert all(len(row)==4 for row in task.computation_inputs['steps'])


def test_error_parameters_and_public_edits():
    task=FindTheErrorTask.generate_random_task(num_steps=1,max_number=1,ops=['*'])
    assert len(task._steps)==1 and task.final_answer=='1'
    task=FindTheErrorTask.generate_random_task(num_steps=1000,max_number=1_000_000,ops=['-'])
    assert len(task._steps)==1000 and task.verify(task.final_answer)==1
    assert all(row[1]=='-' for row in task._steps)
    task._steps=[(2,'*',3,6,0),(2,'+',3,7,0)]
    assert task.verify('2')==1
    task._steps=[(2,'*',3,6,0)]
    with pytest.raises(ValueError,match='expected_one_incorrect_step'):task.solve()


@pytest.mark.parametrize('kwargs',[dict(num_steps=0),dict(num_steps=True),dict(num_steps=1001),dict(num_steps=1.5),dict(max_number=0),dict(max_number=True),dict(max_number=1_000_001),dict(ops=[]),dict(ops=['/']),dict(ops='+')])
def test_invalid_error_parameters(kwargs):
    with pytest.raises(ValueError):FindTheErrorTask(**kwargs)


def test_quadratic_all_small_coefficients_against_real_smt_and_witness_replay():
    from fractions import Fraction
    from z3 import Real,Solver,sat,unsat
    from re_rl.tasks.math.logic.inequality_proof.solver import nonnegative
    x=Real('quadratic_x')
    for a,b,c in itertools.product(range(-3,4),repeat=3):
        solver=Solver();solver.add(a*x*x+b*x+c<0);status=solver.check()
        assert status in (sat,unsat)
        events=[];valid=nonnegative(a,b,c,events)
        assert valid==(status==unsat)
        for event in events:
            if event['operation']=='quad_counterexample':
                witness=Fraction(event['x']);value=a*witness*witness+b*witness+c
                assert value==Fraction(event['value']) and value<0
                assert Fraction(event['square'])+Fraction(event['linear'])+event['constant']==value
            if event['operation']=='quad_minimum':
                witness=Fraction(event['x'])
                assert 2*a*witness+b==0
                assert a*witness*witness+b*witness+c==Fraction(event['minimum'])
        assert bool([e for e in events if e['operation']=='quad_counterexample'])==(not valid)


@pytest.mark.parametrize('language',['ru','en'])
def test_quadratic_all_levels_cache_poison_coeff_bound_and_strict_labels(language):
    from re_rl.tasks.math.logic.inequality_proof.task import InequalityProofTask
    for level in range(1,11):
        random.seed(level);task=InequalityProofTask(language=language,difficulty=level)
        assert max(abs(task.a),abs(task.b),abs(task.c))<=task.max_coeff
        task._always_nonneg=object()
        state=random.getstate();task.solve();assert random.getstate()==state
        saved=json.dumps(task.get_result(),sort_keys=True)
        task.solve();assert json.dumps(task.get_result(),sort_keys=True)==saved
        assert task.verify(task.final_answer)==1
        assert task.verify('YES' if task.final_answer=='NO' else 'NO')==0
        assert task.verify('junk '+task.final_answer)==0
        assert task.verify('yes no')==0
    for coeffs,expected in [((0,0,0),'YES'),((0,0,-1),'NO'),((0,1,0),'NO'),((-1,0,0),'NO'),((1,2,1),'YES'),((2,1,0),'NO')]:
        task=InequalityProofTask(a=coeffs[0],b=coeffs[1],c=coeffs[2])
        task.solve();assert task.final_answer==expected
    task.a,task.b,task.c=0,0,1
    assert task.verify('YES')==1


def test_quadratic_max_coefficient_really_bounds_all_generated_coefficients():
    from re_rl.tasks.math.logic.inequality_proof.task import InequalityProofTask
    for bound in (1,2,7,20,1_000_000):
        for seed in range(10):
            random.seed(seed);task=InequalityProofTask(max_coeff=bound)
            assert max(abs(task.a),abs(task.b),abs(task.c))<=bound
    for kwargs in (dict(max_coeff=0),dict(max_coeff=True),dict(max_coeff=1.5),dict(max_coeff=1_000_001),dict(a=1),dict(a=True,b=0,c=0)):
        with pytest.raises(ValueError):InequalityProofTask(**kwargs)


@pytest.mark.parametrize('language',['ru','en'])
def test_visual_mastermind_dispatch_parameters_hidden_code_and_rendering(language):
    from re_rl.tasks.visual.mastermind.task import MastermindVisualTask
    for level in range(1,11):
        random.seed(level)
        task=MastermindVisualTask.generate_random_task(language=language,difficulty=level)
        expected=task.final_answer;task.secret=(999,)*task.L
        task.solve();assert task.final_answer==expected and task.verify(expected)==1
        assert task.algorithm_trace[-1]['complete']
    task=MastermindVisualTask.generate_random_task(language=language,L=8,C=2)
    assert task.L==8 and task.C==2
    # Maximal feedback requires four rows of key pegs; adjacent guesses must not overlap.
    task.guesses=[((1,1,1,1,2,2,2,2),(8,0)),((2,2,2,2,1,1,1,1),(0,8))]
    image=task.render_image();image.load()
    P,G=task.PEG,task.GAP;legend=P+2*G+24;row=max(P,3*18+14)+G
    fx=G+8*(P+G)+G
    assert image.getpixel((fx+7,legend+3*18+7))==(0,0,0)
    assert image.getpixel((fx+7,legend+row+7))==(255,255,255)
    assert image.height>=legend+2*row
    ten=MastermindVisualTask.generate_random_task(language=language,L=1,C=10)
    assert len({ten._color(i) for i in range(1,11)})==10
    ten.render_image().load()
