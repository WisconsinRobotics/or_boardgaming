import numpy as np
import time, asyncio
from constants import *

def moveMotor_OpenLoop(motor, encoder, distance: float):
    print(encoder.steps)
    if distance > 0:
        motor.forward(MOTOR_SPEED)
    else:
        motor.backward(MOTOR_SPEED)
    time.sleep(abs(distance))
    print(encoder.steps)


def translate_real_world_to_encoder_world(distance_in_cm: float):
    distance_in_one_rev = 0.8 # in cm
    steps_in_one_rev = 2797
    return steps_in_one_rev * distance_in_cm / distance_in_one_rev

async def moveMotor(motor, encoder, distance: float):
    steps = translate_real_world_to_encoder_world(distance)
    curr_encoder_val = encoder.steps
    if steps > 0:
        motor.forward(MOTOR_SPEED)
    else:
        motor.backward(MOTOR_SPEED)
    while True:
        if (((steps >= 0) and (encoder.steps >= (curr_encoder_val + steps))) or 
            ((steps < 0) and (encoder.steps >= (curr_encoder_val - steps)))):
            break
    motor.stop()
    return 0
    



async def move_xy(hardware, curr_location, new_location):
    # Find difference between current and new location
    location_diff = new_location - curr_location
    await moveMotor(hardware['X_MOTOR'], hardware['X_ENCODER'], location_diff[0])
    await moveMotor(hardware['Y_MOTOR'], hardware['Y_ENCODER'], location_diff[1])
    return 0


# Unfortunately i know not numbers or if servo max is open or close so this remains a skeleton 
def move_z(hardware, pick_piece = True):
    if pick_piece:
        # open servo
        pass

    # move z motor down

    if pick_piece:
       # close servo - to pick up piece
       pass
    else:
        # open servo 
        pass

    # move z motor up

    if not pick_piece:
        # close servo - for rest position
        pass

    



def apply_smooth_interp(p1, p2, min_jerk = True):
    displacement = p2 - p1
    distance = np.linalg.norm(displacement)

    nsteps = np.ceil( distance * COMMAND_FREQUENCY / MOTOR_SPEED)
    t_rel = np.arange(nsteps) / nsteps

    #duration_spec = nsteps / COMMAND_FREQUENCY
    #t = t_rel  * duration_spec 

    if min_jerk:
        min_jerk_traj = (10*t_rel**3 - 15*t_rel**4 + 6*t_rel**5)
        disp_traj = np.column_stack( [p_i + disp * min_jerk_traj for p_i, disp in zip(p1, displacement)] )
    else:
        disp_traj = np.linspace(p1, p2, len(t_rel))

    return disp_traj
    

    

# pieces will be kept at opposite sides - bot only responsible to pick up a specific side
def find_and_execute_path(new_location, hardware):

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
    get_points = apply_smooth_interp(REST_LOCATION, PIECE_STORAGE_LOCATION, min_jerk=True)
    for i in range(1, len(get_points)):
        asyncio.run(move_xy(hardware, get_points[i - 1], get_points[i]))
    # pick up piece
    move_z(hardware, pick_piece = True)

    # get smooth interpolation pts piece storage location to new location
    get_points = apply_smooth_interp(PIECE_STORAGE_LOCATION, new_location, min_jerk=True)
    for i in range(1, len(get_points)):
        asyncio.run(move_xy(hardware, get_points[i - 1], get_points[i]))

    # release piece
    move_z(hardware, pick_piece = False)

    # get smooth interpolation pts from new location to rest location
    get_points = apply_smooth_interp(new_location, REST_LOCATION, min_jerk=True)
    for i in range(1, len(get_points)):
        asyncio.run(move_xy(hardware, get_points[i - 1], get_points[i]))
