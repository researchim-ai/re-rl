"""Exact probability arithmetic from fixed public experiment parameters."""
from fractions import Fraction


def bayesian(kind,parameters):
    p = {k:Fraction(str(v)) for k,v in parameters.items()}
    if kind == 'bayes_chain':
        complement_a = 1-p['p_a']
        b_from_a = p['p_b_a']*p['p_a']
        b_from_not_a = p['p_b_not_a']*complement_a
        probability_b = b_from_a+b_from_not_a
        c_from_b = p['p_c_b']*probability_b
        c_from_not_b = p['p_c_not_b']*(1-probability_b)
        result = c_from_b+c_from_not_b
    else:
        false_positive_rate = 1-p['spec'] if kind == 'bayes_basic' else p['fpr']
        true_positives = p['sens']*p['p_d']
        false_positives = false_positive_rate*(1-p['p_d'])
        all_positives = true_positives+false_positives
        result = true_positives/all_positives
    return result


def combination(n,k):
    if k < 0 or k > n:return 0
    k = min(k,n-k)
    value = 1
    for i in range(1,k+1):
        factor = n-k+i
        value = value*factor//i
    return value


def urn(containers,draws,color,kind,x):
    total_probability = Fraction(0)
    for index,dist in enumerate(containers):
        total = sum(count for name,count in dist)
        colored = sum(count for name,count in dist if name == color)
        denominator = combination(total,draws)
        successes = [draws] if kind == 'all' else range(1,draws+1) if kind == 'at_least' else [x]
        favorable = 0
        for k in successes:
            choose_colored = combination(colored,k)
            choose_other = combination(total-colored,draws-k)
            favorable += choose_colored*choose_other
        conditional = Fraction(favorable,denominator) if denominator else Fraction(0)
        weighted = conditional/len(containers)
        total_probability += weighted
    return total_probability


def verify_probability(task,prediction):
    import re
    from re_rl.tasks.math._verify_utils import extract_answer_text
    from re_rl.tasks.prompts import PROMPT_TEMPLATES
    text = extract_answer_text(prediction)
    if task.TASK_TYPE == 'bayesian_reasoning':
        expected = bayesian(task.task_type,task.parameters)
        prefix = ('P(C)' if task.task_type == 'bayes_chain' else 'P(D|+)')+'='
        if text.startswith(prefix):text = text[len(prefix):].strip()
    else:
        expected = urn(task.containers,task.draws,task.color_choice,task.question_kind,task.x_val)
        for language in ('ru','en'):
            prefix = PROMPT_TEMPLATES['urn_probability']['final_answer'][language].split('{prob_value}')[0]
            if text.startswith(prefix):text = text[len(prefix):].strip()
    if not re.fullmatch(r'[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?|[+-]?[0-9]+/[0-9]+',text):return 0.0
    try: value = Fraction(text)
    except (ValueError,ZeroDivisionError):return 0.0
    return float(0 <= value <= 1 and abs(value-expected) <= Fraction(1,20000))
