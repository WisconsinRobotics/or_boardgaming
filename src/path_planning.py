import numpy as np

def move_xy(new_location):
    pass
def move_z(pick_piece = True):
    pass

REST_LOCATION = [0, 0] # placeholder
PIECE_STORAGE_LOCATION = [0, 0] # placeholder

def translate_position_to_location(new_position):
    pass
def apply_smooth_interp(p1, p2):
    
    dr = np.array(p2) - np.array(p1) # actual diff from p1 to p2
    drlength = np.sqrt(dr.dot(dr))  # cartesian distance to p2
    #drmax = endpoint_speed / endpoint_command_frequency
    drmax = 2
    if drlength < drmax:
        loc_diff = dr
    else:
        loc_diff = dr * (drmax / drlength)
    
    i = 0
    steps = max(1, drmax // drlength) #loc_diff // dr
    return np.linspace(p1, p2, num=steps)
    

    

# pieces will be kept at opposite sides - bot only responsible to pick up a specific side
def find_and_execute_path(new_location):

    # main points:
        # rest/start location
        # piece storage location
        # new location - new position from best move translated to actual location
    # process:
        # move_xy from rest/start to piece storage location
        # move_z to pick up piece - should start up then go down to pick piece then go up
        # move_xy to new piece location (given by best move)
        # move_z to place piece - should start up then go down to release piece then go up
        # move_xy from curr location (which was the new piece location) to rest/start

    # get smooth interpolation pts from rest/start to piece storage location
    get_points = apply_smooth_interp(REST_LOCATION, PIECE_STORAGE_LOCATION)
    for pt in get_points:
        move_xy(pt)
    # pick up piece
    move_z(pick_piece = True)

    # get smooth interpolation pts piece storage location to new location
    get_points = apply_smooth_interp(PIECE_STORAGE_LOCATION, new_location)
    for pt in get_points:
        move_xy(pt)

    # release piece
    move_z(pick_piece = False)

    # get smooth interpolation pts from new location to rest location
    get_points = apply_smooth_interp(new_location, REST_LOCATION)
    for pt in get_points:
        move_xy(pt)
