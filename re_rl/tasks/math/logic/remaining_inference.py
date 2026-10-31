"""Public-input inference, calendar arithmetic and visual counting algorithms."""
from itertools import combinations


def ordinal(year,month,day):
    previous_year = year-1
    leap_days = previous_year//4-previous_year//100+previous_year//400
    total = 365*previous_year+leap_days
    leap = year%4 == 0 and (year%100 != 0 or year%400 == 0)
    lengths = [31,29 if leap else 28,31,30,31,30,31,31,30,31,30,31]
    for index in range(month-1):
        total += lengths[index]
    total += day
    return total


def color_counts(grid, palette):
    counts = {color:0 for color in palette}
    for row in grid:
        for color in row:
            counts[color] = counts.get(color,0)+1
    return counts


def queens_valid(cols):
    valid = True
    for a in range(len(cols)):
        for b in range(a+1,len(cols)):
            same_column = cols[a] == cols[b]
            same_diagonal = abs(cols[a]-cols[b]) == b-a
            attacking = same_column or same_diagonal
            valid = valid and not attacking
    return valid


def datalog(objects, facts, rules, target, events):
    closure = {}
    for obj in objects:
        known = set(facts[obj])
        iteration = 0
        while True:
            changed = False
            iteration += 1
            for index,(body,head) in enumerate(rules):
                missing = sorted(set(body)-known)
                added = not missing and head not in known
                if added:
                    known.add(head)
                    changed = True
                events.append(dict(operation='infer_rule',obj=obj,iteration=iteration,
                                   rule=index,body=list(body),head=head,missing=missing,
                                   added=added,known=sorted(known)))
            if not changed:
                break
        closure[obj] = known
        events.append(dict(operation='infer_fixed',obj=obj,known=sorted(known),
                           target=target,present=target in known))
    return closure


def resolution(clauses, one_step, events):
    clauses = [frozenset(c) for c in clauses]
    def encoded(clause):
        return [[v,p] for v,p in sorted(clause)]
    # Literal order and clause processing are stable across hash seeds.
    known = sorted(set(clauses),key=lambda c:(len(c),sorted(c)))
    if not one_step and frozenset() in known:
        events.append(dict(operation='infer_empty',clause=[]))
        return True
    original_count = len(known)
    output = set()
    processed = 0
    while processed < len(known):
        right = known[processed]
        for left in known[:processed]:
            pivots = sorted((v,p) for v,p in left if (v,not p) in right)
            if not pivots:
                events.append(dict(operation='infer_no_pivot',left=encoded(left),right=encoded(right)))
            for variable,polarity in pivots:
                merged = (left-{(variable,polarity)}) | (right-{(variable,not polarity)})
                tautology = any((v,not p) in merged for v,p in merged)
                fresh = not tautology and merged not in output
                if fresh:
                    output.add(merged)
                events.append(dict(operation='infer_resolve',left=encoded(left),right=encoded(right),
                                   pivot=variable,result=encoded(merged),tautology=tautology,new=fresh))
                if not one_step and not tautology:
                    if not merged:
                        events.append(dict(operation='infer_empty',clause=[]))
                        return True
                    # Subsumption: a stronger known clause makes this addition redundant.
                    subsumed = any(c <= merged for c in known)
                    if not subsumed:
                        known.append(merged)
                    events.append(dict(operation='infer_subsumed',clause=encoded(merged),subsumed=subsumed))
        processed += 1
        if one_step and processed == original_count:
            break
    result = len(output) if one_step else False
    events.append(dict(operation='infer_saturated',one_step=one_step,result=result,clauses=len(known)))
    return result


def target_count(objects,closure,target):
    count = 0
    for obj in objects:
        present = target in closure[obj]
        count += int(present)
    return count


def most_color(counts):
    top = max(counts.values())
    winners = []
    for color,count in counts.items():
        if count == top:
            winners.append(color)
    if len(winners) != 1:
        raise ValueError('ambiguous_maximum')
    return winners[0]
