"""Evaluate each recurrence and candidate instead of printing a cached optimum."""
from fractions import Fraction
from math import isqrt
from re_rl.tasks.computation_trace import ExactTrace, texts

TRACED_DP_TASKS = ('max_subarray', 'house_robber', 'stock_profit', 'rod_cutting',
                   'min_path_sum', 'decode_ways', 'subset_sum', 'common_substring',
                   'matrix_chain', 'lis_dp', 'target_sum', 'subsequence_count',
                   'stock_unlimited', 'jump_game', 'max_product', 'min_coins',
                   'min_squares', 'knapsack', 'pair_sum', 'subarray_sum')


def solve_detailed(task):
    tr = ExactTrace(); c = tr.calc
    name = task.TASK_TYPE
    inputs = {}
    if name == 'max_subarray':
        inputs = {'values': task.values}
        end = best = c('end_1=best_1', 'add', task.values[0], 0)
        for i, value in enumerate(task.values[1:], 2):
            end = c(f'end_{i}', 'max', value, c(f'extend_{i}', 'add', end, value))
            best = c(f'best_{i}', 'max', best, end)
        answer = int(best)
    elif name == 'house_robber':
        inputs = {'values': task.values}
        previous, current = Fraction(0), Fraction(0)
        for i, value in enumerate(task.values, 1):
            take = c(f'take_{i}', 'add', previous, value)
            previous, current = current, c(f'dp_{i}', 'max', current, take)
        answer = int(current)
    elif name == 'stock_profit':
        inputs = {'prices': task.prices}
        lowest, best = Fraction(task.prices[0]), Fraction(0)
        c('min_price_1', 'add', lowest, 0)
        for day, price in enumerate(task.prices[1:], 2):
            profit = c(f'sell_profit_{day}', 'sub', price, lowest)
            best = c(f'best_profit_{day}', 'max', best, profit)
            lowest = c(f'min_price_{day}', 'min', lowest, price)
        answer = int(best)
    elif name == 'rod_cutting':
        inputs = {'prices': task.prices}
        dp = [Fraction(0)] * len(task.prices)
        for length in range(1, len(dp)):
            for cut in range(1, length + 1):
                candidate = c(f'candidate({length},{cut})', 'add', task.prices[cut], dp[length-cut])
                dp[length] = c(f'dp_{length}', 'max', dp[length], candidate)
        answer = int(dp[-1])
    elif name == 'min_path_sum':
        inputs = {'grid': task.grid}
        dp = [[Fraction(0)] * task.cols for _ in range(task.rows)]
        for row in range(task.rows):
            for col in range(task.cols):
                candidates = []
                if row: candidates.append(dp[row-1][col])
                if col: candidates.append(dp[row][col-1])
                previous = c(f'predecessor({row},{col})', 'min', *candidates) if len(candidates) == 2 else candidates[0] if candidates else 0
                dp[row][col] = c(f'dp({row},{col})', 'add', previous, task.grid[row][col])
        answer = int(dp[-1][-1])
    elif name == 'decode_ways':
        inputs = {'code': task.code}
        dp = [Fraction(0)] * (len(task.code) + 1)
        dp[0] = c('dp_0', 'add', 1, 0)
        for i in range(1, len(dp)):
            valid = c(f'digit_nonzero_{i}', 'ne', int(task.code[i-1]), 0)
            dp[i] = c(f'single_digit_{i}', 'mul', valid, dp[i-1])
            if i > 1:
                pair = int(task.code[i-2:i])
                low = c(f'pair≥10_{i}', 'ge', pair, 10)
                high = c(f'pair≤26_{i}', 'ge', 26, pair)
                eligible = c(f'valid_pair_{i}', 'mul', low, high)
                dp[i] = c(f'dp_{i}', 'add', dp[i], c(f'two_digits_{i}', 'mul', eligible, dp[i-2]))
        answer = int(dp[-1])
    elif name == 'subset_sum':
        inputs = {'nums': task.nums, 'target': task.target}
        reachable = [Fraction(0)] * (task.target + 1)
        reachable[0] = c('reachable_0', 'add', 1, 0)
        for i, value in enumerate(task.nums, 1):
            old = reachable.copy()
            for total in range(value, task.target + 1):
                reachable[total] = c(f'reachable({i},{total})', 'max', old[total], old[total-value])
        task._answer = bool(reachable[task.target])
        answer = texts.t('yes' if task._answer else 'no', task.language)
    elif name == 'common_substring':
        inputs = {'a': task.a, 'b': task.b}
        dp = [[Fraction(0)] * (len(task.b) + 1) for _ in range(len(task.a) + 1)]
        best = Fraction(0)
        for i, a in enumerate(task.a, 1):
            for j, b in enumerate(task.b, 1):
                same = c(f'a[{i}]={a}==b[{j}]={b}', 'eq', ord(a), ord(b))
                continuation = c(f'extend({i},{j})', 'add', dp[i-1][j-1], 1)
                dp[i][j] = c(f'dp({i},{j})', 'mul', same, continuation)
                best = c('best_length', 'max', best, dp[i][j])
        answer = int(best)
    elif name == 'matrix_chain':
        inputs = {'dims': task.dims}
        n = len(task.dims) - 1
        dp = [[Fraction(0)] * n for _ in range(n)]
        for length in range(2, n+1):
            for i in range(n-length+1):
                j, best = i+length-1, None
                for split in range(i,j):
                    product = c(f'mults({i},{split},{j})', 'mul', c('dimension_product', 'mul', task.dims[i], task.dims[split+1]), task.dims[j+1])
                    candidate = c(f'cost({i},{split},{j})', 'add', c('subproblem_costs', 'add', dp[i][split], dp[split+1][j]), product)
                    best = candidate if best is None else c(f'dp({i},{j})', 'min', best, candidate)
                dp[i][j] = best
        answer = int(dp[0][-1])
    elif name == 'target_sum':
        inputs = {'nums': task.nums, 'target': task.target}
        ways = {0: Fraction(1)}
        c('ways(0,0)', 'add', 1, 0)
        for i, value in enumerate(task.nums, 1):
            following = {}
            for total, count in sorted(ways.items()):
                for operation in ('sub', 'add'):
                    destination = int(c(f'sum({i},{total},{operation})', operation, total, value))
                    following[destination] = c(f'ways({i},{destination})', 'add', following.get(destination, 0), count)
            ways = following
        answer = int(c(f'ways_target_{task.target}', 'add', ways.get(task.target, 0), 0))
    elif name == 'subsequence_count':
        inputs = {'text': task.text, 'pattern': task.pattern}
        ways = [Fraction(0)] * (len(task.pattern) + 1)
        ways[0] = c('ways_0', 'add', 1, 0)
        for i, char in enumerate(task.text, 1):
            for j in range(len(task.pattern), 0, -1):
                equal = c(f'text_{i}==pattern_{j}', 'eq', ord(char), ord(task.pattern[j-1]))
                contribution = c(f'contribution({i},{j})', 'mul', equal, ways[j-1])
                ways[j] = c(f'ways({i},{j})', 'add', ways[j], contribution)
        answer = int(ways[-1])
    elif name == 'stock_unlimited':
        inputs = {'prices': task.prices}
        total = c('profit_0', 'add', 0, 0)
        for i in range(1, len(task.prices)):
            difference = c(f'difference_{i}', 'sub', task.prices[i], task.prices[i-1])
            gain = c(f'gain_{i}', 'max', difference, 0)
            total = c(f'profit_{i}', 'add', total, gain)
        answer = int(total)
    elif name == 'jump_game':
        inputs = {'jumps': task.jumps}
        end = farthest = count = Fraction(0)
        for i in range(len(task.jumps)-1):
            reach = c(f'reach_{i}', 'add', i, task.jumps[i])
            farthest = c(f'farthest_{i}', 'max', farthest, reach)
            if c(f'boundary_{i}', 'eq', i, end):
                count = c('jump_count', 'add', count, 1)
                end = c('layer_end', 'add', farthest, 0)
                if c('target_reached', 'ge', end, len(task.jumps)-1):
                    break
        if end < len(task.jumps)-1:
            raise ValueError('unreachable')
        answer = int(count)
    elif name == 'max_product':
        inputs = {'nums': task.nums}
        high = low = best = c('product_0', 'add', task.nums[0], 0)
        for i, value in enumerate(task.nums[1:], 1):
            extend_high = c(f'extend_max_{i}', 'mul', high, value)
            extend_low = c(f'extend_min_{i}', 'mul', low, value)
            high = c(f'max_ending_{i}', 'max', value, extend_high, extend_low)
            low = c(f'min_ending_{i}', 'min', value, extend_high, extend_low)
            best = c(f'best_{i}', 'max', best, high)
        answer = int(best)
    elif name in ('min_coins', 'min_squares'):
        amount = task.amount if name == 'min_coins' else task.n
        coins = task.coins if name == 'min_coins' else [i*i for i in range(1, isqrt(amount)+1)]
        inputs = {'amount': amount, 'coins': coins}
        dp = [Fraction(0)] + [Fraction(amount+1)] * amount
        for total in range(1, amount+1):
            for coin in coins:
                if c(f'eligible({total},{coin})', 'ge', total, coin):
                    candidate = c(f'take({total},{coin})', 'add', dp[total-coin], 1)
                    dp[total] = c(f'dp_{total}', 'min', dp[total], candidate)
        answer = int(dp[amount])
    elif name == 'knapsack':
        inputs = {'weights': task.weights, 'values': task.values, 'capacity': task.capacity}
        dp = [Fraction(0)] * (task.capacity+1)
        for i, (weight, value) in enumerate(zip(task.weights, task.values), 1):
            for capacity in range(task.capacity, weight-1, -1):
                candidate = c(f'take({i},{capacity})', 'add', dp[capacity-weight], value)
                dp[capacity] = c(f'dp({i},{capacity})', 'max', dp[capacity], candidate)
        answer = int(dp[-1])
        task._answer = answer
    elif name == 'pair_sum':
        inputs = {'values': task.values, 'target': task.target}
        seen = {}
        total = Fraction(0)
        for i, value in enumerate(task.values):
            complement = int(c(f'complement_{i}', 'sub', task.target, value))
            matches = c(f'seen_{complement}', 'add', seen.get(complement, 0), 0)
            total = c(f'pairs_{i}', 'add', total, matches)
            seen[value] = c(f'frequency_{value}', 'add', seen.get(value, 0), 1)
        answer = int(total)
    elif name == 'subarray_sum':
        inputs = {'nums': task.nums, 'target': task.target}
        seen = {0: Fraction(1)}
        prefix = total = Fraction(0)
        c('frequency_0', 'add', 1, 0)
        for i, value in enumerate(task.nums):
            prefix = c(f'prefix_{i}', 'add', prefix, value)
            required = c(f'required_{i}', 'sub', prefix, task.target)
            matches = c(f'frequency_lookup_{required}', 'add', seen.get(required, 0), 0)
            total = c(f'count_{i}', 'add', total, matches)
            seen[prefix] = c(f'frequency_{prefix}', 'add', seen.get(prefix, 0), 1)
        answer = int(total)
    elif task.task_type == 'lis':
        inputs = {'seq': task.seq}
        dp = [Fraction(1)] * len(task.seq)
        for i in range(len(dp)):
            c(f'dp_initial_{i}', 'add', 1, 0)
            for j in range(i):
                if c(f'x_{j}<x_{i}', 'lt', task.seq[j], task.seq[i]):
                    dp[i] = c(f'dp_{i}', 'max', dp[i], c('extend', 'add', dp[j], 1))
        best = dp[0]
        for value in dp[1:]: best = c('LIS', 'max', best, value)
        answer = int(best)
    else:
        inputs = {'text': task.text}
        n = len(task.text)
        dp = [[Fraction(0)] * n for _ in range(n)]
        for i in range(n): dp[i][i] = c(f'dp({i},{i})', 'add', 1, 0)
        for length in range(2,n+1):
            for i in range(n-length+1):
                j = i+length-1
                if c(f'char_{i}==char_{j}', 'eq', ord(task.text[i]), ord(task.text[j])):
                    dp[i][j] = c(f'dp({i},{j})', 'add', dp[i+1][j-1] if length>2 else 0, 2)
                else: dp[i][j] = c(f'dp({i},{j})', 'max', dp[i+1][j], dp[i][j-1])
        answer = int(dp[0][-1])
    task.answer = answer
    tr.finish(task, answer, inputs)
