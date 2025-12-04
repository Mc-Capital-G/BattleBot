from InvertedESC import ESC
from ESC_Manager import ESC_Manager
from Controller import Controller
import pigpio
import time

MAX_THROTTLE_PERCENT = 0.10

joy = Controller("/dev/input/js0")
FL = ESC(5) 
FR = ESC(6)
BR = ESC(27)
BL = ESC(22)

manager = ESC_Manager([FL, FR, BR, BL])
manager.UpdateESCS([0, 0, 0, 0])

#manager.UpdateESCS([0, 1, 0, 0])


while(True):
    if joy.buttons[Controller.FW_BK] < 0: 
        throttle = [1*MAX_THROTTLE_PERCENT] * 4
        manager.UpdateESCS(throttle)
    elif joy.buttons[Controller.FW_BK] > 0: 
        throttle = [-1*MAX_THROTTLE_PERCENT] * 4
        manager.UpdateESCS(throttle)
    else: 
        manager.UpdateESCS([0.0, 0.0, 0.0, 0.0])
    time.sleep(0.1)
    #print(f"FR: {FR.getThrottle():.2f} FL: {FL.getThrottle():.2f} BR: {BR.getThrottle():.2f} BL: {BL.getThrottle():.2f}      ", end="\r")
    #print("\033[F\r\033[F\r")
