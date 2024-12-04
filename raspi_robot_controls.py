from dual_max14870_rpi import motors, MAX_SPEED
import Encoder
import random

robot_turn = False
MOTOR_MAX_SPEED = motors.MAX_SPEED
enc = Encoder.Encoder(5,6) # 5 and 6 are pin numbers

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
def tic_tac_toe_logic():
    board = [["","",""],["","",""],["","",""]] # get board from cv file

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
    if(not block_opp.len == 0): # opponent has a row/col with 2 o's and 1 blank
        return block_opp
    if(board[1][1] == ""):
        return [1,1]
    if(not priority_blank.length == 0): # there's a row/col with 2 blanks and 1 x
        return priority_blank
    
    return all_blanks[ random.randrange(0, all_blanks.len - 1) ]

### move robot when it's its turn to move ###
if robot_turn:
    loc_enc = enc.read()
    [next_x, next_y] = tic_tac_toe_logic()
    motors.enable()

    # distance from desired position
    dist_x = next_x - loc_enc
    dist_y = next_y - loc_enc

    x_speed = dist_x * 5 # idk some random int
    y_speed = dist_y * 5
    motors.setSpeeds(x_speed, y_speed)