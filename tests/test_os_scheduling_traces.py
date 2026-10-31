"""Queue simulation oracles and trace replay, including duplicates and idle periods."""
import itertools
import json
import random

import pytest

from re_rl.tasks.math.logic.os_scheduling.task import OSSchedulingTask
from re_rl.tasks.math.logic.os_scheduling.solver import schedule


def clock_oracle(jobs, sjf=False):
    pending = set(range(len(jobs)))
    clock = 0
    order, waits = [], 0
    # Simulate one time unit at a time, independently of the closed-form solver.
    while pending:
        ready = [i for i in pending if jobs[i][0] <= clock]
        if not ready:
            clock += 1
            continue
        chosen = min(ready, key=lambda i: (jobs[i][1], i) if sjf else (jobs[i][0], i))
        waits += clock-jobs[chosen][0]
        order.append(chosen+1)
        for _ in range(jobs[chosen][1]):
            clock += 1
        pending.remove(chosen)
    return order, waits


def test_small_job_queues_against_time_simulator():
    for bursts in itertools.product(range(1,4), repeat=4):
        assert schedule('sjf_wait',dict(bursts=bursts),[]) == clock_oracle([(0,b) for b in bursts],True)
    choices=list(itertools.product(range(3),range(1,4)))
    for jobs in itertools.product(choices,repeat=3):
        assert schedule('fcfs_wait',dict(jobs=jobs),[]) == clock_oracle(jobs)
    events=[]
    assert schedule('fcfs_wait',dict(jobs=[(3,2),(10,1),(10,2)]),events)==([1,2,3],1)
    assert [e['idle'] for e in events if e['operation']=='schedule_job']==[3,5,0]


def seek_oracle(start, requests):
    requests=list(enumerate(requests))
    order=[];total=0
    while requests:
        # Move a distance frontier outward; lower cylinder wins a distance tie.
        for distance in range(max([abs(c-start) for _,c in requests])+1):
            available=[(c,i) for i,c in requests if abs(c-start)==distance]
            if available:
                cylinder,index=sorted(available)[0]
                break
        total+=distance;order.append(cylinder)
        requests.remove((index,cylinder));start=cylinder
    return order,total


def test_sstf_exhaustive_with_duplicate_requests_and_ties():
    for start in range(4):
        for requests in itertools.product(range(4),repeat=4):
            assert schedule('sstf_seek',dict(start=start,reqs=requests),[])==seek_oracle(start,requests)
    events=[]
    assert schedule('sstf_seek',dict(start=5,reqs=[7,3,3,5]),events)==([5,3,3,7],6)
    moves=[e for e in events if e['operation']=='schedule_seek']
    assert [e['request'] for e in moves]==[4,2,3,1]
    assert [len(e['candidates']) for e in moves]==[4,3,2,1]


@pytest.mark.parametrize('kind',OSSchedulingTask.TASK_TYPES)
@pytest.mark.parametrize('language',['ru','en'])
def test_all_difficulties_recompute_cache_poison_replay(kind,language):
    for difficulty in range(1,11):
        random.seed(difficulty)
        task=OSSchedulingTask(task_type=kind,language=language,difficulty=difficulty)
        task.answer=-999;task.order=[];task.final_answer='bad'
        state=random.getstate();task.solve();assert random.getstate()==state
        trace=json.dumps(task.algorithm_trace,sort_keys=True)
        task.solve();assert json.dumps(task.algorithm_trace,sort_keys=True)==trace
        if kind=='sstf_seek':
            expected=seek_oracle(task.start,task.reqs)
            events=[e for e in task.algorithm_trace if e['operation']=='schedule_seek']
            position=task.start;total=0
            for event in events:
                assert event['position']==position
                winner=min(event['candidates'],key=lambda x:(x[2],x[1],x[0]))
                assert winner==[event['request'],event['target'],abs(event['target']-position)]
                total+=winner[2];assert total==event['total'];position=winner[1]
            assert len(events)==len(task.reqs)
        else:
            jobs=[(0,b) for b in task.bursts] if kind=='sjf_wait' else task.jobs
            expected=clock_oracle(jobs,kind=='sjf_wait')
            clock=0;total=0
            for event in task.algorithm_trace:
                if event['operation']!='schedule_job':continue
                arrival,burst=jobs[event['job']-1]
                assert event['start']==max(clock,arrival)
                assert event['wait']==event['start']-arrival
                assert event['finish']==event['start']+burst
                total+=event['wait'];assert event['total']==total;clock=event['finish']
        assert (task.order,task.answer)==expected
        assert task.verify(task.final_answer)==1
        assert task.verify('junk '+task.final_answer)==0
        assert task.verify(str(task.answer+1))==0
        assert task.get_result()['algorithm_trace']==task.algorithm_trace
        assert len(task.solution_steps)==len(task.algorithm_trace)+1


@pytest.mark.parametrize('kind',OSSchedulingTask.TASK_TYPES)
def test_parameters_and_public_mutation(kind):
    task=OSSchedulingTask.generate_random_task(task_type=kind,n=1,span=1)
    assert task.n==1 and task.span==1
    task=OSSchedulingTask.generate_random_task(task_type=kind,n=40,span=1_000_000)
    if kind=='sstf_seek':
        assert len(task.reqs)==40 and len(set(task.reqs))==40
        task.start=5;task.reqs=[7,3,3,5];expected=6
    elif kind=='sjf_wait':task.bursts=[5,1,1];expected=3
    else:task.jobs=[(3,2),(10,1),(10,2)];expected=1
    task.answer=999
    assert task.verify(str(expected))==1
    assert task.answer==expected


@pytest.mark.parametrize('kwargs',[dict(n=0),dict(n=True),dict(n=1.5),dict(n=501),dict(span=0),dict(span=True),dict(span=1_000_001),dict(task_type='bogus'),dict(task_type='sstf_seek',n=4,span=3)])
def test_invalid_parameters(kwargs):
    with pytest.raises(ValueError):OSSchedulingTask(**kwargs)


@pytest.mark.parametrize('kind,inputs',[
    ('sjf_wait',dict(bursts=[0])),('sjf_wait',dict(bursts=[True])),
    ('fcfs_wait',dict(jobs=[(-1,2)])),('fcfs_wait',dict(jobs=[(0,2,3)])),
    ('sstf_seek',dict(start=-1,reqs=[])),('sstf_seek',dict(start=0,reqs=[1.5]))])
def test_invalid_public_queues(kind,inputs):
    with pytest.raises(ValueError):schedule(kind,inputs,[])
