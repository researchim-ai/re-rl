"""Exact evaluation of ordered arithmetic definitions and public comparisons."""
import operator

OPERATIONS = {'add':operator.add,'sub':operator.sub,'mul':operator.mul}
RELATIONS = {'eq':operator.eq,'ne':operator.ne,'lt':operator.lt,'le':operator.le,'gt':operator.gt,'ge':operator.ge}
SYMBOLS = {'add':'+','sub':'−','mul':'×','eq':'=','ne':'≠','lt':'<','le':'≤','gt':'>','ge':'≥'}


def evaluate(definitions,claims,events):
    values = {}
    def operand(value):
        if type(value) is int:return value
        if isinstance(value,str) and value in values:return values[value]
        raise ValueError('undefined_operand')
    for definition in definitions:
        name,op = definition['name'],definition['op']
        if not isinstance(name,str) or not name.isidentifier() or name in values:
            raise ValueError('invalid_definition')
        if op == 'const':
            args = [operand(definition['value'])];result = args[0]
        else:
            if op not in OPERATIONS:raise ValueError('invalid_operation')
            args = [operand(definition['left']),operand(definition['right'])]
            result = OPERATIONS[op](*args)
        values[name] = result
        events.append(dict(operation='claim_define',name=name,op=op,operands=args,result=result))
    false_indices = []
    for index,claim in enumerate(claims):
        relation = claim['relation']
        if relation not in RELATIONS:raise ValueError('invalid_relation')
        left,right = operand(claim['left']),operand(claim['right'])
        truth = bool(RELATIONS[relation](left,right))
        if not truth:false_indices.append(index)
        events.append(dict(operation='claim_check',index=index,left=left,relation=SYMBOLS[relation],right=right,truth=truth))
    events.append(dict(operation='claim_result',false_indices=list(false_indices)))
    return values,false_indices


def render_definition(definition):
    if definition['op'] == 'const':return definition['name']+' = '+str(definition['value'])
    return definition['name']+' = '+str(definition['left'])+' '+SYMBOLS[definition['op']]+' '+str(definition['right'])


def render_claim(claim):
    return str(claim['left'])+' '+SYMBOLS[claim['relation']]+' '+str(claim['right'])
