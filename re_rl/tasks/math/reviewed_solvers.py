"""Recompute deterministic solvers from the stated instance, observing execution."""
import ast
from fractions import Fraction
from importlib import import_module
from itertools import permutations, product
import math
from re_rl.tasks.reviewed_formulas import MATH, execute_spec

# Existing independent implementations are executed again, not their cached answers.
DIRECT = {
 'container_water': ('max_water', 'heights'), 'histogram_area': ('largest_rectangle','heights'),
 'gas_station': ('circuit_start','gas cost'), 'local_alignment': ('local_alignment','left right'),
 'majority_element': ('majority','values'), 'nussinov': ('nussinov','seq'),
 'optimal_bst': ('optimal_bst','freq'), 'palindrome_subseq': ('lps_length','text'),
 'sequence_alignment': ('alignment_score','left right'), 'shapley_value': ('shapley','values player'),
 'secret_share': ('reconstruct','shares prime'), 'topo_count': ('count_topological_orders','n edges'),
 'trapping_rain': ('trap','heights'), 'weighted_interval': ('max_weighted','jobs'),
}


def sum_iter(values):
    total = 0
    for value in values:
        total += value
    return total


def invert_count(values):
    count = 0
    for i in range(len(values)):
        for j in range(i+1, len(values)):
            inverted = values[i] > values[j]
            count += int(inverted)
    return count


def rpn(tokens):
    stack = []
    for token in tokens:
        if token not in ('+', '-', '*'):
            stack.append(int(token))
        else:
            right, left = stack.pop(), stack.pop()
            value = left+right if token == '+' else left-right if token == '-' else left*right
            stack.append(value)
    return stack[-1]


def bits_count(n):
    digits = []
    while n:
        n, remainder = divmod(n, 2)
        digits.append(remainder)
    ones = sum_iter(digits)
    return ones, len(digits), ''.join(map(str, reversed(digits)))


def modular_power(a, b, m):
    result = 1 % m
    base = a % m
    while b:
        if b % 2:
            result = result * base % m
        base = base * base % m
        b //= 2
    return result


def formula_models(variables, formulas, evaluate, equivalent=False):
    count = 0
    for bits in product((False, True), repeat=len(variables)):
        assignment = dict(zip(variables, bits))
        value = evaluate(formulas[0], assignment)
        if equivalent:
            other = evaluate(formulas[1], assignment)
            if value != other:
                return False
        else:
            count += int(value)
    return True if equivalent else count


def grid_solution(task):
    solutions = []
    for drinks in permutations(task.drinks):
        dmap = dict(zip(task.people, drinks))
        if not all(task._clue_holds(c, dmap, None) for c in task.clues if c[0] in ('d+', 'd-')):
            continue
        for sports in permutations(task.sports):
            smap = dict(zip(task.people, sports))
            if all(task._clue_holds(c, dmap, smap) for c in task.clues):
                solutions.append((dmap, smap))
    if len(solutions) != 1:
        raise ValueError('non_unique')
    mapping = solutions[0][0 if task.query_attr == 'drink' else 1]
    return mapping[task.query_person]


def infer_sequence(given, kind):
    if kind == 'arithmetic':
        differences = [b-a for a,b in zip(given, given[1:])]
        assert len(set(differences)) == 1
        return given[-1] + differences[-1]
    if kind == 'geometric':
        ratios = [Fraction(b,a) for a,b in zip(given,given[1:])]
        assert len(set(ratios)) == 1
        return int(given[-1] * ratios[-1])
    if kind == 'alternating':
        magnitudes = [value * (-1)**i for i,value in enumerate(given)]
        step = magnitudes[1] - magnitudes[0]
        assert all(b-a == step for a,b in zip(magnitudes,magnitudes[1:]))
        return (magnitudes[-1]+step) * (-1)**len(given)
    if kind == 'quadratic':
        differences = [b-a for a,b in zip(given,given[1:])]
        second = [b-a for a,b in zip(differences,differences[1:])]
        assert len(set(second)) == 1
        return given[-1] + differences[-1] + second[-1]
    candidates = []
    for p,q in ((1,1),(2,1),(1,2)):
        fits = all(given[i] == p*given[i-1]+q*given[i-2] for i in range(2,len(given)))
        if fits:
            candidates.append(p*given[-1]+q*given[-2])
    assert len(set(candidates)) == 1
    return candidates[0]


def loop_complexity(code):
    def block(statements):
        costs = []
        for node in statements:
            if isinstance(node, ast.For):
                inner = block(node.body)
                costs.append((inner[0]+1, inner[1]))
            elif isinstance(node, ast.While):
                inner = block(node.body)
                costs.append((inner[0], inner[1]+1))
            else:
                costs.append((0,0))
        return max(costs)
    power, logarithms = block(ast.parse(code).body)
    token = '1' if power == 0 else 'n' if power == 1 else f'n^{power}'
    if logarithms:
        token = 'logn' if power == 0 else token.replace('^','^')+'logn'
        if power == 1: token = 'nlogn'
    return token


def master(a,b,d):
    critical, power = 0, 1
    while power < a:
        power *= b
        critical += 1
    assert power == a
    case = 1 if critical > d else 2 if critical == d else 3
    exponent = max(critical, d)
    token = '1' if exponent == 0 else 'n' if exponent == 1 else f'n^{exponent}'
    if case == 2:
        token = 'nlogn' if exponent == 1 else token+'logn'
    return token, critical, case


def dice_counts(faces, total=None, ways=None):
    counts = {}
    for first in range(1, faces+1):
        for second in range(1, faces+1):
            summed = first + second
            counts[summed] = counts.get(summed, 0) + 1
    if total is not None:
        return counts.get(total, 0)
    candidates = [value for value,count in counts.items() if count == ways]
    return min(candidates)


def closest(points):
    best = None
    for i,a in enumerate(points):
        for b in points[i+1:]:
            squared = (a[0]-b[0])**2 + (a[1]-b[1])**2
            best = squared if best is None else min(best,squared)
    return round(math.sqrt(best), 2)


def tournament_score(results, query):
    points = 0
    for a,b,score in results:
        if query not in (a,b): continue
        if score not in ('A','B'): points += 1
        elif (score == 'A' and query == a) or (score == 'B' and query == b): points += 3
    return points


def solve_math(task, name, module, trace):
    kind = getattr(task,'subtype',None) or getattr(task,'task_type',None)
    def run(function, fields, *extra):
        names = fields.split()
        values = [getattr(task,k) for k in names]
        inputs.update(zip(names,values))
        return trace.call(function, *values, *extra)
    inputs = {'subtype': kind}
    if name == 'inequality_proof':
        from re_rl.tasks.math.logic.inequality_proof.solver import nonnegative
        inputs.update(a=task.a,b=task.b,c=task.c)
        valid=nonnegative(task.a,task.b,task.c,trace.events)
        task.final_answer='YES' if valid else 'NO'
        return inputs,True
    if name in ('mastermind','mastermind_image'):
        from re_rl.tasks.math.logic.mastermind.solver import deduce
        inputs.update(length=task.L,colors=task.C,clues=task.guesses)
        code=deduce(task.L,task.C,task.guesses,trace.events)
        task.final_answer=' '.join(map(str,code))
        return inputs,True
    if name == 'find_the_error':
        from re_rl.tasks.math.logic.find_the_error.solver import locate
        inputs['steps']=[list(row[:4]) for row in task._steps]
        task.final_answer=str(locate(inputs['steps'],trace.events))
        return inputs,True
    if name == 'combinatorial_optimization':
        from re_rl.tasks.math.discrete.combinatorial_optimization.solver import knapsack,set_cover,tsp
        inputs['mode']=task.solve_mode
        if kind=='knapsack':
            inputs.update(items=task.items,capacity=task.capacity)
            value,chosen=knapsack(task.items,task.capacity,task.solve_mode,trace.events)
            task.final_answer=f'value={value};items={chosen}'
        elif kind=='set_cover':
            inputs.update(universe=sorted(task.universe),sets=[sorted(s) for s in task.sets])
            value,chosen=set_cover(task.universe,task.sets,task.solve_mode,trace.events)
            task.final_answer=f'size={value};sets={chosen}'
        else:
            inputs['matrix']=task.matrix
            value,chosen=tsp(task.matrix,task.solve_mode,trace.events)
            task.final_answer=f'distance={value};route={chosen}'
        return inputs,True
    if name == 'sat_smt_mini':
        from re_rl.tasks.math.logic.sat_smt_mini.solver import dpll
        inputs.update(num_vars=task.num_vars,clauses=task._cnf)
        model=dpll(task.num_vars,task._cnf,trace.events)
        task.final_answer='UNSAT' if model is None else 'SAT:'+','.join(f'x{i+1}={v}' for i,v in enumerate(model))
        return inputs,True
    if name == 'proof_cases_counterexample':
        from re_rl.tasks.math.logic.proof_cases_counterexample.solver import analyse
        inputs['claim']=task.claim
        valid,counterexample=analyse(task.claim,trace.events)
        task.final_answer='TRUE' if valid else f'FALSE;n={counterexample}'
        return inputs,True
    if name == 'csp_reasoning':
        from re_rl.tasks.math.logic.csp_reasoning.solver import latin, mini_kakuro
        if kind == 'latin_square':
            inputs.update(size=task.size,puzzle=task._puzzle_grid)
            grid = latin(task._puzzle_grid,trace.events)
            task.final_answer = ';'.join(','.join(map(str,row)) for row in grid)
        else:
            inputs['sums'] = task._kakuro_sums
            values = mini_kakuro(task._kakuro_sums,trace.events)
            task.final_answer = ','.join(f'{k}={v}' for k,v in zip('ABCD',values))
        return inputs,True
    if name == 'os_scheduling':
        from re_rl.tasks.math.logic.os_scheduling.solver import schedule
        fields = ('bursts',) if kind == 'sjf_wait' else ('jobs',) if kind == 'fcfs_wait' else ('start','reqs')
        inputs.update({field: getattr(task,field) for field in fields})
        task.order, task.answer = schedule(kind,inputs,trace.events)
        return inputs
    if name in ('calendar_reasoning','datalog_inference','resolution','grid_color_count','queens_check_image'):
        from re_rl.tasks.math.logic.remaining_inference import ordinal,datalog,resolution,color_counts,queens_valid,target_count,most_color
        if name == 'calendar_reasoning':
            inputs['d1'] = task.d1.isoformat()
            first = trace.call(ordinal,task.d1.year,task.d1.month,task.d1.day)
            if kind == 'date_diff':
                inputs['d2'] = task.d2.isoformat()
                second = trace.call(ordinal,task.d2.year,task.d2.month,task.d2.day)
                task.answer_int = trace.call(calendar_difference,first,second)
            else:
                delta = task.delta if kind == 'add_days' else 0
                inputs['delta'] = delta
                index = trace.call(calendar_weekday,first,delta)
                task.answer_label = module._WD[task.lang][index]
        elif name == 'datalog_inference':
            inputs.update(objects=task.objects,facts={o:sorted(task.facts[o]) for o in task.objects},
                          rules=task.rules,target=task.target)
            task.closure = datalog(task.objects,task.facts,task.rules,task.target,trace.events)
            if kind == 'has_property':
                inputs['query_obj'] = task.query_obj
                task.answer_bool = task.target in task.closure[task.query_obj]
            else:
                task.answer_int = trace.call(target_count,task.objects,task.closure,task.target)
        elif name == 'resolution':
            inputs['clauses'] = [[[v,p] for v,p in sorted(c)] for c in task.clauses]
            value = resolution(task.clauses,kind != 'unsat',trace.events)
            if kind == 'unsat': task.answer_bool = value
            else: task.answer_int = value
        elif name == 'grid_color_count':
            inputs.update(grid=task.grid,palette=task.palette)
            task.counts = trace.call(color_counts,task.grid,task.palette)
            if kind == 'count_color':
                inputs['target'] = task.target
                task.answer_int = task.counts.get(task.target,0)
            else:
                task.most = trace.call(most_color,task.counts)
        else:
            inputs.update(cols=task.cols,n=task.n,index_base=0)
            if len(task.cols) != task.n or any(not isinstance(c,int) or not 0 <= c < task.n for c in task.cols):
                raise ValueError('invalid_board')
            task.answer_bool = trace.call(queens_valid,task.cols)
        return inputs
    if name == 'analogical':
        from re_rl.tasks.math.logic.analogical.solver import infer
        inputs.update(examples=task.examples,query=task.query,coefficient_bound=task.coefficient_bound,
                      offset_bound=task.offset_bound,max_power=task.max_power)
        task.answer = infer(task.examples,task.query,task.coefficient_bound,task.offset_bound,task.max_power,trace.events)
        return inputs
    if name in ('natural_deduction','logical_entailment','syllogism'):
        from re_rl.tasks.math.logic.proof_semantics import proof,entails,syllogism
        if name == 'natural_deduction':
            inputs.update(lines=task.lines,index_base=0)
            task.valid = proof(task.lines,trace.events)
        elif name == 'logical_entailment':
            inputs.update(variables=task.vars,premises=task.premises,conclusion=task.conclusion)
            task._entails = entails(task.vars,task.premises,task.conclusion,trace.events)
        else:
            inputs.update(terms={'S':task.S,'M':task.M,'P':task.P},premise1=task.premise1,premise2=task.premise2,conclusion=task.conclusion)
            task._valid = syllogism(task.premise1,task.premise2,task.conclusion,trace.events)
        return inputs
    if name == 'family_tree':
        from re_rl.tasks.math.logic.family_tree.solver import relationship,fingerprint
        inputs.update(names=task.name,gender=task.gender,couples=task.couples,child_groups=task.child_groups,query=[task.a,task.b])
        task.role = relationship(task.gender,task.couples,task.child_groups,task.a,task.b,trace.events)
        task._kin_certificate = (fingerprint(task),task.role)
        return inputs
    if name == 'contradiction':
        from re_rl.tasks.math.logic.contradiction.solver import evaluate
        inputs.update(definitions=task.definitions,claims=task.claims,statement_index_base=0)
        _,false_indices = evaluate(task.definitions,task.claims,trace.events)
        if len(false_indices) != 1:raise ValueError('expected_one_false_claim')
        task.false_statement_index = false_indices[0]
        return inputs
    if name in ('minesweeper_deduction','minesweeper_image'):
        from re_rl.tasks.math.logic.deduction_search import mine_status
        clues = {cell:task.number[cell] for cell in task.revealed}
        inputs.update(n=task.n,clues=[[r,c,value] for (r,c),value in sorted(clues.items())],target=list(task.target),index_base=0)
        possible = mine_status(task.n,clues,task.target,trace.events)
        if len(possible) != 1:raise ValueError('ambiguous_target' if possible else 'inconsistent_clues')
        task.target_is_mine = bool(possible[0])
        fingerprint = (task.n,tuple(sorted((r,c,value) for (r,c),value in clues.items())),tuple(task.target))
        task._mine_certificate = (fingerprint,possible[0])
        return inputs
    if name == 'zebra_puzzle':
        from re_rl.tasks.math.logic.deduction_search import zebra_answer
        inputs.update(n=task.num_houses,category_values=task.category_values,
                      clues=[{'type':c['type'],'data':c['data']} for c in task.clues],query=list(task.query),index_base=0)
        task.solution,answer = zebra_answer(task.num_houses,task.category_values,task.clues,task.query,trace.events)
        task.answer = module.texts.t('house_answer',task.language,position=answer+1) if task.query[0] == 'position' else answer
        task._answer_certificate = (task._public_fingerprint(),answer)
        return inputs
    if name in ('bayesian_reasoning','urn_probability'):
        from re_rl.tasks.math.probability.inference_traces import bayesian,urn
        if name == 'bayesian_reasoning':
            inputs.update(parameters=task.parameters)
            task.probability = trace.call(bayesian,kind,task.parameters)
            return inputs
        inputs.update(containers=task.containers,draws=task.draws,color=task.color_choice,kind=task.question_kind,x=task.x_val)
        task.probability = trace.call(urn,task.containers,task.draws,task.color_choice,task.question_kind,task.x_val)
        task.final_answer = module.PROMPT_TEMPLATES['urn_probability']['final_answer'][task.language].format(prob_value=format(float(task.probability),'.4f'))
        return inputs,True
    if name in ('futoshiki','cryptarithmetic','knights_knaves'):
        from re_rl.tasks.math.logic.puzzle_inference import futoshiki,cryptarithm,knight_models
        if name == 'futoshiki':
            inputs.update(size=task.size,inequalities=task.inequalities,index_base=0)
            task.solution = futoshiki(task.size,task.inequalities,trace.events)
        elif name == 'cryptarithmetic':
            inputs.update(a=task._word_a,b=task._word_b,c=task._word_c)
            task._mapping = cryptarithm(task._word_a,task._word_b,task._word_c,trace.events)
        else:
            inputs.update(names=task.names,statements=[{k:v for k,v in s.items() if k != 'text'} for s in task.statements],
                          role_encoding='true=knight,false=knave')
            models = knight_models(task.num_persons,task.statements,trace.events)
            task.roles = None if not models else ['knight' if role else 'knave' for role in models[0]]
        return inputs
    if name == 'hanoi_disk':
        inputs.update(pegs=task.pegs,n=task.n,target=3,disk_index_base=1)
        if len(task.pegs) != task.n+1 or any(type(p) is not int or p not in (1,2,3) for p in task.pegs[1:]):
            raise ValueError('invalid_pegs')
        task.trace,task.moves = trace.call(module.hanoi_trace,list(task.pegs))
        task.home = trace.call(count_home,task.pegs)
        task.answer = task.moves if kind == 'moves' else task.home
        return inputs
    if name in ('water_jug','tower_of_hanoi','blocks_world'):
        from re_rl.tasks.math.planning.search_traces import water_jug,hanoi,blocks_world
        if name == 'water_jug':
            inputs.update(capacities=list(task.capacities),target=task.target,index_base=0)
            task.solution_path = water_jug(task.capacities,task.target,trace.events)
            task.is_solvable = bool(task.solution_path)
        elif name == 'tower_of_hanoi':
            inputs.update(num_disks=task.num_disks,source=task.source,target=task.target,auxiliary=task.auxiliary)
            task.moves = hanoi(task.num_disks,task.source,task.target,task.auxiliary,trace.events)
        else:
            inputs.update(blocks=task.blocks,initial=task._init_state,goal=task._goal_state,
                          encoding='support index in blocks; -1=table')
            path = blocks_world(task.blocks,task._init_state,task._goal_state,trace.events)
            task._plan = []
            for state,action in path[1:]:
                block,target = action
                task._plan.append(module.texts.t('s2',task.language,b=task.blocks[block]) if target == -1
                                  else module.texts.t('s4',task.language,b=task.blocks[block],c=task.blocks[target]))
        return inputs
    if name == 'river_crossing':
        inputs.update(problem_type=task.problem_type)
        if task.problem_type == 'jealous_husbands':
            from re_rl.tasks.math.planning.river_crossing.search import jealous
            inputs.update(num_couples=task.num_couples,capacity=task.capacity,
                          person_encoding='2*i=husband,2*i+1=wife',state_encoding='right_bank_mask,boat_side')
            task.solution_path = jealous(task.num_couples,task.capacity,trace.events)
        else:
            inputs.update(missionaries=task.missionaries,cannibals=task.cannibals,capacity=task.capacity)
            task.solution_path = trace.call(task._solve)
        return inputs
    if name in ('sliding_puzzle','sliding_puzzle_image'):
        from re_rl.tasks.math.logic.navigation_traces import sliding
        inputs.update(board=list(task.board), n=task.n, index_base=0)
        value = sliding(task.board,task.n,kind,trace.events)
        if kind == 'solvable':
            task.answer_bool = value
        else:
            task.answer_int = value
        return inputs
    if name in ('grid_navigation','grid_navigation_image'):
        from re_rl.tasks.math.logic.navigation_traces import maze,commands
        if kind == 'maze':
            inputs.update(grid=task.grid, index_base=0)
            task._answer_maze = maze(task.grid,trace.events)
        else:
            inputs.update(start_dir=task.start_dir,commands=task.commands,
                          direction_order=['N','E','S','W'],initial_position=[0,0])
            task.end_x,task.end_y,task.end_dir = commands(task.start_dir,task.commands,trace.events)
        return inputs
    if name in MATH:
        return execute_spec(task,name,trace,MATH)
    if name in DIRECT:
        helper, fields = DIRECT[name]
        task.answer = run(getattr(module,helper),fields)
    elif name == 'alpha_beta':
        task.value, task.visited = run(module.alpha_beta,'branches')
        task.answer = task.value if kind == 'value' else task.visited
    elif name == 'balanced_brackets': task._answer = run(task._is_balanced,'s')
    elif name == 'bit_count':
        task.ones, task.width, task.binary = run(bits_count,'n')
        task.answer = getattr(task,kind)
    elif name == 'cfg_membership':
        inputs.update(nts=task.nts,binary=task.binary,term=task.term)
        task.answer = run(task._cyk,'string')
    elif name == 'collatz_steps':
        task.steps, task.peak = run(module.collatz,'start')
        task.answer = task.steps if kind == 'steps' else task.peak
    elif name in ('computational_geometry','convex_hull_image'):
        if kind == 'convex_hull':
            task.hull = run(module.convex_hull,'points'); task.answer = len(task.hull)
        elif kind == 'segment_intersection':
            inputs['segments'] = task.seg
            task.answer = trace.call(module.segments_intersect,*task.seg)
        elif hasattr(task,'poly'):
            task.answer = run(module.point_in_polygon,'poly query')
        else: task.answer = run(closest,'points')
    elif name in ('connect_four','tic_tac_toe'):
        from re_rl.tasks.math.reviewed_games import minimax
        if hasattr(task,'_cache'): task._cache.clear()
        fields = 'cols player' if name == 'connect_four' else 'board player'
        inputs.update({key:getattr(task,key) for key in fields.split()})
        task.value = minimax(task,name == 'connect_four',trace.events)
    elif name == 'cube_net':
        inputs.update(pos=task.pos,query_label=task.query_label)
        def opposite(pos, query_label, pairs):
            position = next(key for key,value in pos.items() if value == query_label)
            opposite_position = pairs[position]
            return pos[opposite_position]
        task.answer = trace.call(opposite,task.pos,task.query_label,task._OPP)
    elif name == 'dfa_minimization':
        inputs.update(delta=task.delta,accepting=task.accepting,start=0)
        task.answer = trace.call(task._minimize)
    elif name == 'dice_ways':
        if kind == 'ways':
            task.ways = run(dice_counts,'faces total');task.answer = task.ways
        else:
            inputs.update(faces=task.faces,ways=task.ways)
            task.total = trace.call(dice_counts, task.faces, ways=task.ways);task.answer = task.total
    elif name == 'digital_root':
        task.chain, task.root, task.steps = run(module.digit_chain,'n')
        task.answer = task.root if kind == 'root' else task.steps
    elif name == 'direct_mapped_cache':
        task.hits,task.misses,task.trace = run(module.simulate,'addrs block_size n_lines')
        if kind == 'tag':
            inputs['which'] = task.which
            task.answer,_ = trace.call(module.locate,task.addrs[task.which],task.block_size,task.n_lines)
        else: task.answer = getattr(task,kind)
    elif name == 'edit_distance':
        inputs.update(s1=task.s1,s2=task.s2)
        task._answer = trace.call(task._lev if kind == 'edit_distance' else task._lcs)
    elif name == 'euclid_gcd':
        task.gcd,task.steps = run(module.euclid,'a b');task.answer = getattr(task,kind)
    elif name == 'gray_code':
        if kind == 'encode':
            encoded = run(module.gray_encode,'value')
            task.bits = format(encoded,f'0{task.width}b');task.answer = task.bits
        else:
            inputs['bits'] = task.bits
            task.value = trace.call(module.gray_decode,int(task.bits,2));task.answer = task.value
    elif name == 'huffman_coding': task.answer = run(task._huffman_cost,'freqs')
    elif name == 'integer_sqrt':
        task.root,task.remainder = run(module.isqrt_pair,'n');task.answer = getattr(task,kind)
    elif name == 'interval_scheduling':
        inputs['intervals'] = task.intervals
        if kind == 'max_activities': task._answer = trace.call(task._max_nonoverlap)
        elif kind == 'min_rooms': task._answer = trace.call(task._max_concurrent)
        else:
            inputs.update(i=task.i,j=task.j)
            def overlap(a,b):
                starts_before_end = a[0] < b[1]
                ends_after_start = b[0] < a[1]
                return starts_before_end and ends_after_start
            task._answer = trace.call(overlap,task.intervals[task.i],task.intervals[task.j])
    elif name == 'josephus': task.answer,task.eliminated = run(module.josephus,'n k')
    elif name == 'logic_grid':
        inputs.update(people=task.people,drinks=task.drinks,sports=task.sports,clues=task.clues,query_person=task.query_person,query_attr=task.query_attr)
        task.answer = trace.call(grid_solution,task)
    elif name in ('model_counting','logical_equivalence'):
        from re_rl.tasks.math.logic.formal_logic2_shared.base import _eval
        formulas = [task.formula] if name == 'model_counting' else [task.f1,task.f2]
        inputs.update(variables=task.vars,formulas=formulas)
        task._answer = trace.call(formula_models,task.vars,formulas,_eval,name == 'logical_equivalence')
    elif name == 'manhattan_paths':
        inputs.update(x=task.x,y=task.y)
        task.distance = trace.call(sum_iter,[task.x,task.y])
        task.paths = trace.call(module.binom,task.distance,task.x)
        task.answer = task.distance if kind == 'distance' else task.paths
    elif name == 'mixed_nash':
        task.row_prob,task.col_prob = run(module.mixed_equilibrium,'row column')
        task.answer = task.row_prob if kind == 'row' else task.col_prob
    elif name == 'modular_arithmetic':
        task._answer = run(task._smallest_dlog,'g h p') if kind == 'discrete_log' else run(modular_power,'a b m')
    elif name == 'odd_sum':
        if kind == 'sum':
            inputs['n'] = task.n
            task.square = trace.call(sum_iter,range(1,2*task.n,2));task.answer = task.square
        else:
            inputs['square'] = task.square
            def root(value):
                root = math.isqrt(value)
                assert root * root == value
                return root
            task.n = trace.call(root,task.square);task.answer = task.n
    elif name == 'page_replacement':
        task.answer,task.trace = run(task.simulate,'refs frames_n task_type')
    elif name == 'pattern_induction': task._answer = run(infer_sequence,'given subtype')
    elif name == 'polynomial_product':
        task.product = run(module.poly_mul,'left right')
        inputs.update(power=task.power,point=task.point)
        task.value = trace.call(module.poly_eval,task.product,task.point)
        task.answer = task.product[task.power] if kind == 'coefficient' else task.value
    elif name == 'program_trace':
        inputs.update(program=task.prog,variables=task.vars,query=task.query)
        task._answer = trace.call(task._run)
    elif name == 'qbf':
        inputs.update(variables=task.vars,quantifiers=task.quant,matrix=task.matrix)
        task._answer = trace.call(task._eval_qbf,0,{})
    elif name in ('range_add','range_query'):
        helper = module.apply_range_adds if name == 'range_add' else module.apply_updates
        task.range_sum,task.total = run(helper,'values updates left right')
        task.answer = task.range_sum if kind == 'range' else task.total
    elif name == 'rpn_eval': task._answer = run(rpn,'tokens')
    elif name == 'second_price':
        task.winner,task.payment = run(module.second_price,'bids');task.answer = getattr(task,kind)
    elif name == 'sorting_trace':
        inputs['arr'] = task.arr
        if kind == 'inversions': task._answer = trace.call(invert_count,task.arr)
        else:
            inputs['k'] = task.k;task.result = trace.call(task._bubble_passes,task.k)
    elif name == 'stable_matching':
        inputs.update(prefs_p=task.prefs_p,prefs_a=task.prefs_a)
        if kind == 'partner':
            task.match,task.log = trace.call(task.gale_shapley,task.prefs_p,task.prefs_a)
            inputs['who'] = task.who;task.answer = task.match[task.who]
        else:
            inputs['match'] = task.match
            task.block = trace.call(task.blocking_pair,task.match,task.prefs_p,task.prefs_a)
            task.answer = task.block is None
    elif name == 'tournament':
        if kind == 'round_robin': task.answer = run(tournament_score,'results query')
        else:
            inputs.update(rounds=task.rounds,teams=task.bracket_teams)
            def champion(rounds):
                winner = None
                for matches in rounds:
                    for match in matches:
                        winner = match[-1]
                return winner
            task.champion = trace.call(champion,task.rounds)
    elif name == 'turing_machine':
        inputs.update(transitions=task.trans,tape=task.tape0,steps=task.steps)
        task._answer = trace.call(task._run)
    elif name == 'twos_complement':
        inputs['width'] = task.bits
        if kind == 'decode': task.value = run(task._from_bits,'bits_str');task.answer = task.value
        elif kind == 'encode': task.answer = run(task._to_bits,'value')
        else:
            inputs.update(a=task.a,b=task.b)
            def overflow(a,b,width):
                low,high = -(1 << (width-1)),(1 << (width-1))-1
                total = a+b
                return not low <= total <= high
            task.overflow = trace.call(overflow,task.a,task.b,task.bits);task.answer = task.overflow
    elif name == 'unification':
        inputs.update(termA=task.termA,termB=task.termB)
        substitution = trace.call(task._unify,task.termA,task.termB)
        task.unifiable = substitution is not None
        task.result = trace.call(task._resolve,task.termA,substitution) if task.unifiable else None
    elif name == 'word_ladder':
        inputs.update(words=task.words,start=task.start,target=task.target)
        letters = sorted(set(''.join(task.words)))
        distances = trace.call(task._bfs,task.start,set(task.words),letters)
        task.answer = distances[task.target]
    elif name == 'binary_search':
        task.index,task.comps,task.mids = run(module.binary_search,'arr target')
        task.answer = task.index if kind == 'index' else task.comps
    elif name == 'kmp_matching':
        if kind == 'failure_function': task.pi = run(task._prefix_function,'pattern')
        else: task.count = run(task._count_occurrences,'text pattern')
    elif name in ('game_of_life','game_of_life_image'):
        from re_rl.tasks.math.reviewed_cellular import life
        inputs.update(initial_grid=task.grid0,steps=task.k,boundary=0)
        task.grid = life(task,trace.events)
    elif name == 'elementary_ca':
        from re_rl.tasks.math.reviewed_cellular import elementary
        inputs.update(initial_row=task.row0,steps=task.k,boundary=0,rule=task.rule)
        task.row = elementary(task,trace.events)
    elif name == 'truth_table':
        from re_rl.tasks.math.logic.inference_traces import classify_formula
        task.klass,task.true_count,task.truth_rows = run(classify_formula,'vars formula')
    elif name == 'three_sat':
        from re_rl.tasks.math.logic.inference_traces import solve_cnf
        task.assignment = run(solve_cnf,'nv clauses')
    elif name in ('arc_grid_induction','arc_grid_image'):
        from re_rl.tasks.math.logic.inference_traces import infer_arc
        grids = [grid for pair in task.train for grid in pair] + [task.test_in]
        colors = 1+max(value for grid in grids for row in grid for value in row)
        inputs.update(train=task.train,test_in=task.test_in,palette=list(range(colors)))
        task.test_out = infer_arc(task.train,task.test_in,colors,trace)
    elif name in ('binary_puzzle','nonogram','battleship'):
        from re_rl.tasks.math.logic.grid_search_traces import takuzu,nonogram,battleship
        inputs['index_base'] = 0
        if name == 'binary_puzzle':
            inputs.update(size=task.n,given=[dict(row=r,col=c,value=value) for (r,c),value in sorted(task.given.items())])
            solution = takuzu(task.n,task.given,trace.events)
        elif name == 'nonogram':
            inputs.update(row_clues=task.row_clues,col_clues=task.col_clues)
            solution = nonogram(task.row_clues,task.col_clues,trace.events)
        else:
            inputs.update(row_counts=task.row_counts,col_counts=task.col_counts,fleet=task.fleet)
            solution = battleship(task.row_counts,task.col_counts,task.fleet,trace.events)
        if solution is None:
            raise ValueError('unsatisfiable')
        task.sol = solution
    elif name in ('kakuro','kenken','magic_square','magic_square_image','n_queens','skyscrapers'):
        from re_rl.tasks.math.logic.csp_search_traces import kakuro_solutions,kenken,magic_square,queens,skyscrapers
        inputs['index_base'] = 0
        if name == 'kakuro':
            inputs.update(s1=task.s1,s2=task.s2,v1=task.v1,v2=task.v2)
            solutions = kakuro_solutions(task.s1,task.s2,task.v1,task.v2,trace.events)
            if not solutions: raise ValueError('unsatisfiable')
            task.solution = solutions[0]
        elif name == 'kenken':
            inputs.update(size=task.n,cages=task.cages,clues=task.clues)
            grid = kenken(task.n,task.cages,task.clues,trace.events)
            task.solution = tuple(map(tuple,grid)) if grid is not None else None
        elif name in ('magic_square','magic_square_image'):
            inputs.update(size=3,total=15,given={str(cell):value for cell,value in sorted(task.given.items())})
            values = magic_square(task.given,trace.events)
            task.solution = tuple(values) if values is not None else None
        elif name == 'n_queens':
            inputs.update(size=task.n,subtype=task.subtype)
            count,first = queens(task.n,task.subtype == 'count',trace.events)
            if task.subtype == 'count': task._count = count
            else: task.solution = first
        else:
            inputs.update(size=task.n,clues=task.clues)
            grid = skyscrapers(task.n,task.clues,trace.events)
            task.solution = tuple(map(tuple,grid)) if grid is not None else None
        if name != 'kakuro' and not (name == 'n_queens' and task.subtype == 'count') and task.solution is None:
            raise ValueError('unsatisfiable')
    elif name in ('hitori','star_battle','sudoku','sudoku_image'):
        from re_rl.tasks.math.logic.board_search_traces import hitori,star_battle,sudoku
        inputs['index_base'] = 0
        if name == 'hitori':
            inputs['grid'] = task.grid
            result = hitori(task.grid,trace.events)
            if result is None: raise ValueError('unsatisfiable')
            task.shaded = result
        elif name == 'star_battle':
            inputs['regions'] = task.region
            result = star_battle(task.region,trace.events)
            if result is None: raise ValueError('unsatisfiable')
            task.stars = result
        else:
            inputs.update(puzzle=task.puzzle,block_size=task.block_size)
            results = sudoku(task.puzzle,events=trace.events)
            if not results: raise ValueError('unsatisfiable')
            task.solution = results[0]
            if name == 'sudoku_image':
                r,c = task.target
                inputs['target'] = task.target
                value = task.solution[r][c]
                if sudoku(task.puzzle,events=trace.events,forbidden=(r,c,value)):
                    raise ValueError('ambiguous_target')
                trace.events.append(dict(operation='sudoku_target_unique',row=r,col=c,value=value))
                task.target_value = value
                task._target_certificate = (tuple(map(tuple,task.puzzle)),tuple(task.target),value)
    elif name == 'algorithm_complexity':
        if kind == 'loops': task.answer = run(loop_complexity,'code')
        else: task.answer,task.crit,task.case = run(master,'a b d')
    else:
        raise NotImplementedError(name)
    return inputs


def calendar_difference(first,second):
    difference = second-first
    return difference


def calendar_weekday(ordinal,delta):
    shifted = ordinal+delta
    weekday = (shifted-1)%7
    return weekday


def count_home(pegs):
    count = 0
    for disk,peg in enumerate(pegs[1:],1):
        on_target = peg == 3
        count += int(on_target)
    return count
