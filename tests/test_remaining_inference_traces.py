"""Independent logic, date and visual-board oracles for previously cached answers."""
import calendar
import datetime
import itertools
import json
import random
from unittest.mock import patch
import pytest
from re_rl.tasks.math.logic.remaining_inference import ordinal,resolution,datalog,color_counts,queens_valid
from re_rl.tasks.visual.generators import ALL_VISUAL_TASK_GENERATORS
from re_rl.tasks.registry import registry


def test_calendar_arithmetic_against_standard_library():
    for year in (1,4,100,400,1582,1600,1700,1800,1900,1999,2000,2004,2100,2400,9999):
        for month in range(1,13):
            for day in (1,calendar.monthrange(year,month)[1]):
                date = datetime.date(year,month,day)
                value = ordinal(year,month,day)
                assert value == date.toordinal()
                assert (value-1)%7 == date.weekday()


def test_resolution_all_two_variable_clause_sets():
    universe = []
    for digits in itertools.product((0,1,2),repeat=2):
        universe.append(frozenset((v,d == 1) for v,d in zip(('A','B'),digits) if d))
    for mask in range(1 << len(universe)):
        clauses = [c for i,c in enumerate(universe) if mask & (1 << i)]
        satisfiable = any(all(any(assignment[v] == p for v,p in c) for c in clauses)
                          for values in itertools.product((False,True),repeat=2)
                          for assignment in [dict(zip(('A','B'),values))])
        events = []
        assert resolution(clauses,False,events) == (not satisfiable)
        expected = set()
        for a,b in itertools.combinations(clauses,2):
            for v,p in a:
                if (v,not p) in b:
                    combined = (a-{(v,p)}) | (b-{(v,not p)})
                    if all((w,not sign) not in combined for w,sign in combined):
                        expected.add(combined)
        assert resolution(clauses,True,[]) == len(expected)
        for event in events:
            if event['operation'] != 'infer_resolve': continue
            a,b = (set(map(tuple,event[k])) for k in ('left','right'))
            v = event['pivot']
            assert any((v,p) in a and (v,not p) in b and
                       (a-{(v,p)}) | (b-{(v,not p)}) == set(map(tuple,event['result']))
                       for p in (True,False))


def test_datalog_cycles_empty_bodies_and_event_replay():
    random.seed(19)
    props = ['A','B','C','D']
    for _ in range(150):
        rules = [(random.sample(props,random.randrange(3)),random.choice(props)) for _ in range(8)]
        facts = {'o1':set(random.sample(props,random.randrange(5))), 'o2':set()}
        events = []
        actual = datalog(list(facts),facts,rules,'D',events)
        expected = {o:set(v) for o,v in facts.items()}
        # Simultaneous rounds, unlike implementation's in-place rule updates.
        for _ in range(len(props)):
            expected = {o:known | {head for body,head in rules if set(body) <= known}
                        for o,known in expected.items()}
        assert actual == expected
        replay = {o:set(v) for o,v in facts.items()}
        for e in events:
            if e['operation'] == 'infer_rule':
                known = replay[e['obj']]
                assert e['missing'] == sorted(set(e['body'])-known)
                assert e['added'] == (not e['missing'] and e['head'] not in known)
                if e['added']: known.add(e['head'])
                assert sorted(known) == e['known']


def test_visual_counts_and_queen_pairs():
    for bits in itertools.product(range(2),repeat=6):
        assert color_counts([bits[:3],bits[3:]],[0,1]) == {c:bits.count(c) for c in range(2)}
    for cols in itertools.product(range(4),repeat=4):
        squares = list(enumerate(cols))
        expected = len({c for r,c in squares}) == 4 and len({r+c for r,c in squares}) == 4 and len({r-c for r,c in squares}) == 4
        assert queens_valid(cols) == expected


@pytest.mark.parametrize('name',['calendar_reasoning','datalog_inference','resolution','grid_color_count','queens_check_image'])
@pytest.mark.parametrize('level',range(1,11))
def test_cache_poison_all_subtypes(name,level):
    cls = registry[name]
    for kind in getattr(cls,'TASK_TYPES',[None]):
        random.seed(level)
        task = cls(language='en',difficulty=level,task_type=kind)
        task.solve()
        expected = task.final_answer
        for field in ('answer_int','answer_bool','answer_label','counts','most','closure'):
            if hasattr(task,field): setattr(task,field,'poison')
        task.solve()
        assert task.final_answer == expected
        if name == 'datalog_inference':
            assert not any('\u0400' <= ch <= '\u04ff' for ch in task.description)
        assert task.verify('<answer>'+expected+'</answer>') == 1
        json.dumps(task.get_result(),allow_nan=False)


def test_ambiguous_color_maximum_rejected_and_english_prompt():
    cls = registry['grid_color_count']
    task = cls(task_type='most_color')
    task.grid = [[0,1],[1,0]]
    task.palette = [0,1]
    with pytest.raises(ValueError,match='ambiguous_maximum'): task.solve()
    counter = itertools.count()
    with patch('random.choice',side_effect=lambda values:values[next(counter)%2]):
        with pytest.raises(ValueError,match='generation_failed'):
            cls(task_type='most_color',difficulty=3)
    task = cls(task_type='count_color',language='en')
    assert not any('\u0400' <= ch <= '\u04ff' for ch in task.description)
