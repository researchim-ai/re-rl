"""Constraint and truth-model search from public puzzle descriptions."""
from itertools import product
from .csp_search_traces import finite_csp


def futoshiki(n,inequalities,events):
    domains = [set(range(1,n+1)) for _ in range(n*n)]
    allowed = tuple((a,b) for a in range(1,n+1) for b in range(a+1,n+1))
    tables = []
    for r,c,s,t in inequalities:
        if any(type(v) is not int or not 0 <= v < n for v in (r,c,s,t)):
            raise ValueError('invalid_inequality')
        if (r,c) == (s,t):
            events.append(dict(operation='puzzle_conflict',reason='self_inequality'))
            return None
        tables.append(((r*n+c,s*n+t),allowed))
    groups = [tuple(r*n+c for c in range(n)) for r in range(n)]
    groups += [tuple(r*n+c for r in range(n)) for c in range(n)]
    result = finite_csp(domains,tables,groups,events)
    return None if result is None else [result[r*n:(r+1)*n] for r in range(n)]


def cryptarithm(a,b,c,events):
    words = (a,b,c)
    if any(not w or not w.isascii() or not w.isalpha() or not w.isupper() for w in words) or len(set(a+b+c)) > 10:
        raise ValueError('invalid_words')
    leading = {w[0] for w in words}
    mapping = {};used = set();width = max(map(len,words))
    def assign(letter,continuation):
        if letter is None or letter in mapping:
            return continuation()
        candidates = [v for v in range(10) if v not in used and (v or letter not in leading)]
        events.append(dict(operation='puzzle_digit_domain',letter=letter,used=sorted(used),leading=letter in leading,candidates=candidates))
        for value in candidates:
            mapping[letter] = value;used.add(value)
            events.append(dict(operation='puzzle_digit_place',letter=letter,value=value))
            result = continuation()
            if result is not None:return result
            del mapping[letter];used.remove(value)
            events.append(dict(operation='puzzle_digit_remove',letter=letter,value=value))
        return None
    def column(index,carry):
        if index == width:
            if carry:
                events.append(dict(operation='puzzle_conflict',reason='remaining_carry'))
                return None
            result = dict(mapping)
            events.append(dict(operation='puzzle_mapping',mapping=result.copy()))
            return result
        letters = [w[-1-index] if index < len(w) else None for w in words]
        left,right,out = letters
        def add_column():
            x = mapping[left] if left else 0;y = mapping[right] if right else 0
            total = x+y+carry;next_carry,digit = divmod(total,10)
            valid = (digit == 0 if out is None else mapping[out] == digit if out in mapping
                     else digit not in used and (digit != 0 or out not in leading))
            events.append(dict(operation='puzzle_column',index=index,letters=letters,x=x,y=y,carry=carry,
                               total=total,digit=digit,next_carry=next_carry,valid=bool(valid)))
            if not valid:return None
            placed = out is not None and out not in mapping
            if placed:
                mapping[out] = digit;used.add(digit)
                events.append(dict(operation='puzzle_digit_place',letter=out,value=digit))
            result = column(index+1,next_carry)
            if placed and result is None:
                del mapping[out];used.remove(digit)
                events.append(dict(operation='puzzle_digit_remove',letter=out,value=digit))
            return result
        return assign(left,lambda:assign(right,add_column))
    return column(0,0)


def statement_value(statement,roles):
    form = statement['form_key'];s = statement['speaker'];y = statement['y'];z = statement.get('z')
    desired = statement.get('polarity',True)
    if form == 'about_self':return roles[s] == desired
    if form == 'about_other':return roles[y] == desired
    if form == 'and':return roles[y] == desired and roles[z] == desired
    if form == 'or':return roles[y] == desired or roles[z] == desired
    if form == 'same':return roles[y] == roles[z]
    if form == 'different':return roles[y] != roles[z]
    count = sum(role == desired for role in roles)
    if form == 'at_least_one':return count >= 1
    if form == 'exactly_one':return count == 1
    raise ValueError('invalid_statement')


def knight_models(n,statements,events):
    models = []
    for roles in product((False,True),repeat=n):
        valid = True
        for index,statement in enumerate(statements):
            truth = statement_value(statement,roles)
            consistent = roles[statement['speaker']] == truth
            valid = valid and consistent
            events.append(dict(operation='puzzle_statement',roles=list(roles),index=index,speaker=statement['speaker'],truth=truth,consistent=consistent))
        events.append(dict(operation='puzzle_model',roles=list(roles),valid=valid))
        if valid:models.append(roles)
    return models
