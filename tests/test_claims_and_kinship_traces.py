"""Public arithmetic oracles and generic path-language kinship checks."""
import copy
import itertools
import json
import random
import operator
from unittest.mock import patch
import pytest
from re_rl.tasks.math.logic.contradiction.task import ContradictionTask
from re_rl.tasks.math.logic.contradiction.solver import evaluate
from re_rl.tasks.math.logic.family_tree.task import FamilyTreeTask
from re_rl.tasks.math.logic.family_tree.solver import relationship


def test_generated_claims_against_symbolic_exact_oracle():
    import sympy as sp
    for language in ('ru','en'):
        for level in range(1,11):
            random.seed(level)
            task = ContradictionTask(language=language,difficulty=level)
            env = {};ops = {'add':operator.add,'sub':operator.sub,'mul':operator.mul}
            for d in task.definitions:
                def value(v):return env[v] if isinstance(v,str) else sp.Integer(v)
                env[d['name']] = value(d['value']) if d['op'] == 'const' else ops[d['op']](value(d['left']),value(d['right']))
            relations = {'eq':sp.Eq,'ne':sp.Ne,'lt':sp.Lt,'le':sp.Le,'gt':sp.Gt,'ge':sp.Ge}
            truths = [bool(relations[c['relation']](env[c['left']],c['right'])) for c in task.claims]
            assert truths.count(False) == 1
            false_index = truths.index(False)
            task.false_statement_index = 'poison';task.statements = ['poison'];task.solve()
            assert task.false_statement_index == false_index
            assert task.verify(str(false_index+1)) == task.verify(task.final_answer) == 1
            assert task.verify(str((false_index+1)%len(task.claims)+1)) == 0
            assert 'algorithm_trace' in task.get_result()
            replay = {}
            for e in task.algorithm_trace:
                if e['operation'] == 'claim_define':
                    expected = e['operands'][0] if e['op'] == 'const' else ops[e['op']](*e['operands'])
                    assert expected == e['result'];replay[e['name']] = e['result']
            assert {k:int(v) for k,v in env.items()} == replay
            assert all(str(c['right']) in task.description for c in task.claims)


def test_all_integer_relations_and_claim_failures():
    relations = {'eq':operator.eq,'ne':operator.ne,'lt':operator.lt,'le':operator.le,'gt':operator.gt,'ge':operator.ge}
    for a,b,relation in itertools.product(range(-2,3),range(-2,3),relations):
        _,false = evaluate([dict(name='a',op='const',value=a)],[dict(left='a',relation=relation,right=b)],[])
        assert false == ([] if relations[relation](a,b) else [0])
    for definitions in ([dict(name='a',op='add',left='a',right=1)],
                        [dict(name='a',op='const',value=1),dict(name='a',op='const',value=2)],
                        [dict(name='a',op='const',value=True)]):
        with pytest.raises(ValueError):evaluate(definitions,[],[])
    task = ContradictionTask(num_statements=1,chain_depth=0);task.solve()
    assert task.verify('1') == 1 and task.verify('1 extra') == 0
    task.claims[0] = dict(left='a',relation='eq',right=task.definitions[0]['value'])
    with pytest.raises(ValueError,match='expected_one_false_claim'):task.solve()
    assert task.verify('1') == 0
    for kwargs in ({'num_statements':0},{'chain_depth':-1},{'chain_depth':21},{'num_statements':2.5}):
        with pytest.raises(ValueError):ContradictionTask(**kwargs)
    task = ContradictionTask(num_statements=70,chain_depth=2);task.solve()
    expected = task.final_answer;task.false_statement_index = 'poison'
    assert len(task.claims) == 70 and task.verify(expected) == 1
    task.claims = [dict(left='a',relation='ne',right=task.definitions[0]['value'])]*2
    with pytest.raises(ValueError,match='expected_one_false_claim'):task.solve()
    assert task.verify('1') == task.verify('2') == 0


PATTERNS = {('P',):('father','mother'),('C',):('son','daughter'),('S',):('husband','wife'),
            ('P','P'):('grandfather','grandmother'),('C','C'):('grandson','granddaughter'),
            ('C','P'):('brother','sister'),('C','P','P'):('uncle','aunt'),
            ('C','C','P'):('nephew','niece'),('C','C','P','P'):('cousin_m','cousin_f')}


def path_roles(task,a,b):
    graph = {p:[] for p in task.gender}
    for x,y in task.couples:graph[x].append((y,'S'));graph[y].append((x,'S'))
    for x,y,kids in task.child_groups:
        for child in kids:
            for parent in (x,y):graph[parent].append((child,'P'));graph[child].append((parent,'C'))
    result = set()
    def walk(node,path,pattern):
        if node == b:
            if pattern in PATTERNS:result.add(PATTERNS[pattern][task.gender[a] == 'f'])
            return
        if len(pattern) == 4:return
        for other,edge in graph[node]:
            if other not in path:walk(other,path+(other,),pattern+(edge,))
    walk(a,(a,),())
    return result,graph


def test_every_family_pair_against_generic_path_oracle_and_replay():
    all_roles = set()
    for seed in range(10):
        random.seed(seed);task = FamilyTreeTask()
        for a,b in itertools.permutations(task.gender,2):
            expected,graph = path_roles(task,a,b)
            events = []
            if len(expected) != 1:
                with pytest.raises(ValueError):relationship(task.gender,task.couples,task.child_groups,a,b,events)
            else:
                role = relationship(task.gender,task.couples,task.child_groups,a,b,events)
                assert role in expected;all_roles.add(role)
                for e in events:
                    if e['operation'] == 'kin_witness':
                        assert e['path'][0] == a and e['path'][-1] == b
                        for x,y,kind in zip(e['path'],e['path'][1:],e['kinds']):
                            assert (y,{'parent':'P','child':'C','spouse':'S'}[kind]) in graph[x]
    assert all_roles == set(role for pair in PATTERNS.values() for role in pair)


@pytest.mark.parametrize('language',['ru','en'])
@pytest.mark.parametrize('level',range(1,11))
def test_family_public_facts_cache_and_depth(language,level):
    random.seed(level);task = FamilyTreeTask(language=language,difficulty=level);task.solve()
    expected = task.final_answer
    witness = next(e for e in task.algorithm_trace if e['operation'] == 'kin_witness')
    assert len(witness['kinds']) == task.relation_hops
    assert task.relation_hops == (1 if level <= 2 else 2 if level <= 6 else 3 if level <= 8 else 4)
    task.parents = task.spouse = task.role = 'poison'
    assert task.verify(expected) == 1
    task.solve();assert task.final_answer == expected
    assert task.verify('not '+expected) == task.verify('garbage '+expected) == 0
    before = json.dumps(task.get_result(),sort_keys=True,allow_nan=False);rng = random.getstate()
    task.solve();assert json.dumps(task.get_result(),sort_keys=True,allow_nan=False) == before
    assert rng == random.getstate()


def test_bad_family_models_and_public_mutation_invalidate_certificate():
    for kwargs in ({'relation_hops':0},{'relation_hops':5}):
        with pytest.raises(ValueError):FamilyTreeTask(**kwargs)
    task = FamilyTreeTask(difficulty=None,relation_hops=4);task.solve()
    expected = task.final_answer
    task.child_groups = [];task.couples = []
    assert task.verify(expected) == 0
    with pytest.raises(ValueError,match='ancestry_cycle'):
        relationship({'a':'m','b':'f','c':'m'},[],[('a','c',['b']),('b','c',['a'])],'a','b',[])
    with pytest.raises(ValueError,match='invalid_couples'):
        relationship({'a':'m','b':'f','c':'m'},[('a','b'),('a','c')],[],'a','b',[])


def test_ambiguous_kinship_and_old_fact_labels_are_not_active():
    from re_rl.tasks.prompts import PROMPT_TEMPLATES
    assert 'contradiction_facts' not in PROMPT_TEMPLATES
    with pytest.raises(ValueError,match='ambiguous_relation'):
        relationship({'a':'m','b':'f','c':'m'},[('a','b')],[('a','c',['b'])],'a','b',[])
