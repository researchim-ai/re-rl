"""Deterministic scheduling from public queues, preserving every request."""


def integer(value, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError('invalid_queue_value')
    return value


def schedule(kind, inputs, events):
    order, total = [], 0
    if kind in ('sjf_wait', 'fcfs_wait'):
        if kind == 'sjf_wait':
            jobs = [(0, integer(b, 1)) for b in inputs['bursts']]
            indices = sorted(range(len(jobs)), key=lambda i: (jobs[i][1], i))
        else:
            jobs = []
            for job in inputs['jobs']:
                if len(job) != 2:
                    raise ValueError('invalid_job')
                jobs.append((integer(job[0]), integer(job[1], 1)))
            indices = sorted(range(len(jobs)), key=lambda i: (jobs[i][0], i))
        events.append(dict(operation='schedule_order', kind=kind,
                           keys=[[i+1, jobs[i][1] if kind == 'sjf_wait' else jobs[i][0]]
                                 for i in indices], order=[i+1 for i in indices]))
        clock = 0
        for i in indices:
            arrival, burst = jobs[i]
            start = max(clock, arrival)
            wait = start - arrival
            total += wait
            events.append(dict(operation='schedule_job', job=i+1, arrival=arrival,
                               burst=burst, clock=clock, idle=start-clock,
                               start=start, finish=start+burst, wait=wait, total=total))
            clock = start + burst
            order.append(i+1)
    elif kind == 'sstf_seek':
        position = integer(inputs['start'])
        pending = [(i+1, integer(c)) for i, c in enumerate(inputs['reqs'])]
        while pending:
            candidates = [[i, c, abs(c-position)] for i, c in pending]
            chosen = min(pending, key=lambda item: (abs(item[1]-position), item[1], item[0]))
            request, target = chosen
            distance = abs(target-position)
            total += distance
            events.append(dict(operation='schedule_seek', position=position,
                               candidates=candidates, request=request, target=target,
                               distance=distance, total=total))
            pending.remove(chosen)
            order.append(target)
            position = target
    else:
        raise ValueError('invalid_task_type')
    events.append(dict(operation='schedule_result', order=order[:], total=total))
    return order, total
