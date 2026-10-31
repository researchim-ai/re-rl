"""Signed trajectories, exact turning-point path integrals and reachable projectile states."""
from fractions import Fraction
import sympy as sp
from re_rl.tasks.physics.mechanical_models import Model as BaseModel,Quantity,DIMS
from re_rl.tasks.physics.conservation_models import number,parse_quantity,DIMENSION_AXES,CONFIG
from re_rl.tasks.math.logic._logic_utils import clean

FIELDS={'kinematics':{'uniform_motion':('v','t'),'find_velocity':('s','t'),
        'accelerated_distance':('v0','a','t'),'accelerated_velocity':('v0','a','t'),
        'projectile_max_height':('v0','g'),'projectile_range':('v0','angle','g'),
        'circular_velocity':('r','T'),'circular_acceleration':('r','v')},
        'projectile_motion':{'range':('v0','angle','g'),'max_height':('v0','angle','g'),
        'flight_time':('v0','angle','g'),'velocity_at_height':('v0','angle','g','height_query')}}
UNITS={'v':'m/s','v0':'m/s','a':'m/s^2','g':'m/s^2','t':'s','T':'s','s':'m','r':'m',
       'angle':'deg','height_query':'m'}


def symbolic(value):
    value=number(value)
    return sp.Rational(value.numerator,value.denominator)


def ballistic_parameters(v0,angle,g):
    speed,theta,gravity=symbolic(v0),symbolic(angle)*sp.pi/180,symbolic(g)
    vx=speed*sp.cos(theta);vy=speed*sp.sin(theta)
    return dict(vx=vx,vy=vy,time=2*vy/gravity,height=vy**2/(2*gravity),range=2*vx*vy/gravity)


def validate(family,kind,inputs):
    if family not in FIELDS or kind not in FIELDS[family]:raise ValueError('invalid_task_type')
    data={key:number(inputs[key]) for key in FIELDS[family][kind]}
    if any(data[key]<=0 for key in ('g','r','T') if key in data):raise ValueError('nonpositive_model_parameter')
    if 't' in data and (data['t']<0 or (kind=='find_velocity' and data['t']==0)):
        raise ValueError('invalid_time_interval')
    if any(abs(data[key])>10000 for key in ('v','v0') if key in data):raise ValueError('velocity_out_of_model')
    if family=='projectile_motion' or kind in ('projectile_max_height','projectile_range'):
        if data['v0']<0:raise ValueError('negative_launch_speed')
        if 'angle' in data and not 0<=data['angle']<=90:raise ValueError('invalid_launch_angle')
    if kind in ('accelerated_distance','accelerated_velocity') and abs(data['v0']+data['a']*data['t'])>10000:
        raise ValueError('final_velocity_out_of_model')
    if kind=='find_velocity' and abs(data['s']/data['t'])>10000:raise ValueError('velocity_out_of_model')
    if kind=='circular_velocity' and 2*sp.pi*symbolic(data['r'])/symbolic(data['T'])>10000:
        raise ValueError('velocity_out_of_model')
    if kind=='circular_acceleration' and data['v']<0:raise ValueError('negative_speed_magnitude')
    if kind=='velocity_at_height':
        if data['height_query']<0:raise ValueError('height_below_launch_plane')
        apex=ballistic_parameters(data['v0'],data['angle'],data['g'])['height']
        gap=sp.simplify(apex-symbolic(data['height_query']))
        if gap.is_nonnegative is False:raise ValueError('unreachable_height')
        if gap.is_nonnegative is None:
            sign=sp.N(gap,120)
            if sign<0:raise ValueError('unreachable_height')
            if sign==0:raise ValueError('reachability_precision_undetermined')
    return data


class Model(BaseModel):
    def absolute(self,label,value):
        result=sp.Abs(value.value)
        self.events.append(dict(operation='spec_calc',label=label,operator='abs',operands=[str(value.value)],
                               operand_dimensions=[list(value.dim)],value=str(result),dimension=list(value.dim)))
        return Quantity(result,value.dim)


def calculate(family,kind,inputs,events):
    data=validate(family,kind,inputs);model=Model(events);c=model.calc
    q={key:model.input(key,value,UNITS[key]) for key,value in data.items()}
    if kind=='uniform_motion':
        displacement=c('delta_x=v*t','*',q['v'],q['t'])
        return {'distance':model.output('distance',model.absolute('distance=abs(delta_x)',displacement),'m')}
    if kind=='find_velocity':return {'v':model.output('v',c('v=delta_x/t','/',q['s'],q['t']),'m/s')}
    if kind in ('accelerated_distance','accelerated_velocity'):
        final=c('v_final=v0+a*t','+',q['v0'],c('a*t','*',q['a'],q['t']))
        if kind=='accelerated_velocity':return {'v_final':model.output('v_final',final,'m/s')}
        zero=model.input('t_start',0,'s');nodes=[zero]
        turn=None;inside=False
        if data['a']!=0:
            turn=c('turn_time=-v0/a','/',c('-v0','*',model.constant('-1',-1),q['v0']),q['a'])
            inside=bool(0<turn.value<q['t'].value)
            if inside:nodes.append(turn)
        nodes.append(q['t'])
        events.append(dict(operation='traj_turn',candidate=None if turn is None else str(turn.value),inside=inside,
                           duration=str(q['t'].value),nodes=[str(node.value) for node in nodes]))
        two=model.constant('2',2);positions=[]
        for i,time in enumerate(nodes):
            linear=c(f'x[{i}]:v0*t','*',q['v0'],time)
            quadratic=c(f'x[{i}]:a*t^2/2','/',c(f'x[{i}]:a*t^2','*',q['a'],c(f'x[{i}]:t^2','*',time,time)),two)
            positions.append(c(f'x[{i}]','+',linear,quadratic))
        total=model.input('distance_initial',0,'m')
        for i in range(len(positions)-1):
            displacement=c(f'segment[{i}]:delta_x','-',positions[i+1],positions[i])
            distance=model.absolute(f'segment[{i}]:abs(delta_x)',displacement)
            total=c(f'distance_through_segment[{i}]','+',total,distance)
        return {'distance':model.output('distance',total,'m')}
    if kind=='circular_velocity':
        circumference=c('2*pi*r','*',c('2*pi','*',model.constant('2',2),model.constant('pi',sp.pi)),q['r'])
        speed=c('v=2*pi*r/T','/',circumference,q['T'])
        model.identity('one_turn_arc',c('v*T','*',speed,q['T']),circumference)
        return {'v':model.output('v',speed,'m/s')}
    if kind=='circular_acceleration':
        squared=c('v^2','*',q['v'],q['v']);acceleration=c('a_c=v^2/r','/',squared,q['r'])
        model.identity('normal_acceleration',c('a_c*r','*',acceleration,q['r']),squared)
        return {'a_c':model.output('a_c',acceleration,'m/s^2')}
    two=model.constant('2',2)
    if kind=='projectile_max_height':
        time=c('t_apex=v0/g','/',q['v0'],q['g'])
        height=c('H=v0^2/(2*g)','/',c('v0^2','*',q['v0'],q['v0']),c('2*g','*',two,q['g']))
        zero=c('v_at_apex','-',q['v0'],c('g*t_apex','*',q['g'],time))
        model.identity('vertical_apex',zero,model.input('v_zero',0,'m/s'))
        return {'H':model.output('H',height,'m')}
    angle=c('angle_radians','/',c('angle*pi','*',q['angle'],model.constant('pi',sp.pi)),model.constant('180',180))
    vx=c('vx_initial','*',q['v0'],c('cos(angle)','cos',angle))
    vy=c('vy_initial','*',q['v0'],c('sin(angle)','sin',angle))
    flight=c('t_return=2*vy/g','/',c('2*vy','*',two,vy),q['g'])
    apex=c('H=vy^2/(2*g)','/',c('vy^2','*',vy,vy),c('2*g','*',two,q['g']))
    distance=c('range=vx*t_return','*',vx,flight)
    y_return=c('y(t_return)','-',c('vy*t_return','*',vy,flight),c('g*t_return^2/2','/',c('g*t_return^2','*',q['g'],c('t_return^2','*',flight,flight)),two))
    model.identity('same_level_return',y_return,model.input('y_zero',0,'m'))
    if kind in ('projectile_range','range'):return {'range':model.output('range',distance,'m')}
    if kind=='max_height':return {'H':model.output('H',apex,'m')}
    if kind=='flight_time':return {'t_flight':model.output('t_flight',flight,'s')}
    vertical_squared=c('vy_at_h^2','-',c('vy_initial^2','*',vy,vy),c('2*g*h','*',c('2*g','*',two,q['g']),q['height_query']))
    vertical=c('abs(vy_at_h)','sqrt',vertical_squared)
    t_up=c('t_ascending','/',c('vy_initial-abs(vy_h)','-',vy,vertical),q['g'])
    t_down=c('t_descending','/',c('vy_initial+abs(vy_h)','+',vy,vertical),q['g'])
    for label,time in [('ascending',t_up),('descending',t_down)]:
        height=c('y_'+label,'-',c('vy*t_'+label,'*',vy,time),c('g*t_'+label+'^2/2','/',c('g*t_'+label+'^2','*',q['g'],c('t_'+label+'^2','*',time,time)),two))
        model.identity('height_'+label,height,q['height_query'])
    speed_squared=c('speed_at_h^2','+',c('vx^2','*',vx,vx),vertical_squared)
    energy_speed=c('v0^2-2*g*h','-',c('v0^2','*',q['v0'],q['v0']),c('2*g*h','*',c('2*g','*',two,q['g']),q['height_query']))
    model.identity('projectile_energy',speed_squared,energy_speed)
    events.append(dict(operation='traj_height_states',vx=str(vx.value),vy_up=str(vertical.value),vy_down=str(-vertical.value),
                       t_up=str(t_up.value),t_down=str(t_down.value),distinct_times=1 if sp.simplify(t_up.value-t_down.value)==0 else 2))
    return {'speed':model.output('speed',c('speed_at_h','sqrt',speed_squared),'m/s')}


def task_inputs(task):return {key:getattr(task,key) for key in FIELDS[task.TASK_TYPE][task.task_type]}


def prepare_task(task,events):
    inputs=task_inputs(task);outputs=calculate(task.TASK_TYPE,task.task_type,inputs,events)
    task.trajectory_outputs={key:{'exact':str(value),'decimal':str(sp.N(value,40)),'unit':unit} for key,(value,unit) in outputs.items()}
    value,unit=next(iter(outputs.values()));task.final_answer=str(sp.N(value,12))+' '+CONFIG['display_units'][unit][task.language]
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
