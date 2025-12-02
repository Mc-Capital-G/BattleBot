from InvertedESC import ESC
import pigpio
from Controller import Controller
import time

MAX_THROTTLE_PERCENT = .1

pg = pigpio.pi()
pg.wave_clear()

joy = Controller("/dev/input/js0")
FR = ESC(19, pg)
FL = ESC(26, pg)
BR = ESC(5, pg)
BL = ESC(6, pg)

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
    print(f"FR: {FR.getThrottle():.2f} FL: {FL.getThrottle():.2f} BR: {BR.getThrottle():.2f} BL: {BL.getThrottle():.2f}                 ", end='\r')