"""Synchronous cellular updates record every inspected neighborhood and output."""
from re_rl.tasks.execution_trace import snapshot


def life(task,events):
    grid = [row[:] for row in task.grid0]
    for generation in range(1,task.k+1):
        following = [[0]*task.c for _ in range(task.r)]
        for row in range(task.r):
            for col in range(task.c):
                neighbors = [(i,j,grid[i][j])
                             for i in range(max(0,row-1),min(task.r,row+2))
                             for j in range(max(0,col-1),min(task.c,col+2))
                             if (i,j) != (row,col)]
                live_count = sum(value for _,_,value in neighbors)
                previous = grid[row][col]
                survives = bool(previous and live_count in (2,3))
                born = bool(not previous and live_count == 3)
                following[row][col] = int(survives or born)
                events.append(dict(operation='life_cell',generation=generation,row=row,col=col,
                                   neighbors=snapshot(neighbors),count=live_count,previous=previous,
                                   survives=survives,born=born,result=following[row][col]))
        grid = following
        events.append(dict(operation='cellular_generation',generation=generation,result=snapshot(grid)))
    return grid


def elementary(task,events):
    row = task.row0[:]
    for generation in range(1,task.k+1):
        following = []
        for i in range(len(row)):
            left = row[i-1] if i else 0
            middle = row[i]
            right = row[i+1] if i+1 < len(row) else 0
            index = (left << 2) | (middle << 1) | right
            value = (task.rule >> index) & 1
            following.append(value)
            events.append(dict(operation='elementary_cell',generation=generation,index=i,
                               neighborhood=[left,middle,right],rule=task.rule,rule_index=index,result=value))
        row = following
        events.append(dict(operation='cellular_generation',generation=generation,result=row[:]))
    return row
