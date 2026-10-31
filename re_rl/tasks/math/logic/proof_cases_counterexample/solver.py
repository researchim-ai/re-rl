"""Finite complete proofs of integer-polynomial congruences and identities."""
from math import lcm


def validate_claim(claim):
    if claim['kind']=='identity':
        if any(type(claim[k]) is not int for k in ('shift','linear','constant')):
            raise ValueError('invalid_identity')
    elif claim['kind']=='divisible':
        coefficients=claim['coefficients']
        if not 1 <= len(coefficients) <= 9 or any(type(c) is not int or abs(c)>1000 for c in coefficients):
            raise ValueError('invalid_coefficients')
        m,p=claim['modulus'],claim['premise_modulus']
        if any(type(v) is not int or not 1 <= v <= 256 for v in (m,p)) or m<2 or lcm(m,p)>4096:
            raise ValueError('invalid_modulus')
        residues=claim['premise_residues']
        if not residues or any(type(r) is not int or not 0 <= r < p for r in residues) or len(set(residues))!=len(residues):
            raise ValueError('invalid_premise')
    else:raise ValueError('invalid_claim')


def evaluate(coefficients,n,events=None):
    value=0
    for power in range(len(coefficients)-1,-1,-1):
        previous=value
        value=value*n+coefficients[power]
        if events is not None:
            events.append(dict(operation='proof_horner',n=n,power=power,previous=previous,
                               coefficient=coefficients[power],result=value))
    return value


def is_counterexample(claim,n):
    if claim['kind']=='identity':
        return (n+claim['shift'])**2-n*n != claim['linear']*n+claim['constant']
    return (n%claim['premise_modulus'] in claim['premise_residues']
            and evaluate(claim['coefficients'],n)%claim['modulus'] != 0)


def analyse(claim,events):
    validate_claim(claim)
    if claim['kind']=='identity':
        shift=claim['shift']
        # Expand (n+s)(n+s)-n*n, then subtract the stated RHS coefficient by coefficient.
        product=[0,0,0]
        for i,a in enumerate((shift,1)):
            for j,b in enumerate((shift,1)):
                product[i+j]+=a*b
                events.append(dict(operation='proof_product',left_power=i,right_power=j,
                                   left=a,right=b,power=i+j,coefficient=product[i+j]))
        product[2]-=1
        rhs=[claim['constant'],claim['linear'],0]
        difference=[a-b for a,b in zip(product,rhs)]
        events.append(dict(operation='proof_identity',left=product,right=rhs,difference=difference))
        if all(c==0 for c in difference):
            events.append(dict(operation='proof_identical',coefficients=difference))
            return True,None
        # A nonzero degree-d polynomial cannot vanish at all d+1 distinct integers.
        degree=max(i for i,c in enumerate(difference) if c)
        for n in range(degree+1):
            value=evaluate(difference,n,events)
            events.append(dict(operation='proof_witness',n=n,difference=value))
            if value:return False,n
        raise RuntimeError('nonzero_polynomial_without_witness')
    period=lcm(claim['modulus'],claim['premise_modulus'])
    events.append(dict(operation='proof_period',modulus=claim['modulus'],premise_modulus=claim['premise_modulus'],period=period))
    for residue in range(period):
        applicable=residue%claim['premise_modulus'] in claim['premise_residues']
        events.append(dict(operation='proof_case',residue=residue,applicable=applicable))
        if not applicable:continue
        value=evaluate(claim['coefficients'],residue,events)
        remainder=value%claim['modulus']
        events.append(dict(operation='proof_remainder',n=residue,value=value,modulus=claim['modulus'],remainder=remainder))
        if remainder:
            events.append(dict(operation='proof_counterexample',n=residue))
            return False,residue
    events.append(dict(operation='proof_exhausted',period=period))
    return True,None
