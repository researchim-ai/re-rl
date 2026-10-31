"""Explicit inverse formulas use only quantities supplied by the problem."""
import ast
from re_rl.tasks.formula_trace import evaluate, _FUNCTIONS

# Each pair is (destination, expression). Destinations are computed in order.
MATH = {
 'age_gap': {'gap': [('answer','older - young')], 'twice': [('answer','older - 2 * young')]},
 'clock_hands': {'*': [('raw','abs(60 * hour - 11 * minute) / 2'), ('smaller','min(raw, 360 - raw)'), ('larger','360 - smaller')]},
 'grid_diagonal': {'*': [('g','gcd(m,n)'), ('squares','m + n - g'), ('interior','g - 1')]},
 'map_scale': {'real': [('answer','cm * scale / 100')], 'map': [('answer','real * 100 / scale')]},
 'mixture_concentration': {'result': [('answer','(c1 * v1 + c2 * v2) / (v1 + v2)')], 'second': [('answer','(result * (v1 + v2) - c1 * v1) / v2')]},
 'ratio_split': {'first': [('answer','total * a / (a + b)')], 'second': [('answer','total * b / (a + b)')]},
 'pick_theorem': {'area': [('answer','interior + boundary / 2 - 1')], 'interior': [('answer','area - boundary / 2 + 1')]},
 'pigeonhole': {'*': [('answer','colors * (k - 1) + 1')]},
 'polygon_angles': {'sum': [('answer','(n - 2) * 180')], 'angle': [('answer','(n - 2) * 180 / n')], 'diagonals': [('answer','n * (n - 3) / 2')]},
 'shadow_height': {'pole': [('answer','stick * pole_shadow / stick_shadow')], 'stick_shadow': [('answer','stick * pole_shadow / pole')]},
 'solid_volume': {'cylinder': [('answer','r * r * h')], 'cone': [('answer','r * r * h / 3')], 'sphere': [('answer','4 * r ** 3 / 3')]},
 'work_rates': {'together': [('answer','a * b / (a + b)')], 'partner': [('answer','together * a / (a - together)')]},
 'paper_folding': {'layers': [('answer','2 ** k')], 'holes': [('answer','h * 2 ** k')]},
 'set_reasoning': {'union': [('answer','A + B - both')], 'only_a': [('answer','A - both')], 'neither': [('answer','total - (A + B - both)')]},
 'dice_reasoning': {'opposite': [('answer','7 - v')], 'corner_sum': [('answer','21 - sum(faces)')]},
}

PHYSICS = {
 'average_speed': {'average': [('answer','2 * v1 * v2 / (v1 + v2)')], 'other_speed': [('answer','average * v1 / (2 * v1 - average)')]},
 'ballistic_pendulum': {'block_speed': [('answer','m * v / (m + M)')], 'height': [('block_speed','m * v / (m + M)'), ('answer','block_speed ** 2 / 20')], 'bullet_speed': [('block_speed','sqrt(20 * h)'), ('answer','block_speed * (m + M) / m')]},
 'boat_current': {'downstream':[('answer','vb + vc')], 'upstream':[('answer','vb - vc')], 'boat':[('answer','(down + up) / 2')], 'current':[('answer','(down - up) / 2')]},
 'cyclotron': {'frequency':[('answer','charge * field / mass')], 'charge':[('answer','omega * mass / field')], 'mass':[('answer','charge * field / omega')]},
 'density': {'density':[('answer','mass / volume')], 'mass':[('answer','density * volume')], 'volume':[('answer','mass / density')]},
 'doppler_shift': {'observed':[('answer','frequency * (sound + observer) / (sound - source)')], 'source_speed':[('answer','sound - frequency * (sound + observer) / observed')], 'observer_speed':[('answer','observed * (sound - source) / frequency - sound')]},
 'echo_delay': {'distance':[('answer','340 * time / 2')], 'time':[('answer','2 * distance / 340')]},
 'fourier_conduction': {'rate':[('answer','k * area * delta / thickness')], 'thickness':[('answer','k * area * delta / rate')]},
 'free_fall': {'height':[('answer','5 * time ** 2')], 'time':[('answer','sqrt(height / 5)')]},
 'gear_ratio': {'speed':[('answer','n1 * w1 / n2')], 'teeth':[('answer','n1 * w1 / w2')]},
 'hooke_law': {'force':[('answer','k * x')], 'extension':[('answer','force / k')], 'stiffness':[('answer','force / x')]},
 'hubble_law': {'velocity':[('answer','constant * distance')], 'distance':[('answer','velocity / constant')], 'constant':[('answer','velocity / distance')]},
 'inductor_energy': {'energy':[('answer','inductance * current ** 2 / 2')], 'inductance':[('answer','2 * energy / current ** 2')], 'current':[('answer','sqrt(2 * energy / inductance)')]},
 'internal_resistance': {'resistance':[('answer','(v1 - v2) / (i2 - i1)')], 'emf':[('r_computed','(v1 - v2) / (i2 - i1)'), ('answer','v1 + i1 * r_computed')]},
 'joule_heat': {'heat':[('answer','i ** 2 * r * t')], 'time':[('answer','heat / (i ** 2 * r)')], 'current':[('answer','sqrt(heat / (r * t))')]},
 'lc_oscillator': {'omega_squared':[('answer','1 / (L * C)')], 'inductance':[('answer','1 / (omega_sq * C)')]},
 'lever_balance': {'mass':[('answer','m1 * d1 / d2')], 'distance':[('answer','m1 * d1 / m2')]},
 'mechanical_efficiency': {'efficiency':[('answer','useful / total')], 'useful':[('answer','efficiency * total')]},
 'mirror_glance': {'glance':[('answer','90 - angle')], 'deviation':[('answer','180 - 2 * angle')]},
 'pendulum_ratio': {'ratio':[('answer','length / gravity')], 'length':[('answer','ratio * gravity')]},
 'rational_gamma': {'gamma':[('answer','1 / sqrt(1 - (numer / denom) ** 2)')], 'proper_time':[('answer','lab_time * sqrt(1 - (numer / denom) ** 2)')]},
 'reduced_mass': {'reduced':[('answer','m1 * m2 / (m1 + m2)')], 'reciprocal':[('answer','1 / m1 + 1 / m2')]},
 'relative_velocity': {'relative':[('answer','va - vb')], 'first_speed':[('answer','relative + vb')]},
 'resistor_pair': {'series':[('answer','r1 + r2')], 'parallel':[('answer','r1 * r2 / (r1 + r2)')]},
 'restitution': {'first_speed':[('answer','(m1 - e * m2) * u / (m1 + m2)')], 'second_speed':[('answer','m1 * (1 + e) * u / (m1 + m2)')]},
 'sensible_heat': {'heat':[('answer','specific * mass * delta')], 'mass':[('answer','heat / (specific * delta)')], 'specific_heat':[('answer','heat / (mass * delta)')]},
 'spectral_redshift': {'redshift':[('answer','(observed - rest) / rest')], 'observed':[('answer','rest * (1 + z)')], 'rest':[('answer','observed / (1 + z)')]},
 'spring_energy': {'energy':[('answer','k * x ** 2 / 2')], 'stiffness':[('answer','2 * energy / x ** 2')]},
 'stefan_ratio': {'ratio':[('answer','(t2 / t1) ** 4')], 'hot':[('answer','t1 * ratio ** Fraction(1,4)')]},
 'stellar_parallax': {'distance':[('answer','1 / parallax')], 'parallax':[('answer','1 / distance')]},
 'wave_relation': {'speed':[('answer','frequency * wavelength')], 'frequency':[('answer','speed / wavelength')], 'wavelength':[('answer','speed / frequency')]},
}


def execute_spec(task, name, trace, specs):
    kind = getattr(task, 'task_type', None) or getattr(task, 'subtype', None)
    variants = specs[name]
    statements = variants.get(kind, variants.get('*'))
    if statements is None:
        raise ValueError((name, kind))
    variables = {}
    inputs = {'subtype': kind}
    for target, expression in statements:
        for node in ast.walk(ast.parse(expression, mode='eval')):
            if isinstance(node, ast.Name) and node.id not in _FUNCTIONS and node.id not in variables:
                variables[node.id] = getattr(task, node.id)
                inputs[node.id] = variables[node.id]
        variables[target] = evaluate(expression, variables, trace.events)
        value = variables[target]
        if getattr(value, 'denominator', None) == 1:
            value = int(value)
        elif isinstance(value, float) and value.is_integer():
            value = int(value)
        setattr(task, target, value)
    if name == 'clock_hands': task.answer = getattr(task, kind)
    if name == 'grid_diagonal': task.answer = getattr(task, kind)
    if name == 'set_reasoning': task._answer = task.answer
    return inputs
