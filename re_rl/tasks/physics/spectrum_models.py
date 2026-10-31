"""Symbolic oscillation/wave calculations with executed dimension and identity checks."""
from dataclasses import dataclass
from fractions import Fraction
import sympy as sp
from re_rl.tasks.physics.conservation_models import number,parse_quantity,DIMENSION_AXES
from re_rl.tasks.math.logic._logic_utils import clean

# Dimensions: mass, length, time, temperature, electric current. Angles are dimensionless.
DIMS={'1':(0,0,0,0),'rad':(0,0,0,0),'m':(0,1,0,0),'s':(0,0,1,0),
      'kg':(1,0,0,0),'m/s':(0,1,-1,0),'m/s^2':(0,1,-2,0),'N/m':(1,0,-2,0),
      'Hz':(0,0,-1,0),'rad/s':(0,0,-1,0),'H':(1,2,-2,-2),'F':(-1,-2,4,2)}
DIMS={unit:dim[:3]+(0,dim[3]) for unit,dim in DIMS.items()}
FIELDS={'oscillations':{'harmonic':('A','omega','phi'),'pendulum':('L','g'),'spring':('m','k'),
                       'lc_circuit':('L_ind','C'),'resonance':('L_ind','C')},
        'waves':{'wavelength':('v','f'),'frequency':('v','lambda_'),'period':('f',),
                 'sound_speed':('f','lambda_'),'doppler':('f0','v','v_s','v_o')}}
UNITS={'A':'m','omega':'rad/s','phi':'rad','L':'m','g':'m/s^2','m':'kg','k':'N/m',
       'L_ind':'H','C':'F','v':'m/s','f':'Hz','lambda_':'m','f0':'Hz','v_s':'m/s','v_o':'m/s'}


def validate(family,kind,inputs):
    if family not in FIELDS or kind not in FIELDS[family]:raise ValueError('invalid_task_type')
    values={key:number(inputs[key]) for key in FIELDS[family][kind]}
    if any(value<=0 for key,value in values.items() if key not in ('phi','v_s','v_o')):
        raise ValueError('nonpositive_model_parameter')
    if family=='oscillations' and kind=='harmonic' and values['A']*values['omega']>3000000:
        raise ValueError('nonclassical_harmonic_speed')
    if family=='waves':
        if 'v' in values and values['v']>100000:raise ValueError('wave_speed_out_of_model')
        if kind=='sound_speed' and values['f']*values['lambda_']>100000:raise ValueError('wave_speed_out_of_model')
        if kind=='doppler' and (abs(values['v_s'])>=values['v'] or abs(values['v_o'])>=values['v']):
            raise ValueError('doppler_requires_subsonic_motion')
    return values


@dataclass(frozen=True)
class Quantity:
    value: object
    dim: tuple


class Model:
    def __init__(self,events):self.events=events

    def input(self,label,value,unit):
        value=number(value);expr=sp.Rational(value.numerator,value.denominator)
        self.events.append(dict(operation='spec_input',label=label,value=str(expr),unit=unit,dimension=list(DIMS[unit])))
        return Quantity(expr,DIMS[unit])

    def constant(self,label,value):
        value=sp.sympify(value)
        self.events.append(dict(operation='spec_constant',label=label,value=str(value)))
        return Quantity(value,DIMS['1'])

    def calc(self,label,op,*args):
        dims=[q.dim for q in args];values=[q.value for q in args]
        if op in ('+','-'):
            if dims[0]!=dims[1]:raise ValueError('dimension_mismatch')
            result=values[0]+values[1] if op=='+' else values[0]-values[1];dim=dims[0]
        elif op in ('*','/'):
            result=values[0]*values[1] if op=='*' else values[0]/values[1]
            dim=tuple(a+b if op=='*' else a-b for a,b in zip(*dims))
        elif op=='sqrt':
            if values[0]<0 or any(d%2 for d in dims[0]):raise ValueError('invalid_dimensioned_square_root')
            result=sp.sqrt(values[0]);dim=tuple(d//2 for d in dims[0])
        elif op in ('sin','cos'):
            if dims[0]!=DIMS['1']:raise ValueError('trig_requires_dimensionless_phase')
            result=sp.sin(values[0]) if op=='sin' else sp.cos(values[0]);dim=DIMS['1']
        else:raise ValueError('invalid_model_operation')
        result=sp.cancel(result) if op in ('+','-','*','/') else result
        self.events.append(dict(operation='spec_calc',label=label,operator=op,operands=[str(v) for v in values],
                               operand_dimensions=[list(d) for d in dims],value=str(result),dimension=list(dim)))
        return Quantity(result,dim)

    def identity(self,label,left,right):
        if left.dim!=right.dim:raise ValueError('identity_dimension_mismatch')
        residual=sp.simplify(left.value-right.value)
        self.events.append(dict(operation='spec_identity',label=label,left=str(left.value),right=str(right.value),
                               residual=str(residual),dimension=list(left.dim)))
        if residual!=0:raise RuntimeError('physical_identity_failed')

    def output(self,label,value,unit):
        if value.dim!=DIMS[unit]:raise ValueError('output_dimension_mismatch')
        self.events.append(dict(operation='spec_output',label=label,value=str(value.value),
                               decimal=str(sp.N(value.value,40)),unit=unit,dimension=list(value.dim)))
        return value.value,unit


def calculate(family,kind,inputs,events):
    data=validate(family,kind,inputs);model=Model(events);c=model.calc
    q={key:model.input(key,value,UNITS[key]) for key,value in data.items()}
    one=model.constant('1',1)
    if family=='waves':
        if kind=='period':
            period=c('T=1/f','/',one,q['f']);model.identity('T*f=1',c('T*f','*',period,q['f']),one)
            return {'T':model.output('T',period,'s')}
        if kind=='doppler':
            period=c('T_emission','/',one,q['f0'])
            spacing_speed=c('v-v_source','-',q['v'],q['v_s'])
            spacing=c('crest_spacing','*',spacing_speed,period)
            closing=c('v+v_observer','+',q['v'],q['v_o'])
            observed=c('f_observed','/',closing,spacing)
            model.identity('crest_crossing_rate',c('f_observed*spacing','*',observed,spacing),closing)
            return {'f_observed':model.output('f_observed',observed,'Hz')}
        if kind=='wavelength':length=c('lambda=v/f','/',q['v'],q['f']);frequency=q['f'];speed=q['v']
        elif kind=='frequency':frequency=c('f=v/lambda','/',q['v'],q['lambda_']);length=q['lambda_'];speed=q['v']
        else:speed=c('v=lambda*f','*',q['lambda_'],q['f']);length=q['lambda_'];frequency=q['f']
        model.identity('v=lambda*f',speed,c('lambda*f','*',length,frequency))
        if kind=='wavelength':return {'lambda':model.output('lambda',length,'m')}
        if kind=='frequency':return {'f':model.output('f',frequency,'Hz')}
        return {'v':model.output('v',speed,'m/s')}
    pi=model.constant('pi',sp.pi);two=model.constant('2',2);two_pi=c('2*pi','*',two,pi)
    if kind=='harmonic':
        omega=q['omega'];period=c('T=2*pi/omega','/',two_pi,omega)
        vmax=c('v_max=A*omega','*',q['A'],omega)
        cosine=c('cos(phi)','cos',q['phi']);sine=c('sin(phi)','sin',q['phi'])
        initial_x=c('x(0)','*',q['A'],cosine)
        initial_v=c('v(0)','*',model.constant('-1',-1),c('A*omega*sin(phi)','*',vmax,sine))
        quadrature=c('omega*x(0)','*',omega,initial_x)
        conserved=c('v0^2+(omega*x0)^2','+',c('v0^2','*',initial_v,initial_v),c('(omega*x0)^2','*',quadrature,quadrature))
        energy=c('E/m','/',conserved,two)
        peak_energy=c('v_max^2/2','/',c('v_max^2','*',vmax,vmax),two)
        model.identity('harmonic_energy_per_mass',energy,peak_energy)
        return {'T':model.output('T',period,'s'),'v_max':model.output('v_max',vmax,'m/s')}
    if kind=='pendulum':omega=c('omega=sqrt(g/L)','sqrt',c('g/L','/',q['g'],q['L']))
    elif kind=='spring':omega=c('omega=sqrt(k/m)','sqrt',c('k/m','/',q['k'],q['m']))
    else:
        product=c('L*C','*',q['L_ind'],q['C'])
        omega=c('omega=1/sqrt(LC)','/',one,c('sqrt(LC)','sqrt',product))
        model.identity('omega^2*L*C=1',c('omega^2*LC','*',c('omega^2','*',omega,omega),product),one)
        if kind=='resonance':
            inductive=c('X_L=omega*L','*',omega,q['L_ind'])
            capacitive=c('X_C=1/(omega*C)','/',one,c('omega*C','*',omega,q['C']))
            model.identity('series_reactance_cancellation',inductive,capacitive)
            reactance=c('X_L-X_C','-',inductive,capacitive)
            square=c('(X_L-X_C)^2','*',reactance,reactance)
            events.append(dict(operation='spec_current_peak',reactance=str(reactance.value),square=str(square.value),dimension=list(reactance.dim)))
    period=c('T=2*pi/omega','/',two_pi,omega);frequency=c('f=1/T','/',one,period)
    model.identity('T*f=1',c('T*f','*',period,frequency),one)
    if kind=='pendulum':return {'T':model.output('T',period,'s')}
    if kind=='spring':return {'T':model.output('T',period,'s'),'f':model.output('f',frequency,'Hz')}
    return {'f':model.output('f',frequency,'Hz')}


def task_inputs(task):return {k:getattr(task,k) for k in FIELDS[task.TASK_TYPE][task.task_type]}


def prepare_task(task,events):
    from re_rl.tasks.physics.conservation_models import CONFIG
    inputs=task_inputs(task);outputs=calculate(task.TASK_TYPE,task.task_type,inputs,events)
    task.spectrum_outputs={k:{'exact':str(value),'decimal':str(sp.N(value,40)),'unit':unit} for k,(value,unit) in outputs.items()}
    def render(value,unit):return str(sp.N(value,12))+' '+CONFIG['display_units'][unit][task.language]
    if len(outputs)==1:task.final_answer=render(*next(iter(outputs.values())))
    else:task.final_answer='; '.join(label+'='+render(value,unit) for label,(value,unit) in outputs.items())
    return dict(model=task.task_type,dimension_axes=list(DIMENSION_AXES),**{key:str(number(value)) for key,value in inputs.items()})


def solve_task(task):
    from re_rl.tasks.reviewed_solvers import solve_reviewed
    return solve_reviewed(task)


def verify_task(task,prediction):
    from re_rl.tasks.math.logic.deduction_search import DiscardEvents
    outputs=calculate(task.TASK_TYPE,task.task_type,task_inputs(task),DiscardEvents());text=clean(prediction).strip()
    def valid(text,expected,unit):
        actual=parse_quantity(text,unit)
        reference=Fraction(str(sp.N(expected,40)))
        return actual is not None and abs(actual-reference)<=abs(reference)*Fraction(1,10**9)
    if len(outputs)==1:
        label,(value,unit)=next(iter(outputs.items()))
        if '=' in text:
            key,_,text=text.partition('=')
            if key.strip()!=label:return 0.0
        return float(valid(text,value,unit))
    parts=text.split(';');seen=set()
    if len(parts)!=len(outputs):return 0.0
    for part in parts:
        key,separator,text=part.strip().partition('=');key=key.strip()
        if not separator or key not in outputs or key in seen:return 0.0
        if not valid(text,*outputs[key]):return 0.0
        seen.add(key)
    return float(seen==set(outputs))
