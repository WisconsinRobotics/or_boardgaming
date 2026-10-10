from limit import *
from constants import *

lm = LimitManager()
def ur_mom_x():
    print("x pressed")

def ur_mom_y():
    print("y pressed")


lm.on_pressed(X_LIMIT_SWITCH_NEG_PIN, ur_mom_x)
lm.on_pressed(Y_LIMIT_SWITCH_NEG_PIN, ur_mom_y)

while(True):
    pass
