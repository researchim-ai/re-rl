"""Recompute every displayed equality, ignoring generation-time answer metadata."""


def locate(steps,events):
    errors=[]
    for index,row in enumerate(steps,1):
        if len(row)!=4:raise ValueError('invalid_step')
        a,op,b,claimed=row
        if any(type(v) is not int for v in (a,b,claimed)):raise ValueError('invalid_operand')
        if op=='+':actual=a+b
        elif op=='-':actual=a-b
        elif op=='*':actual=a*b
        else:raise ValueError('invalid_operator')
        equal=actual==claimed
        events.append(dict(operation='error_check',index=index,left=a,operator=op,right=b,
                           claimed=claimed,actual=actual,delta=claimed-actual,equal=equal))
        if not equal:errors.append(index)
    events.append(dict(operation='error_result',errors=errors[:]))
    if len(errors)!=1:raise ValueError('expected_one_incorrect_step')
    return errors[0]
