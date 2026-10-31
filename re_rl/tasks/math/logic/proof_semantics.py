"""Syntactic proof checking and finite semantic countermodels from public formulas."""
from itertools import product
from re_rl.tasks.execution_trace import snapshot


def formula(node,atom='var'):
    if not isinstance(node,(list,tuple)) or not node:raise ValueError('invalid_formula')
    op = node[0]
    if op == atom:
        if len(node) != 2 or not isinstance(node[1],str) or not node[1]:raise ValueError('invalid_formula')
        return (op,node[1])
    if op == 'not' and len(node) == 2:return (op,formula(node[1],atom))
    if op in ('and','or','imp','iff') and len(node) == 3:
        return (op,formula(node[1],atom),formula(node[2],atom))
    raise ValueError('invalid_formula')


def proof(lines,events):
    prior = [];valid = True
    for index,line in enumerate(lines):
        rule,refs = line.get('rule'),line.get('refs')
        try:current = formula(line.get('formula'),'atom')
        except ValueError:
            events.append(dict(operation='logic_proof_line',index=index,rule=snapshot(rule),refs=snapshot(refs),forms=[],conclusion=snapshot(line.get('formula')),valid=False))
            return False
        refs_ok = isinstance(refs,(list,tuple)) and all(type(r) is int and 0 <= r < len(prior) for r in refs)
        forms = [prior[r] for r in refs] if refs_ok else []
        correct = False
        if rule == 'premise':correct = refs_ok and len(refs) == 0
        elif refs_ok:
            if rule in ('MP','MT') and len(forms) == 2:
                for a,b in ((0,1),(1,0)):
                    implication = forms[b]
                    if implication[0] != 'imp':continue
                    if rule == 'MP':correct |= forms[a] == implication[1] and current == implication[2]
                    else:correct |= forms[a] == ('not',implication[2]) and current == ('not',implication[1])
            elif rule == 'AND_I' and len(forms) == 2:
                correct = current in (('and',forms[0],forms[1]),('and',forms[1],forms[0]))
            elif rule in ('AND_E1','AND_E2') and len(forms) == 1 and forms[0][0] == 'and':
                correct = current == forms[0][1 if rule == 'AND_E1' else 2]
        events.append(dict(operation='logic_proof_line',index=index,rule=snapshot(rule),refs=snapshot(refs),forms=forms,conclusion=current,valid=bool(correct)))
        valid = valid and correct
        if not correct:return False
        prior.append(current)
    events.append(dict(operation='logic_proof_complete',lines=len(lines),valid=bool(valid)))
    return bool(valid)


def eval_formula(node,assignment,events,path):
    op = node[0]
    if op == 'var':
        if node[1] not in assignment:raise ValueError('unknown_variable')
        value = assignment[node[1]];operands = [value]
    elif op == 'not':
        operands = [eval_formula(node[1],assignment,events,path+[0])];value = not operands[0]
    else:
        a = eval_formula(node[1],assignment,events,path+[0]);b = eval_formula(node[2],assignment,events,path+[1])
        operands = [a,b]
        value = {'and':a and b,'or':a or b,'imp':not a or b,'iff':a == b}[op]
    events.append(dict(operation='logic_eval',path=path,operator=op,operands=operands,value=bool(value)))
    return bool(value)


def entails(variables,premises,conclusion,events):
    if len(set(variables)) != len(variables):raise ValueError('duplicate_variables')
    premises = [formula(p) for p in premises];conclusion = formula(conclusion)
    for bits in product((False,True),repeat=len(variables)):
        assignment = dict(zip(variables,bits))
        events.append(dict(operation='logic_assignment',assignment=assignment))
        values = [eval_formula(p,assignment,events,[i]) for i,p in enumerate(premises)]
        end = eval_formula(conclusion,assignment,events,[len(premises)])
        counterexample = all(values) and not end
        events.append(dict(operation='logic_truth_row',assignment=assignment,premises=values,conclusion=end,counterexample=counterexample))
        if counterexample:return False
    events.append(dict(operation='logic_no_counterexample',worlds=2**len(variables)))
    return True


def categorical(statement,occupied):
    quant,x,y = statement
    idx = {'S':0,'M':1,'P':2}
    if quant not in ('all','no','some','some_not') or x not in idx or y not in idx:raise ValueError('invalid_statement')
    relevant = [list(r) for r in occupied if r[idx[x]] and (r[idx[y]] if quant in ('no','some') else not r[idx[y]])]
    return (not relevant if quant in ('all','no') else bool(relevant)),relevant


def syllogism(premise1,premise2,conclusion,events):
    regions = list(product((0,1),repeat=3))
    events.append(dict(operation='logic_regions',regions=[list(r) for r in regions]))
    for mask in range(256):
        occupied = [r for i,r in enumerate(regions) if mask & (1 << i)]
        values = []
        for statement in (premise1,premise2,conclusion):
            holds,relevant = categorical(statement,occupied)
            values.append(holds)
            events.append(dict(operation='logic_category_check',mask=mask,statement=list(statement),relevant=relevant,holds=holds))
        counterexample = values[0] and values[1] and not values[2]
        events.append(dict(operation='logic_category_world',mask=mask,occupied=[list(r) for r in occupied],values=values,counterexample=counterexample))
        if counterexample:return False
    events.append(dict(operation='logic_no_counterexample',worlds=256))
    return True


def verify_boolean(prediction,expected):
    from re_rl.tasks.math.logic._logic_utils import clean,_YES,_NO
    text = clean(prediction).strip().rstrip('.!').strip().casefold()
    return float(text in (_YES if expected else _NO))
