"""Detailed exact computations for metrics, regression, filtering and stump search."""
from fractions import Fraction
from re_rl.tasks.computation_trace import ExactTrace

TRACED_ML_TASKS = ('mae_loss', 'mse_loss', 'brier_score', 'r2_score', 'univariate_regression',
                   'precision_at_k', 'reciprocal_rank', 'cohen_kappa', 'jaccard_index',
                   'mean_average_precision', 'elimination_query', 'decision_stump', 'gradient_step', 'kmeans_step')


def solve_detailed(task):
    tr = ExactTrace()
    c = tr.calc
    name, kind = task.TASK_TYPE, task.task_type
    inputs = {}
    if name in ('mae_loss', 'mse_loss', 'brier_score'):
        pairs = list(zip(task.pred, task.truth)) if name != 'brier_score' else task.pairs
        inputs = {'pairs': pairs}
        errors = []
        for i, (pred, truth) in enumerate(pairs, 1):
            error = c(f'e_{i}', 'sub', pred, truth)
            errors.append(c(f'loss_{i}', 'abs' if name == 'mae_loss' else 'square', error))
        total = tr.accumulate('Σloss', errors)
        mean = c('mean_loss', 'div', total, len(pairs))
        if name == 'mae_loss': task.mae, task.sae = mean, total
        elif name == 'mse_loss': task.mse, task.sse = mean, total
        answer = total if kind in ('sae', 'sse') else mean
    elif name == 'r2_score':
        inputs = {'truth': task.truth, 'pred': task.pred}
        mean = c('y_mean', 'div', tr.accumulate('Σy', task.truth), len(task.truth))
        residuals, deviations = [], []
        for i, (truth, pred) in enumerate(zip(task.truth, task.pred), 1):
            residuals.append(c(f'residual²_{i}', 'square', c(f'residual_{i}', 'sub', pred, truth)))
            deviations.append(c(f'deviation²_{i}', 'square', c(f'deviation_{i}', 'sub', truth, mean)))
        task.ss_res, task.ss_tot = tr.accumulate('SS_res', residuals), tr.accumulate('SS_tot', deviations)
        task.r2 = c('R²', 'sub', 1, c('SS_res/SS_tot', 'div', task.ss_res, task.ss_tot))
        answer = task.r2 if kind == 'r2' else task.ss_tot
    elif name == 'univariate_regression':
        inputs = {'points': task.points}
        n = len(task.points)
        sx = tr.accumulate('Σx', [x for x, _ in task.points]); sy = tr.accumulate('Σy', [y for _, y in task.points])
        sxx = tr.accumulate('Σx²', [c(f'x²_{i}', 'square', x) for i, (x, _) in enumerate(task.points, 1)])
        sxy = tr.accumulate('Σxy', [c(f'xy_{i}', 'mul', x, y) for i, (x, y) in enumerate(task.points, 1)])
        numerator = c('b_num', 'sub', c('nΣxy', 'mul', n, sxy), c('ΣxΣy', 'mul', sx, sy))
        denominator = c('b_den', 'sub', c('nΣx²', 'mul', n, sxx), c('(Σx)²', 'square', sx))
        task.slope = c('b', 'div', numerator, denominator)
        task.intercept = c('a', 'div', c('Σy−bΣx', 'sub', sy, c('bΣx', 'mul', task.slope, sx)), n)
        answer = task.slope if kind == 'slope' else task.intercept
    elif name == 'cohen_kappa':
        inputs = {key: getattr(task, key) for key in ('tp', 'fp', 'fn', 'tn')}
        n = tr.accumulate('N', inputs.values())
        task.agreement = c('p_o', 'div', c('TP+TN', 'add', task.tp, task.tn), n)
        pos = c('positive_marginals', 'mul', c('TP+FP', 'add', task.tp, task.fp), c('TP+FN', 'add', task.tp, task.fn))
        neg = c('negative_marginals', 'mul', c('TN+FN', 'add', task.tn, task.fn), c('TN+FP', 'add', task.tn, task.fp))
        expected = c('p_e', 'div', c('marginal_sum', 'add', pos, neg), c('N²', 'square', n))
        task.kappa = c('κ', 'div', c('p_o−p_e', 'sub', task.agreement, expected), c('1−p_e', 'sub', 1, expected))
        answer = task.kappa if kind == 'kappa' else task.agreement
    elif name == 'jaccard_index':
        inputs = {'left': task.left, 'right': task.right}
        intersection = union = Fraction(0)
        for i, (a, b) in enumerate(zip(task.left, task.right), 1):
            intersection = c(f'intersection_{i}', 'add', intersection, c(f'AND_{i}', 'min', a, b))
            union = c(f'union_{i}', 'add', union, c(f'OR_{i}', 'max', a, b))
        task.intersection, task.union = int(intersection), int(union)
        task.index = c('J', 'div', intersection, union)
        answer = task.index if kind == 'index' else intersection
    elif name in ('precision_at_k', 'reciprocal_rank', 'mean_average_precision'):
        inputs = {'labels': task.labels}
        order = list(range(len(task.labels)))
        if name == 'precision_at_k':
            # Stable insertion sort records comparisons, not an opaque final ranking.
            inputs.update(scores=task.scores, k=task.k)
            order = []
            for i, score in enumerate(task.scores):
                position = len(order)
                while position and c(f'score_{i+1}>score_{order[position-1]+1}', 'lt', task.scores[order[position-1]], score):
                    position -= 1
                order.insert(position, i)
                c(f'rank_{i+1}', 'add', position, 1)
        hits, precision_sum, last, first = Fraction(0), Fraction(0), Fraction(0), None
        for rank, index in enumerate(order, 1):
            if name == 'precision_at_k' and rank > task.k: break
            label = task.labels[index]
            hits = c(f'hits_{rank}', 'add', hits, label)
            precision = c(f'precision_{rank}', 'div', hits, rank)
            if label:
                first = first or rank
                last = precision
                precision_sum = c(f'Σprecision_{rank}', 'add', precision_sum, precision)
            if name == 'reciprocal_rank' and label: break
        if name == 'precision_at_k':
            task.hits, task.precision = int(hits), c('P@k', 'div', hits, task.k)
            answer = hits if kind == 'hits' else task.precision
        elif name == 'reciprocal_rank':
            task.rank, task.reciprocal = first, c('RR', 'div', 1, first)
            answer = Fraction(first) if kind == 'rank' else task.reciprocal
        else:
            task.ap, task.last_precision = c('AP', 'div', precision_sum, hits), last
            answer = task.ap if kind == 'ap' else last
    elif name == 'elimination_query':
        inputs = {'start': task.start, 'steps': task.steps}
        marginal, given = task.start, Fraction(1)
        for i, (yes, no) in enumerate(task.steps, 2):
            def advance(value, label):
                yes_term = c(f'{label}.yes_{i}', 'mul', yes, value)
                no_term = c(f'{label}.no_{i}', 'mul', no, c(f'{label}.complement_{i}', 'sub', 1, value))
                return c(f'{label}.p_{i}', 'add', yes_term, no_term)
            marginal, given = advance(marginal, 'marginal'), advance(given, 'conditional')
        task.marginal = marginal
        task.posterior = c('posterior', 'div', c('joint', 'mul', given, task.start), marginal)
        answer = marginal if kind == 'marginal' else task.posterior
    elif name == 'decision_stump':
        inputs = {'points': task.points}
        best = Fraction(len(task.points))
        candidates = [(None, 0), (None, 1)] + [(threshold, polarity) for threshold in sorted({x for x, _ in task.points}) for polarity in (1, 0)]
        for threshold, polarity in candidates:
            errors = Fraction(0)
            for i, (x, y) in enumerate(task.points, 1):
                pred = Fraction(polarity) if threshold is None else c(f'ŷ(t={threshold},p={polarity},i={i})', 'ge' if polarity else 'lt', x, threshold)
                error = c(f'error(t={threshold},p={polarity},i={i})', 'ne', pred, y)
                errors = c('Σerrors', 'add', errors, error)
            best = c('best_errors', 'min', best, errors)
        answer = int(best)
    elif name == 'kmeans_step':
        inputs = {'centers':[task.c1,task.c2]}
        def assign(point,label):
            distances = []
            for cluster,center in enumerate((task.c1,task.c2),1):
                dx = c(f'{label}.dx_{cluster}','sub',point[0],center[0])
                dy = c(f'{label}.dy_{cluster}','sub',point[1],center[1])
                distances.append(c(f'{label}.distance²_{cluster}','add',
                                   c(f'{label}.dx²_{cluster}','square',dx),
                                   c(f'{label}.dy²_{cluster}','square',dy)))
            return c(f'{label}.cluster1','ge',distances[1],distances[0])
        if kind == 'nearest':
            inputs['query'] = task.query
            first = assign(task.query,'query')
            task.nearest = 1 if first else 2
            answer = task.nearest
        else:
            inputs['points'] = task.points
            count = total = Fraction(0)
            task.in_first = []
            for i,point in enumerate(task.points,1):
                first = assign(point,f'point_{i}')
                task.in_first.append(bool(first))
                count = c(f'count_{i}','add',count,first)
                contribution = c(f'x_contribution_{i}','mul',first,point[0])
                total = c(f'x_total_{i}','add',total,contribution)
            task.count = int(count)
            if kind == 'count':
                answer = task.count
            else:
                if not count:
                    raise ValueError('empty_cluster')
                task.mean_x = c('centroid1.x','div',total,count)
                answer = task.mean_x
    elif name == 'gradient_step':
        inputs = {'points': task.points, 'w': task.w}
        terms = []
        for i, (x, y) in enumerate(task.points, 1):
            pred = c(f'ŷ_{i}', 'mul', task.w, x)
            terms.append(c(f'gradient_term_{i}', 'mul', c(f'error_{i}', 'sub', pred, y), x))
        task.grad = int(tr.accumulate('gradient', terms))
        task.w_new = int(c('w_new', 'sub', task.w, task.grad))
        answer = task.grad if kind == 'gradient' else task.w_new
    else:
        raise ValueError(name)
    task.answer = answer
    tr.finish(task, answer, inputs)
