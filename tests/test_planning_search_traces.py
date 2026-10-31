"""Independent finite-state planning oracles, transition replay and semantic grading."""
import itertools
from collections import deque
import json
import random
import pytest
from re_rl.tasks.math.planning.search_traces import water_jug,blocks_world,hanoi
from re_rl.tasks.math.planning.water_jug.task import WaterJugTask
from re_rl.tasks.math.planning.tower_of_hanoi.task import TowerOfHanoiTask
from re_rl.tasks.math.planning.blocks_world.task import BlocksWorldTask


def jug_edges(state,caps):
    result = set()
    for i in range(len(caps)):
        for value in (0,caps[i]):
            other = list(state);other[i] = value
            if tuple(other) != state: result.add(tuple(other))
        for j in range(len(caps)):
            if i == j: continue
            other = list(state)
            while other[i] and other[j] < caps[j]:
                other[i] -= 1;other[j] += 1
            if tuple(other) != state: result.add(tuple(other))
    return result


def distances(start,edges):
    queue = deque([start]);result = {start:0}
    while queue:
        state = queue.popleft()
        for other in edges(state):
            if other not in result:
                result[other] = result[state]+1;queue.append(other)
    return result


def test_all_small_jug_instances_and_replay():
    for n in range(1,4):
        for caps in itertools.product(range(1,5),repeat=n):
            oracle = distances((0,)*n,lambda s:jug_edges(s,caps))
            for target in range(max(caps)+2):
                expected = min((d for s,d in oracle.items() if target in s),default=None)
                events = [];path = water_jug(caps,target,events)
                assert (len(path)-1 if path else None) == expected
                for (a,_),(b,action) in zip(path,path[1:]):
                    assert b in jug_edges(a,caps)
                queue = deque([(0,)*n]);seen = {(0,)*n}
                for event in events:
                    if event['operation'] == 'plan_pop': assert tuple(event['state']) == queue.popleft()
                    if event['operation'] == 'plan_edge':
                        a,b = tuple(event['state']),tuple(event['neighbor'])
                        assert b in jug_edges(a,caps)
                        assert event['visited'] == (b in seen)
                        if not event['visited']:seen.add(b);queue.append(b)


def test_hanoi_moves_and_recursion_replay():
    for n in range(9):
        events = [];moves = hanoi(n,'start','finish','spare',events)
        assert len(moves) == 2**n-1
        pegs = {'start':list(range(n,0,-1)),'finish':[],'spare':[]}
        stack = []
        for e in events:
            if e['operation'] == 'plan_hanoi_call':
                assert e['depth'] == len(stack);stack.append(e['n'])
            elif e['operation'] == 'plan_hanoi_return':
                assert stack.pop() == e['n'];assert len(stack) == e['depth']
            else:
                assert e['before'] == pegs
                disk = pegs[e['source']].pop()
                assert disk == e['disk']
                assert not pegs[e['target']] or pegs[e['target']][-1] > disk
                pegs[e['target']].append(disk)
                assert e['after'] == pegs
        assert not stack and pegs['finish'] == list(range(n,0,-1))
        if n <= 4:
            # Encode each disk's peg; a legal move moves a peg's smallest disk.
            def edges(state):
                top = {p:next((i for i,v in enumerate(state) if v == p),n) for p in range(3)}
                for source,disk in top.items():
                    if disk == n: continue
                    for target in range(3):
                        if source != target and top[target] > disk:
                            other = list(state);other[disk] = target;yield tuple(other)
            assert distances((0,)*n,edges)[(1,)*n] == len(moves)


def test_all_three_block_configurations_against_graph_oracle():
    blocks = ['A','B','C'];states = []
    for supports in itertools.product(range(-1,3),repeat=3):
        non_table = [v for v in supports if v != -1]
        if len(set(non_table)) != len(non_table):continue
        valid = True
        for i in range(3):
            seen = set();j = i
            while j != -1:
                if j in seen:valid = False;break
                seen.add(j);j = supports[j]
        if valid:states.append(supports)
    def edges(state):
        for other in states:
            changed = [i for i in range(3) if state[i] != other[i]]
            if len(changed) == 1:
                block = changed[0];target = other[block]
                if block not in state and (target == -1 or target not in state):yield other
    def decoded(s):return {b:('table' if v == -1 else blocks[v]) for b,v in zip(blocks,s)}
    for initial in states:
        oracle = distances(initial,edges)
        for goal in states:
            events = [];path = blocks_world(blocks,decoded(initial),decoded(goal),events)
            assert len(path)-1 == oracle[goal]
            for (a,_),(b,action) in zip(path,path[1:]):assert b in set(edges(a))


@pytest.mark.parametrize('cls',[WaterJugTask,TowerOfHanoiTask,BlocksWorldTask])
@pytest.mark.parametrize('language',['ru','en'])
@pytest.mark.parametrize('level',range(1,11))
def test_all_levels_cache_poison_and_idempotence(cls,language,level):
    random.seed(level)
    task = cls(language=language,difficulty=level);task.solve()
    expected = task.final_answer
    for key in ('solution_path','moves','_plan','is_solvable'):
        if hasattr(task,key):setattr(task,key,'poison')
    task.solve();assert task.final_answer == expected
    assert task.verify(expected) == task.verify('<answer>'+expected+'</answer>') == 1
    before = json.dumps(task.get_result(),sort_keys=True,allow_nan=False)
    task.solve();assert json.dumps(task.get_result(),sort_keys=True,allow_nan=False) == before


def test_zero_targets_and_custom_pegs():
    for language in ('ru','en'):
        task = WaterJugTask(capacities=(5,),target=0,language=language);task.solve()
        assert task.target == 0 and len(task.solution_path) == 1
        assert task.verify('[]') == task.verify(task.final_answer) == 1
        for n in (0,1,4):
            task = TowerOfHanoiTask(num_disks=n,source='X',target='Y',auxiliary='Z',language=language);task.solve()
            assert 'X' in task.description and 'peg A.' not in task.description
            assert task.verify(json.dumps(task.moves)) == task.verify(task.final_answer) == 1


def test_semantic_graders_alternative_plans_and_garbage():
    task = WaterJugTask(capacities=(3,5),target=3);task.solve()
    assert task.verify('[["fill",1],["empty",1],["fill",0]]') == 1
    for text in ('3','[["fill",1]]','[["pour",0,1]]','[["fill",true]]',task.final_answer+' garbage'):
        assert task.verify(text) == 0
    task.solution_path = 'poison';task.final_answer = 'poison'
    assert task.verify('[["fill",0]]') == 1
    task = TowerOfHanoiTask(num_disks=2);task.solve()
    for text in ('3','[[2,"A","C"]]',json.dumps(task.moves[:-1]),task.final_answer+' garbage'):
        assert task.verify(text) == 0
    task.moves = [];task.final_answer = 'poison'
    assert task.verify('[[1,"A","B"],[2,"A","C"],[1,"B","C"]]') == 1
    task = BlocksWorldTask(num_blocks=2)
    task._init_state = {'A':'table','B':'table'};task._goal_state = {'A':'table','B':'A'};task.solve()
    assert task.verify('move B onto A') == 1
    for text in ('garbage; move B onto A','move B onto A; move A onto B','move B onto A rubbish','move B onto A; move Q onto table'):
        assert task.verify(text) == 0
    task._goal_state = dict(task._init_state);task.solve()
    assert task.verify(task.final_answer) == 1 and task.verify('garbage') == 0


@pytest.mark.parametrize('cls,kwargs',[(WaterJugTask,{'capacities':()}),(WaterJugTask,{'capacities':(0,3)}),
    (WaterJugTask,{'target':-1}),(TowerOfHanoiTask,{'num_disks':-1}),(TowerOfHanoiTask,{'num_disks':13}),
    (TowerOfHanoiTask,{'source':'C'}),(BlocksWorldTask,{'num_blocks':7}),(BlocksWorldTask,{'num_blocks':2.5})])
def test_invalid_parameters_rejected(cls,kwargs):
    with pytest.raises(ValueError):cls(**kwargs)


def test_hanoi_arbitrary_start_states_and_visual_cache():
    from re_rl.tasks.visual.hanoi_disk.task import hanoi_trace,HanoiDiskTask
    for n in range(1,6):
        def edges(state):
            top = {p:next((i for i,v in enumerate(state) if v == p),n) for p in (1,2,3)}
            for source,disk in top.items():
                if disk == n: continue
                for target in (1,2,3):
                    if source != target and top[target] > disk:
                        other = list(state);other[disk] = target;yield tuple(other)
        oracle = distances((3,)*n,edges)
        for state in itertools.product((1,2,3),repeat=n):
            assert hanoi_trace([0]+list(state))[1] == oracle[state]
    for level in range(1,11):
        for kind in ('moves','home'):
            task = HanoiDiskTask(task_type=kind,difficulty=level);task.solve()
            expected = task.final_answer
            task.trace = task.moves = task.home = task.answer = 'poison'
            task.solve();assert task.final_answer == expected
            assert task.verify(expected) == 1
            assert task.get_result()['computation_inputs']['pegs'] == task.pegs
    task = HanoiDiskTask(difficulty=10)
    task.pegs = [0]+[1]*task.n
    image = task.render_image()
    max_half = 16+task.n*12
    assert image.width == 56+2*max_half+2*(2*max_half+24)
    assert image.getpixel((28,image.height-14-18+8)) != (255,255,255)


def test_auditor_detects_cached_plan_formatters():
    from scripts.audit_task_traces import static_indicators
    for cls in (WaterJugTask,TowerOfHanoiTask,BlocksWorldTask):
        report = static_indicators(cls)
        assert report['rendered_cached_plan'] and report['candidate'] and report['delegated_execution']
