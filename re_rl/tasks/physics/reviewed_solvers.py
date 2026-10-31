"""Physics computations from stated quantities, with exact inverse operations."""
from fractions import Fraction
from re_rl.tasks.reviewed_formulas import PHYSICS, execute_spec
from re_rl.tasks.formula_trace import evaluate


def halve(initial, steps=None, remaining=None):
    value = Fraction(initial)
    count = 0
    while (count < steps if steps is not None else value > remaining):
        value /= 2
        count += 1
    if remaining is not None:
        assert value == remaining
    return value if steps is not None else count


def visible_mobile(node, hidden):
    if node['kind'] == 'leaf':
        return {'kind':'leaf','id':node['id'],'mass':None if node['id'] == hidden else node['mass']}
    return {'kind':'rod','id':node['id'],'arm_l':node['arm_l'],'arm_r':node['arm_r'],
            'left':visible_mobile(node['left'],hidden),'right':visible_mobile(node['right'],hidden)}


def mobile(tree):
    equations = []
    def reduce(node):
        if node['kind'] == 'leaf':
            return (Fraction(1),Fraction(0)) if node['mass'] is None else (Fraction(0),Fraction(node['mass']))
        left_a,left_b = reduce(node['left'])
        right_a,right_b = reduce(node['right'])
        coefficient = node['arm_l'] * left_a - node['arm_r'] * right_a
        constant = node['arm_r'] * right_b - node['arm_l'] * left_b
        if coefficient:
            equations.append(constant/coefficient)
        else:
            assert constant == 0
        return left_a+right_a,left_b+right_b
    a,b = reduce(tree)
    assert equations and len(set(equations)) == 1
    hidden = equations[0]
    load = a*hidden+b
    return hidden,load


def solve_physics(task, name, trace):
    kind = task.task_type
    if name in ('kinematics','projectile_motion'):
        from re_rl.tasks.physics.trajectory_models import prepare_task
        return prepare_task(task,trace.events),True
    if name in ('energy','dynamics'):
        from re_rl.tasks.physics.mechanical_models import prepare_task
        return prepare_task(task,trace.events),True
    if name in ('oscillations','waves'):
        from re_rl.tasks.physics.spectrum_models import prepare_task
        return prepare_task(task,trace.events),True
    if name in ('momentum','heat_transfer'):
        from re_rl.tasks.physics.conservation_models import prepare_task
        return prepare_task(task,trace.events),True
    if name in PHYSICS:
        return execute_spec(task,name,trace,PHYSICS)
    if name in ('ac_circuits','unit_conversion'):
        keys = ('R','L','C','f') if name == 'ac_circuits' else ('value','conversion','factor')
        inputs = {key:getattr(task,key) for key in keys}
        if name == 'ac_circuits':
            task.C_farads = evaluate('C * Fraction(1, 1000000)', {'C':task.C}, trace.events)
        trace.call(task._solve_before_trace)
        return inputs, True
    if name == 'adiabatic':
        specs = {'adiabatic':{
            'temperature':[('answer','T1 * (V1 / V2) ** (gamma - 1)')],
            'pressure':[('answer','P1 * (V1 / V2) ** gamma')],
            'volume':[('answer','V1 * (T1 / T2) ** (1 / (gamma - 1))')]}}
        return execute_spec(task,name,trace,specs)
    if name == 'meeting_motion':
        expression = '(xb - xa) / (va + vb)' if task.mode == 'head_on' else '(xa - xb) / (vb - va)'
        statements = [('meeting_time',expression)]
        statements.append(('answer','meeting_time' if kind == 'time' else 'xa + va * meeting_time'))
        return execute_spec(task,name,trace,{name:{'*':statements}})
    if name == 'half_life_steps':
        if kind in ('remaining','activity'):
            initial = task.n0 if kind == 'remaining' else task.activity0
            task.answer = trace.call(halve,initial,steps=task.k)
            return {'initial':initial,'steps':task.k}
        task.answer = trace.call(halve,task.n0,remaining=task.remaining)
        return {'initial':task.n0,'remaining':task.remaining}
    if name == 'mobile_torque':
        tree = visible_mobile(task.root,task.k)
        hidden,load = trace.call(mobile,tree)
        task.hidden_mass,task.load = int(hidden),int(load)
        task.answer = task.hidden_mass if kind == 'hidden' else task.load
        return {'tree':tree,'hidden_leaf':task.k}
    raise NotImplementedError(name)
