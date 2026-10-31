"""Reproduce every arithmetic event and compare against independent existing oracles."""
from fractions import Fraction
import json
import operator
import random

import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.registry import registry
from re_rl.tasks.ml.detailed_solvers import TRACED_ML_TASKS
from re_rl.tasks.rl.detailed_solvers import TRACED_RL_TASKS

OPERATIONS = {'add': operator.add, 'sub': operator.sub, 'mul': operator.mul,
              'div': operator.truediv, 'abs': abs, 'square': lambda v: v ** 2,
              'min': min, 'max': max, 'lt': lambda a,b: int(a < b),
              'ge': lambda a,b: int(a >= b), 'ne': lambda a,b: int(a != b),
              'floor': lambda v: v.numerator // v.denominator, 'eq': lambda a,b: int(a == b)}


@pytest.mark.parametrize('name', TRACED_ML_TASKS + TRACED_RL_TASKS)
@pytest.mark.parametrize('language', ['ru', 'en'])
@pytest.mark.parametrize('difficulty', range(1, 11))
def test_recorded_execution_matches_original_oracle(name, language, difficulty):
    cls = registry[name]
    for kind in cls.TASK_TYPES:
        for seed in (0, 4):
            random.seed(seed)
            task = cls(language=language, difficulty=difficulty, task_type=kind)
            # Constructors still compute the original independent oracle functions.
            if name == 'kmeans_step': expected = getattr(task,kind)
            elif name == 'gradient_step': expected = task.grad if kind == 'gradient' else task.w_new
            elif name == 'bellman_backup': expected = task.value if kind == 'value' else task.greedy
            else: expected = task.answer
            task.solve()
            assert task.final_answer == str(expected)
            assert task.verify(f'<answer>{task.final_answer}</answer>') == 1
            result = task.get_result()
            assert result['algorithm_trace'] and result['computation_inputs']
            assert len(result['solution_steps']) == len(result['algorithm_trace']) + 1
            json.dumps(result)
            for event in result['algorithm_trace']:
                operands = [Fraction(value) for value in event['operands']]
                expected_operation = OPERATIONS[event['operation']](*operands)
                assert Fraction(event['result']) == expected_operation
                assert event['label']
            previous = task.get_result()
            task.solve()
            assert task.get_result() == previous
            if language == 'en':
                assert not any('\u0400' <= c <= '\u04ff' for c in '\n'.join(task.solution_steps))


def test_error_terms_are_accumulated_in_input_order():
    from re_rl.tasks.ml.mse.task import MseTask
    task = MseTask()
    task.pred, task.truth = [3, 1, 4], [1, 2, 4]
    task.task_type = 'mse'
    task.solve()
    assert task.final_answer == '5/3'
    squares = [Fraction(e['result']) for e in task.algorithm_trace if e['operation'] == 'square']
    assert squares == [4, 1, 0]
    sums = [Fraction(e['result']) for e in task.algorithm_trace if e['label'].startswith('Σloss')]
    assert sums == [4, 5, 5]


def test_stump_checks_constants_and_both_polarities():
    from re_rl.tasks.ml.decision_stump.task import DecisionStumpTask
    task = DecisionStumpTask()
    task.points = [(0,1),(0,0),(1,0)]
    task.solve()
    assert task.final_answer == '1'
    comparisons = [e for e in task.algorithm_trace if e['label'] == 'best_errors']
    assert len(comparisons) == 2 + 2 * len({x for x, _ in task.points})


def test_stable_topk_ties_and_negative_ppo_advantage():
    from re_rl.tasks.ml.precision_at_k.task import PrecisionAtKTask
    from re_rl.tasks.rl.ppo.task import PpoClipTask
    task = PrecisionAtKTask()
    task.scores, task.labels, task.k, task.task_type = [5,5,1], [0,1,1], 1, 'hits'
    task.solve()
    assert task.final_answer == '0'
    task = PpoClipTask()
    task.ratio, task.epsilon, task.advantage, task.task_type = Fraction(2), Fraction(1,5), -3, 'surrogate'
    task.solve()
    assert task.final_answer == '-6'


def test_export_retains_computation_inputs_without_graph(tmp_path):
    from re_rl.dataset_generator import DatasetGenerator
    result = DatasetGenerator(output_dir=str(tmp_path)).generate_single_task('q_learning')
    assert result['algorithm_trace'] and result['computation_inputs']
    assert 'graph' not in result
    json.dumps(result)


from re_rl.tasks.math.algorithm_traces.solvers import TRACED_DP_TASKS
from re_rl.tasks.physics.detailed_solvers import TRACED_PHYSICS_TASKS


@pytest.mark.parametrize('name', TRACED_DP_TASKS + TRACED_PHYSICS_TASKS)
@pytest.mark.parametrize('language', ['ru', 'en'])
@pytest.mark.parametrize('difficulty', range(1, 11))
def test_dp_execution_matches_existing_oracles(name, language, difficulty):
    cls = registry[name]
    for kind in getattr(cls, 'TASK_TYPES', [None]):
        for seed in (2, 9):
            random.seed(seed)
            task = cls(task_type=kind, language=language, difficulty=difficulty)
            expected = task._answer if name in ('subset_sum', 'knapsack') else task.answer
            task.solve()
            if name == 'subset_sum':
                assert task._answer == expected
            else:
                assert task.final_answer == str(expected)
            assert task.verify(f'<answer>{task.final_answer}</answer>') == 1
            for event in task.algorithm_trace:
                values = [Fraction(v) for v in event['operands']]
                assert Fraction(event['result']) == OPERATIONS[event['operation']](*values)
            assert len(task.solution_steps) == len(task.algorithm_trace) + 1
            json.dumps(task.get_result())
            before = task.get_result()
            task.solve()
            assert task.get_result() == before


def test_zero_decodings_and_nonempty_negative_kadane():
    from re_rl.tasks.math.logic.decode_ways.task import DecodeWaysTask
    from re_rl.tasks.math.logic.max_subarray.task import MaxSubarrayTask
    task = DecodeWaysTask()
    for code, expected in [('0',0),('100',0),('101',1),('226',3)]:
        task.code = code
        task.solve()
        assert task.final_answer == str(expected)
    task = MaxSubarrayTask()
    task.values = [-8,-2,-5]
    task.solve()
    assert task.final_answer == '-2'


def test_extended_dp_against_exhaustive_enumeration():
    from itertools import product, combinations
    for nums in product((-2, 0, 3), repeat=4):
        task = registry['max_product']()
        task.nums = list(nums)
        task.solve()
        candidates = []
        for start in range(len(nums)):
            value = 1
            for end in range(start, len(nums)):
                value *= nums[end]
                candidates.append(value)
        assert task.final_answer == str(max(candidates))
    task = registry['target_sum']()
    for nums in ([0, 0, 2], [1, 1, 1], [2, 3, 5]):
        for target in range(-10, 11):
            task.nums, task.target = list(nums), target
            task.solve()
            count = sum(sum(x*s for x, s in zip(nums, signs)) == target
                        for signs in product((-1, 1), repeat=len(nums)))
            assert task.final_answer == str(count)
    task = registry['subsequence_count']()
    for text in ('aaaa', 'abab', 'bbaa'):
        for pattern in ('a', 'aa', 'ab', 'bbb', 'aaaaa'):
            task.text, task.pattern = text, pattern
            task.solve()
            count = sum(''.join(text[i] for i in indices) == pattern
                        for indices in combinations(range(len(text)), len(pattern)))
            assert task.final_answer == str(count)


def test_jump_frontiers_match_independent_shortest_distance():
    from itertools import product
    task = registry['jump_game']()
    for jumps in product((1, 2, 3), repeat=4):
        task.jumps = list(jumps) + [0]
        distances = [0] + [100] * 4
        for i in range(4):
            for destination in range(i+1, min(5, i+jumps[i]+1)):
                distances[destination] = min(distances[destination], distances[i]+1)
        task.solve()
        assert task.final_answer == str(distances[-1])


def test_counting_and_knapsack_against_enumeration():
    from itertools import product, combinations
    pair = registry['pair_sum']()
    subarray = registry['subarray_sum']()
    for nums in product((-1, 0, 1), repeat=4):
        for target in (-1, 0, 1):
            pair.values, pair.target = list(nums), target
            pair.solve()
            assert int(pair.final_answer) == sum(a+b == target for a, b in combinations(nums, 2))
            subarray.nums, subarray.target = list(nums), target
            subarray.solve()
            assert int(subarray.final_answer) == sum(
                sum(nums[i:j]) == target for i in range(4) for j in range(i+1, 5))
    task = registry['knapsack']()
    task.weights, task.values = [2, 3, 4], [3, 5, 6]
    for capacity in range(10):
        task.capacity = capacity
        task.solve()
        expected = max(sum(v*s for v, s in zip(task.values, mask))
                       for mask in product((0, 1), repeat=3)
                       if sum(w*s for w, s in zip(task.weights, mask)) <= capacity)
        assert int(task.final_answer) == expected


def test_coin_recurrence_and_square_boundaries():
    task = registry['min_coins']()
    task.coins, task.amount = [1, 3, 4], 6
    task.solve()
    assert task.final_answer == '2'
    task = registry['min_squares']()
    for value, expected in [(1, 1), (7, 4), (12, 3), (13, 2), (16, 1)]:
        task.n = value
        task.solve()
        assert int(task.final_answer) == expected


@pytest.mark.parametrize('name', TRACED_DP_TASKS + TRACED_PHYSICS_TASKS)
def test_dp_solver_ignores_stale_cached_answer(name):
    task = registry[name](language='en')
    task.solve()
    before = task.get_result()
    task.answer = -999999
    if hasattr(task, '_answer'):
        task._answer = -999999
    task.solve()
    assert task.get_result() == before


def test_circuit_trace_matches_requested_quantity():
    task = registry['network_reduce']()
    task.tree = ('parallel', ('leaf', 6), ('leaf', 6))
    task.task_type = 'leaf_sum'
    task.solve()
    assert task.final_answer == '12'
    assert not any(e['operation'] == 'div' for e in task.algorithm_trace)
    task.task_type = 'equivalent'
    task.solve()
    assert task.final_answer == '3'
    assert task.algorithm_trace[-1]['operation'] == 'div'
    task = registry['switch_net']()
    task.tree = ('series', ('leaf', 1, 1), ('parallel', ('leaf', 2, 0), ('leaf', 3, 1)))
    task.task_type = 'flip'
    # Deliberately leave constructor caches untouched: they describe another tree.
    for switch, expected in [(1, 1), (2, 0), (3, 1)]:
        task.k = switch
        task.solve()
        assert int(task.final_answer) == expected
        assert any(e['label'].endswith(f'flip_{switch}') for e in task.algorithm_trace)
