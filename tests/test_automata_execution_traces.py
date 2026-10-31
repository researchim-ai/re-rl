"""Replay the actual gate operations and DFA transitions for text and visual tasks."""
import json
import random
from fractions import Fraction
import pytest
from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.visual.generators import ALL_VISUAL_TASK_GENERATORS
from re_rl.tasks.registry import registry
from re_rl.tasks.math.algorithm_traces.automata import TRACED_AUTOMATA_TASKS


@pytest.mark.parametrize('name', TRACED_AUTOMATA_TASKS)
@pytest.mark.parametrize('language', ['ru', 'en'])
@pytest.mark.parametrize('difficulty', range(1, 11))
def test_executed_gates_and_transitions(name, language, difficulty):
    cls = registry[name]
    kinds = ['evaluate', 'count'] if 'circuit' in name else [None]
    for kind in kinds:
        random.seed(42)
        task = cls(language=language, difficulty=difficulty, task_type=kind)
        expected = task._answer
        task._answer = 'stale'
        task.solve()
        assert task._answer == expected
        assert task.verify(f'<answer>{task.final_answer}</answer>') == 1
        json.dumps(task.get_result())
        if 'circuit' in name:
            assert task.subtype == kind
            from re_rl.tasks.computation_trace import ExactTrace
            for event in task.algorithm_trace:
                args = [Fraction(v) for v in event['operands']]
                assert Fraction(event['result']) == ExactTrace.OPERATIONS[event['operation']](*args)
            assignments = 1 if kind == 'evaluate' else 2**task.k
            gates = [e for e in task.algorithm_trace if ':g' in e['label']]
            assert len(gates) == assignments * len(task.gates)
        else:
            state = 0
            transitions = [e for e in task.algorithm_trace if e['operation'] == 'transition']
            assert len(transitions) == len(task.word)
            for index, event in enumerate(transitions):
                assert event['source'] == state
                assert event['symbol'] == task.word[index]
                state = task.delta[state][task.word[index]]
                assert event['destination'] == state
            assert task.algorithm_trace[-1]['result'] == (state in task.accepting)
        before = task.get_result()
        task.solve()
        assert task.get_result() == before
