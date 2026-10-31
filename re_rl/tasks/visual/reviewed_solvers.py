"""Read scene coordinates and accumulate visual answers without answer caches."""
from fractions import Fraction
from re_rl.tasks.reviewed_formulas import execute_spec


def trapezoids(xs,ys):
    total = Fraction(0)
    for i in range(1,len(xs)):
        width = xs[i] - xs[i-1]
        height_sum = ys[i] + ys[i-1]
        area = Fraction(width * height_sum,2)
        total += area
    return float(total)


def count_cells(pieces, kind):
    count = 0
    for row,col in pieces:
        dark = (row+col) % 2 == 1
        included = kind == 'total' or kind == 'on_dark' and dark or kind == 'on_light' and not dark
        count += int(included)
    return count


def dice(faces,value=None):
    total = 0
    for face in faces:
        contribution = face if value is None else int(face == value)
        total += contribution
    return total


def line_plot(xs,ys,kind,index=None):
    if kind == 'value_at':
        x,y = xs[index],ys[index]
        return y
    if kind == 'max_x':
        best = 0
        for i in range(1,len(ys)):
            if ys[i] > ys[best]: best = i
        return xs[best]
    count = 0
    for i in range(1,len(ys)):
        increasing = ys[i] > ys[i-1]
        count += int(increasing)
    return count


def stats(values, counts, kind):
    data = []
    best_count,mode = -1,None
    for value,count in zip(values,counts):
        data.extend([value]*count)
        if count > best_count: best_count,mode = count,value
    if kind == 'mode': return mode
    if kind == 'range': return data[-1] - data[0]
    middle = len(data)//2
    return data[middle] if len(data)%2 else (data[middle-1]+data[middle])/2


def count_labels(groups):
    count = 0
    for group in groups:
        for label in group:
            count += 1
    return count


def solve_visual(task,name,trace):
    kind = task.task_type
    inputs = {'subtype':kind}
    specs = {
        'balance_scale':{'lever':[('answer','m_l * d_l / d_r')], '*':[('answer','sum(left) - sum(right)')]},
        'box_plot':{'median':[('answer','med')], 'iqr':[('answer','q3 - q1')], 'range':[('answer','hi - lo')]},
        'geometry_figure':{'right_triangle_area':[('answer','a * b / 2')], 'perimeter':[('answer','sum(sides)')], 'missing_angle':[('answer','180 - alpha - beta')]},
        'number_line':{'value':[('answer','a')], 'distance':[('answer','abs(b - a)')], 'midpoint':[('answer','(a + b) / 2')]},
    }
    if name in specs: return execute_spec(task,name,trace,specs)
    if name == 'area_read':
        inputs['xs'] = task.xs
        if kind == 'under_curve':
            inputs['ys'] = task.ys;task.answer = trace.call(trapezoids,task.xs,task.ys)
        else:
            inputs.update(top=task.top,bottom=task.bottom)
            upper = trace.call(trapezoids,task.xs,task.top)
            lower = trace.call(trapezoids,task.xs,task.bottom)
            task.answer = upper-lower
    elif name == 'chessboard_count':
        inputs['pieces'] = task.pieces;task.answer = trace.call(count_cells,task.pieces,kind)
    elif name == 'dice_read':
        inputs['faces'] = task.faces
        value = task.value if kind == 'count_value' else None
        inputs['value'] = value;task.answer = trace.call(dice,task.faces,value)
    elif name == 'kinematics_graph':
        inputs.update(times=task.ts,velocities=task.vs)
        if kind == 'displacement': task.answer = trace.call(trapezoids,task.ts,task.vs)
        else:
            i = task.seg
            inputs['segment'] = i
            specs = {name:{'*':[('answer','(v2 - v1) / (t2 - t1)')]}}
            from re_rl.tasks.formula_trace import evaluate
            task.answer = evaluate('(v2 - v1) / (t2 - t1)',dict(v2=task.vs[i+1],v1=task.vs[i],t2=task.ts[i+1],t1=task.ts[i]),trace.events)
    elif name == 'line_plot_read':
        inputs.update(xs=task.xs,ys=task.ys)
        index = getattr(task,'k',None)
        inputs['index'] = index;task.answer = trace.call(line_plot,task.xs,task.ys,kind,index)
    elif name == 'projectile_graph':
        points = [(0,0),(task.R/2,task.H),(task.R,0)]
        inputs['points'] = points
        def extrema(points,kind):
            best = 0
            for x,y in points:
                value = x if kind == 'range' else y
                best = max(best,value)
            return best
        task.answer = trace.call(extrema,points,kind)
    elif name == 'slope_read':
        x1,y1 = 0,task.b
        x2,y2 = task.x1,task.m*task.x1+task.b
        inputs['points'] = [(x1,y1),(x2,y2)]
        from re_rl.tasks.formula_trace import evaluate
        expression = '(y2 - y1) / (x2 - x1)' if kind == 'slope' else 'y1'
        task.answer = evaluate(expression,dict(x1=x1,y1=y1,x2=x2,y2=y2),trace.events)
    elif name == 'stats_histogram':
        inputs.update(values=task.values,counts=task.counts)
        task.answer = trace.call(stats,task.values,task.counts,kind)
    elif name == 'venn_diagram':
        inputs.update(only_a=task.only_a,only_b=task.only_b,both=task.both,outside=task.outside)
        groups = {'intersection':[task.both], 'union':[task.only_a,task.only_b,task.both], 'only_a':[task.only_a], 'sym_diff':[task.only_a,task.only_b]}[kind]
        task.answer = trace.call(count_labels,groups)
    else: raise NotImplementedError(name)
    if isinstance(task.answer,Fraction):
        task.answer = int(task.answer) if task.answer.denominator == 1 else float(task.answer)
    return inputs
