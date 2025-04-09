import random

# check status of each row
# returns 1 if there's a move that results in immediate win
# otherwise will set block_opp / priority_blank if conditions met
def check_moves(x_cnt, o_cnt, b_cnt, b, b_o, p_b):
    if(x_cnt == 2 and b_cnt == 1):
        return 1
    elif(o_cnt == 2 and b_cnt == 1):
        b_o = b
    elif(x_cnt == 1 and b_cnt == 2):
        p_b = b

# robot use x, player use o (for now)
# algo:
# 1. will prioritize any row/col/diag with 2 x's and 1 blank
# 2. otherwise will block any row/dol/diag with 2 o's and 1 blank
# 3. otherwise will play middle square if empty
# 4. otherwise will play any row/col with 1 x and 2 blank
# 5. otherwise will pick a random empty square
def tic_tac_toe_logic(board):
    #board = [["","",""],["","",""],["","",""]] # get board from cv file

    block_opp = [] # move to block opponent from winning
    all_blanks = []
    priority_blank = [] # records any row/col/diag that already has an x, only tracks 1 at a time

    ### CHECKING ROWS ###
    for i in range(0,2):
        x_count = 0
        o_count = 0
        b_count = 0
        blank = []

        # check all boxes in row
        for j in range(0,2):
            if(board[i][j] == "x"):
                x_count += 1
            elif(board[i][j] == "o"):
                o_count += 1
            else:
                b_count += 1
                blank = [i,j]
                all_blanks.append([i,j]) # tracking all blank spaces
        
        if(check_moves(x_count, o_count, b_count, blank, block_opp, priority_blank) == 1):
            return blank
    
    ### CHECKING COLUMNS ###
    for i in range(0,2):
        x_count = 0
        o_count = 0
        b_count = 0
        blank = []

        for j in range(0,2):
            if(board[j][i] == "x"):
                x_count += 1
            elif(board[j][i] == "o"):
                o_count += 1
            else:
                b_count += 1
                blank = [j,i]
        
        if(check_moves(x_count, o_count, b_count, blank, block_opp, priority_blank) == 1):
            return blank
    
    ### CHECKING DIAGONALS ###
    x_count = 0
    o_count = 0
    b_count = 0
    blank = []

    ### checking for left to right diag ###
    for r in range(0,2):
        if(board[r][r] == "x"):
            x_count += 1
        elif(board[r][r] == "o"):
            o_count += 1
        else:
            b_count += 1
            blank = [r,r]
    if(check_moves(x_count, o_count, b_count, blank, block_opp, priority_blank) == 1):
        return blank
    
    ### checking right to left diag ###
    x_count = 0
    o_count = 0
    b_count = 0
    i = 0
    j = 2

    while(i <= 2 and j >= 0):
        if(board[i][j] == "x"):
            x_count += 1
        elif(board[i][j] == "o"):
            o_count += 1
        else:
            b_count += 1
            blank = [i,j]
        i += 1
        j -= 1

    if(check_moves(x_count, o_count, b_count, blank, block_opp, priority_blank) == 1):
        return blank
    
    ### CHECK FOR REMAINING MOVES ###
    if(not len(block_opp) == 0): # opponent has a row/col with 2 o's and 1 blank
        return block_opp
    if(board[1][1] == ""):
        return [1,1]
    if(not len(priority_blank) == 0): # there's a row/col with 2 blanks and 1 x
        return priority_blank
    
    return all_blanks[ random.randrange(0, len(all_blanks) - 1) ]
