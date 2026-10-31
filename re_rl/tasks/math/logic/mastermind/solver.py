"""Prefix search with sound exact-match/multiset bounds; no hidden-code input."""
from collections import Counter


def feedback(guess,code):
    exact=sum(a==b for a,b in zip(guess,code))
    common=sum((Counter(guess)&Counter(code)).values())
    return exact,common-exact


def validate_clues(length,colors,clues):
    if type(length) is not int or not 1 <= length <= 8:
        raise ValueError('invalid_length')
    if type(colors) is not int or not 1 <= colors <= 10 or colors**length>32768:
        raise ValueError('invalid_alphabet_or_search_space')
    if len(clues)>128:raise ValueError('too_many_clues')
    for clue in clues:
        if not isinstance(clue,(list,tuple)) or len(clue)!=2:raise ValueError('invalid_clue')
        guess,result=clue
        if len(guess)!=length or any(type(d) is not int or not 1 <= d <= colors for d in guess):
            raise ValueError('invalid_guess')
        if len(result)!=2 or any(type(v) is not int or v<0 for v in result) or sum(result)>length:
            raise ValueError('invalid_feedback')


def deduce(length,colors,clues,events):
    validate_clues(length,colors,clues)
    histograms=[Counter(guess) for guess,_ in clues]
    solutions=[]
    def search(prefix):
        depth=len(prefix);remaining=length-depth;counts=Counter(prefix)
        for index,((guess,(wanted_exact,wanted_partial)),histogram) in enumerate(zip(clues,histograms)):
            exact=sum(d==guess[i] for i,d in enumerate(prefix))
            common=sum(min(counts[d],histogram[d]) for d in counts)
            missing=sum(max(count-counts[d],0) for d,count in histogram.items())
            upper_common=common+min(remaining,missing)
            valid=(exact<=wanted_exact<=exact+remaining
                   and common<=wanted_exact+wanted_partial<=upper_common)
            events.append(dict(operation='code_bound',prefix=list(prefix),clue=index+1,
                               exact_min=exact,exact_max=exact+remaining,common_min=common,
                               common_max=upper_common,wanted_exact=wanted_exact,
                               wanted_common=wanted_exact+wanted_partial,valid=valid))
            if not valid:
                events.append(dict(operation='code_prune',prefix=list(prefix),clue=index+1))
                return False
        if depth==length:
            solutions.append(prefix)
            events.append(dict(operation='code_solution',code=list(prefix),count=len(solutions)))
            return len(solutions)>=2
        for digit in range(1,colors+1):
            events.append(dict(operation='code_branch',prefix=list(prefix),digit=digit))
            if search(prefix+(digit,)):return True
        events.append(dict(operation='code_exhausted',prefix=list(prefix)))
        return False
    stopped=search(())
    events.append(dict(operation='code_result',count=len(solutions),complete=not stopped,
                       solutions=[list(code) for code in solutions]))
    if not solutions:raise ValueError('inconsistent_clues')
    if len(solutions)>1:raise ValueError('ambiguous_clues')
    return solutions[0]
