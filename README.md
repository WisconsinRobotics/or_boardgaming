# or_boardgaming
Code for Outreach's Board Game Playing Robot

Integrated logic:
- turn on camera
- setup
    - run the corner detect logic and get the board params
    - detect the lines and points of board n create the perspective transform as needed

- when human turn:
    - wait until button pressed
- when bot turn:
    - determine current board state
        - click pic
        - find current piece positions
        - update board state
    - get best move
        - run tic tac toe algorithm to determine next best position
    - get path
        - determine location of best move from board position
        - smooth interp to go from rest location to pieces location to best move location to rest location
    - actual move
        - execute path to reach pieces
        - pick up piece
        - execute said path place piece
        - move arm to rest position away from human
    - indicate end of turn with light n sound