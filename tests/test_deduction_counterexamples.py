"""Exhaustive independent worlds and counterexample-based grading checks."""
from itertools import product,permutations,combinations
import json
import random
from unittest.mock import patch
import pytest
from re_rl.tasks.math.logic.deduction_search import mine_status,zebra_model,zebra_answer,zebra_valid,query_answer
from re_rl.tasks.math.logic.minesweeper_deduction.task import MinesweeperDeductionTask
from re_rl.tasks.math.logic.zebra_puzzle.task import ZebraPuzzleTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.visual.minesweeper.task import MinesweeperVisualTask


def test_all_two_by_two_mine_views_vs_full_worlds():
    cells = [(0,0),(0,1),(1,0),(1,1)]
    # All reveal subsets, target cells, and numeric clues 0..3 (including inconsistency).
    for count in range(4):
        for revealed in combinations(cells,count):
            hidden = [c for c in cells if c not in revealed]
            for numbers in product(range(4),repeat=count):
                clues = dict(zip(revealed,numbers))
                worlds = []
                for bits in product((0,1),repeat=len(hidden)):
                    mines = {cell for cell,bit in zip(hidden,bits) if bit}
                    if all(sum(nb in mines for nb in cells if nb != cell) == value for cell,value in clues.items()):worlds.append(mines)
                for target in hidden:
                    events = [];actual = mine_status(2,clues,target,events)
                    assert actual == sorted({int(target in world) for world in worlds})
                    for event in events:
                        if event['operation'] == 'deduce_mine_witness' and event['exists']:
                            witness = set(map(tuple,event['mines']))
                            assert witness in worlds and int(target in witness) == event['value']


def oracle_zebra(n,values,clues):
    # Explicit house permutations; evaluate clues directly rather than using solver tables.
    result = []
    for rows in product(*[list(permutations(v)) for v in values.values()]):
        model = dict(zip(values,rows))
        positions = {cat:{v:i for i,v in enumerate(items)} for cat,items in model.items()}
        valid = True
        for clue in clues:
            kind,d = clue['type'],clue['data']
            if len(d) == 3:ok = positions[d[0]][d[1]] == d[2]
            else:
                a,b = positions[d[0]][d[1]],positions[d[2]][d[3]]
                ok = {'same_house':a==b,'neighbor':abs(a-b)==1,'left_of':a<b,'not_neighbor':abs(a-b)!=1}[kind]
            valid = valid and ok
        if valid:result.append({c:list(row) for c,row in model.items()})
    return result


def test_house_constraint_types_and_forbidden_answers_vs_permutations():
    values = {'people':['A','B','C'],'pets':['cat','dog','fox']}
    random.seed(21)
    pool = [dict(type=k,data=('people','A','pets','cat')) for k in ('same_house','neighbor','left_of','not_neighbor')]
    pool += [dict(type='position',data=('people','A',i)) for i in range(3)]
    pool += [dict(type='first',data=('people','A',0)),dict(type='middle',data=('people','A',1))]
    queries = [('position','people','B'),('owner','pets','cat','people')]
    for _ in range(80):
        clues = random.sample(pool,random.randrange(5))
        expected = oracle_zebra(3,values,clues)
        actual = zebra_model(3,values,clues)
        assert (actual is not None) == bool(expected)
        if actual is None:continue
        assert actual in expected
        for query in queries:
            answer = query_answer(actual,query)
            alternatives = [m for m in expected if query_answer(m,query) != answer]
            other = zebra_model(3,values,clues,forbidden=(query,answer))
            assert (other is not None) == bool(alternatives)
            if alternatives:
                with pytest.raises(ValueError,match='ambiguous_answer'):zebra_answer(3,values,clues,query,[])
            else:
                model,found = zebra_answer(3,values,clues,query,[])
                assert model in expected and found == answer


@pytest.mark.parametrize('cls',[MinesweeperDeductionTask,MinesweeperVisualTask,ZebraPuzzleTask])
@pytest.mark.parametrize('language',['ru','en'])
@pytest.mark.parametrize('level',range(1,11))
def test_all_levels_public_inputs_and_hidden_cache_poison(cls,language,level):
    random.seed(level)
    task = cls(language=language,difficulty=level);task.solve()
    expected = task.final_answer
    if issubclass(cls,MinesweeperDeductionTask):
        task.mines = 'poison';task.hidden = 'poison';task.target_is_mine = not task.target_is_mine
        for cell in set(task.number)-task.revealed:task.number[cell] = 999
    else:
        task.solution = 'poison';task.answer = 'poison'
        # Every domain value must appear in the published condition, not only in metadata.
        assert all(v in task.description for items in task.category_values.values() for v in items)
    rng = random.getstate()
    task.solve();assert task.final_answer == expected
    assert random.getstate() == rng
    assert task.verify(expected) == task.verify('<answer>'+expected+'</answer>') == 1
    before = json.dumps(task.get_result(),sort_keys=True,allow_nan=False)
    task.solve();assert json.dumps(task.get_result(),sort_keys=True,allow_nan=False) == before


def test_mine_ambiguity_inconsistency_cache_and_generator_failure():
    task = MinesweeperDeductionTask(difficulty=1);task.solve()
    expected = task.final_answer
    task.target_is_mine = not task.target_is_mine
    assert task.verify(expected) == 1
    task.n = 2;task.revealed = set();task.number = {};task.target = (0,0)
    with pytest.raises(ValueError,match='ambiguous_target'):task.solve()
    assert task.verify('mine') == task.verify('safe') == 0
    task.revealed = {(0,1),(1,0)};task.number = {(0,1):0,(1,0):3}
    with pytest.raises(ValueError,match='inconsistent_clues'):task.solve()
    with patch('re_rl.tasks.math.logic.deduction_search.mine_status',return_value=[0,1]):
        with pytest.raises(ValueError,match='generation_failed'):MinesweeperDeductionTask(difficulty=1)


def test_zebra_neighbor_schema_and_semantic_table_check():
    random.seed(8);task = ZebraPuzzleTask(difficulty=10)
    for _ in range(100):
        clue = task._create_clue('neighbor',PROMPT_TEMPLATES['zebra_puzzle']['clue_templates'])
        assert zebra_valid(task.num_houses,task.category_values,[clue],task.solution)
    task.solve();answer = task.answer;original = task.final_answer
    original_model = {c:list(v) for c,v in task.solution.items()}
    rejected = False
    for cat in task.categories:
        bad = {c:list(v) for c,v in original_model.items()}
        bad[cat][0],bad[cat][1] = bad[cat][1],bad[cat][0]
        if not zebra_valid(task.num_houses,task.category_values,task.clues,bad):
            task.solution = bad
            wrong_table = PROMPT_TEMPLATES['zebra_puzzle']['final_answer'][task.language].format(answer=answer,table=task._format_solution_table())
            assert task.verify(wrong_table) == 0
            rejected = True
            break
    assert rejected
    task.answer = 'poison';task.solution = 'poison'
    assert task.verify(answer) == task.verify(original) == 1
    assert task.verify(original+' garbage') == 0
    lines = original.splitlines();lines[-1] = lines[-2]
    assert task.verify('\n'.join(lines)) == 0
    task.clues = []
    with pytest.raises(ValueError,match='ambiguous_answer'):task.solve()
    assert task.verify(answer) == 0


def test_zebra_explicit_parameters_are_not_silently_replaced():
    task = ZebraPuzzleTask(num_houses=2,num_categories=2,num_clues=0)
    assert task.num_clues == 0
    task.solve();assert task.verify(task.final_answer) == 1
    assert len(task.clues) > 0  # Public distinguishing clues are added to guarantee the query.
    for kwargs in ({'num_houses':0},{'num_categories':6},{'num_clues':-1}):
        with pytest.raises(ValueError):ZebraPuzzleTask(**kwargs)


def test_mine_explicit_controls_and_invalid_parameters():
    for kwargs in (dict(n=2,num_mines=0,extra_hidden=1),dict(n=2,num_mines=3,extra_hidden=0),dict(n=8,num_mines=1,extra_hidden=0)):
        task = MinesweeperDeductionTask(**kwargs);task.solve()
        assert (task.n,task.num_mines,task.extra_hidden) == (kwargs['n'],kwargs['num_mines'],kwargs['extra_hidden'])
        assert task.verify(task.final_answer) == 1
    for kwargs in (dict(n=1),dict(n=2,num_mines=4),dict(num_mines=-1),dict(n=2,num_mines=0,extra_hidden=0),dict(extra_hidden=15)):
        with pytest.raises(ValueError):MinesweeperDeductionTask(**kwargs)


def test_invalid_positional_clue_metadata_rejected():
    values = {'people':['A','B','C'],'pets':['cat','dog','fox']}
    for clue in (dict(type='first',data=('people','A',2)),dict(type='middle',data=('people','A',0))):
        with pytest.raises(ValueError,match='invalid_position'):zebra_model(3,values,[clue])


def test_three_by_three_mine_geometry_against_king_move_worlds():
    cells = [(r,c) for r in range(3) for c in range(3)]
    adjacency = {cell:{(cell[0]+dr,cell[1]+dc) for dr in (-1,0,1) for dc in (-1,0,1)
                       if (dr,dc) != (0,0) and (cell[0]+dr,cell[1]+dc) in cells} for cell in cells}
    random.seed(24)
    for _ in range(80):
        planted = set(random.sample(cells,random.randrange(4)))
        safe = [c for c in cells if c not in planted]
        revealed = random.sample(safe,random.randrange(len(safe)))
        clues = {cell:len(adjacency[cell]&planted) for cell in revealed}
        hidden = [c for c in cells if c not in clues]
        worlds = []
        for bits in product((0,1),repeat=len(hidden)):
            mines = {c for c,bit in zip(hidden,bits) if bit}
            if all(len(adjacency[cell]&mines) == value for cell,value in clues.items()):worlds.append(mines)
        target = random.choice(hidden)
        assert mine_status(3,clues,target) == sorted({int(target in m) for m in worlds})


def test_mine_grader_handles_negation_and_rejects_conflicting_labels():
    mine = MinesweeperDeductionTask(n=2,num_mines=3,extra_hidden=0);mine.solve()
    safe = MinesweeperDeductionTask(n=2,num_mines=0,extra_hidden=1);safe.solve()
    for answer in ('not mine','not a mine'):
        assert mine.verify(answer) == 0 and safe.verify(answer) == 1
    for task in (mine,safe):
        assert task.verify('mine safe') == task.verify('not safe mine') == task.verify('garbage mine') == 0


def test_visual_mine_parameters_render_and_certificate():
    task = MinesweeperVisualTask.generate_random_task(n=2,num_mines=0,extra_hidden=1)
    assert task.n == 2 and not task.target_is_mine
    image = task.render_image()
    assert image.size == (2*task.CELL+1,2*task.CELL+1)
    assert task.verify('not a mine') == 1
    assert task.computation_inputs['n'] == 2
