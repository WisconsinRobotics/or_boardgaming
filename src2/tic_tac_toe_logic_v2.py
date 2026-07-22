import numpy as np

# uses same logic as the old file but with numpy

# will return 'x' or 'o' or '' depending on if win done
def check_win_condition(board):
    if (board == '').sum() >= 5:
        return ''
    for piece in ['x', 'o']:
        if (
                any((board == piece).sum(axis=0) == 3) or 
                any((board == piece).sum(axis=1) == 3) or
                np.diag(board == piece).sum() == 3 or
                np.diag(np.fliplr(board == piece)).sum() == 3
        ):
            return piece
    return ''

def helper_func(board, p1, p2, shift_position = False):
    shift_val = 1 if shift_position else 0
    pos = np.where((board == p1).sum(axis=0) == 2)[0]
    for j in pos:
        i = np.where(board[:, j] == p2)[0]
        if len(i) > 0:
            return (abs(i[0] - shift_val), j)

    pos = np.where((board == p1).sum(axis=1) == 2)[0]
    for i in pos:
        j = np.where(board[i, :] == p2)[0]
        if len(j) > 0:
            return (i, abs(j[0] - shift_val))

    pos = np.diag(board)
    if len(np.where(pos == p1)[0]) == 2:
        i = np.where(pos == p2)[0]
        if len(i) > 0:
            return (abs(i[0] - shift_val), abs(i[0] - shift_val))

    pos = np.diag(np.fliplr(board))
    if len(np.where(pos == p1)[0]) == 2:
        i = np.where(pos == p2)[0]
        if len(i) > 0:
            if shift_position:
                if i[0] == 1:
                    return (0, 2)
                else:
                    return (1, 1)
            else:
                return (i[0], abs(i[0] - 2))
    return None

def tic_tac_toe_logic_v2(board, bot_piece = 'o'):
    human_piece = 'x' if bot_piece == 'o' else 'o'

    # first check if bot can win next turn n if yes return that
    # then check if human can be blocked from winning n again if yes then block human
    for piece in [bot_piece, human_piece]:
        res = helper_func(board = board, p1 = piece, p2 = '', shift_position=False)
        if not (res is None):
            return res

    # if neither bot nor human are not winning next turn return middle square if empty
    if board[1][1] == '':
        return (1, 1)
    
    # if 1 bot piece and 2 blanks return that blank
    res = helper_func(board = board, p1 = '', p2 = bot_piece, shift_position=True)
    if not (res is None):
        return res

    # else choose random blank position
    blank_positions = np.where(board == '')
    rand_index = np.random.randint(0, len(blank_positions[0]))
    return (blank_positions[0][rand_index], blank_positions[1][rand_index])
    
    

