"""Independent proof soundness, set models, truth assignments and analogy hypotheses."""
import itertools
import random
import json
from unittest.mock import patch
import pytest
import sympy as sp
from re_rl.tasks.math.logic.proof_semantics import proof,entails,syllogism
from re_rl.tasks.math.logic.natural_deduction.task import NaturalDeductionTask,_check_line
from re_rl.tasks.math.logic.logical_entailment.task import LogicalEntailmentTask
from re_rl.tasks.math.logic.syllogism.task import SyllogismTask
from re_rl.tasks.math.logic.analogical.task import AnalogicalTask
from re_rl.tasks.math.logic.analogical.solver import infer
from re_rl.tasks.generators import generate_random_analogical_task

A=('atom','p');B=('atom','q');C=('atom','r')


def test_each_proof_rule_and_bad_references():
    cases=[('MP',[A,('imp',A,B)],B),('MT',[('not',B),('imp',A,B)],('not',A)),
           ('AND_I',[A,B],('and',A,B)),('AND_E1',[('and',A,B)],A),('AND_E2',[('and',A,B)],B)]
    for rule,prior,result in cases:
        line=dict(rule=rule,formula=result,refs=list(range(len(prior))))
        assert _check_line(line,prior)
        line['formula']=C;assert not _check_line(line,prior)
        line['formula']=result
        for refs in ([True],[-1],[len(prior)],[0.0],['0'],None):
            line['refs']=refs;assert not _check_line(line,prior)
    assert not proof([dict(rule='premise',formula=A,refs=[0])],[])
    assert not proof([dict(rule='premise',formula=('bogus','p'),refs=[])],[])
    assert proof(json.loads(json.dumps([dict(rule='premise',formula=A,refs=[]),dict(rule='premise',formula=('imp',A,B),refs=[]),dict(rule='MP',formula=B,refs=[0,1])])),[])


def test_local_rule_soundness_against_truth_tables():
    # Exhaust all formulas and reference orders in a small independently evaluated pool.
    atoms=[A,B];forms=atoms+[('not',a) for a in atoms]+[(op,a,b) for op in ('and','imp') for a,b in itertools.product(atoms,repeat=2)]
    def truth(f,assignment):
        if f[0]=='atom':return assignment[f[1]]
        if f[0]=='not':return not truth(f[1],assignment)
        a,b=truth(f[1],assignment),truth(f[2],assignment)
        return (a and b) if f[0]=='and' else (not a or b)
    for rule in ('MP','MT','AND_I','AND_E1','AND_E2'):
        arity=1 if rule.startswith('AND_E') else 2
        for prior in itertools.product(forms,repeat=arity):
            for output in forms:
                if _check_line(dict(rule=rule,refs=list(range(arity)),formula=output),list(prior)):
                    for values in itertools.product((False,True),repeat=2):
                        assignment=dict(zip(('p','q'),values))
                        assert not all(truth(f,assignment) for f in prior) or truth(output,assignment)


def test_all_syllogism_moods_against_set_interpretations():
    quantifiers=('all','no','some','some_not')
    regions=list(itertools.product((False,True),repeat=3))
    worlds=[]
    for bits in itertools.product((False,True),repeat=8):
        worlds.append({term:{i for i,r in enumerate(regions) if bits[i] and r[j]} for j,term in enumerate(('S','M','P'))})
    def holds(q,x,y,sets):
        a,b=sets[x],sets[y]
        return {'all':a<=b,'no':not bool(a&b),'some':bool(a&b),'some_not':bool(a-b)}[q]
    for figure,q1,q2,q3 in itertools.product(range(1,5),quantifiers,quantifiers,quantifiers):
        major,minor={1:(('M','P'),('S','M')),2:(('P','M'),('S','M')),3:(('M','P'),('M','S')),4:(('P','M'),('M','S'))}[figure]
        statements=[(q1,*major),(q2,*minor),(q3,'S','P')]
        expected=all(not(holds(*statements[0],s) and holds(*statements[1],s)) or holds(*statements[2],s) for s in worlds)
        events=[];assert syllogism(*statements,events)==expected
        for e in events:
            if e['operation']=='logic_category_world' and e['counterexample']:
                sets={term:{i for i,r in enumerate(e['occupied']) if r[j]} for j,term in enumerate(('S','M','P'))}
                assert holds(*statements[0],sets) and holds(*statements[1],sets) and not holds(*statements[2],sets)
    # Universal premises do not imply existential conclusions.
    assert not syllogism(('all','M','P'),('all','S','M'),('some','S','P'),[])


def test_entailment_against_sympy_and_node_trace():
    p,q=sp.symbols('p q')
    pairs=[(('var','p'),p),(('var','q'),q),(('not',('var','p')),~p)]
    for op,constructor in [('and',sp.And),('or',sp.Or),('imp',sp.Implies),('iff',sp.Equivalent)]:
        pairs.extend([((op,('var','p'),('var','q')),constructor(p,q))])
    for left,right in itertools.product(pairs,repeat=2):
        events=[];actual=entails(['p','q'],[left[0]],right[0],events)
        assert actual == (sp.satisfiable(sp.And(left[1],sp.Not(right[1]))) is False)
        assert any(e['operation']=='logic_eval' for e in events)
    assert entails(['p'],[('and',('var','p'),('not',('var','p')))],('var','p'),[])
    with pytest.raises(ValueError):entails(['p'],[],('unknown',('var','p'),('var','p')),[])


def test_analogy_ambiguous_predictions_and_exact_candidate_checks():
    # x and x^3 agree on -1,0,1 but differ at 2.
    with pytest.raises(ValueError,match='ambiguous_prediction'):AnalogicalTask(examples=[(-1,-1),(0,0),(1,1)],query=2,max_power=3,coefficient_bound=1,offset_bound=0)
    with pytest.raises(ValueError,match='inconsistent_examples'):AnalogicalTask(examples=[(0,1),(0,2)],query=2)
    task=AnalogicalTask(examples=[(1,3),(2,5),(3,7)],query=5,max_power=1);task.solve()
    assert task.final_answer=='11' and task.verify('11')==1
    for e in task.algorithm_trace:
        if e['operation']=='analogy_candidate':
            assert e['calculated']==[e['a']*x**e['power']+e['b'] for x,y in task.examples]
            assert e['consistent']==(e['calculated']==[y for x,y in task.examples])
    with pytest.raises(ValueError,match='structured_examples_required'):AnalogicalTask(description='arbitrary prose')
    for kwargs in ({'coefficient_bound':0},{'offset_bound':-1},{'max_power':4}):
        with pytest.raises(ValueError):AnalogicalTask(**kwargs)


@pytest.mark.parametrize('cls',[NaturalDeductionTask,LogicalEntailmentTask,SyllogismTask,AnalogicalTask])
@pytest.mark.parametrize('language',['ru','en'])
@pytest.mark.parametrize('level',range(1,11))
def test_all_levels_poison_cache_and_public_text(cls,language,level):
    random.seed(level);task=cls(language=language,difficulty=level);task.solve();expected=task.final_answer
    for key in ('valid','_valid','_entails','answer'):
        if hasattr(task,key):setattr(task,key,'poison')
    task.solve();assert task.final_answer==expected
    assert task.verify(expected)==1 and task.verify('garbage '+expected)==0
    assert task.verify('not '+expected)==0
    before=json.dumps(task.get_result(),sort_keys=True,allow_nan=False);rng=random.getstate()
    task.solve();assert json.dumps(task.get_result(),sort_keys=True,allow_nan=False)==before
    assert random.getstate()==rng
    assert '{x}' not in task.description and '{y}' not in task.description
    if cls is SyllogismTask:assert task.S in task.description and task.M in task.description and task.P in task.description
    if cls is AnalogicalTask:assert task.query not in [x for x,y in task.examples]


def test_analogy_generator_forwards_parameters_and_proof_fallback_errors():
    task=generate_random_analogical_task(language='en',difficulty=10,augment=False,max_power=1,offset_bound=0)
    assert task.max_power==1 and task.offset_bound==0 and task.verify(task.final_answer)==1
    with patch.object(NaturalDeductionTask,'_candidates',return_value=[]):
        with pytest.raises(ValueError,match='generation_failed'):NaturalDeductionTask(difficulty=10)


def test_syllogism_explicit_figures_and_moods():
    for figure in range(1,5):
        task=SyllogismTask(figure=figure,mood=('all','all','some'));task.solve()
        assert task.figure==figure and task.conclusion==('some','S','P')
        assert task.verify('not valid')==1 and task.verify('valid invalid')==0
    for kwargs in ({'figure':0},{'mood':('all','all')},{'mood':('all','all','unknown')}):
        with pytest.raises(ValueError):SyllogismTask(**kwargs)


def test_proof_event_snapshots_survive_input_mutation():
    lines=[dict(rule='premise',formula=A,refs=[]),dict(rule='premise',formula=('imp',A,B),refs=[]),dict(rule='MP',formula=B,refs=[0,1])]
    events=[];assert proof(lines,events)
    saved=json.dumps(events,sort_keys=True)
    lines[-1]['refs'][0]=999
    assert json.dumps(events,sort_keys=True)==saved
    malformed=[dict(rule='premise',formula=['invalid',['atom','p']],refs=[])]
    events=[];assert not proof(malformed,events)
    saved=json.dumps(events,sort_keys=True)
    malformed[0]['formula'][1][1]='changed'
    assert json.dumps(events,sort_keys=True)==saved
    assert not _check_line(dict(rule='AND_E1',formula=B,refs=[0]),[('and',A,B)])
    assert not _check_line(dict(rule='AND_E2',formula=A,refs=[0]),[('and',A,B)])
