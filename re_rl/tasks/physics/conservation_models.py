"""Exact classical conservation models, executable dimensions and strict SI-aware grading."""
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
import json
import math
import re
from re_rl.tasks.math.logic._logic_utils import clean

# Dimensions: mass, length, time, temperature, electric current.
DIMS={'kg':(1,0,0,0),'m/s':(0,1,-1,0),'N':(1,1,-2,0),'s':(0,0,1,0),
      '°C':(0,0,0,1),'J/kg/K':(0,2,-2,-1),'J/kg':(0,2,-2,0),
      'J':(1,2,-2,0),'kg*m/s':(1,1,-1,0),'N*s':(1,1,-1,0),'%':(0,0,0,0),'1':(0,0,0,0)}
DIMENSION_AXES=("M","L","T","Theta","I")
DIMS={unit:dim+(0,) for unit,dim in DIMS.items()}
FIELDS={
 'momentum':{'momentum':('m','v'),'impulse':('F','t'),
             'inelastic_collision':('m1','m2','v1','v2'),'elastic_collision':('m1','m2','v1','v2')},
 'heat_transfer':{'heat_capacity':('m','T1','T2','c','substance'),
                  'mixing':('m1','m2','T1','T2','c'),'phase_change':('m','lambda_ice'),'efficiency':('Q1','Q2')}}
INPUT_UNITS={'m':'kg','m1':'kg','m2':'kg','v':'m/s','v1':'m/s','v2':'m/s','F':'N','t':'s',
             'T1':'°C','T2':'°C','c':'J/kg/K','lambda_ice':'J/kg','Q1':'J','Q2':'J'}


def number(value):
    if isinstance(value,bool) or not isinstance(value,(int,float,Fraction,Decimal)):
        raise ValueError('invalid_physical_number')
    if isinstance(value,float) and not math.isfinite(value):raise ValueError('nonfinite_physical_number')
    if isinstance(value,Decimal) and not value.is_finite():raise ValueError('nonfinite_physical_number')
    if abs(value)>10**12:raise ValueError('physical_input_out_of_range')
    if isinstance(value,Decimal) and value and value.adjusted() < -100:raise ValueError('physical_precision_out_of_range')
    if isinstance(value,Fraction) and max(value.numerator.bit_length(),value.denominator.bit_length())>1024:raise ValueError('physical_precision_out_of_range')
    try:result=Fraction(str(value))
    except (ValueError,ZeroDivisionError,OverflowError):raise ValueError('nonfinite_physical_number') from None
    if abs(result)>10**12:raise ValueError('physical_input_out_of_range')
    if max(result.numerator.bit_length(),result.denominator.bit_length())>1024:raise ValueError('physical_precision_out_of_range')
    return result


def validate_inputs(family,kind,inputs):
    if family not in FIELDS or kind not in FIELDS[family]:raise ValueError('invalid_task_type')
    values={k:number(inputs[k]) for k in FIELDS[family][kind] if k!='substance'}
    for key in ('m','m1','m2','c','lambda_ice'):
        if key in values and values[key]<=0:raise ValueError('nonpositive_physical_quantity')
    for key in ('v','v1','v2'):
        if key in values and abs(values[key])>10000:raise ValueError('nonclassical_velocity')
    if 't' in values and values['t']<0:raise ValueError('negative_duration')
    if family=='heat_transfer':
        if kind=='heat_capacity':
            substance=inputs['substance']
            if substance=='ice':low,high=-100,0
            elif substance=='water':low,high=0,100
            elif substance in ('aluminum','iron','copper','lead'):low,high=-100,200
            else:raise ValueError('invalid_substance')
            if not all(low<=values[k]<=high for k in ('T1','T2')):raise ValueError('phase_or_temperature_out_of_model')
        elif kind=='mixing' and not all(0<=values[k]<=100 for k in ('T1','T2')):
            raise ValueError('liquid_water_temperature_out_of_model')
        elif kind=='efficiency' and not 0<values['Q2']<=values['Q1']:
            raise ValueError('invalid_cyclic_heat_engine')
    return values


@dataclass(frozen=True)
class Quantity:
    value: Fraction
    dim: tuple


class Model:
    def __init__(self,events):self.events=events

    def input(self,label,value,unit):
        result=Quantity(number(value),DIMS[unit])
        self.events.append(dict(operation='phys_input',label=label,value=str(result.value),unit=unit,dimension=list(result.dim)))
        return result

    def calc(self,label,op,left,right):
        a,b=left.value,right.value
        if op in ('+','-'):
            if left.dim!=right.dim:raise ValueError('dimension_mismatch')
            value=a+b if op=='+' else a-b;dim=left.dim
        elif op=='*':value=a*b;dim=tuple(x+y for x,y in zip(left.dim,right.dim))
        elif op=='/':value=a/b;dim=tuple(x-y for x,y in zip(left.dim,right.dim))
        else:raise ValueError('invalid_physical_operation')
        self.events.append(dict(operation='phys_calc',label=label,operator=op,left=str(a),right=str(b),
                               left_dim=list(left.dim),right_dim=list(right.dim),value=str(value),dimension=list(dim)))
        return Quantity(value,dim)

    def balance(self,label,left,right):
        residual=self.calc(label+':residual','-',left,right)
        self.events.append(dict(operation='phys_balance',label=label,left=str(left.value),right=str(right.value),
                               residual=str(residual.value),dimension=list(residual.dim)))
        if residual.value:raise RuntimeError('physical_balance_failed')

    def output(self,label,quantity,unit):
        if quantity.dim!=DIMS[unit]:raise ValueError('output_dimension_mismatch')
        self.events.append(dict(operation='phys_output',label=label,value=str(quantity.value),unit=unit,dimension=list(quantity.dim)))
        return quantity.value,unit


def calculate(family,kind,inputs,events):
    values=validate_inputs(family,kind,inputs);model=Model(events)
    q={key:model.input(key,value,INPUT_UNITS[key]) for key,value in values.items()}
    c=model.calc
    if family=='momentum':
        if kind=='momentum':return {'p':model.output('p',c('p=m*v','*',q['m'],q['v']),'kg*m/s')}
        if kind=='impulse':return {'J':model.output('J',c('J=F*t','*',q['F'],q['t']),'N*s')}
        two=model.input('2',2,'1')
        m1,m2,v1,v2=(q[k] for k in ('m1','m2','v1','v2'))
        total=c('m1+m2','+',m1,m2)
        initial=c('p_initial','+',c('m1*v1','*',m1,v1),c('m2*v2','*',m2,v2))
        relative=c('v1-v2','-',v1,v2)
        if kind=='inelastic_collision':
            out=c('v_common','/',initial,total)
            w1=w2=out
        else:
            # Collision impulse gives both signed velocities without assuming v2=0.
            reduced=c('m_reduced','/',c('m1*m2','*',m1,m2),total)
            impulse=c('collision_impulse','*',c('2*mu','*',two,reduced),relative)
            w1=c('v1_out','-',v1,c('J/m1','/',impulse,m1))
            w2=c('v2_out','+',v2,c('J/m2','/',impulse,m2))
            model.balance('relative_velocity_reversal',c('v2_out-v1_out','-',w2,w1),relative)
        final=c('p_final','+',c('m1*v1_out','*',m1,w1),c('m2*v2_out','*',m2,w2))
        model.balance('momentum',initial,final)
        def kinetic(label,a,b):
            first=c(label+':K1','/',c(label+':m1*v1^2','*',m1,c(label+':v1^2','*',a,a)),two)
            second=c(label+':K2','/',c(label+':m2*v2^2','*',m2,c(label+':v2^2','*',b,b)),two)
            return c(label,'+',first,second)
        before=kinetic('K_initial',v1,v2);after=kinetic('K_final',w1,w2)
        if kind=='elastic_collision':
            model.balance('kinetic_energy',before,after)
            return {'v1_out':model.output('v1_out',w1,'m/s'),'v2_out':model.output('v2_out',w2,'m/s')}
        loss=c('K_dissipated','-',before,after)
        reduced=c('m_reduced','/',c('m1*m2','*',m1,m2),total)
        expected=c('mu*(v1-v2)^2/2','/',c('mu*(v1-v2)^2','*',reduced,c('relative^2','*',relative,relative)),two)
        model.balance('inelastic_energy_loss',loss,expected)
        if loss.value<0:raise RuntimeError('negative_dissipation')
        return {'v_common':model.output('v_common',out,'m/s')}
    if kind=='heat_capacity':
        delta=c('delta_T','-',q['T2'],q['T1'])
        heat=c('Q=c*m*delta_T','*',c('c*m','*',q['c'],q['m']),delta)
        return {'Q':model.output('Q',heat,'J')}
    if kind=='mixing':
        total=c('m1+m2','+',q['m1'],q['m2'])
        weighted=c('weighted_temperatures','+',c('m1*T1','*',q['m1'],q['T1']),c('m2*T2','*',q['m2'],q['T2']))
        out=c('T_final','/',weighted,total)
        d1=c('T_final-T1','-',out,q['T1']);d2=c('T2-T_final','-',q['T2'],out)
        gained=c('Q1','*',c('c*m1','*',q['c'],q['m1']),d1)
        lost=c('Q2','*',c('c*m2','*',q['c'],q['m2']),d2)
        model.balance('isolated_mixing_heat',gained,lost)
        if not min(q['T1'].value,q['T2'].value)<=out.value<=max(q['T1'].value,q['T2'].value):raise RuntimeError('invalid_mixture_temperature')
        return {'T_final':model.output('T_final',out,'°C')}
    if kind=='phase_change':
        return {'Q':model.output('Q',c('Q=lambda*m','*',q['lambda_ice'],q['m']),'J')}
    work=c('W=Q1-Q2','-',q['Q1'],q['Q2'])
    model.balance('cycle_first_law',q['Q1'],c('W+Q2','+',work,q['Q2']))
    ratio=c('eta=W/Q1','/',work,q['Q1'])
    percent=c('eta_percent','*',ratio,model.input('100',100,'1'))
    return {'eta':model.output('eta',percent,'%')}


def task_inputs(task):
    fields=FIELDS[task.TASK_TYPE][task.task_type]
    return {k:getattr(task,k) for k in fields}


def render_number(value):
    # Exact decimal round-to-nearest, ties-to-even at four decimal places.
    negative=value<0;value=abs(value)*10000
    rounded,remainder=divmod(value.numerator,value.denominator)
    if 2*remainder>value.denominator or (2*remainder==value.denominator and rounded%2):rounded+=1
    integer,decimal=divmod(rounded,10000)
    text=str(integer)+(('.'+str(decimal).zfill(4)).rstrip('0') if decimal else '')
    return ('-' if negative and rounded else '')+text


CONFIG=json.loads(Path(__file__).with_name('conservation_models_i18n.json').read_text())


def prepare_task(task,events):
    inputs=task_inputs(task)
    outputs=calculate(task.TASK_TYPE,task.task_type,inputs,events)
    task.physical_outputs={label:{'value':str(value),'unit':unit} for label,(value,unit) in outputs.items()}
    if len(outputs)==1:
        value,unit=next(iter(outputs.values()));task.final_answer=render_number(value)+' '+CONFIG['display_units'][unit][task.language]
    else:task.final_answer='; '.join(label+'='+render_number(value)+' '+CONFIG['display_units'][unit][task.language] for label,(value,unit) in outputs.items())
    # No decimal binary expansions are exported as model inputs.
    exported={k:(v if isinstance(v,str) else str(number(v))) for k,v in inputs.items()}
    exported.update(model=task.task_type,dimension_axes=list(DIMENSION_AXES))
    return exported


def solve_task(task):
    from re_rl.tasks.reviewed_solvers import solve_reviewed
    return solve_reviewed(task)


NUMBER=r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'
QUANTITY=re.compile('('+NUMBER+r'(?:\s*/\s*'+NUMBER+r')?)\s*(.*)')


def parse_quantity(text,unit):
    text=text.replace(",",".").replace("−","-")
    if len(text)>256:return None
    if any(abs(int(m.group(1)))>1000 for m in re.finditer(r'[eE]([+-]?\d+)',text)):
        return None
    match=QUANTITY.fullmatch(text.strip())
    if not match:return None
    try:
        parts=re.split(r'\s*/\s*',match.group(1))
        value=Fraction(parts[0]) if len(parts)==1 else Fraction(parts[0])/Fraction(parts[1])
    except (ValueError,ZeroDivisionError,OverflowError):return None
    suffix=match.group(2).strip().replace(' ','')
    if not suffix:return value
    conversion=CONFIG['accepted_units'][unit].get(suffix)
    if conversion is None:return None
    return value*Fraction(conversion[0])+Fraction(conversion[1])


def verify_task(task,prediction):
    from re_rl.tasks.math.logic.deduction_search import DiscardEvents
    outputs=calculate(task.TASK_TYPE,task.task_type,task_inputs(task),DiscardEvents())
    text=clean(prediction).strip()
    if len(outputs)==1:
        label,(expected,unit)=next(iter(outputs.items()))
        if '=' in text:
            name,separator,text=text.partition('=')
            if name.strip()!=label:return 0.0
        actual=parse_quantity(text,unit)
        return float(actual is not None and abs(actual-expected)<=Fraction(51,1000000))
    parts=text.split(';')
    if len(parts)!=len(outputs):return 0.0
    seen=set()
    for part in parts:
        label,separator,quantity=part.strip().partition('=')
        label=label.strip()
        if not separator or label not in outputs or label in seen:return 0.0
        expected,unit=outputs[label];actual=parse_quantity(quantity,unit)
        if actual is None or abs(actual-expected)>Fraction(51,1000000):return 0.0
        seen.add(label)
    return float(seen==set(outputs))
