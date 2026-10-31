"""Independent Newton systems, vector projections, work integrals and ODE energy checks."""
from fractions import Fraction as F
import itertools
import json
import math
import random
import numpy as np
import pytest
import sympy as sp
from scipy.integrate import quad,solve_ivp
from re_rl.tasks.physics.mechanics.energy.task import EnergyTask
from re_rl.tasks.physics.mechanics.dynamics.task import DynamicsTask
from re_rl.tasks.physics.mechanical_models import calculate,DIMS
from re_rl.tasks.physics.generators import generate_random_energy_task,generate_random_dynamics_task


def value(outputs):return next(iter(outputs.values()))[0]


def test_atwood_against_independent_newton_linear_system_and_ode_energy():
    for m1,m2 in itertools.product(range(1,7),repeat=2):
        for g in (F(1),F(981,100),F(10)):
            events=[];tension=value(calculate('dynamics','tension',dict(m1=m1,m2=m2,g=g),events))
            # Unknowns T,a; upwards for mass 1 and downwards for mass 2.
            T,a=sp.Matrix([[1,-m1],[1,m2]]).inv()*sp.Matrix([m1*sp.Rational(g),m2*sp.Rational(g)])
            assert tension==T and abs(a)<g and T>0
            actual=next(e for e in events if e['operation']=='spec_calc' and e['label']=='a_signed')
            assert sp.sympify(actual['value'])==a
    m1,m2,g=2,3,9.81
    T,a=np.linalg.solve([[1,-m1],[1,m2]],[m1*g,m2*g])
    trajectory=solve_ivp(lambda t,y:[y[1],a],[0,0.5],[0,0],rtol=1e-11,atol=1e-12)
    x,v=trajectory.y
    energy=(m1+m2)*v*v/2+m1*g*(1+x)+m2*g*(1-x)
    assert energy==pytest.approx(np.full_like(energy,(m1+m2)*g),abs=1e-9)
    assert float(value(calculate('dynamics','tension',dict(m1=m1,m2=m2,g=g),[])))==pytest.approx(T)
    assert value(calculate('dynamics','tension',dict(m1=3,m2=3,g=10),[]))==30


def test_incline_against_cartesian_force_projection_and_work_energy():
    for angle in (0,15,30,37.5,45,60,90):
        m,g=3,9.81;radians=math.radians(angle)
        tangent=np.array([math.cos(radians),-math.sin(radians)])
        normal=np.array([math.sin(radians),math.cos(radians)])
        gravity=np.array([0,-m*g]);reaction=-np.dot(gravity,normal)
        net=gravity+reaction*normal
        expected=float(np.dot(net,tangent))
        actual=value(calculate('dynamics','inclined_plane',dict(m=m,g=g,angle=angle),[]))
        assert float(actual)==pytest.approx(expected,abs=1e-11)
        acceleration=expected/m
        trajectory=solve_ivp(lambda t,y:[y[1],acceleration],[0,0.5],[0,0],rtol=1e-11,atol=1e-12)
        distance,speed=trajectory.y[:,-1]
        assert m*speed*speed/2==pytest.approx(m*g*distance*math.sin(radians),abs=1e-10)
    assert value(calculate('dynamics','inclined_plane',dict(m=3,g=10,angle=0),[]))==0
    assert value(calculate('dynamics','inclined_plane',dict(m=3,g=10,angle=90),[]))==30


def test_sliding_friction_dissipation_and_stationary_support():
    m,g,mu,v0=2,9.81,0.2,10
    friction=float(value(calculate('dynamics','friction',dict(m=m,g=g,mu=mu),[])))
    def stop(t,y):return y[1]
    stop.direction=-1;stop.terminal=True
    motion=solve_ivp(lambda t,y:[y[1],-friction/m],[0,10],[0,v0],events=stop,rtol=1e-11,atol=1e-12)
    assert motion.t_events[0][0]==pytest.approx(v0/(mu*g))
    distance=motion.y_events[0][0][0]
    assert friction*distance==pytest.approx(m*v0*v0/2)
    assert value(calculate('dynamics','friction',dict(m=2,g=10,mu=0),[]))==0
    assert value(calculate('dynamics','friction',dict(m=2,g=10,mu=1.5),[]))==30
    assert value(calculate('dynamics','weight',dict(m=2,g=10),[]))==20


def test_work_against_vector_line_integrals_and_exact_perpendicular_zero():
    for angle in (0,30,45,60,90,120,150,180):
        force,distance=23,7
        vector=np.array([force*math.cos(math.radians(angle)),force*math.sin(math.radians(angle))])
        integral=quad(lambda t:np.dot(vector,[distance,0]),0,1)[0]
        actual=value(calculate('energy','work_angle',dict(F=force,s=distance,angle=angle),[]))
        assert float(actual)==pytest.approx(integral,abs=1e-11)
    assert value(calculate('energy','work_angle',dict(F=23,s=7,angle=90),[]))==0
    assert value(calculate('energy','work_angle',dict(F=23,s=7,angle=180),[]))==-161
    assert value(calculate('energy','work',dict(F=0,s=10),[]))==0
    assert value(calculate('energy','work_angle',dict(F=10,s=0,angle=45),[]))==0


def test_free_fall_with_signed_initial_velocity_against_ode_impact():
    def impact(t,y):return y[0]
    impact.direction=-1;impact.terminal=True
    for v0,g,h in itertools.product((-10,0,10),(1,9.81),(1,20)):
        result=calculate('energy','conservation',dict(m=3,g=g,h=h,v0=v0),[])
        speed=float(value(result));time_bound=(v0+math.sqrt(v0*v0+2*g*h))/g+1
        motion=solve_ivp(lambda t,y:[y[1],-g],[0,time_bound],[h,v0],events=impact,rtol=1e-11,atol=1e-12)
        assert len(motion.t_events[0])==1
        assert speed==pytest.approx(abs(motion.y_events[0][0][1]),rel=1e-10)
        energy=3*motion.y[1]**2/2+3*g*motion.y[0]
        assert energy==pytest.approx(np.full_like(energy,3*v0*v0/2+3*g*h),abs=1e-8)
        other=value(calculate('energy','conservation',dict(m=30,g=g,h=h,v0=v0),[]))
        assert float(other)==pytest.approx(speed)
    assert value(calculate('energy','conservation',dict(m=1,g=10,h=0,v0=0),[]))==0


def test_signed_potential_reference_energy_and_average_not_instantaneous_power():
    potential=lambda h:value(calculate('energy','potential_energy',dict(m=2,g=10,h=h),[]))
    assert potential(-3)==-60 and potential(0)==0 and potential(3)==60
    assert potential(-2)-potential(-3)==20
    assert value(calculate('energy','kinetic_energy',dict(m=2,v=-3),[]))==9
    assert value(calculate('energy','kinetic_energy',dict(m=2,v=0),[]))==0
    # Constant force 3 N, v(t)=2t for 0..2 s: average power is 6 W, final instantaneous is 12 W.
    work=quad(lambda t:3*2*t,0,2)[0]
    assert value(calculate('energy','power',dict(W=work,t=2),[]))==6
    assert value(calculate('energy','power',dict(W=-12,t=2),[]))==-6
    assert value(calculate('dynamics','newton_second',dict(F=-12,m=3),[]))==-4
    assert value(calculate('dynamics','find_force',dict(a=-4,m=3),[]))==-12


@pytest.mark.parametrize('cls',[EnergyTask,DynamicsTask])
@pytest.mark.parametrize('language',['ru','en'])
def test_every_subtype_all_levels_exact_execution_units_and_stability(cls,language):
    for level in range(1,11):
        for kind in cls.TASK_TYPES:
            random.seed(level);task=cls(task_type=kind,language=language,difficulty=level,reasoning_mode=True)
            description=task.description;state=random.getstate();task.solve()
            assert random.getstate()==state and task.description==description
            assert task.reasoning_mode and task.difficulty==level
            original=json.dumps(task.get_result(),sort_keys=True);answer=task.final_answer
            task.final_answer='stale';task.mechanical_outputs={'wrong':999}
            assert task.verify(answer)==1
            task.solve();assert json.dumps(task.get_result(),sort_keys=True)==original
            assert task.verify('junk '+answer)==0
            assert len(task.solution_steps)==len(task.algorithm_trace)+1
            assert 'outputs' not in task.computation_inputs
            for event in task.algorithm_trace:
                if event['operation']=='spec_identity':assert sp.sympify(event['residual'])==0
                if event['operation']=='spec_output':assert tuple(event['dimension'])==DIMS[event['unit']]
                if event['operation']=='spec_calc':
                    args=list(map(sp.sympify,event['operands']));op=event['operator']
                    expected={'+':lambda:args[0]+args[1],'-':lambda:args[0]-args[1],
                              '*':lambda:args[0]*args[1],'/':lambda:args[0]/args[1],
                              'cos':lambda:sp.cos(args[0]),'sin':lambda:sp.sin(args[0]),'sqrt':lambda:sp.sqrt(args[0])}[op]()
                    assert sp.simplify(expected-sp.sympify(event['value']))==0


def test_factories_explicit_gravity_initial_velocity_and_unit_aware_sign_checks():
    task=generate_random_energy_task(task_type='conservation',m=2,h=10,g=5,v0=10,reasoning_mode=True,output_format='latex')
    assert task.g==5 and task.v0==10 and task.output_format=='latex' and task.reasoning_mode
    assert task.verify(str(math.sqrt(200))+' m/s')==1
    task=generate_random_energy_task(task_type='work_angle',F=2,s=3,angle=180)
    assert task.verify('-6 J')==1 and task.verify('6 J')==0 and task.verify('-6 N')==0
    task=generate_random_energy_task(task_type='work_angle',F=1000,s=1000,angle=90)
    assert task.verify('0 J')==1 and task.verify('0.001 J')==0
    task=generate_random_energy_task(task_type='power',W=2000,t=2)
    assert task.verify('1 kW')==1 and task.verify('1000 J/s')==1 and task.verify('1000 J')==0
    task=generate_random_dynamics_task(task_type='newton_second',m=2,F=-4)
    assert task.verify('-2 N/kg')==1 and task.verify('-2 m/s²')==1 and task.verify('-2 m/s')==0
    task=generate_random_dynamics_task(task_type='friction',m=100,g=10,mu=2)
    assert task.verify('2 kN')==1 and task.verify('-2 kN')==0
    task=generate_random_dynamics_task(task_type='tension',m1=1,m2=1,g=F(1,2))
    assert task.verify('500 mN')==1


@pytest.mark.parametrize('cls,kwargs',[
 (EnergyTask,dict(task_type='bad')),(EnergyTask,dict(F=-1)),(EnergyTask,dict(s=-1)),
 (EnergyTask,dict(task_type='work_angle',angle=-1)),(EnergyTask,dict(task_type='work_angle',angle=181)),
 (EnergyTask,dict(task_type='kinetic_energy',m=0)),(EnergyTask,dict(task_type='kinetic_energy',m=True)),
 (EnergyTask,dict(task_type='kinetic_energy',v=10001)),(EnergyTask,dict(task_type='power',t=0)),
 (EnergyTask,dict(task_type='potential_energy',g=0)),(EnergyTask,dict(task_type='conservation',h=-1)),
 (EnergyTask,dict(task_type='conservation',h=1e12)),(EnergyTask,dict(task_type='conservation',v0=float('nan'))),
 (DynamicsTask,dict(m=-1)),(DynamicsTask,dict(F=float('inf'))),(DynamicsTask,dict(task_type='bad')),
 (DynamicsTask,dict(task_type='weight',g=0)),(DynamicsTask,dict(task_type='friction',mu=-1)),
 (DynamicsTask,dict(task_type='friction',mu=True)),(DynamicsTask,dict(task_type='inclined_plane',angle=91)),
 (DynamicsTask,dict(task_type='tension',m2=0)),(DynamicsTask,dict(task_type='find_force',a=float('nan'))),
])
def test_invalid_domains(cls,kwargs):
    with pytest.raises(ValueError):cls(**kwargs)
