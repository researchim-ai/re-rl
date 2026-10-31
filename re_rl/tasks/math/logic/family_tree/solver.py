"""Blood and spouse relation witnesses using only published family facts."""
import json


def fingerprint(task):
    return json.dumps([task.gender,task.couples,task.child_groups,task.a,task.b],sort_keys=True)


def relationship(gender,couples,groups,a,b,events):
    if a not in gender or b not in gender or a == b or any(g not in ('m','f') for g in gender.values()):
        raise ValueError('invalid_people')
    parents = {p:set() for p in gender};spouses = {}
    for x,y in couples:
        if x not in gender or y not in gender or x == y or (x in spouses and spouses[x] != y) or (y in spouses and spouses[y] != x):
            raise ValueError('invalid_couples')
        spouses[x] = y;spouses[y] = x
        events.append(dict(operation='kin_spouse',a=x,b=y))
    for x,y,kids in groups:
        if x not in gender or y not in gender or x == y:raise ValueError('invalid_parents')
        for child in kids:
            if child not in gender or child in (x,y):raise ValueError('invalid_parents')
            parents[child].update((x,y))
            if len(parents[child]) > 2:raise ValueError('invalid_parents')
    for child in sorted(parents):
        for parent in sorted(parents[child]):events.append(dict(operation='kin_parent',parent=parent,child=child))
    active = set();done = set()
    def visit(person):
        if person in active:raise ValueError('ancestry_cycle')
        if person in done:return
        active.add(person)
        for parent in sorted(parents[person]):visit(parent)
        active.remove(person);done.add(person)
    for person in sorted(gender):visit(person)
    witnesses = {}
    def add(male,female,path,kinds):
        role = male if gender[a] == 'm' else female
        witnesses.setdefault(role,(path,kinds))
    if a in parents[b]:add('father','mother',[a,b],['parent'])
    if b in parents[a]:add('son','daughter',[a,b],['child'])
    if spouses.get(a) == b:add('husband','wife',[a,b],['spouse'])
    for p in sorted(parents[b]):
        if a in parents[p]:add('grandfather','grandmother',[a,p,b],['parent','parent'])
    for p in sorted(parents[a]):
        if b in parents[p]:add('grandson','granddaughter',[a,p,b],['child','child'])
    for p in sorted(parents[a]&parents[b]):add('brother','sister',[a,p,b],['child','parent'])
    for p in sorted(parents[b]):
        if p != a:
            for grand in sorted(parents[a]&parents[p]):add('uncle','aunt',[a,grand,p,b],['child','parent','parent'])
    for p in sorted(parents[a]):
        if p != b:
            for grand in sorted(parents[b]&parents[p]):add('nephew','niece',[a,p,grand,b],['child','child','parent'])
    for pa in sorted(parents[a]):
        for pb in sorted(parents[b]):
            if pa == pb:continue
            for grand in sorted(parents[pa]&parents[pb]):add('cousin_m','cousin_f',[a,pa,grand,pb,b],['child','child','parent','parent'])
    for role,(path,kinds) in witnesses.items():
        events.append(dict(operation='kin_witness',role=role,path=path,kinds=kinds))
    if len(witnesses) != 1:raise ValueError('ambiguous_relation' if witnesses else 'undefined_relation')
    return next(iter(witnesses))
