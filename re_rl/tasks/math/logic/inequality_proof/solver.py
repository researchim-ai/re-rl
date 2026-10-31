"""Exact minimum or a rational negative witness, including linear/constant cases."""
from fractions import Fraction


def nonnegative(a,b,c,events):
    if any(type(v) is not int for v in (a,b,c)):raise ValueError('invalid_coefficients')
    events.append(dict(operation='quad_input',a=a,b=b,c=c))
    if a>0:
        discriminant=b*b-4*a*c
        x=Fraction(-b,2*a);minimum=Fraction(4*a*c-b*b,4*a)
        events.append(dict(operation='quad_minimum',b_squared=b*b,four_ac=4*a*c,
                           discriminant=discriminant,x=str(x),minimum=str(minimum)))
        if minimum>=0:
            events.append(dict(operation='quad_result',valid=True))
            return True
    elif a==0 and b==0:
        events.append(dict(operation='quad_constant',value=c))
        if c>=0:
            events.append(dict(operation='quad_result',valid=True))
            return True
        x=Fraction(0)
    elif a==0:
        x=Fraction(-abs(c)-1,b)
        events.append(dict(operation='quad_linear',b=b,c=c,x=str(x)))
    else:
        x=Fraction((abs(c)+1)*(-1 if b>0 else 1))
        events.append(dict(operation='quad_downward',a=a,b=b,c=c,x=str(x)))
    value=a*x*x+b*x+c
    if value>=0:raise RuntimeError('invalid_negative_witness')
    events.append(dict(operation='quad_counterexample',x=str(x),square=str(a*x*x),
                       linear=str(b*x),constant=c,value=str(value)))
    events.append(dict(operation='quad_result',valid=False))
    return False
