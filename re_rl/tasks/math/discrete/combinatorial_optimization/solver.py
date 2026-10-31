"""Exact DP/BFS and explicitly defined deterministic heuristics with certificates."""
from collections import deque
from fractions import Fraction
from re_rl.tasks.math.logic.deduction_search import DiscardEvents


def mode_check(mode):
    if mode not in ('exact','approx'):raise ValueError('invalid_solve_mode')


def knapsack(items,capacity,mode,events=None):
    mode_check(mode)
    if events is None:events=DiscardEvents()
    if type(capacity) is not int or not 0 <= capacity <= 5000 or len(items)>100:
        raise ValueError('invalid_capacity_or_items')
    if any(len(item)!=2 or any(type(v) is not int for v in item) or item[0]<=0 or item[1]<0 for item in items):
        raise ValueError('invalid_item')
    chosen=[]
    if mode=='approx':
        order=sorted(range(len(items)),key=lambda i:(-Fraction(items[i][1],items[i][0]),i))
        events.append(dict(operation='opt_density',order=order[:],ratios=[str(Fraction(v,w)) for w,v in items]))
        weight=value=0
        for i in order:
            w,v=items[i];accepted=weight+w<=capacity
            before=weight
            if accepted:weight+=w;value+=v;chosen.append(i)
            events.append(dict(operation='opt_pack',item=i,weight=w,value=v,before=before,
                               capacity=capacity,accepted=accepted,total_weight=weight,total_value=value))
    else:
        dp=[[0]*(capacity+1)]
        for i,(w,v) in enumerate(items):
            row=[]
            for cap in range(capacity+1):
                skip=dp[-1][cap]
                take=dp[-1][cap-w]+v if cap>=w else None
                best=max(skip,take) if take is not None else skip
                row.append(best)
                events.append(dict(operation='opt_knapsack_cell',item=i,capacity=cap,skip=skip,take=take,best=best))
            dp.append(row)
        value=dp[-1][capacity];cap=capacity
        for i in range(len(items)-1,-1,-1):
            take=dp[i+1][cap]>dp[i][cap]
            before=cap
            if take:chosen.append(i);cap-=items[i][0]
            events.append(dict(operation='opt_knapsack_backtrack',item=i,before=before,chosen=take,remaining=cap))
        chosen.reverse()
    events.append(dict(operation='opt_result',value=value,chosen=chosen[:]))
    return value,chosen


def set_cover(universe,sets,mode,events=None):
    mode_check(mode)
    if events is None:events=DiscardEvents()
    universe=set(universe)
    if len(universe)>(12 if mode=='exact' else 100) or len(sets)>100 or any(not set(s)<=universe for s in sets):
        raise ValueError('invalid_cover')
    if set().union(*sets)!=universe:raise ValueError('uncovered_universe')
    chosen=[]
    if mode=='approx':
        uncovered=set(universe)
        while uncovered:
            gains=[sorted(set(s)&uncovered) for s in sets]
            index=min(range(len(sets)),key=lambda i:(-len(gains[i]),i))
            before=sorted(uncovered);uncovered-=set(sets[index]);chosen.append(index)
            events.append(dict(operation='opt_cover_greedy',before=before,gains=gains,
                               chosen=index,remaining=sorted(uncovered)))
    else:
        values=sorted(universe);positions={v:i for i,v in enumerate(values)}
        masks=[sum(1<<positions[v] for v in set(s)) for s in sets]
        full=(1<<len(values))-1
        events.append(dict(operation='opt_cover_masks',universe=values,masks=masks[:],goal=full))
        queue=deque([0]);distance={0:0};parent={}
        while queue and full not in distance:
            state=queue.popleft()
            events.append(dict(operation='opt_cover_pop',state=state,distance=distance[state]))
            for i,mask in enumerate(masks):
                nxt=state|mask;previous=distance.get(nxt);candidate=distance[state]+1
                if previous is None:
                    distance[nxt]=candidate;parent[nxt]=(state,i);queue.append(nxt)
                events.append(dict(operation='opt_cover_edge',state=state,index=i,mask=mask,
                                   target=nxt,candidate=candidate,previous=previous,updated=previous is None))
                if nxt==full:break
        state=full
        while state:
            previous,index=parent[state];chosen.append(index)
            events.append(dict(operation='opt_cover_backtrack',state=state,previous=previous,index=index))
            state=previous
        chosen.reverse()
    events.append(dict(operation='opt_result',value=len(chosen),chosen=chosen[:]))
    return len(chosen),chosen


def tsp(matrix,mode,events=None):
    mode_check(mode)
    if events is None:events=DiscardEvents()
    n=len(matrix)
    if not 1 <= n <= (12 if mode=='exact' else 100) or any(len(row)!=n for row in matrix):
        raise ValueError('invalid_matrix')
    if any(type(v) is not int or v<0 for row in matrix for v in row):raise ValueError('invalid_distance')
    if any(matrix[i][i]!=0 for i in range(n)) or any(matrix[i][j]!=matrix[j][i] for i in range(n) for j in range(n)):
        raise ValueError('non_symmetric_matrix')
    if n==1:
        events.append(dict(operation='opt_result',value=0,chosen=[0,0]))
        return 0,[0,0]
    if mode=='approx':
        route=[0];unvisited=set(range(1,n))
        while unvisited:
            current=route[-1];candidates=[[i,matrix[current][i]] for i in sorted(unvisited)]
            nxt=min(unvisited,key=lambda i:(matrix[current][i],i))
            events.append(dict(operation='opt_tsp_nearest',current=current,candidates=candidates,chosen=nxt))
            route.append(nxt);unvisited.remove(nxt)
        route.append(0)
        # One complete lexicographic pass, including exchanges touching the closing edge.
        for i in range(1,n-1):
            for j in range(i+1,n):
                a,b,c,d=route[i-1],route[i],route[j],route[j+1]
                removed=matrix[a][b]+matrix[c][d];added=matrix[a][c]+matrix[b][d]
                accepted=added<removed
                if accepted:route[i:j+1]=reversed(route[i:j+1])
                events.append(dict(operation='opt_tsp_swap',i=i,j=j,edges=[a,b,c,d],removed=removed,
                                   added=added,delta=added-removed,accepted=accepted,route=route[:]))
        value=sum(matrix[a][b] for a,b in zip(route,route[1:]))
    else:
        dp={};parent={}
        for j in range(1,n):
            mask=1<<(j-1);dp[mask,j]=matrix[0][j]
            events.append(dict(operation='opt_tsp_base',mask=mask,end=j,cost=dp[mask,j]))
        for mask in range(1,1<<(n-1)):
            if mask.bit_count()<2:continue
            for end in range(1,n):
                if not mask&(1<<(end-1)):continue
                previous=mask^(1<<(end-1))
                candidates=[[k,dp[previous,k],matrix[k][end],dp[previous,k]+matrix[k][end]]
                            for k in range(1,n) if previous&(1<<(k-1))]
                best=min(candidates,key=lambda row:(row[3],row[0]))
                dp[mask,end]=best[3];parent[mask,end]=best[0]
                events.append(dict(operation='opt_tsp_cell',mask=mask,end=end,previous=previous,
                                   candidates=candidates,chosen=best[0],cost=best[3]))
        mask=(1<<(n-1))-1
        candidates=[[j,dp[mask,j],matrix[j][0],dp[mask,j]+matrix[j][0]] for j in range(1,n)]
        best=min(candidates,key=lambda row:(row[3],row[0]));value=best[3];end=best[0]
        events.append(dict(operation='opt_tsp_close',candidates=candidates,end=end,cost=value))
        backwards=[]
        while mask:
            backwards.append(end);previous=parent.get((mask,end),0)
            events.append(dict(operation='opt_tsp_backtrack',mask=mask,end=end,previous=previous))
            mask^=1<<(end-1);end=previous
        route=[0]+list(reversed(backwards))+[0]
    events.append(dict(operation='opt_result',value=value,chosen=route[:]))
    return value,route
