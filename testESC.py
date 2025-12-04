from ESC import ESC
from Controller import Controller
import time

MAX_THROTTLE_PERCENT = .1

joy = Controller("/dev/input/js0")
FR = ESC(27)
FL = ESC(22)
BR = ESC(5)
BL = ESC(6)

motors = [FR, FL, BR, BL]
#motors = [FR]

time.sleep(5)
print("motor setup complete")


while True:
    if joy.buttons[Controller.FW_BK] < 0: 
        for i in motors:
            i.SetThrottle(1*MAX_THROTTLE_PERCENT)
    elif joy.buttons[Controller.FW_BK] > 0: 
        for i in motors:
            i.SetThrottle(-1*MAX_THROTTLE_PERCENT)
    else: 
        for i in motors:
            i.SetThrottle(0)
    joy.printButtons()


