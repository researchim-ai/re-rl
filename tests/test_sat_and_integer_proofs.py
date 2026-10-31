"""Truth-table/SMT SAT oracles and symbolic universal-integer proof checks."""
import itertools
import json
import random
from math import lcm
import pytest
import sympy as sp
from z3 import Bool, Solver, Or, Not, sat
from re_rl.tasks.math.logic.sat_smt_mini.task import SATSMTMiniTask
from re_rl.tasks.math.logic.sat_smt_mini.solver import dpll
from re_rl.tasks.math.logic.proof_cases_counterexample.task import ProofCasesCounterexampleTask
from re_rl.tasks.math.logic.proof_cases_counterexample.solver import analyse,is_counterexample


def models(n,clauses):
    return [values for values in itertools.product((False,True),repeat=n)
            if all(any(values[i]==sign for i,sign in clause) for clause in clauses)]


def test_all_small_cnfs_against_truth_tables_and_replay():
    literals=list(itertools.product(range(2),(False,True)))
    choices=[[]]+[[literal] for literal in literals]+list(itertools.combinations_with_replacement(literals,2))
    for size in range(4):
        for cnf in itertools.combinations_with_replacement(choices,size):
            expected=models(2,cnf);events=[];actual=dpll(2,cnf,events)
            assert (actual is None)==(not expected)
            if actual is not None:assert tuple(actual) in expected
            for event_index,event in enumerate(events):
                if event['operation'] in ('sat_unit','sat_conflict'):
                    previous=next(e for e in reversed(events[:event_index]) if e['operation']=='sat_clause' and e['depth']==event['depth'] and e['clause']==event['clause'])
                    if event['operation']=='sat_conflict':assert all(value is False for _,_,value in previous['literals'])
                    else:
                        unresolved={(i,positive) for i,positive,value in previous['literals'] if value is None}
                        assert unresolved=={(event['variable'],event['value'])}
                        assert not previous['satisfied']
                if event['operation']=='sat_clause':
                    assignment={int(k[1:])-1:v for k,v in event['assignment'].items()}
                    clause=cnf[event['clause']-1]
                    assert event['literals']==[[i+1,sign,None if i not in assignment else assignment[i]==sign] for i,sign in clause]
                    assert event['satisfied']==any(value is True for _,_,value in event['literals'])
    # Neither root branch can satisfy these four binary clauses: require backtracking.
    cnf=[[(0,a),(1,b)] for a,b in itertools.product((False,True),repeat=2)]
    events=[];assert dpll(2,cnf,events) is None
    assert {e['value'] for e in events if e['operation']=='sat_backtrack' and e['depth']==0}=={False,True}


def test_sat_against_independent_z3():
    rng=random.Random(47)
    for _ in range(100):
        cnf=[[(rng.randrange(3),bool(rng.getrandbits(1))) for _ in range(rng.randrange(4))] for _ in range(rng.randrange(9))]
        variables=[Bool(f'x{i}') for i in range(3)];solver=Solver()
        for clause in cnf:solver.add(Or(*[variables[i] if sign else Not(variables[i]) for i,sign in clause]))
        result=dpll(3,cnf,[])
        assert (result is not None)==(solver.check()==sat)


@pytest.mark.parametrize('target',['sat','unsat','mixed'])
def test_generator_targets_exact_counts_and_one_variable(target):
    for seed in range(30):
        random.seed(seed)
        task=SATSMTMiniTask.generate_random_task(target=target,num_vars=1,num_clauses=2)
        assert len(task._cnf)==2
        if target!='mixed':assert bool(models(1,task._cnf))==(target=='sat')
    for count in (0,1,256):
        task=SATSMTMiniTask.generate_random_task(target='sat',num_vars=3,num_clauses=count)
        assert len(task._cnf)==count and task.verify(task.final_answer)==1


def test_long_unsat_chain_and_maximum_variable_count():
    task=SATSMTMiniTask.generate_random_task(target='unsat',num_vars=64,num_clauses=65)
    assert task.final_answer=='UNSAT'
    assert len([e for e in task.algorithm_trace if e['operation']=='sat_unit'])==64
    assert len(task._cnf)==65
    task=SATSMTMiniTask.generate_random_task(target='sat',num_vars=64,num_clauses=0)
    assert len(task.final_answer.split(','))==64 and task.verify(task.final_answer)==1


def test_sat_semantic_grader_alternatives_and_invalid_witnesses():
    task=SATSMTMiniTask(num_vars=2,target='sat',num_clauses=0)
    task._cnf=[[(0,True),(1,True)]]
    for a,b in itertools.product((False,True),repeat=2):
        assert task.verify(f'SAT:x1={a},x2={b}')==float(a or b)
    for text in ('SAT','UNSAT','SAT:x1=True','SAT:x1=True,x1=False','SAT:x1=True,x3=False','SAT:x1=True,x2=False junk','SAT:x1=notfalse,x2=False'):
        assert task.verify(text)==0
    task._cnf=[[(0,True)],[(0,False)]]
    assert task.verify('UNSAT')==1 and task.verify('SAT:x1=True,x2=False')==0
    task._cnf=[[]]
    task.solve();assert task.final_answer=='UNSAT'


def test_residue_proofs_against_symbolic_polynomials():
    n=sp.Symbol('n',integer=True)
    for coefficients in itertools.product((-1,0,1),repeat=3):
        expression=sum(c*n**i for i,c in enumerate(coefficients))
        for modulus in range(2,9):
            for premise in (1,2):
                residues=[0] if premise==1 else [1]
                claim=dict(kind='divisible',coefficients=coefficients,modulus=modulus,premise_modulus=premise,premise_residues=residues)
                valid,example=analyse(claim,[])
                expected=all(int(expression.subs(n,r))%modulus==0 for r in range(lcm(modulus,premise)) if r%premise in residues)
                assert valid==expected
                if not valid:assert is_counterexample(claim,example)
                events=[];analyse(claim,events)
                cases=[e['residue'] for e in events if e['operation']=='proof_case']
                assert cases==list(range(lcm(modulus,premise))) if valid else cases==list(range(example+1))
                for event in events:
                    if event['operation']=='proof_horner':assert event['result']==event['previous']*event['n']+event['coefficient']
                    if event['operation']=='proof_remainder':
                        assert event['value']==int(expression.subs(n,event['n']))
                        assert event['remainder']==event['value']%modulus
    # A few initial examples are insufficient: n*(n-1) is not divisible by 3.
    claim=dict(kind='divisible',coefficients=[0,-1,1],modulus=3,premise_modulus=1,premise_residues=[0])
    assert analyse(claim,[])==(False,2)


def test_identity_expansion_against_sympy():
    n=sp.Symbol('n',integer=True)
    for shift in range(1,11):
        for delta,offset in itertools.product((-1,0,1),repeat=2):
            claim=dict(kind='identity',shift=shift,linear=2*shift+delta,constant=shift**2+offset)
            events=[];valid,witness=analyse(claim,events)
            expression=sp.expand((n+shift)**2-n**2-claim['linear']*n-claim['constant'])
            assert valid==(expression==0)
            if not valid:assert expression.subs(n,witness)!=0
            identity=next(e for e in events if e['operation']=='proof_identity')
            assert sp.Poly(expression,n)==sp.Poly(sum(c*n**i for i,c in enumerate(identity['difference'])),n)


@pytest.mark.parametrize('cls',[SATSMTMiniTask,ProofCasesCounterexampleTask])
@pytest.mark.parametrize('language',['ru','en'])
def test_all_levels_stability_public_inputs_and_rng(cls,language):
    for level in range(1,11):
        random.seed(level)
        task=cls(language=language,difficulty=level)
        description=task.description;state=random.getstate();task.solve()
        assert task.description==description and random.getstate()==state
        original=json.dumps(task.get_result(),sort_keys=True)
        task.final_answer='stale';task.truth=False;task.answer=-999
        task.solve();assert json.dumps(task.get_result(),sort_keys=True)==original
        assert task.verify('<answer>'+task.final_answer+'</answer>')==1
        assert len(task.solution_steps)==len(task.algorithm_trace)+1
        if language=='ru':assert any('А'<=c<='я' for c in task.description)


@pytest.mark.parametrize('kind',ProofCasesCounterexampleTask.TASK_TYPES)
@pytest.mark.parametrize('bias',[0,1])
def test_legacy_claims_computed_not_prelabelled(kind,bias):
    task=ProofCasesCounterexampleTask.generate_random_task(task_type=kind,truth_bias=bias,shift=7)
    assert task.final_answer.startswith('TRUE' if bias else 'FALSE')
    if not bias:
        witnesses=[n for n in range(-20,21) if is_counterexample(task.claim,n)]
        assert witnesses
        for n in witnesses:assert task.verify(f'FALSE;n={n}')==1
        assert task.verify('TRUE')==0
    else:
        assert task.verify('FALSE;n=0')==0
    assert task.verify('junk '+task.final_answer)==0


def test_public_proof_parameters_and_mutation():
    task=ProofCasesCounterexampleTask(task_type='parity_quadratic',coefficients=[0,-1,1],modulus=3)
    task.solve();assert task.final_answer=='FALSE;n=2'
    task.claim['modulus']=2
    assert task.verify('TRUE')==1
    task.solve();assert task.final_answer=='TRUE'
    task.claim=dict(kind='identity',shift=1,linear=3,constant=1)
    task.solve();assert task.final_answer=='FALSE;n=1'


@pytest.mark.parametrize('kwargs',[dict(num_vars=0),dict(num_vars=True),dict(num_vars=65),dict(num_clauses=-1),dict(num_clauses=True),dict(num_clauses=257),dict(target='bad'),dict(target='unsat',num_clauses=1)])
def test_invalid_sat_parameters(kwargs):
    with pytest.raises(ValueError):SATSMTMiniTask(**kwargs)


@pytest.mark.parametrize('kwargs',[dict(task_type='bad'),dict(truth_bias=-1),dict(truth_bias=float('nan')),dict(truth_bias=True),dict(shift=0),dict(shift=True),dict(task_type='parity_quadratic',modulus=1),dict(task_type='parity_quadratic',coefficients=[1.5]),dict(task_type='factorization_form',modulus=3)])
def test_invalid_proof_parameters(kwargs):
    with pytest.raises(ValueError):ProofCasesCounterexampleTask(**kwargs)


@pytest.mark.parametrize('clauses',[[[(True,True)]],[[(0,1)]],[[(2,True)]],[[(0,True,1)]]])
def test_invalid_cnf_literals(clauses):
    with pytest.raises(ValueError):dpll(2,clauses,[])
