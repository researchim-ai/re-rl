"""Independent absolute-velocity integrals, ballistic event ODEs and circular trajectories."""
from fractions import Fraction as F
import itertools
import json
import math
import random
from unittest.mock import patch
import numpy as np
import pytest
import sympy as sp
from scipy.integrate import quad,solve_ivp
from re_rl.tasks.physics.mechanics.kinematics.task import KinematicsTask
from re_rl.tasks.physics.mechanics.projectile_motion.task import ProjectileMotionTask
from re_rl.tasks.physics.trajectory_models import calculate
from re_rl.tasks.physics.generators import generate_random_kinematics_task,generate_random_projectile_motion_task


def value(outputs):return next(iter(outputs.values()))[0]


def test_all_small_signed_paths_against_absolute_velocity_integrals():
    for v0,a,t in itertools.product(range(-3,4),range(-3,4),(F(0),F(1,2),F(1),F(3))):
        events=[];actual=value(calculate('kinematics','accelerated_distance',dict(v0=v0,a=a,t=t),events))
        turn=None if not a else F(-v0,a)
        points=[float(turn)] if turn is not None and 0<turn<t else None
        expected=quad(lambda u:abs(v0+a*u),0,float(t),points=points)[0]
        assert float(actual)==pytest.approx(expected,abs=1e-10)
        displacement=v0*t+F(a,2)*t*t
        assert actual>=abs(displacement)
        event=next(e for e in events if e['operation']=='traj_turn')
        assert event['inside']==(turn is not None and 0<turn<t)
    assert value(calculate('kinematics','accelerated_distance',dict(v0=2,a=-1,t=4),[]))==4
    assert value(calculate('kinematics','accelerated_distance',dict(v0=-2,a=1,t=4),[]))==4
    assert value(calculate('kinematics','accelerated_distance',dict(v0=3,a=-1,t=3),[]))==F(9,2)
    assert value(calculate('kinematics','uniform_motion',dict(v=-3,t=4),[]))==12
    assert value(calculate('kinematics','find_velocity',dict(s=-12,t=4),[]))==-3
    assert value(calculate('kinematics','accelerated_velocity',dict(v0=2,a=-1,t=4),[]))==-2


def test_ballistic_ranges_apices_and_times_against_event_ode():
    def ground(t,y):return y[1]
    ground.direction=-1;ground.terminal=True
    def apex(t,y):return y[3]
    apex.direction=-1
    for speed,angle,g in itertools.product((5,20),(15,30,45,60,90),(1,9.81)):
        theta=math.radians(angle);vx=speed*math.cos(theta);vy=speed*math.sin(theta)
        motion=solve_ivp(lambda t,y:[y[2],y[3],0,-g],[0,2*vy/g+1],[0,0,vx,vy],
                         events=(ground,apex),rtol=1e-11,atol=1e-12)
        inputs=dict(v0=speed,angle=angle,g=g)
        actual_range=float(value(calculate('projectile_motion','range',inputs,[])))
        actual_height=float(value(calculate('projectile_motion','max_height',inputs,[])))
        actual_time=float(value(calculate('projectile_motion','flight_time',inputs,[])))
        assert actual_range==pytest.approx(motion.y_events[0][0][0],abs=1e-9)
        assert actual_height==pytest.approx(motion.y_events[1][0][1],abs=1e-9)
        assert actual_time==pytest.approx(motion.t_events[0][0],rel=1e-10)
        if angle==90:assert actual_range==0
    for angle in (0,90):
        assert value(calculate('kinematics','projectile_range',dict(v0=10,angle=angle,g=10),[]))==0
    assert value(calculate('kinematics','projectile_max_height',dict(v0=0,g=10),[]))==0


def test_height_reachability_and_both_time_branches():
    with pytest.raises(ValueError,match='unreachable_height'):
        ProjectileMotionTask(task_type='velocity_at_height',v0=10,angle=30,g=10,height_query=2)
    events=[];outputs=calculate('projectile_motion','velocity_at_height',dict(v0=10,angle=30,g=10,height_query=F(1,2)),events)
    assert float(value(outputs))==pytest.approx(math.sqrt(90))
    state=next(e for e in events if e['operation']=='traj_height_states')
    assert state['distinct_times']==2
    assert sp.sympify(state['vy_up'])==-sp.sympify(state['vy_down'])
    for name in ('t_up','t_down'):
        t=sp.sympify(state[name]);assert sp.simplify(5*t-5*t*t-F(1,2))==0
    events=[];apex=value(calculate('projectile_motion','velocity_at_height',dict(v0=10,angle=30,g=10,height_query=F(5,4)),events))
    assert sp.simplify(apex-5*sp.sqrt(3))==0
    assert next(e for e in events if e['operation']=='traj_height_states')['distinct_times']==1
    assert value(calculate('projectile_motion','velocity_at_height',dict(v0=10,angle=90,g=10,height_query=5),[]))==0


def test_uniform_circle_against_rotation_ode_and_norms():
    radius,period=3,2*math.pi;omega=2*math.pi/period
    orbit=solve_ivp(lambda t,y:[y[2],y[3],-omega**2*y[0],-omega**2*y[1]],
                    [0,period],[radius,0,0,radius*omega],rtol=1e-11,atol=1e-12)
    speed=float(value(calculate('kinematics','circular_velocity',dict(r=radius,T=period),[])))
    acceleration=float(value(calculate('kinematics','circular_acceleration',dict(r=radius,v=speed),[])))
    assert np.hypot(orbit.y[0],orbit.y[1])==pytest.approx(np.full(len(orbit.t),radius),abs=1e-9)
    assert np.hypot(orbit.y[2],orbit.y[3])==pytest.approx(np.full(len(orbit.t),speed),abs=1e-9)
    assert acceleration==pytest.approx(radius*omega*omega)
    assert orbit.y[:,-1]==pytest.approx([radius,0,0,radius*omega],abs=1e-9)


@pytest.mark.parametrize('cls',[KinematicsTask,ProjectileMotionTask])
@pytest.mark.parametrize('language',['ru','en'])
def test_all_subtypes_levels_stability_and_exact_trace_replay(cls,language):
    for level in range(1,11):
        for kind in cls.TASK_TYPES:
            random.seed(level);task=cls(task_type=kind,language=language,difficulty=level,reasoning_mode=True)
            description=task.description;state=random.getstate();task.solve()
            assert random.getstate()==state and description==task.description
            assert task.reasoning_mode and task.difficulty==level
            saved=json.dumps(task.get_result(),sort_keys=True);answer=task.final_answer
            task.final_answer='stale';task.trajectory_outputs={'bad':999}
            for name in ('vx','vy','range_val','max_height','flight_time'):
                if hasattr(task,name):setattr(task,name,object())
            assert task.verify(answer)==1
            task.solve();assert json.dumps(task.get_result(),sort_keys=True)==saved
            assert task.verify('junk '+answer)==0
            for event in task.algorithm_trace:
                if event['operation']=='spec_identity':assert sp.sympify(event['residual'])==0
                if event['operation']=='spec_calc':
                    args=list(map(sp.sympify,event['operands']));op=event['operator']
                    result={'+':lambda:args[0]+args[1],'-':lambda:args[0]-args[1],
                            '*':lambda:args[0]*args[1],'/':lambda:args[0]/args[1],
                            'sin':lambda:sp.sin(args[0]),'cos':lambda:sp.cos(args[0]),
                            'sqrt':lambda:sp.sqrt(args[0]),'abs':lambda:sp.Abs(args[0])}[op]()
                    assert sp.simplify(result-sp.sympify(event['value']))==0
            assert len(task.solution_steps)==len(task.algorithm_trace)+1


def test_parameters_zero_launches_factories_and_visible_precision():
    for kind in ('projectile_max_height','projectile_range'):
        task=KinematicsTask(task_type=kind,v0=0,v=123,angle=45,g=10)
        task.solve();assert task.verify('0 m')==1 and task.v0==0
    task=generate_random_kinematics_task(task_type='projectile_range',v0=20,v=50,angle=45,g=10,reasoning_mode=True,output_format='latex')
    assert task.verify('40 m')==1 and task.reasoning_mode and task.output_format=='latex'
    task=generate_random_kinematics_task(task_type='accelerated_distance',v0=2,a=-1,t=4)
    assert task.verify('4 m')==1 and task.verify('0 m')==0 and task.verify('-4 m')==0
    with patch('re_rl.tasks.physics.mechanics.projectile_motion.task.random.uniform',side_effect=AssertionError('must_not_replace_zero')):
        task=ProjectileMotionTask(task_type='range',v0=0,angle=45,g=10)
    task.solve();assert task.verify('0 m')==1
    speed,angle=12.3456789,33.33337
    task=generate_random_projectile_motion_task(task_type='range',v0=speed,angle=angle,g=10,reasoning_mode=True)
    assert str(speed) in task.description and str(angle) in task.description
    assert F(task.computation_inputs['v0'])==F(str(speed)) and F(task.computation_inputs['angle'])==F(str(angle))
    expected=speed*speed*math.sin(2*math.radians(angle))/10
    assert task.verify(str(expected)+' m')==1
    assert task.verify(str(expected)+' s')==0
    task=ProjectileMotionTask.generate_random_task(task_type='velocity_at_height',v0=0,angle=30,g=10)
    assert task.height_query==0 and task.verify('0 m/s')==1
    task=generate_random_kinematics_task(task_type='find_velocity',s=-12,t=4)
    assert task.verify('-10.8 km/h')==1


@pytest.mark.parametrize('cls,kwargs',[
 (KinematicsTask,dict(task_type='bad')),(KinematicsTask,dict(t=-1)),(KinematicsTask,dict(v=True)),
 (KinematicsTask,dict(task_type='find_velocity',t=0)),(KinematicsTask,dict(task_type='find_velocity',s=10001,t=1)),
 (KinematicsTask,dict(task_type='accelerated_distance',v0=0,a=10000,t=2)),
 (KinematicsTask,dict(task_type='projectile_max_height',v0=-1)),(KinematicsTask,dict(task_type='projectile_range',angle=91)),
 (KinematicsTask,dict(task_type='circular_velocity',T=0)),(KinematicsTask,dict(task_type='circular_velocity',r=0)),
 (KinematicsTask,dict(task_type='circular_velocity',r=10000,T=1)),(KinematicsTask,dict(task_type='circular_acceleration',v=-1)),
 (ProjectileMotionTask,dict(task_type='bad')),(ProjectileMotionTask,dict(task_type=1)),
 (ProjectileMotionTask,dict(v0=-1)),(ProjectileMotionTask,dict(angle=-1)),(ProjectileMotionTask,dict(g=0)),
 (ProjectileMotionTask,dict(v0=float('nan'))),(ProjectileMotionTask,dict(task_type='velocity_at_height',height_query=-1)),
 (ProjectileMotionTask,dict(task_type='range',height_query=1)),
 (ProjectileMotionTask,dict(task_type='velocity_at_height',v0=10,angle=0,height_query=0.01)),
])
def test_invalid_domains(cls,kwargs):
    with pytest.raises(ValueError):cls(**kwargs)


def test_generation_diversity_and_common_factory_options():
    state=random.getstate()
    try:
        velocities=set()
        for seed in range(100):
            random.seed(seed)
            task=KinematicsTask(task_type='projectile_max_height',difficulty=1)
            assert 5<=task.v0<=10
            velocities.add(task.v0)
        assert len(velocities)>=95
        task=generate_random_projectile_motion_task(task_type='range',v0=10,angle=45,g=10,augment=False)
        assert task.verify(str(task.final_answer))==1
    finally:random.setstate(state)


def test_sampled_displacement_respects_velocity_bound_for_short_and_long_times():
    state=random.getstate()
    try:
        for seed in range(300):
            random.seed(seed)
            task=KinematicsTask(task_type='find_velocity',difficulty=10,t=2)
            assert abs(F(task.s)/F(task.t))<=300
        task=generate_random_kinematics_task(task_type='find_velocity',difficulty=10,t=10**6)
        assert task.verify(str(task.final_answer))==1
    finally:random.setstate(state)
