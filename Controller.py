import struct
import time
import threading
from enum import Enum

class Controller:

    FW_BK = 0
    LR = 1
    DRIVE_LINEAR = 2
    DRIVE_STANDARD = 3

    JS_EVENT_BUTTON = 0x01  # button pressed/released
    JS_EVENT_AXIS   = 0x02  # joystick moved
    JS_EVENT_INIT   = 0x80  # initial state

    # js_event struct = uint32 time, int16 value, uint8 type, uint8 number
    EVENT_FORMAT = "IhBB"
    EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

    def __init__(self, inputPath="/dev/input/js0"):
        self.path = inputPath
        self.js = open(self.path, 'rb')

        self.buttons = [0, 0, 0, 0]

        self.running = True
        self.thread = threading.Thread(target=self.readInput, daemon=True)
        self.thread.start()


    def readInput(self):
        while self.running:
            ev = self.js.read(Controller.EVENT_SIZE)
            if not ev:
                continue

            time_ms, value, etype, number = struct.unpack(Controller.EVENT_FORMAT, ev)

            # Ignore initialization events
            if etype & Controller.JS_EVENT_INIT:
                continue
            
            if etype & Controller.JS_EVENT_BUTTON:
                if number == 2: self.buttons[Controller.DRIVE_STANDARD] = value
                elif number == 3: self.buttons[Controller.DRIVE_LINEAR] = value

            elif etype & Controller.JS_EVENT_AXIS:
                if number == 0: self.buttons[Controller.LR] = value
                if number == 1: self.buttons[Controller.FW_BK] = value
        
            time.sleep(0.02)

    def printButtons(self):
        print(f"Forward/Back: {self.buttons[0]}")
        print(f"Left/Right: {self.buttons[1]}")
        print(f"Drive Standard: {self.buttons[2]}")
        print(f"Drive Linear: {self.buttons[3]}")
        print("----")

    def __del__(self):
        self.running = False
        self.thread.join()
        
        
