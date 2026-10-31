"""Independent ODE trajectories, forced-response maxima and crest arrival times."""
import json
import math
import random
from fractions import Fraction as F
import numpy as np
import pytest
import sympy as sp
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from re_rl.tasks.physics.oscillations.oscillations.task import OscillationsTask
from re_rl.tasks.physics.waves.waves.task import WavesTask
from re_rl.tasks.physics.spectrum_models import calculate,Model,Quantity,DIMS
from re_rl.tasks.physics.generators import generate_random_waves_task,generate_random_oscillations_task


def numeric(outputs,label):return float(sp.N(outputs[label][0],30))


def integrate_period(rate,period,initial):
    result=solve_ivp(lambda t,y:[y[1],-rate*y[0]],[0,period],initial,rtol=1e-11,atol=1e-12,dense_output=True)
    assert result.success and result.y[:,-1]==pytest.approx(initial,abs=1e-9)
    return result


def test_harmonic_requested_speed_phase_and_conserved_trajectory():
    inputs=dict(A=F(2,5),omega=3,phi=F(37,100));events=[]
    outputs=calculate('oscillations','harmonic',inputs,events)
    assert set(outputs)=={'T','v_max'} and numeric(outputs,'v_max')==pytest.approx(1.2)
    period=numeric(outputs,'T');initial=[0.4*math.cos(0.37),-1.2*math.sin(0.37)]
    trajectory=integrate_period(9,period,initial)
    at_peak=trajectory.sol((math.pi/2-0.37)/3)
    assert abs(at_peak[1])==pytest.approx(numeric(outputs,'v_max'),rel=1e-10)
    energy=trajectory.y[1]**2+9*trajectory.y[0]**2
    assert energy==pytest.approx(np.full_like(energy,1.44),abs=1e-9)
    initials={e['label']:float(sp.N(sp.sympify(e['value']),30)) for e in events if e['operation']=='spec_calc' and e['label'] in ('x(0)','v(0)')}
    assert [initials['x(0)'],initials['v(0)']]==pytest.approx(initial,abs=1e-12)
    energy_event=next(e for e in events if e['operation']=='spec_calc' and e['label']=='E/m')
    assert sp.simplify(sp.sympify(energy_event['value'])-sp.Rational(18,25))==0


def test_spring_and_linear_pendulum_against_odes_and_finite_angle_limit():
    spring=calculate('oscillations','spring',dict(k=8,m=2),[])
    assert set(spring)=={'T','f'}
    period=numeric(spring,'T');frequency=numeric(spring,'f')
    integrate_period(4,period,[0.3,0])
    assert frequency==pytest.approx(1/period) and frequency!=pytest.approx(2)
    pendulum=calculate('oscillations','pendulum',dict(L=4,g=1),[])
    period=numeric(pendulum,'T');integrate_period(0.25,period,[0.02,0])
    def cross(t,y):return y[0]
    cross.direction=-1;cross.terminal=True
    nonlinear=solve_ivp(lambda t,y:[y[1],-0.25*math.sin(y[0])],[0,period],[0.1,0],events=cross,rtol=1e-11,atol=1e-12)
    actual=4*nonlinear.t_events[0][0]
    # The small-angle model is an approximation to a finite-amplitude pendulum.
    assert 0.0001<(actual-period)/period<0.001


def test_lc_free_energy_and_series_current_resonance():
    L,C,R=2,0.5,3
    outputs=calculate('oscillations','lc_circuit',dict(L_ind=L,C=C),[])
    frequency=numeric(outputs,'f');period=1/frequency
    trajectory=integrate_period(1/(L*C),period,[0.1,0])
    energy=L*trajectory.y[1]**2/2+trajectory.y[0]**2/(2*C)
    assert energy==pytest.approx(np.full_like(energy,0.01),abs=1e-10)
    resonance_events=[]
    resonance=calculate('oscillations','resonance',dict(L_ind=L,C=C),resonance_events)
    certificate=next(e for e in resonance_events if e['operation']=='spec_current_peak')
    assert certificate['reactance']==certificate['square']=='0'
    peak_omega=2*math.pi*numeric(resonance,'f')
    amplitudes=[]
    for factor in (0.8,1,1.2):
        omega=peak_omega*factor;cycle=2*math.pi/omega
        solution=solve_ivp(lambda t,y:[y[1],(math.cos(omega*t)-R*y[1]-y[0]/C)/L],
                           [0,30*cycle],[0,0],rtol=1e-9,atol=1e-11,dense_output=True)
        current=solution.sol(np.linspace(25*cycle,30*cycle,3001))[1]
        measured=(max(current)-min(current))/2
        expected=1/math.sqrt(R*R+(omega*L-1/(omega*C))**2)
        assert measured==pytest.approx(expected,rel=1e-5)
        amplitudes.append(measured)
    assert amplitudes[1]>amplitudes[0] and amplitudes[1]>amplitudes[2]


def test_doppler_against_geometric_wavefront_arrivals():
    for speed in (1,100,343):
        for source_fraction in (F(-4,5),0,F(1,5),F(4,5)):
            for observer_fraction in (F(-4,5),0,F(1,5),F(4,5)):
                vs=float(source_fraction*speed);vo=float(observer_fraction*speed);f0=100
                outputs=calculate('waves','doppler',dict(v=speed,v_s=source_fraction*speed,v_o=observer_fraction*speed,f0=f0),[])
                arrivals=[]
                for n in range(3):
                    emission=n/f0
                    def separation(t):return vs*emission+speed*(t-emission)-(10000-vo*t)
                    arrivals.append(brentq(separation,emission,1000000))
                observed=1/(arrivals[2]-arrivals[1])
                assert numeric(outputs,'f_observed')==pytest.approx(observed,rel=2e-8)
    approaching=numeric(calculate('waves','doppler',dict(v=343,v_s=20,v_o=0,f0=100),[]),'f_observed')
    receding=numeric(calculate('waves','doppler',dict(v=343,v_s=-20,v_o=0,f0=100),[]),'f_observed')
    assert approaching>100>receding


@pytest.mark.parametrize('cls',[OscillationsTask,WavesTask])
@pytest.mark.parametrize('language',['ru','en'])
def test_all_subtypes_all_levels_symbolic_replay_and_cache_poison(cls,language):
    for level in range(1,11):
        for kind in cls.TASK_TYPES:
            random.seed(level);task=cls(task_type=kind,language=language,difficulty=level,reasoning_mode=True)
            description=task.description;state=random.getstate();task.solve()
            assert task.reasoning_mode and task.difficulty==level
            assert random.getstate()==state and task.description==description
            original=json.dumps(task.get_result(),sort_keys=True);answer=task.final_answer
            task.final_answer='stale';task.spectrum_outputs={'bad':999};task.solve()
            assert json.dumps(task.get_result(),sort_keys=True)==original
            assert task.verify('<answer>'+answer+'</answer>')==1
            assert task.verify('junk '+answer)==0
            assert 'outputs' not in task.computation_inputs
            for e in task.algorithm_trace:
                if e['operation']=='spec_identity':assert sp.sympify(e['residual'])==0
                if e['operation']=='spec_output':assert tuple(e['dimension'])==DIMS[e['unit']]
                if e['operation']=='spec_calc':
                    args=list(map(sp.sympify,e['operands']));op=e['operator']
                    expected={'+':lambda:args[0]+args[1],'-':lambda:args[0]-args[1],
                              '*':lambda:args[0]*args[1],'/':lambda:args[0]/args[1],
                              'sqrt':lambda:sp.sqrt(args[0]),'cos':lambda:sp.cos(args[0]),'sin':lambda:sp.sin(args[0])}[op]()
                    assert sp.simplify(sp.sympify(e['value'])-expected)==0
            if kind=='sound_speed':assert 0<task.f*task.lambda_<=100000


def test_factories_explicit_parameters_no_period_rounding_or_length_clamp():
    task=generate_random_oscillations_task(task_type='pendulum',L=1000,g=1,reasoning_mode=True,output_format='latex')
    assert task.L==1000 and task.reasoning_mode and task.output_format=='latex'
    assert task.verify(str(2*math.pi*math.sqrt(1000))+' s')==1
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr('re_rl.tasks.physics.oscillations.oscillations.task.random.uniform',lambda a,b:b)
        task=OscillationsTask(task_type='pendulum',difficulty=10)
    assert task.L==1000
    task=generate_random_waves_task(task_type='period',f=100000000,reasoning_mode=True)
    assert task.verify('1e-8 s')==1 and task.verify('0 s')==0
    assert task.verify('0.01 us')==1 and task.verify('1e-8 Hz')==0
    task=generate_random_waves_task(task_type='wavelength',f=1,v=1)
    assert task.verify('100 cm')==1
    task=generate_random_waves_task(task_type='doppler',v=1,v_s=0,v_o=0,f0=1)
    assert task.verify('1 Hz')==1
    for kwargs in (dict(f=1),dict(lambda_=F(1,3)),dict(f=1,lambda_=4)):
        task=WavesTask.generate_random_task(task_type='sound_speed',**kwargs)
        assert task.verify(task.final_answer)==1
    # Extreme but bounded ideal-model parameters must still have a nonzero, gradable answer.
    task=WavesTask.generate_random_task(task_type='frequency',v=100000,lambda_=1e-100)
    assert task.verify(task.final_answer)==1


def test_requested_outputs_and_units_cannot_be_swapped_or_omitted():
    task=OscillationsTask(task_type='harmonic',A=1,omega=2,phi=0)
    assert task.verify(f'T={math.pi} s; v_max=2 m/s')==1
    assert task.verify(f'T={math.pi} s; v_max={1/math.pi} Hz')==0
    assert task.verify(f'T={math.pi} s')==0
    task=OscillationsTask(task_type='spring',m=1,k=4)
    assert task.verify(f'T={math.pi} s; f={1/math.pi} Hz')==1
    assert task.verify(f'T={math.pi} s; f=2 Hz')==0
    assert task.verify(f'T={math.pi} s; f={1/math.pi} rad/s')==0
    assert task.verify(f'T={math.pi} s; T={math.pi} s')==0
    task=WavesTask(task_type='frequency',v=1000,lambda_=1)
    assert task.verify('1 kHz')==1
    model=Model([])
    with pytest.raises(ValueError,match='invalid_dimensioned_square_root'):
        model.calc('bad','sqrt',Quantity(sp.Integer(2),DIMS['m']))
    with pytest.raises(ValueError,match='trig_requires_dimensionless_phase'):
        model.calc('bad','sin',Quantity(sp.Integer(1),DIMS['s']))


@pytest.mark.parametrize('cls,kwargs',[
 (OscillationsTask,dict(task_type='bad')),(OscillationsTask,dict(task_type='harmonic',A=0)),
 (OscillationsTask,dict(task_type='harmonic',A=-1)),(OscillationsTask,dict(task_type='harmonic',omega=0)),
 (OscillationsTask,dict(task_type='harmonic',A=1000,omega=10000)),
 (OscillationsTask,dict(L=0)),(OscillationsTask,dict(g=-1)),(OscillationsTask,dict(L=True)),
 (OscillationsTask,dict(task_type='spring',m=0)),(OscillationsTask,dict(task_type='spring',k=-1)),
 (OscillationsTask,dict(task_type='lc_circuit',C=0)),(OscillationsTask,dict(task_type='resonance',L_ind=-1)),
 (WavesTask,dict(f=0)),(WavesTask,dict(v=0)),(WavesTask,dict(v=100001)),
 (WavesTask,dict(task_type='period',f=float('nan'))),(WavesTask,dict(task_type='frequency',lambda_=0)),
 (WavesTask,dict(task_type='sound_speed',f=100000000,lambda_=1000000)),
 (WavesTask,dict(task_type='doppler',v=100,v_s=100)),(WavesTask,dict(task_type='doppler',v=100,v_s=-100)),
 (WavesTask,dict(task_type='doppler',v=100,v_o=100)),(WavesTask,dict(task_type='doppler',v=100,v_o=-100)),
 (WavesTask,dict(task_type='doppler',v=100,f0=-1)),
])
def test_invalid_domains(cls,kwargs):
    with pytest.raises(ValueError):cls(**kwargs)


def test_shared_dimension_axes_and_resource_precision_are_explicit():
    from re_rl.tasks.physics.conservation_models import DIMS as other_dims,number,DIMENSION_AXES
    assert DIMENSION_AXES==('M','L','T','Theta','I')
    for unit in DIMS.keys() & other_dims.keys():assert DIMS[unit]==other_dims[unit]
    for cls in (OscillationsTask,WavesTask):
        task=cls.generate_random_task()
        assert task.computation_inputs['dimension_axes']==list(DIMENSION_AXES)
    with pytest.raises(ValueError,match='physical_precision_out_of_range'):
        number(F(1,2**2000))
