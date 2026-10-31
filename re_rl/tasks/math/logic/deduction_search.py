"""Counterexample certificates for public mine and house constraints."""
from itertools import product
from .csp_search_traces import finite_csp


class DiscardEvents:
    def append(self,event):
        pass


def mine_status(n,clues,target,events=None):
    if events is None:events = DiscardEvents()
    cells = [(r,c) for r in range(n) for c in range(n)]
    if n < 1 or target not in cells or target in clues or any(cell not in cells or type(v) is not int or not 0 <= v <= 8 for cell,v in clues.items()):
        raise ValueError('invalid_mine_board')
    hidden = [cell for cell in cells if cell not in clues]
    indices = {cell:i for i,cell in enumerate(hidden)}
    events.append(dict(operation="deduce_mine_variables",cells=[list(cell) for cell in hidden]))
    tables = []
    for (r,c),value in sorted(clues.items()):
        neighbors = [indices[s,t] for s,t in hidden if max(abs(s-r),abs(t-c)) == 1]
        allowed = tuple(bits for bits in product((0,1),repeat=len(neighbors)) if sum(bits) == value)
        tables.append((neighbors,allowed))
    possible = []
    for value in (0,1):
        events.append(dict(operation='deduce_mine_assume',target=list(target),value=value))
        domains = [{0,1} for _ in hidden];domains[indices[target]] = {value}
        result = finite_csp(domains,tables,[],events)
        if result is not None:possible.append(value)
        events.append(dict(operation='deduce_mine_witness',value=value,exists=result is not None,
                           mines=[] if result is None else [list(cell) for cell,bit in zip(hidden,result) if bit]))
    events.append(dict(operation='deduce_mine_status',target=list(target),possible=possible))
    return possible


def zebra_model(n,values,clues,events=None,forbidden=None):
    if events is None:events = DiscardEvents()
    keys = [(cat,value) for cat,items in values.items() for value in items]
    if n < 1 or any(len(items) != n or len(set(items)) != n for items in values.values()):
        raise ValueError('invalid_categories')
    indices = {key:i for i,key in enumerate(keys)}
    events.append(dict(operation="deduce_zebra_variables",keys=[list(key) for key in keys]))
    domains = [set(range(n)) for _ in keys]
    groups = [[indices[cat,value] for value in items] for cat,items in values.items()]
    tables = []
    for clue in clues:
        kind,data = clue['type'],clue['data']
        if kind in ('position','first','middle'):
            cat,value,position = data
            if type(position) is not int or position not in range(n):raise ValueError('invalid_position')
            if kind == 'first' and position != 0:raise ValueError('invalid_position')
            if kind == 'middle' and (n % 2 == 0 or position != n//2):raise ValueError('invalid_position')
            domains[indices[cat,value]] &= {position}
        else:
            cat,a,other,b = data
            left,right = indices[cat,a],indices[other,b]
            if kind == 'same_house':allowed = tuple((i,i) for i in range(n))
            elif kind == 'neighbor':allowed = tuple((i,j) for i in range(n) for j in range(n) if abs(i-j) == 1)
            elif kind == 'left_of':allowed = tuple((i,j) for i in range(n) for j in range(n) if i < j)
            elif kind == 'not_neighbor':allowed = tuple((i,j) for i in range(n) for j in range(n) if abs(i-j) != 1)
            else:raise ValueError('invalid_clue')
            tables.append(((left,right),allowed))
    if forbidden:
        query,answer = forbidden
        if query[0] == 'position':domains[indices[query[1],query[2]]] -= {answer}
        else:
            a = indices[query[1],query[2]];b = indices[query[3],answer]
            tables.append(((a,b),tuple((i,j) for i in range(n) for j in range(n) if i != j)))
    result = finite_csp(domains,tables,groups,events)
    if result is None:return None
    model = {cat:[None]*n for cat in values}
    for (cat,value),position in zip(keys,result):model[cat][position] = value
    return model


def query_answer(model,query):
    position = model[query[1]].index(query[2])
    return position if query[0] == 'position' else model[query[3]][position]


def zebra_answer(n,values,clues,query,events):
    model = zebra_model(n,values,clues,events)
    if model is None:raise ValueError('inconsistent_clues')
    answer = query_answer(model,query)
    events.append(dict(operation='deduce_zebra_candidate',query=list(query),answer=answer))
    alternative = zebra_model(n,values,clues,events,forbidden=(query,answer))
    events.append(dict(operation='deduce_zebra_unique',answer=answer,unique=alternative is None))
    if alternative is not None:raise ValueError('ambiguous_answer')
    return model,answer


def zebra_valid(n,values,clues,model):
    if set(model) != set(values) or any(len(model[c]) != n or sorted(model[c]) != sorted(values[c]) for c in values):return False
    positions = {(c,v):i for c,items in model.items() for i,v in enumerate(items)}
    for clue in clues:
        kind,data = clue['type'],clue['data']
        if kind not in ('position','first','middle','same_house','neighbor','left_of','not_neighbor'):return False
        if kind == 'first' and data[2] != 0:return False
        if kind == 'middle' and (n % 2 == 0 or data[2] != n//2):return False
        if kind in ('position','first','middle'):
            if positions[data[0],data[1]] != data[2]:return False
        else:
            a,b = positions[data[0],data[1]],positions[data[2],data[3]]
            if kind == 'same_house' and a != b:return False
            if kind == 'neighbor' and abs(a-b) != 1:return False
            if kind == 'left_of' and a >= b:return False
            if kind == 'not_neighbor' and abs(a-b) == 1:return False
    return True
