"""Recorded RL backup, clipping, exploration and trace updates."""
from fractions import Fraction
from re_rl.tasks.computation_trace import ExactTrace

TRACED_RL_TASKS = ('sarsa', 'q_learning', 'polyak_update', 'vtrace', 'epsilon_greedy',
                   'expected_sarsa', 'reward_clip', 'bellman_backup', 'policy_expectation',
                   'ppo_clip', 'eligibility_trace')


def solve_detailed(task):
    tr = ExactTrace()
    c = tr.calc
    name, kind = task.TASK_TYPE, task.task_type
    inputs = {}
    if name in ('sarsa', 'q_learning'):
        next_value = task.q_next if name == 'sarsa' else task.max_next
        inputs = dict(q=task.q, reward=task.reward, alpha=task.alpha, gamma=task.gamma, next_value=next_value)
        target = c('target', 'add', task.reward, c('γQ_next', 'mul', task.gamma, next_value))
        task.delta = c('δ', 'sub', target, task.q)
        task.q_new = c('Q_new', 'add', task.q, c('αδ', 'mul', task.alpha, task.delta))
        answer = task.q_new if kind == 'q_new' else task.delta
    elif name == 'polyak_update':
        inputs = dict(theta=task.theta, old=task.old, tau=task.tau, index=task.index)
        complement = c('1−τ', 'sub', 1, task.tau)
        task.updated = []
        for i, (theta, old) in enumerate(zip(task.theta, task.old), 1):
            new_part = c(f'τθ_{i}', 'mul', task.tau, theta)
            old_part = c(f'(1−τ)θold_{i}', 'mul', complement, old)
            task.updated.append(c(f'θtarget_{i}', 'add', new_part, old_part))
        answer = task.updated[task.index]
        if kind == 'delta': answer = c('Δθ', 'sub', answer, task.old[task.index])
    elif name == 'vtrace':
        inputs = dict(ratio=task.ratio, rho_bar=task.rho_bar, reward=task.reward, gamma=task.gamma, value=task.value, nxt=task.nxt)
        task.rho = c('ρ', 'min', task.ratio, task.rho_bar)
        target = c('r+γV_next', 'add', task.reward, c('γV_next', 'mul', task.gamma, task.nxt))
        delta = c('δ', 'sub', target, task.value)
        task.target = c('v_target', 'add', task.value, c('ρδ', 'mul', task.rho, delta))
        answer = task.rho if kind == 'rho' else task.target
    elif name == 'epsilon_greedy':
        inputs = dict(q_values=task.q_values, epsilon=task.epsilon, draw=task.draw)
        explore = c('u<ε', 'lt', task.draw, task.epsilon)
        if explore:
            normalized = c('u/ε', 'div', task.draw, task.epsilon)
            index = c('floor(nu/ε)', 'floor', c('nu/ε', 'mul', len(task.q_values), normalized))
            answer = int(c('action', 'add', index, 1))
        else:
            best, action = Fraction(task.q_values[0]), 1
            c('Q_best', 'add', best, 0)
            for i, q in enumerate(task.q_values[1:], 2):
                if c(f'Q_{i}>Q_best', 'lt', best, q): best, action = Fraction(q), i
                c('action_best', 'add', action, 0)
            answer = action
    elif name == 'expected_sarsa':
        inputs = dict(q_values=task.q_values, reward=task.reward, gamma=task.gamma)
        total = tr.accumulate('ΣQ', task.q_values)
        task.mean = c('E_Q', 'div', total, len(task.q_values))
        task.target = c('target', 'add', task.reward, c('γE_Q', 'mul', task.gamma, task.mean))
        answer = task.target if kind == 'target' else task.mean
    elif name == 'reward_clip':
        inputs = dict(rewards=task.rewards, limit=task.limit, gamma=task.gamma, t=task.t)
        task.clipped = []
        for i, reward in enumerate(task.rewards):
            task.clipped.append(int(c(f'clip_{i}', 'min', task.limit, c(f'lower_clip_{i}', 'max', -task.limit, reward))))
        value = Fraction(0)
        for i in reversed(range(len(task.clipped))):
            value = c(f'G_{i}', 'add', task.clipped[i], c(f'γG_{i+1}', 'mul', task.gamma, value))
        task.ret = value
        answer = Fraction(task.clipped[task.t]) if kind == 'clipped' else value
    elif name == 'bellman_backup':
        inputs = dict(r_a=task.r_a, r_b=task.r_b, v_a=task.v_a, v_b=task.v_b, gamma=task.gamma)
        task.q_a = c('Q(A)', 'add', task.r_a, c('γV(A)', 'mul', task.gamma, task.v_a))
        task.q_b = c('Q(B)', 'add', task.r_b, c('γV(B)', 'mul', task.gamma, task.v_b))
        task.value = c('V', 'max', task.q_a, task.q_b)
        task.greedy = 'A' if c('Q(B)<Q(A)', 'lt', task.q_b, task.q_a) else 'B'
        answer = task.value if kind == 'value' else task.greedy
    elif name == 'policy_expectation':
        inputs = dict(weights=task.weights, q_values=task.q_values, action=task.action)
        total = tr.accumulate('Σw', task.weights)
        terms = []
        for i, (weight, value) in enumerate(zip(task.weights, task.q_values), 1):
            probability = c(f'π_{i}', 'div', weight, total)
            terms.append(c(f'πQ_{i}', 'mul', probability, value))
        task.value = tr.accumulate('V', terms)
        task.advantage = c('A', 'sub', task.q_values[task.action], task.value)
        answer = task.value if kind == 'value' else task.advantage
    elif name == 'ppo_clip':
        inputs = dict(ratio=task.ratio, epsilon=task.epsilon, advantage=task.advantage)
        low, high = c('1−ε', 'sub', 1, task.epsilon), c('1+ε', 'add', 1, task.epsilon)
        task.clipped = c('clipped_ratio', 'min', high, c('lower_clip', 'max', low, task.ratio))
        raw = c('rA', 'mul', task.ratio, task.advantage)
        clipped = c('clip(r)A', 'mul', task.clipped, task.advantage)
        task.surrogate = c('L_clip', 'min', raw, clipped)
        answer = task.clipped if kind == 'clipped' else task.surrogate
    elif name == 'eligibility_trace':
        inputs = dict(trace=task.trace, gamma=task.gamma, lam=task.lam, visited=task.visited, index=task.index)
        decay = c('γλ', 'mul', task.gamma, task.lam)
        task.updated = []
        for i, value in enumerate(task.trace):
            faded = c(f'e_decay_{i+1}', 'mul', decay, value)
            task.updated.append(c(f'e_new_{i+1}', 'add', faded, int(i == task.visited)))
        answer = task.updated[task.index]
    else:
        raise ValueError(name)
    task.answer = answer
    tr.finish(task, answer, inputs)
