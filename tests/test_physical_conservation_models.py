"""Independent conservation, center-of-mass and numerical thermal-relaxation checks."""
from decimal import Decimal
from fractions import Fraction as F
import itertools
import json
import random
import operator
import pytest
from scipy.integrate import solve_ivp
from re_rl.tasks.physics.mechanics.momentum.task import MomentumTask
from re_rl.tasks.physics.thermodynamics.heat_transfer.task import HeatTransferTask,SPECIFIC_HEAT
from re_rl.tasks.physics.conservation_models import calculate,Model,Quantity,DIMS,render_number,parse_quantity
from re_rl.tasks.physics.generators import generate_random_momentum_task,generate_random_heat_transfer_task


def values(outputs):return {label:value for label,(value,unit) in outputs.items()}


def test_all_small_collisions_against_center_of_mass_and_conservation():
    for m1,m2 in itertools.product(range(1,5),repeat=2):
        for v1,v2 in itertools.product(range(-3,4),repeat=2):
            inputs=dict(m1=m1,m2=m2,v1=v1,v2=v2)
            center=F(m1*v1+m2*v2,m1+m2)
            incoming=F(m1*v1*v1+m2*v2*v2,2)
            elastic=values(calculate('momentum','elastic_collision',inputs,[]))
            w1,w2=elastic['v1_out'],elastic['v2_out']
            # Independently reflect both velocities in the center-of-mass frame.
            assert w1==center-(v1-center) and w2==center-(v2-center)
            assert m1*w1+m2*w2==m1*v1+m2*v2
            assert (m1*w1*w1+m2*w2*w2)/2==incoming
            assert w2-w1==v1-v2
            sticky=values(calculate('momentum','inelastic_collision',inputs,[]))['v_common']
            assert sticky==center and min(v1,v2)<=sticky<=max(v1,v2)
            assert incoming-(m1+m2)*sticky*sticky/2>=0
    assert values(calculate('momentum','elastic_collision',dict(m1=2,m2=2,v1=-3,v2=4),[]))==dict(v1_out=F(4),v2_out=F(-3))


def test_galilean_boost_and_impulse_signs():
    base=dict(m1=F(1,3),m2=F(7,5),v1=F(-2,3),v2=F(9,7))
    for kind in ('elastic_collision','inelastic_collision'):
        original=values(calculate('momentum',kind,base,[]))
        for boost in (-10,0,F(1,11),8):
            shifted=dict(base,v1=base['v1']+boost,v2=base['v2']+boost)
            transformed=values(calculate('momentum',kind,shifted,[]))
            assert transformed=={k:v+boost for k,v in original.items()}
    assert values(calculate('momentum','impulse',dict(F=-3,t=F(1,10)),[]))['J']==F(-3,10)
    assert values(calculate('momentum','impulse',dict(F=100,t=0),[]))['J']==0
    assert values(calculate('momentum','momentum',dict(m=Decimal('0.1'),v=Decimal('0.2')),[]))['p']==F(1,50)


def test_thermal_models_against_enthalpy_and_numerical_relaxation():
    cold,hot,m1,m2=F(20),F(80),F(2),F(3)
    target=F(56)
    inputs=dict(m1=m1,m2=m2,T1=cold,T2=hot,c=4186)
    assert values(calculate('heat_transfer','mixing',inputs,[]))['T_final']==target
    # Two isolated bodies exchanging heat with equal/constant c. Conductance=c.
    def rhs(t,temperatures):
        a,b=temperatures
        return [(b-a)/float(m1),-(b-a)/float(m2)]
    experiment=solve_ivp(rhs,[0,100],[float(cold),float(hot)],rtol=1e-10,atol=1e-11)
    assert experiment.success
    assert experiment.y[:,-1]==pytest.approx([float(target)]*2,abs=1e-7)
    for a,b in experiment.y.T:
        assert float(m1)*a+float(m2)*b==pytest.approx(float(m1*cold+m2*hot),abs=1e-9)
    for a,b in ((0,100),(100,0),(25,25)):
        out=values(calculate('heat_transfer','mixing',dict(m1=1,m2=4,T1=a,T2=b,c=4186),[]))['T_final']
        assert min(a,b)<=out<=max(a,b)
    heat=values(calculate('heat_transfer','heat_capacity',dict(m=Decimal('0.1'),T1=Decimal('25.25'),T2=Decimal('43.75'),c=385,substance='copper'),[]))['Q']
    assert heat==F(2849,4)
    cooling=values(calculate('heat_transfer','heat_capacity',dict(m=1,T1=0,T2=-10,c=2090,substance='ice'),[]))['Q']
    assert cooling==-20900
    assert values(calculate('heat_transfer','phase_change',dict(m=F(3,2),lambda_ice=334000),[]))['Q']==501000
    assert values(calculate('heat_transfer','efficiency',dict(Q1=10,Q2=4),[]))['eta']==60


@pytest.mark.parametrize('cls',[MomentumTask,HeatTransferTask])
@pytest.mark.parametrize('language',['ru','en'])
def test_every_subtype_level_real_arithmetic_dimensions_and_stability(cls,language):
    operators={'+':operator.add,'-':operator.sub,'*':operator.mul,'/':operator.truediv}
    for level in range(1,11):
        for kind in cls.TASK_TYPES:
            random.seed(level)
            task=cls(task_type=kind,language=language,difficulty=level,reasoning_mode=True)
            description=task.description;state=random.getstate();task.solve()
            assert task.reasoning_mode is True and task.difficulty==level
            assert random.getstate()==state and task.description==description
            saved=json.dumps(task.get_result(),sort_keys=True)
            answer=task.final_answer;task.final_answer='stale';task.physical_outputs={'invalid':999}
            task.solve();assert json.dumps(task.get_result(),sort_keys=True)==saved
            assert task.verify('<answer>'+answer+'</answer>')==1
            assert task.verify('junk '+answer)==0
            assert len(task.solution_steps)==len(task.algorithm_trace)+1
            assert 'outputs' not in task.computation_inputs
            for event in task.algorithm_trace:
                if event['operation']=='phys_calc':
                    assert F(event['value'])==operators[event['operator']](F(event['left']),F(event['right']))
                    a,b=event['left_dim'],event['right_dim']
                    if event['operator'] in ('+','-'):assert a==b==event['dimension']
                    else:
                        dims=[x+y if event['operator']=='*' else x-y for x,y in zip(a,b)]
                        assert event['dimension']==dims
                elif event['operation']=='phys_balance':assert F(event['left'])==F(event['right']) and F(event['residual'])==0
                elif event['operation']=='phys_output':assert event['dimension']==list(DIMS[event['unit']])


def test_signed_collision_grader_requires_both_velocities_and_correct_units():
    task=MomentumTask(task_type='elastic_collision',m1=1,m2=2,v1=3,v2=0)
    task.solve();assert task.physical_outputs['v1_out']['value']=='-1'
    assert task.verify('v1_out=-1 m/s; v2_out=2 m/s')==1
    assert task.verify('v1_out=−1,0 m/s; v2_out=2,0 m/s')==1
    assert task.verify('v2_out=7.2 km/h; v1_out=-3.6 km/h')==1
    for text in ('v1_out=1 m/s; v2_out=2 m/s','v1_out=-1 J; v2_out=2 m/s','v1_out=-1 m/s; v1_out=2 m/s','2 m/s','v1_out=-1 m/s; v2_out=2 m/s junk'):
        assert task.verify(text)==0
    task.v2=-3
    assert task.verify('v1_out=-5 m/s; v2_out=1 m/s')==1
    task=MomentumTask(task_type='momentum',m=2,v=-3)
    assert task.verify('-6 N*s')==1 and task.verify('6 kg*m/s')==0
    assert task.verify('-6 J')==0
    assert task.verify('1e999999999 kg*m/s')==0


def test_units_temperature_offsets_percent_and_rounding():
    task=HeatTransferTask(task_type='mixing',m1=1,m2=1,T1=20,T2=80)
    assert task.verify('50 °C')==1 and task.verify('323.15 K')==1
    assert task.verify('323,15 K')==1
    assert task.verify('50 K')==0 and task.verify('50 J')==0
    task=HeatTransferTask(task_type='phase_change',m=1)
    assert task.verify('334 kJ')==1 and task.verify('334000 J')==1
    assert task.verify('334 J')==0
    task=HeatTransferTask(task_type='efficiency',Q1=1,Q2=F(1,3))
    task.solve();assert task.final_answer.startswith('66.6667') and task.verify(task.final_answer)==1
    assert task.verify('66.66666666666667 %')==1 and task.verify('2/3')==0
    assert parse_quantity('nan J','J') is None and parse_quantity('1/0 J','J') is None
    for value,text in ((F(1,3),'0.3333'),(F(1,20000),'0'),(F(3,20000),'0.0002'),(F(-1,20000),'0')):
        assert render_number(value)==text
    model=Model([])
    with pytest.raises(ValueError,match='dimension_mismatch'):
        model.calc('bad','+',Quantity(F(1),DIMS['kg']),Quantity(F(1),DIMS['J']))


def test_factories_forward_parameters_and_small_heat_input():
    task=generate_random_momentum_task(task_type='inelastic_collision',m1=2,m2=3,v1=-2,v2=4,reasoning_mode=True,output_format='latex')
    assert task.reasoning_mode and task.output_format=='latex' and task.verify('1.6 m/s')==1
    task=generate_random_heat_transfer_task(task_type='efficiency',Q1=1,reasoning_mode=True)
    assert 0<task.Q2<=task.Q1 and task.verify(task.final_answer)==1
    task=generate_random_heat_transfer_task(task_type='heat_capacity',substance='ice',m=1,T1=-10,T2=0)
    assert task.verify('20900 J')==1
    for level in range(1,11):
        for substance in SPECIFIC_HEAT:
            task=HeatTransferTask(task_type='heat_capacity',substance=substance,difficulty=level)
            if substance=='ice':assert -100<=task.T1<=task.T2<=0
            elif substance=='water':assert 0<=task.T1<=task.T2<=100


@pytest.mark.parametrize('cls,kwargs',[
    (MomentumTask,dict(task_type='bad')),(MomentumTask,dict(m=0)),(MomentumTask,dict(m=True)),
    (MomentumTask,dict(v=float('nan'))),(MomentumTask,dict(v=float('inf'))),(MomentumTask,dict(v=10001)),
    (MomentumTask,dict(task_type='impulse',t=-1)),(MomentumTask,dict(task_type='elastic_collision',m2=-1)),
    (HeatTransferTask,dict(task_type='bad')),(HeatTransferTask,dict(substance='unknown')),(HeatTransferTask,dict(substance='')),(HeatTransferTask,dict(substance=[])),
    (HeatTransferTask,dict(substance='ice',T1=-1,T2=1)),(HeatTransferTask,dict(substance='water',T1=-1)),
    (HeatTransferTask,dict(task_type='mixing',substance='ice')),(HeatTransferTask,dict(task_type='mixing',T2=101)),
    (HeatTransferTask,dict(task_type='phase_change',m=-1)),(HeatTransferTask,dict(task_type='phase_change',substance='water')),
    (HeatTransferTask,dict(task_type='efficiency',Q1=0)),(HeatTransferTask,dict(task_type='efficiency',Q1=1,Q2=2)),
    (HeatTransferTask,dict(task_type='efficiency',Q1=1,Q2=0)),(HeatTransferTask,dict(m=float('nan'))),
])
def test_invalid_physical_domains(cls,kwargs):
    with pytest.raises(ValueError):cls(**kwargs)
