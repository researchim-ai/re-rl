"""Independent subset/permutation optima and complete heuristic/trace replay."""
import itertools
import json
import random
import pytest
from re_rl.tasks.math.discrete.combinatorial_optimization.task import CombinatorialOptimizationTask as Task
from re_rl.tasks.math.discrete.combinatorial_optimization.solver import knapsack,set_cover,tsp


def subsets(n):
    return [list(indices) for size in range(n+1) for indices in itertools.combinations(range(n),size)]


def test_knapsack_against_all_small_subsets_and_dp_replay():
    for items in itertools.product(((1,0),(1,1),(2,1),(2,3)),repeat=3):
        for capacity in range(7):
            feasible=[indices for indices in subsets(3) if sum(items[i][0] for i in indices)<=capacity]
            expected=max(sum(items[i][1] for i in indices) for indices in feasible)
            events=[];value,chosen=knapsack(items,capacity,'exact',events)
            assert value==expected and chosen in feasible
            assert sum(items[i][1] for i in chosen)==value
            for e in events:
                if e['operation']=='opt_knapsack_cell':
                    prefix=items[:e['item']+1]
                    oracle=max(sum(prefix[i][1] for i in indices) for indices in subsets(len(prefix)) if sum(prefix[i][0] for i in indices)<=e['capacity'])
                    assert e['best']==oracle
    # Empty and zero-capacity instances have legitimate value zero.
    assert knapsack([],0,'exact')==(0,[])


def greedy_cover(universe,sets):
    covered=set();chosen=[]
    while covered!=universe:
        index=sorted(range(len(sets)),key=lambda i:(-len(set(sets[i])-covered),i))[0]
        assert set(sets[index])-covered
        chosen.append(index);covered.update(sets[index])
    return len(chosen),chosen


def test_all_three_set_covers_and_greedy():
    universe={1,2,3};choices=[set(indices) for indices in subsets(3)]
    # Convert 0-based subset members to the public 1-based universe labels.
    choices=[{i+1 for i in s} for s in choices]
    for sets in itertools.product(choices,repeat=3):
        feasible=[indices for indices in subsets(3) if set().union(*(sets[i] for i in indices))==universe]
        if not feasible:
            for mode in ('exact','approx'):
                with pytest.raises(ValueError,match='uncovered_universe'):set_cover(universe,sets,mode)
            continue
        events=[];size,chosen=set_cover(universe,sets,'exact',events)
        assert size==min(map(len,feasible)) and chosen in feasible
        assert set_cover(universe,sets,'approx')==greedy_cover(universe,sets)
        distances={0:0}
        for e in events:
            if e['operation']=='opt_cover_edge':
                assert e['target']==e['state']|e['mask']
                assert e['candidate']==distances[e['state']]+1
                assert e['previous']==distances.get(e['target'])
                if e['updated']:distances[e['target']]=e['candidate']
    assert set_cover(set(),[],'exact')==(0,[])


def tour_length(matrix,route):return sum(matrix[a][b] for a,b in zip(route,route[1:]))


def brute_tsp(matrix):
    return min((tour_length(matrix,[0,*p,0]),[0,*p,0]) for p in itertools.permutations(range(1,len(matrix))))


def heuristic_tsp(matrix):
    remaining=list(range(1,len(matrix)));route=[0]
    while remaining:
        best=sorted(remaining,key=lambda i:(matrix[route[-1]][i],i))[0]
        remaining.remove(best);route.append(best)
    route.append(0)
    for i in range(1,len(matrix)-1):
        for j in range(i+1,len(matrix)):
            candidate=route[:i]+list(reversed(route[i:j+1]))+route[j+1:]
            if tour_length(matrix,candidate)<tour_length(matrix,route):route=candidate
    return tour_length(matrix,route),route


def matrix_from_weights(n,weights):
    matrix=[[0]*n for _ in range(n)]
    for (i,j),w in zip(itertools.combinations(range(n),2),weights):matrix[i][j]=matrix[j][i]=w
    return matrix


def test_all_binary_weighted_four_city_tours_and_held_karp_candidates():
    for weights in itertools.product((1,3),repeat=6):
        matrix=matrix_from_weights(4,weights);events=[]
        cost,route=tsp(matrix,'exact',events)
        assert cost==brute_tsp(matrix)[0] and tour_length(matrix,route)==cost
        assert set(route[:-1])==set(range(4))
        assert tsp(matrix,'approx')==heuristic_tsp(matrix)
        for e in events:
            if e['operation']=='opt_tsp_cell':
                vertices=[i for i in range(1,4) if e['mask']&(1<<(i-1))]
                others=[i for i in vertices if i!=e['end']]
                expected=min(tour_length(matrix,[0,*p,e['end']]) for p in itertools.permutations(others))
                assert e['cost']==expected
                assert all(total==prefix+edge for _,prefix,edge,total in e['candidates'])
    for mode in ('exact','approx'):
        assert tsp([[0]],mode)==(0,[0,0])
        assert tsp([[0,3],[3,0]],mode)[0]==6


def test_two_opt_includes_closing_edge_and_replays_real_delta():
    rng=random.Random(91);accepted_closing=False
    for _ in range(30):
        matrix=matrix_from_weights(6,[rng.randrange(1,30) for _ in range(15)])
        events=[];actual=tsp(matrix,'approx',events)
        assert actual==heuristic_tsp(matrix)
        previous=None
        for e in events:
            if e['operation']=='opt_tsp_swap':
                a,b,c,d=e['edges']
                assert e['delta']==matrix[a][c]+matrix[b][d]-matrix[a][b]-matrix[c][d]
                assert e['accepted']==(e['delta']<0)
                if previous is not None:assert tour_length(matrix,e['route'])==previous+min(0,e['delta'])
                previous=tour_length(matrix,e['route'])
                if e['accepted'] and e['j']==5:accepted_closing=True
    assert accepted_closing


def test_approximate_tour_grader_accepts_every_better_feasible_route():
    task=Task(task_type='tsp_small',solve_mode='approx')
    rng=random.Random(32)
    for _ in range(5):
        task.matrix=matrix_from_weights(5,[rng.randrange(1,30) for _ in range(10)])
        baseline=heuristic_tsp(task.matrix)[0]
        for permutation in itertools.permutations(range(1,5)):
            route=[0,*permutation,0];cost=tour_length(task.matrix,route)
            assert task.verify(f'distance={cost};route={route}')==float(cost<=baseline)
    events=[]
    assert knapsack([(2,3),(4,6)],4,'approx',events)==(3,[0])
    assert events[0]['order']==[0,1]  # Exact equal densities use the smaller index.


@pytest.mark.parametrize('kind',Task.TASK_TYPES)
@pytest.mark.parametrize('mode',['exact','approx'])
@pytest.mark.parametrize('language',['ru','en'])
def test_all_difficulties_stable_and_published_parameters(kind,mode,language):
    for level in range(1,11):
        random.seed(level)
        task=Task(task_type=kind,solve_mode=mode,language=language,difficulty=level)
        description=task.description;state=random.getstate();task.solve()
        assert task.description==description and random.getstate()==state
        saved=json.dumps(task.get_result(),sort_keys=True)
        task.final_answer='stale';task.answer=-999;task.solve()
        assert json.dumps(task.get_result(),sort_keys=True)==saved
        assert task.verify(task.final_answer)==1
        assert task.verify('junk '+task.final_answer)==0
        assert len(task.solution_steps)==len(task.algorithm_trace)+1
        if kind=='set_cover':assert set().union(*task.sets)==task.universe
        if kind=='tsp_small':assert len(task.matrix)==task.n


def test_semantic_grader_ties_better_heuristics_and_bad_certificates():
    task=Task(task_type='knapsack',solve_mode='exact')
    task.items=[(2,3),(2,3)];task.capacity=2
    for chosen in ([0],[1]):assert task.verify(f'value=3;items={chosen}')==1
    for text in ('value=3;items=[0,0]','value=3;items=[-1]','value=3;items=[True]','value=3;items=[0] junk','value=0;items=[]','value=9;items=[0]'):
        assert task.verify(text)==0
    task.solve_mode='approx';task.items=[(10,60),(20,100),(30,120)];task.capacity=50
    assert task.verify('value=160;items=[0,1]')==1
    assert task.verify('value=220;items=[1,2]')==1
    assert task.verify('value=60;items=[0]')==0
    task=Task(task_type='set_cover',solve_mode='approx')
    task.universe=set(range(1,7));task.sets=[{1,2,3,4},{1,2,5},{3,4,6}]
    assert task.verify('size=3;sets=[0,1,2]')==1
    assert task.verify('size=2;sets=[1,2]')==1
    assert task.verify('size=1;sets=[0]')==0
    assert task.verify('size=2;sets=[1,1]')==0
    task.solve_mode='exact';assert task.verify('size=3;sets=[0,1,2]')==0
    task=Task(task_type='tsp_small',solve_mode='exact')
    task.matrix=[[0 if i==j else 1 for j in range(4)] for i in range(4)]
    assert task.verify('distance=4;route=[0,1,2,3,0]')==1
    assert task.verify('distance=4;route=[0,3,2,1,0]')==1
    for text in ('distance=4;route=[0,1,2,0]','distance=4;route=[0,1,2,2,0]','distance=3;route=[0,1,2,3,0]'):
        assert task.verify(text)==0


@pytest.mark.parametrize('kind',Task.TASK_TYPES)
@pytest.mark.parametrize('mode',['exact','approx'])
def test_one_element_instances(kind,mode):
    task=Task.generate_random_task(task_type=kind,solve_mode=mode,n=1)
    assert task.verify(task.final_answer)==1
    if kind=='set_cover':assert task.sets==[{1}]
    if kind=='tsp_small':assert task.final_answer=='distance=0;route=[0, 0]'


@pytest.mark.parametrize('kwargs',[dict(task_type='bad'),dict(solve_mode='bad'),dict(n=0),dict(n=True),dict(n=1.5),dict(n=101),dict(task_type='tsp_small',solve_mode='exact',n=13),dict(task_type='set_cover',solve_mode='exact',n=13)])
def test_invalid_parameters(kwargs):
    with pytest.raises(ValueError):Task(**kwargs)


def test_resource_bounds_rejected_without_silent_shrink():
    task=Task(task_type='tsp_small',solve_mode='approx',n=30)
    assert len(task.matrix)==30
    task.solve()
    assert task.verify(task.final_answer)==1
    assert len(task.algorithm_trace[-1]["chosen"])==31
    with pytest.raises(ValueError):tsp(task.matrix,'exact')
    with pytest.raises(ValueError):tsp([[0,1],[2,0]],'approx')
    with pytest.raises(ValueError):knapsack([(0,2)],2,'exact')
    with pytest.raises(ValueError):knapsack([(1,2)],5001,'exact')
    with pytest.raises(ValueError,match='uncovered_universe'):set_cover({1,2},[{1}],'exact')
