"""DPLL events record every literal evaluation, unit deduction and failed branch."""


def validate_cnf(num_vars, clauses):
    if type(num_vars) is not int or not 1 <= num_vars <= 64:
        raise ValueError('invalid_num_vars')
    for clause in clauses:
        for literal in clause:
            if not isinstance(literal,(list,tuple)) or len(literal)!=2:
                raise ValueError('invalid_literal')
            variable,positive=literal
            if type(variable) is not int or not 0 <= variable < num_vars or type(positive) is not bool:
                raise ValueError('invalid_literal')


def dpll(num_vars, clauses, events):
    validate_cnf(num_vars,clauses)
    def search(assignment,depth):
        while True:
            pending=[]
            for index,clause in enumerate(clauses):
                unresolved=[]
                values=[]
                for variable,positive in clause:
                    value=None if variable not in assignment else assignment[variable]==positive
                    values.append([variable+1,positive,value])
                    if value is None and (variable,positive) not in unresolved:
                        unresolved.append((variable,positive))
                satisfied=any(value is True for _,_,value in values)
                events.append(dict(operation='sat_clause',depth=depth,clause=index+1,
                                   assignment={f'x{i+1}':v for i,v in sorted(assignment.items())},
                                   literals=values,satisfied=satisfied))
                if satisfied:continue
                if not unresolved:
                    events.append(dict(operation='sat_conflict',depth=depth,clause=index+1))
                    return None
                pending.append((index+1,unresolved))
            if not pending:
                model=[assignment.get(i,False) for i in range(num_vars)]
                events.append(dict(operation='sat_model',depth=depth,model=model[:]))
                return model
            unit=next(((index,literals[0]) for index,literals in pending if len(literals)==1),None)
            if unit is None:break
            index,(variable,positive)=unit
            events.append(dict(operation='sat_unit',depth=depth,clause=index,variable=variable+1,value=positive))
            assignment[variable]=positive
        variable=min(v for _,literals in pending for v,_ in literals)
        for value in (False,True):
            events.append(dict(operation='sat_branch',depth=depth,variable=variable+1,value=value))
            branch=dict(assignment);branch[variable]=value
            model=search(branch,depth+1)
            if model is not None:return model
            events.append(dict(operation='sat_backtrack',depth=depth,variable=variable+1,value=value))
        return None
    model=search({},0)
    events.append(dict(operation='sat_result',satisfiable=model is not None))
    return model
