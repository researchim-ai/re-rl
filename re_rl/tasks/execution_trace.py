"""Record executed solver statements, changed local state, calls and returns.

Only deterministic solver calls are traced, never random instance construction.
Snapshots are copied at execution time; events cannot change with later mutations.
The hook is thread-local and always restores any caller's profiling hook.
"""
from collections import deque
from fractions import Fraction
from functools import lru_cache
import inspect
import json
import linecache
import io
import tokenize
from pathlib import Path
import sys

from re_rl.tasks.i18n import TaskTexts

texts = TaskTexts(__file__, 'execution_trace_i18n.json')
ROOT = Path(__file__).resolve().parent
_SKIP = {'self', 'task', 'texts', 'trace'}


def snapshot(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, (list, tuple, deque)):
        return [snapshot(v) for v in value]
    if isinstance(value, (set, frozenset)):
        return sorted((snapshot(v) for v in value), key=repr)
    if isinstance(value, dict):
        return {str(k): snapshot(v) for k, v in value.items()}
    return {'type': type(value).__name__}


def display(value):
    if isinstance(value, dict):
        return '⟨' + '; '.join(str(k)+' = '+display(v) for k,v in value.items()) + '⟩'
    if isinstance(value, list):
        return '[' + ', '.join(display(v) for v in value) + ']'
    return str(value)


def translation_map(value):
    if not isinstance(value, dict):
        return False
    if 'ru' in value and 'en' in value:
        return True
    return any(translation_map(child) for child in value.values() if isinstance(child,dict))


@lru_cache(maxsize=None)
def eligible(filename):
    try:
        path = Path(filename).resolve()
        return path.is_relative_to(ROOT) and 'i18n' not in path.relative_to(ROOT).parts and path.name not in {
            'execution_trace.py', 'i18n.py', 'base_task.py', 'registry.py',
            'task_augmentation.py', 'computation_trace.py'}
    except (OSError, ValueError):
        return False


@lru_cache(maxsize=None)
def statement_source(filename, number):
    source = linecache.getline(filename, number).strip()
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type == tokenize.COMMENT:
                return source[:token.start[1]].rstrip()
    except (tokenize.TokenError, IndentationError):
        pass
    return source


class ExecutionTrace:
    def __init__(self):
        self.events = []
        self._next_call = 0

    def call(self, function, *args, **kwargs):
        """Run a solver normally while observing its actual Python execution."""
        pending = {}
        calls = {}
        last = {}
        previous = sys.gettrace()

        def state(frame):
            return {key: snapshot(value) for key, value in frame.f_locals.items()
                    if key not in _SKIP and not callable(value) and not inspect.ismodule(value)
                    and not translation_map(value)}

        def flush(frame, next_line=None):
            item = pending.pop(id(frame), None)
            if item is None:
                return
            current = state(frame)
            changes = {k: v for k, v in current.items() if k not in last[id(frame)] or v != last[id(frame)][k]}
            removed = [k for k in last[id(frame)] if k not in current]
            item.update(changes=changes, removed=removed, next_line=next_line)
            self.events.append(item)
            last[id(frame)] = current

        def observer(frame, event, value):
            if not eligible(frame.f_code.co_filename) or frame.f_code.co_name == '_show':
                return None
            key = id(frame)
            if event == 'call':
                self._next_call += 1
                calls[key] = self._next_call
                last[key] = state(frame)
                self.events.append(dict(operation='call', call=calls[key],
                                        function=frame.f_code.co_name, inputs=last[key]))
            elif event == 'line':
                flush(frame, frame.f_lineno)
                pending[key] = dict(operation='statement', call=calls[key],
                                    function=frame.f_code.co_name,
                                    line=frame.f_lineno,
                                    expression=statement_source(frame.f_code.co_filename, frame.f_lineno))
            elif event == 'return':
                flush(frame)
                self.events.append(dict(operation='return', call=calls[key],
                                        function=frame.f_code.co_name, result=snapshot(value)))
                calls.pop(key, None); last.pop(key, None)
            elif event == 'exception':
                # The exception is allowed to propagate normally; never manufacture an answer.
                flush(frame)
                self.events.append(dict(operation='exception', call=calls.get(key),
                                        exception=value[0].__name__))
            return observer

        try:
            sys.settrace(observer)
            return function(*args, **kwargs)
        finally:
            sys.settrace(previous)

    def finish(self, task, inputs):
        task.computation_inputs = snapshot(inputs)
        task.algorithm_trace = self.events
        steps = []
        for event in self.events:
            op = event['operation']
            if op == 'call':
                steps.append(texts.t('call', task.language, function=event['function'], inputs=display(event['inputs'])))
            elif op == 'statement':
                steps.append(texts.t('statement', task.language, expression=(event['expression'] if '{' not in event['expression'] else event['function']+':'+str(event['line'])), changes=display(event['changes'])))
            elif op in ('life_cell','elementary_cell','cellular_generation'):
                steps.append(texts.t(op, task.language, **{k:display(v) for k,v in event.items() if k != 'operation'}))
            elif op in ('arc_candidate','arc_prediction'):
                steps.append(texts.t(op,task.language,**{k:display(v) for k,v in event.items() if k != 'operation'}))
            elif op.startswith(('grid_','fleet_')):
                values = {k:display(v) for k,v in event.items() if k != 'operation'}
                if 'reason' in event: values['reason'] = texts.t('grid_reason_'+event['reason'],task.language)
                if 'axis' in event: values['axis'] = texts.t('grid_axis_'+str(event['axis']),task.language)
                steps.append(texts.t(op,task.language,**values))
            elif op == 'cage_candidates':
                for check in event['checks']:
                    values = {k:display(v) for k,v in event.items() if k not in ('operation','checks')}
                    values.update({k:display(v) for k,v in check.items()})
                    steps.append(texts.t('cage_candidate',task.language,**values))
            elif op == 'sky_candidates':
                for check in event['checks']:
                    values = {k:display(v) for k,v in event.items() if k not in ('operation','checks')}
                    values.update({k:display(v) for k,v in check.items() if k not in ('forward','backward')})
                    values['actual_forward'] = check['forward']
                    values['actual_backward'] = check['backward']
                    steps.append(texts.t('sky_candidate',task.language,**values))
            elif op.startswith(('csp_','queens_')) or op == 'kakuro_candidate':
                values = {k:display(v) for k,v in event.items() if k != 'operation'}
                if op.startswith('csp_') and 'reason' in event:
                    values['reason'] = texts.t('csp_reason_'+event['reason'],task.language)
                if op == 'csp_conflict':
                    values['details'] = display({k:v for k,v in event.items() if k not in ('operation','depth','reason')})
                steps.append(texts.t(op,task.language,**values))
            elif op.startswith(('hitori_','star_','sudoku_','nav_','river_','infer_','plan_','puzzle_','deduce_','claim_','kin_','logic_','analogy_','schedule_','sat_','proof_','opt_','code_','error_','quad_','phys_','spec_','traj_')):
                steps.append(texts.t(op,task.language,**{k:display(v) for k,v in event.items() if k != 'operation'}))
            elif op.startswith('game_'):
                steps.append(texts.t(op, task.language, **{k:json.dumps(v, ensure_ascii=False) for k,v in event.items() if k != 'operation'}))
            elif op == 'expression':
                steps.append(texts.t('expression', task.language, expression=event['expression'], operands=display(event['operands']), result=event['result']))
            elif op == 'return':
                steps.append(texts.t('return', task.language, function=event['function'], result=display(event['result'])))
        task.solution_steps = steps + [texts.common('answer_line', task.language, answer=task.final_answer)]
