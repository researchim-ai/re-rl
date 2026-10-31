"""Finite, explicitly declared analogy hypotheses; reject ambiguous predictions."""


def infer(examples,query,coefficient_bound,offset_bound,max_power,events=None):
    predictions = set();fits = []
    for power in range(1,max_power+1):
        for a in range(-coefficient_bound,coefficient_bound+1):
            if a == 0:continue
            for b in range(-offset_bound,offset_bound+1):
                calculated = [a*x**power+b for x,y in examples]
                expected = [y for x,y in examples]
                consistent = calculated == expected
                prediction = a*query**power+b if consistent else None
                if events is not None:events.append(dict(operation='analogy_candidate',a=a,b=b,power=power,
                    calculated=calculated,expected=expected,consistent=consistent,prediction=prediction))
                if consistent:
                    fits.append((a,b,power));predictions.add(prediction)
    if events is not None:events.append(dict(operation='analogy_predictions',fits=[list(f) for f in fits],predictions=sorted(predictions)))
    if not predictions:raise ValueError('inconsistent_examples')
    if len(predictions) != 1:raise ValueError('ambiguous_prediction')
    return next(iter(predictions))
