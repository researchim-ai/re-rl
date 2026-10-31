"""Independent permutation and SMT models for both public CSP contracts."""
import itertools
import json
import random
import pytest
from z3 import Int, Solver, Distinct, sat
from re_rl.tasks.math.logic.csp_reasoning.task import CSPReasoningTask
from re_rl.tasks.math.logic.csp_reasoning.solver import latin,mini_kakuro


def all_latin(n):
    rows=list(itertools.permutations(range(1,n+1)))
    return [grid for grid in itertools.product(rows,repeat=n)
            if all(len({grid[r][c] for r in range(n)})==n for c in range(n))]


def test_all_two_by_two_partial_grids():
    solutions=all_latin(2)
    for values in itertools.product(range(3),repeat=4):
        grid=[values[:2],values[2:]]
        expected=[s for s in solutions if all(not values[i] or s[i//2][i%2]==values[i] for i in range(4))]
        if not expected:
            with pytest.raises(ValueError,match='unsatisfiable'):latin(grid,[])
        else:
            assert tuple(map(tuple,latin(grid,[]))) in expected


def test_mini_kakuro_all_feasible_sum_vectors_against_exhaustive_assignments():
    by_sums={}
    for a,b,c,d in itertools.product(range(1,10),repeat=4):
        if a!=b and c!=d:
            by_sums.setdefault((a+b,c+d,a+c,b+d),set()).add((a,b,c,d))
    for sums,solutions in by_sums.items():
        assert tuple(mini_kakuro(dict(zip(('S1','S2','S3','S4'),sums)),[])) in solutions
    # Equality in a column is permitted: the statement only forbids equal row entries.
    assert mini_kakuro(dict(S1=3,S2=3,S3=2,S4=4),[])==[1,2,1,2]
    with pytest.raises(ValueError,match='unsatisfiable'):mini_kakuro(dict(S1=2,S2=2,S3=2,S4=2),[])


@pytest.mark.parametrize('kind',CSPReasoningTask.TASK_TYPES)
@pytest.mark.parametrize('language',['ru','en'])
def test_stable_all_levels_and_smt_model(kind,language):
    for level in range(1,11):
        random.seed(level)
        task=CSPReasoningTask(task_type=kind,language=language,difficulty=level)
        description=task.description;state=random.getstate()
        task.solve()
        assert task.description==description and random.getstate()==state
        result=json.dumps(task.get_result(),sort_keys=True)
        task._solution_grid=[[999]];task.final_answer='poison'
        task.solve();assert json.dumps(task.get_result(),sort_keys=True)==result
        assert task.verify(task.final_answer)==1
        assert task.verify('junk '+task.final_answer)==0
        assert task.verify('-'+task.final_answer)==0
        assert len(task.solution_steps)==len(task.algorithm_trace)+1
        solver=Solver()
        if kind=='latin_square':
            grid=[[int(x) for x in row.split(',')] for row in task.final_answer.split(';')]
            variables=[[Int(f'x{r}_{c}') for c in range(task.size)] for r in range(task.size)]
            for r in range(task.size):
                solver.add(Distinct(variables[r]))
                for c in range(task.size):
                    x=variables[r][c];solver.add(x>=1,x<=task.size,x==grid[r][c])
                    if task._puzzle_grid[r][c]:solver.add(x==task._puzzle_grid[r][c])
            for c in range(task.size):solver.add(Distinct([variables[r][c] for r in range(task.size)]))
        else:
            a,b,c,d=[Int(k) for k in 'ABCD']
            for v in (a,b,c,d):solver.add(v>=1,v<=9)
            sums=task._kakuro_sums
            solver.add(a!=b,c!=d,a+b==sums['S1'],c+d==sums['S2'],a+c==sums['S3'],b+d==sums['S4'])
            pairs=dict(p.split('=') for p in task.final_answer.split(','))
            for k,v in zip('ABCD',(a,b,c,d)):solver.add(v==int(pairs[k]))
        assert solver.check()==sat
        assert any(e['operation']=='csp_solution' for e in task.algorithm_trace)


def test_parameters_alternative_solutions_and_strict_grader():
    task=CSPReasoningTask(task_type='latin_square',size=3,clues=0)
    assert sum(bool(v) for row in task._puzzle_grid for v in row)==0
    for solution in all_latin(3):
        assert task.verify(';'.join(','.join(map(str,row)) for row in solution))==1
    assert task.verify('1,2,3;1,2,3;1,2,3')==0
    assert task.verify('1.2,2,3;2,3,1;3,1,2')==0
    task=CSPReasoningTask(task_type='latin_square',size=9,clues=81)
    task.solve();assert task.verify(task.final_answer)==1
    task=CSPReasoningTask(task_type='kakuro_mini')
    task._kakuro_sums=dict(S1=3,S2=3,S3=3,S4=3)
    assert task.verify('A=1,B=2,C=2,D=1')==1
    assert task.verify('A=2,B=1,C=1,D=2')==1
    for answer in ('A=-1,B=2,C=2,D=1','A=1,B=2,C=2,D=1,A=9','A=1,B=2,C=2,C=1','A=1,B=2,C=2,D=1 junk'):
        assert task.verify(answer)==0
    task._kakuro_sums=dict(S1=2,S2=2,S3=2,S4=2)
    with pytest.raises(ValueError,match='unsatisfiable'):task.solve()


@pytest.mark.parametrize('kwargs',[dict(size=1),dict(size=10),dict(size=True),dict(clues=-1),dict(clues=17),dict(clues=True),dict(task_type='bad'),dict(task_type='kakuro_mini',size=3),dict(task_type='kakuro_mini',clues=1)])
def test_invalid_parameters(kwargs):
    with pytest.raises(ValueError):CSPReasoningTask(**kwargs)
