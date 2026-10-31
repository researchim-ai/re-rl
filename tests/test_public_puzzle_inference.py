"""Independent model enumeration, carry witnesses and public constraint graders."""
import itertools
import json
import random
from unittest.mock import patch
import pytest
from re_rl.tasks.math.logic.puzzle_inference import futoshiki,cryptarithm,knight_models,statement_value
from re_rl.tasks.math.logic.futoshiki.task import FutoshikiTask
from re_rl.tasks.math.logic.cryptarithmetic.task import CryptarithmeticTask
from re_rl.tasks.math.logic.knights_knaves.task import KnightsKnavesTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES


def latin_squares(n):
    return [rows for rows in itertools.product(list(itertools.permutations(range(1,n+1))),repeat=n)
            if all(len({row[c] for row in rows}) == n for c in range(n))]


def test_futoshiki_small_inputs_vs_latin_oracle():
    for n in (2,3):
        grids = latin_squares(n)
        cells = list(itertools.product(range(n),repeat=2))
        pairs = [a+b for a,b in itertools.permutations(cells,2)]
        random.seed(12)
        conditions = [[],[(0,0,0,0)]]
        if n == 2:
            for k in range(1,4):conditions.extend(itertools.combinations(pairs,k))
        else:conditions += [random.sample(pairs,random.randrange(10)) for _ in range(70)]
        for inequalities in conditions:
            valid = [g for g in grids if all(g[r][c] < g[s][t] for r,c,s,t in inequalities)]
            events = [];result = futoshiki(n,inequalities,events)
            assert (result is not None) == bool(valid)
            if result is not None:assert tuple(map(tuple,result)) in valid


def crypt_models(a,b,c):
    letters = sorted(set(a+b+c));leading = {a[0],b[0],c[0]}
    result = []
    for digits in itertools.permutations(range(10),len(letters)):
        mapping = dict(zip(letters,digits))
        if any(mapping[x] == 0 for x in leading):continue
        def val(w):return int(''.join(str(mapping[x]) for x in w))
        if val(a)+val(b) == val(c):result.append(mapping)
    return result


def test_column_addition_against_exhaustive_digit_permutations():
    random.seed(32)
    words = ['A','B','AB','BA','AA','BB','ABA','BAB']
    for _ in range(70):
        a,b,c = [random.choice(words) for _ in range(3)]
        expected = crypt_models(a,b,c)
        events = [];result = cryptarithm(a,b,c,events)
        assert (result is not None) == bool(expected)
        if result is not None:assert result in expected
        for event in events:
            if event['operation'] == 'puzzle_column':
                assert event['x']+event['y']+event['carry'] == event['total']
                assert divmod(event['total'],10) == (event['next_carry'],event['digit'])
    events = [];answer = cryptarithm('SEND','MORE','MONEY',events)
    assert answer == dict(S=9,E=5,N=6,D=7,M=1,O=0,R=8,Y=2)
    assert any(e['operation'] == 'puzzle_digit_remove' for e in events)


def direct_truth(form,roles,s,y,z,p):
    true_people = {i for i,v in enumerate(roles) if v == p}
    if form == 'about_self':return s in true_people
    if form == 'about_other':return y in true_people
    if form == 'and':return {y,z} <= true_people
    if form == 'or':return bool({y,z}&true_people)
    if form == 'same':return len({y,z}&true_people) in (0,2)
    if form == 'different':return len({y,z}&true_people) == 1
    if form == 'at_least_one':return bool(true_people)
    return len(true_people) == 1


def test_every_statement_form_and_model_trace():
    forms = ['about_self','about_other','and','or','same','different','at_least_one','exactly_one']
    for form,p in itertools.product(forms,(False,True)):
        s = dict(form_key=form,speaker=0,y=1,z=2,polarity=p)
        for roles in itertools.product((False,True),repeat=3):
            assert statement_value(s,roles) == direct_truth(form,roles,0,1,2,p)
    random.seed(16)
    for _ in range(50):
        statements = [dict(form_key=random.choice(forms),speaker=0,y=1,z=2,polarity=bool(random.getrandbits(1))) for _ in range(4)]
        expected = [r for r in itertools.product((False,True),repeat=3)
                    if all(r[s['speaker']] == direct_truth(s['form_key'],r,s['speaker'],s['y'],s['z'],s['polarity']) for s in statements)]
        events = [];assert knight_models(3,statements,events) == expected
        for e in events:
            if e['operation'] == 'puzzle_model':assert e['valid'] == (tuple(e['roles']) in expected)


@pytest.mark.parametrize('cls',[FutoshikiTask,CryptarithmeticTask,KnightsKnavesTask])
@pytest.mark.parametrize('language',['ru','en'])
@pytest.mark.parametrize('level',range(1,11))
def test_public_solver_cache_poison_and_parameters(cls,language,level):
    random.seed(level)
    task = cls(language=language,difficulty=level);task.solve()
    expected = task.final_answer
    for field in ('solution','_mapping','roles'):
        if hasattr(task,field):setattr(task,field,'poison')
    task.solve();assert task.final_answer == expected
    assert task.verify('<answer>'+expected+'</answer>') == 1
    before = json.dumps(task.get_result(),sort_keys=True,allow_nan=False)
    task.solve();assert json.dumps(task.get_result(),sort_keys=True,allow_nan=False) == before
    assert 'algorithm_trace' in task.get_result()
    if cls is FutoshikiTask:assert task.solution is not None
    if cls is KnightsKnavesTask:
        assert task.num_persons == (level+1)//2+1
        assert task.names and len(task.names) == task.num_persons
        for s in task.statements:assert s['text'] == task._build_statement_text(s)
        if language == 'ru':assert all('knight' not in s['text'] and 'knave' not in s['text'] for s in task.statements)


def test_futoshiki_alternative_answers_unsat_and_generation_bounds():
    task = FutoshikiTask(size=2,num_inequalities=0);task.solve()
    assert task.verify('1 2\n2 1') == task.verify('2 1\n1 2') == 1
    assert task.verify('1.2 2 1') == task.verify('junk 1 2 2 1') == 0
    task.inequalities = [(0,0,0,1),(0,1,0,0)];task.solve()
    assert task.solution is None and task.verify(task.final_answer) == 1
    assert task.verify('1 2 2 1') == 0
    task = FutoshikiTask(size=1,num_inequalities=0);task.solve();assert task.verify(task.final_answer) == 1
    for kwargs in ({'size':0},{'size':2,'num_inequalities':5},{'size':2,'num_inequalities':-1}):
        with pytest.raises(ValueError):FutoshikiTask(**kwargs)


def test_cryptarithm_strict_grader_and_failed_generation():
    task = CryptarithmeticTask();task._word_a,task._word_b,task._word_c = 'A','A','B';task.solve()
    for answer in ('A=1,B=2','A=2,B=4'):assert task.verify(answer) == 1
    for answer in ('A=10,B=2','A=1,B=2,B=2','A=1.5,B=2','junk A=1,B=2','A=1,B=2,Q=9','A=0,B=0'):
        assert task.verify(answer) == 0
    with patch('random.randint',return_value=0):
        with pytest.raises(ValueError,match='generation_failed'):CryptarithmeticTask()
    with pytest.raises(ValueError):CryptarithmeticTask(num_digits=7)
    task._word_a = task._word_b = task._word_c = 'A'
    task.solve();assert task.verify(task.final_answer) == 1 and task._mapping is None


def test_knights_any_model_and_shared_names_pool_unchanged():
    saved = list(PROMPT_TEMPLATES['knights_knaves']['names_pool']['en'])
    task = KnightsKnavesTask(complexity=1)
    assert PROMPT_TEMPLATES['knights_knaves']['names_pool']['en'] == saved
    task.statements = [dict(form_key='about_self',speaker=0,y=1,z=None,polarity=True)]
    for roles in itertools.product(('knight','knave'),repeat=2):
        answer = ', '.join(n+': '+r for n,r in zip(task.names,roles))
        assert task.verify(answer) == 1
        assert task.verify(answer+', '+task.names[0]+': knight') == 0
    task.statements = [dict(form_key='about_self',speaker=0,y=1,z=None,polarity=False)]
    task.solve();assert task.roles is None and task.verify(task.final_answer) == 1
    with pytest.raises(ValueError):KnightsKnavesTask(complexity=6)


def test_probability_exact_oracles_and_stable_instances():
    from fractions import Fraction
    from re_rl.tasks.math.probability.inference_traces import bayesian,urn
    from re_rl.tasks.math.probability.bayesian_reasoning.task import BayesianReasoningTask
    from re_rl.tasks.math.probability.urn_probability.task import UrnProbabilityTask
    # Explicit joint population: 2 diseased/98 healthy, 90% sensitivity, 5% FPR.
    assert bayesian('bayes_basic',dict(p_d=.02,sens=.9,spec=.95)) == Fraction(18,67)
    assert bayesian('base_rate',dict(p_d=.02,sens=.9,fpr=.05)) == Fraction(18,67)
    parameters = dict(p_a=.3,p_b_a=.7,p_c_b=.8,p_b_not_a=.2,p_c_not_b=.1)
    total = Fraction(0)
    for a,b,c in itertools.product((False,True),repeat=3):
        pa = Fraction(3,10) if a else Fraction(7,10)
        pb = Fraction(7,10) if a else Fraction(2,10)
        pc = Fraction(8,10) if b else Fraction(1,10)
        if c:total += pa*(pb if b else 1-pb)*pc
    assert bayesian('bayes_chain',parameters) == total
    for red,blue in itertools.product(range(4),repeat=2):
        balls = ['red']*red+['blue']*blue
        for draws in range(1,len(balls)+1):
            subsets = list(itertools.combinations(range(len(balls)),draws))
            for kind,x in [('all',None),('at_least',None)]+[('exactly',x) for x in range(draws+1)]:
                counts = [sum(balls[i] == 'red' for i in subset) for subset in subsets]
                matched = sum(k == draws if kind == 'all' else k > 0 if kind == 'at_least' else k == x for k in counts)
                assert urn([[('red',red),('blue',blue)]],draws,'red',kind,x) == Fraction(matched,len(subsets))
    for cls in (BayesianReasoningTask,UrnProbabilityTask):
        for language in ('ru','en'):
            for level in range(1,11):
                kinds = cls.TASK_TYPES if cls is BayesianReasoningTask else [None]
                for kind in kinds:
                    random.seed(level)
                    task = cls(language=language,difficulty=level,task_type=kind) if cls is BayesianReasoningTask else cls(language=language)
                    initial_description = task.description
                    result = task.get_result();state = random.getstate()
                    task.probability = 'poison';task.final_answer = 'poison';task.solve()
                    assert random.getstate() == state and task.description == initial_description
                    assert task.get_result() == result
                    assert task.verify(task.final_answer) == task.verify(str(task.probability)) == 1
                    assert task.verify('nan') == task.verify('garbage '+task.final_answer) == 0
    for kwargs in ({'draws':0},{'draws':-1},{'count_containers':0}):
        with pytest.raises(ValueError):UrnProbabilityTask(**kwargs)
    task = UrnProbabilityTask(draws=10)
    assert all(sum(c for name,c in dist) >= 10 for dist in task.containers)


class RandomizedExplanation:
    def solve(self):
        self.solution_steps = [str(random.randint(0,9))]


def test_audit_detects_random_explanations():
    from scripts.audit_task_traces import static_indicators
    report = static_indicators(RandomizedExplanation)
    assert report['random_solver_calls'] == ['randint'] and report['candidate']


def test_futoshiki_generation_does_not_repeat_an_expensive_solver():
    with patch.object(FutoshikiTask,'_solve_with_z3',side_effect=AssertionError('unnecessary_search')):
        task = FutoshikiTask(size=7,num_inequalities=20)
    task.solution = 'poison';task.solve()
    assert task.verify(task.final_answer) == 1
