"""Work/energy and Newtonian force balances with exact angles and signed coordinates."""
from fractions import Fraction
import sympy as sp
from re_rl.tasks.physics.spectrum_models import Model as SymbolicModel,Quantity,DIMS as SPECTRUM_DIMS
from re_rl.tasks.physics.conservation_models import number,parse_quantity,DIMENSION_AXES,CONFIG,DIMS as CONSERVATION_DIMS
from re_rl.tasks.math.logic._logic_utils import clean

DIMS={**SPECTRUM_DIMS,**CONSERVATION_DIMS,'W':(1,2,-3,0,0),'deg':(0,0,0,0,0)}
FIELDS={'energy':{'work':('F','s'),'work_angle':('F','s','angle'),'kinetic_energy':('m','v'),
                  'potential_energy':('m','g','h'),'power':('W','t'),'conservation':('m','g','h','v0')},
        'dynamics':{'newton_second':('m','F'),'find_force':('m','a'),'weight':('m','g'),
                    'friction':('m','g','mu'),'inclined_plane':('m','g','angle'),'tension':('m1','m2','g')}}
UNITS={'F':'N','s':'m','angle':'deg','m':'kg','v':'m/s','g':'m/s^2','h':'m','W':'J','t':'s',
       'v0':'m/s','a':'m/s^2','mu':'1','m1':'kg','m2':'kg'}


def validate(family,kind,inputs):
    if family not in FIELDS or kind not in FIELDS[family]:raise ValueError('invalid_task_type')
    data={key:number(inputs[key]) for key in FIELDS[family][kind]}
    if any(data[key]<=0 for key in ('m','m1','m2','g','t') if key in data):raise ValueError('nonpositive_model_parameter')
    if any(abs(data[key])>10000 for key in ('v','v0') if key in data):raise ValueError('velocity_out_of_model')
    if family=='energy':
        if kind in ('work','work_angle') and (data['F']<0 or data['s']<0):raise ValueError('negative_vector_magnitude')
        if kind=='work_angle' and not 0<=data['angle']<=180:raise ValueError('invalid_vector_angle')
        if kind=='conservation':
            if data['h']<0:raise ValueError('negative_drop_height')
            if data['v0']**2+2*data['g']*data['h']>10000**2:raise ValueError('impact_speed_out_of_model')
    else:
        if kind=='friction' and data['mu']<0:raise ValueError('negative_friction_coefficient')
        if kind=='inclined_plane' and not 0<=data['angle']<=90:raise ValueError('invalid_incline_angle')
    return data


class Model(SymbolicModel):
    def input(self,label,value,unit):
        value=number(value);expr=sp.Rational(value.numerator,value.denominator)
        self.events.append(dict(operation='spec_input',label=label,value=str(expr),unit=unit,dimension=list(DIMS[unit])))
        return Quantity(expr,DIMS[unit])

    def output(self,label,value,unit):
        if value.dim!=DIMS[unit]:raise ValueError('output_dimension_mismatch')
        self.events.append(dict(operation='spec_output',label=label,value=str(value.value),
                               decimal=str(sp.N(value.value,40)),unit=unit,dimension=list(value.dim)))
        return value.value,unit


def calculate(family,kind,inputs,events):
    data=validate(family,kind,inputs);model=Model(events);c=model.calc
    q={key:model.input(key,value,UNITS[key]) for key,value in data.items()}
    if family=='energy':
        if kind in ('work','work_angle'):
            work=c('W=F*s','*',q['F'],q['s'])
            if kind=='work_angle':
                radians=c('angle_radians','/',c('angle*pi','*',q['angle'],model.constant('pi',sp.pi)),model.constant('180',180))
                work=c('W=F*s*cos(angle)','*',work,c('cos(angle)','cos',radians))
            return {'W':model.output('W',work,'J')}
        if kind=='kinetic_energy':
            energy=c('K=m*v^2/2','/',c('m*v^2','*',q['m'],c('v^2','*',q['v'],q['v'])),model.constant('2',2))
            return {'K':model.output('K',energy,'J')}
        if kind=='potential_energy':
            potential=c('U=m*g*h','*',c('m*g','*',q['m'],q['g']),q['h'])
            return {'U':model.output('U',potential,'J')}
        if kind=='power':return {'P':model.output('P',c('P_average=W/t','/',q['W'],q['t']),'W')}
        two=model.constant('2',2)
        speed_squared=c('v_impact^2','+',c('v0^2','*',q['v0'],q['v0']),c('2*g*h','*',c('2*g','*',two,q['g']),q['h']))
        speed=c('v_impact','sqrt',speed_squared)
        initial_kinetic=c('K_initial','/',c('m*v0^2','*',q['m'],c('v0^2','*',q['v0'],q['v0'])),two)
        potential=c('U_initial','*',c('m*g','*',q['m'],q['g']),q['h'])
        initial=c('E_initial','+',initial_kinetic,potential)
        final=c('K_final','/',c('m*v_impact^2','*',q['m'],c('v_impact^2','*',speed,speed)),two)
        model.identity('mechanical_energy_conservation',initial,final)
        return {'v_impact':model.output('v_impact',speed,'m/s')}
    if kind=='newton_second':
        acceleration=c('a=F_net/m','/',q['F'],q['m'])
        model.identity('Newton_second_law',c('m*a','*',q['m'],acceleration),q['F'])
        return {'a':model.output('a',acceleration,'m/s^2')}
    if kind=='find_force':return {'F':model.output('F',c('F_net=m*a','*',q['m'],q['a']),'N')}
    if kind=='tension':
        total=c('m1+m2','+',q['m1'],q['m2'])
        difference=c('m2-m1','-',q['m2'],q['m1'])
        acceleration=c('a_signed','/',c('(m2-m1)*g','*',difference,q['g']),total)
        tension=c('T=m1*(g+a)','*',q['m1'],c('g+a','+',q['g'],acceleration))
        other=c('T=m2*(g-a)','*',q['m2'],c('g-a','-',q['g'],acceleration))
        model.identity('massless_string_same_tension',tension,other)
        model.identity('mass1_Newton',c('T-m1*g','-',tension,c('m1*g','*',q['m1'],q['g'])),c('m1*a','*',q['m1'],acceleration))
        model.identity('mass2_Newton',c('m2*g-T','-',c('m2*g','*',q['m2'],q['g']),tension),c('m2*a','*',q['m2'],acceleration))
        if not abs(acceleration.value)<q['g'].value or tension.value<=0:raise RuntimeError('invalid_Atwood_state')
        return {'T':model.output('T',tension,'N')}
    gravity=c('m*g','*',q['m'],q['g'])
    if kind in ('weight','friction'):
        normal=gravity
        model.identity('horizontal_normal_balance',normal,gravity)
        if kind=='weight':return {'P':model.output('P',normal,'N')}
        friction=c('F_kinetic=mu*N','*',q['mu'],normal)
        return {'F_friction':model.output('F_friction',friction,'N')}
    radians=c('angle_radians','/',c('angle*pi','*',q['angle'],model.constant('pi',sp.pi)),model.constant('180',180))
    parallel=c('F_parallel=m*g*sin(angle)','*',gravity,c('sin(angle)','sin',radians))
    perpendicular=c('N=m*g*cos(angle)','*',gravity,c('cos(angle)','cos',radians))
    # In the normal direction there is no acceleration; N cancels the normal gravity component.
    model.identity('normal_balance',perpendicular,c('gravity_normal','*',gravity,c('cos(angle)','cos',radians)))
    magnitude=c('F_parallel^2+N^2','+',c('F_parallel^2','*',parallel,parallel),c('N^2','*',perpendicular,perpendicular))
    model.identity('gravity_projection_norm',magnitude,c('(m*g)^2','*',gravity,gravity))
    acceleration=c('a_parallel','/',parallel,q['m'])
    model.identity('incline_Newton',parallel,c('m*a_parallel','*',q['m'],acceleration))
    return {'F_parallel':model.output('F_parallel',parallel,'N')}


def task_inputs(task):return {key:getattr(task,key) for key in FIELDS[task.TASK_TYPE][task.task_type]}


def prepare_task(task,events):
    inputs=task_inputs(task);outputs=calculate(task.TASK_TYPE,task.task_type,inputs,events)
    task.mechanical_outputs={key:{'exact':str(value),'decimal':str(sp.N(value,40)),'unit':unit} for key,(value,unit) in outputs.items()}
    value,unit=next(iter(outputs.values()))
    task.final_answer=str(sp.N(value,12))+' '+CONFIG['display_units'][unit][task.language]
    return dict(model=task.task_type,dimension_axes=list(DIMENSION_AXES),**{key:str(number(value)) for key,value in inputs.items()})


def solve_task(task):
    from re_rl.tasks.reviewed_solvers import solve_reviewed
    return solve_reviewed(task)


def verify_task(task,prediction):
    from re_rl.tasks.math.logic.deduction_search import DiscardEvents
    outputs=calculate(task.TASK_TYPE,task.task_type,task_inputs(task),DiscardEvents())
    label,(value,unit)=next(iter(outputs.items()));text=clean(prediction).strip()
    if '=' in text:
        key,_,text=text.partition('=')
        if key.strip()!=label:return 0.0
    actual=parse_quantity(text,unit)
    if actual is None:return 0.0
    expected=Fraction(str(sp.N(value,40)))
    return float(abs(actual-expected)<=abs(expected)*Fraction(1,10**9))
