"""Memoized minimax with a verifiable event for each state and legal move."""
from re_rl.tasks.execution_trace import snapshot


def minimax(task, connect_four, events):
    memo = {}
    def search(board, player):
        key = (board,player)
        if key in memo:
            events.append(dict(operation='game_cache',board=snapshot(board),player=player,value=memo[key]))
            return memo[key]
        winner = task._winner(board)
        moves = task._valid(board) if connect_four else [i for i,v in enumerate(board) if v == ' ']
        if winner is not None or not moves:
            value = 1 if winner == 'X' else -1 if winner == 'O' else 0
            events.append(dict(operation='game_leaf',board=snapshot(board),player=player,winner=winner,value=value))
        else:
            scores = []
            for move in moves:
                if connect_four: child = task._drop(board,move,player)
                else: child = board[:move]+(player,)+board[move+1:]
                score = search(child,'O' if player == 'X' else 'X')
                scores.append(score)
                events.append(dict(operation='game_move',board=snapshot(board),player=player,move=move+1,child=snapshot(child),value=score))
            value = max(scores) if player == 'X' else min(scores)
            events.append(dict(operation='game_reduce',board=snapshot(board),player=player,scores=scores,value=value))
        memo[key] = value
        return value
    board = task.cols if connect_four else tuple(task.board)
    return search(board,task.player)
