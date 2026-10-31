"""Parse explicit plans and validate actions instead of comparing answer numbers."""
import json
import re
from string import Formatter
from math import gcd
from functools import reduce
from re_rl.rewards import extract_reasoning_and_answer
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from .search_traces import jug_successors


def match_template(template,text):
    pattern = ''
    for literal,field,spec,conversion in Formatter().parse(template):
        pattern += re.escape(literal)
        if field is not None:
            pattern += '(?P<'+field+'>'+('.*?' if field in ('actions','moves') else '.+?')+')'
    match = re.fullmatch(pattern,text,flags=re.DOTALL)
    return match.groupdict() if match else None


def answer_text(prediction):
    if not isinstance(prediction,str):
        return ''
    _,answer = extract_reasoning_and_answer(prediction)
    return (answer if '<answer>' in prediction else prediction).strip()


def hanoi_verify(task,prediction):
    text = answer_text(prediction)
    moves = None
    try:
        moves = json.loads(text)
    except (ValueError,TypeError):
        for language in ('ru','en'):
            section = PROMPT_TEMPLATES['tower_of_hanoi']
            header = section['final_answer'][language].split('{moves}')[0].strip()
            lines = text.splitlines()
            claimed = match_template(header,lines[0]) if lines else None
            if claimed:
                if claimed != dict(n=str(2**task.num_disks-1),disks=str(task.num_disks),optimal=str(2**task.num_disks-1)):
                    continue
                lines = lines[1:]
            parsed = []
            for i,line in enumerate(lines):
                fields = match_template(section['steps']['move'][language],line)
                if not fields or fields['n'] != str(i+1) or not fields['disk'].isdigit():
                    break
                parsed.append([int(fields['disk']),fields['from_peg'],fields['to_peg']])
            else:
                moves = parsed
                break
    if not isinstance(moves,list) or len(moves) != 2**task.num_disks-1:
        return 0.0
    pegs = {p:[] for p in (task.source,task.target,task.auxiliary)}
    pegs[task.source] = list(range(task.num_disks,0,-1))
    for move in moves:
        if not isinstance(move,(list,tuple)) or len(move) != 3:
            return 0.0
        disk,source,target = move
        if type(disk) is not int or not isinstance(source,str) or not isinstance(target,str):
            return 0.0
        if source not in pegs or target not in pegs or source == target or not pegs[source] or pegs[source][-1] != disk:
            return 0.0
        if pegs[target] and pegs[target][-1] < disk:
            return 0.0
        pegs[source].pop();pegs[target].append(disk)
    return float(pegs[task.target] == list(range(task.num_disks,0,-1)))


def jug_verify(task,prediction):
    text = answer_text(prediction)
    possible = task.target <= max(task.capacities) and task.target % reduce(gcd,task.capacities) == 0
    if not possible:
        return float(any(text == PROMPT_TEMPLATES['water_jug']['no_solution'][language].format(
            target=task.target,capacities=', '.join(map(str,task.capacities))) for language in ('ru','en')))
    actions = None
    announced = None
    summary = None
    try:
        actions = json.loads(text)
    except (ValueError,TypeError):
        for language in ('ru','en'):
            section = PROMPT_TEMPLATES['water_jug']
            full = match_template(section['final_answer'][language],text)
            body = full['actions'] if full else text
            parsed,states = [],[]
            lines = body.splitlines() if body else []
            for index,line in enumerate(lines):
                step = match_template(section['steps']['action'][language],line)
                if not step or step['n'] != str(index+1): break
                for kind,template in section['operations'].items():
                    fields = match_template(template[language],step['action'])
                    if fields is None: continue
                    try:
                        if kind == 'fill':
                            jug = int(fields['jug'])-1
                            if not 0 <= jug < len(task.capacities) or int(fields['capacity']) != task.capacities[jug]: break
                            action = [kind,jug]
                        elif kind == 'empty': action = [kind,int(fields['jug'])-1]
                        else: action = [kind,int(fields['from_jug'])-1,int(fields['to_jug'])-1]
                    except (ValueError,KeyError): break
                    parsed.append(action);states.append(step['state']);break
                else: break
                if len(parsed) != index+1: break
            else:
                actions,announced,summary = parsed,(states,language),full
                break
    if not isinstance(actions,list): return 0.0
    state = (0,)*len(task.capacities)
    for index,action in enumerate(actions):
        if not isinstance(action,list) or not action or not isinstance(action[0],str) or any(type(i) is not int for i in action[1:]):
            return 0.0
        successors = {a:s for s,a in jug_successors(state,task.capacities)}
        next_state = successors.get(tuple(action))
        if next_state is None: return 0.0
        state = next_state
        if announced:
            states,language = announced
            from re_rl.tasks.prompts import get_template
            rendered = ', '.join(get_template(PROMPT_TEMPLATES['inline'],'water_jug_state_item',language,
                                  augment=False,idx=i+1,value=v) for i,v in enumerate(state))
            if states[index] != rendered: return 0.0
    if task.target not in state: return 0.0
    if summary:
        try:
            jug = int(summary['jug'])-1
            if summary['n'] != str(len(actions)) or summary['target'] != str(task.target) or not 0 <= jug < len(state) or state[jug] != task.target:
                return 0.0
        except ValueError: return 0.0
    return 1.0
