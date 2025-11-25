import gpiozero 
#from gpiozero.pins.lgpio import LGPIOFactory
from gpiozero import Device
from gpiozero import Servo
import threading
import time

class ESC():
    def __init__(self, GPIO_PIN):
        self.pin = GPIO_PIN
        self.throttle = 0.0
        self.running = True
        self.esc = Servo(self.pin, min_pulse_width=1/1000, max_pulse_width=2/1000, frame_width=20/1000)

        self.thread = threading.Thread(target=self.pwm, daemon=True)
        self.thread.start()
    
    def pwm(self):
        while self.running:
            self.esc.value = self.throttle
            time.sleep(0.02)
    
    def SetThrottle(self, value):
        if abs(value) > 1:
            if value > 0: self.throttle = 1
            if value < 0: self.throttle = -1
            return
        self.throttle = value
    
    def getThrottle(self):
        return self.throttle
    
    def __del__(self):
        self.running = False
        self.thread.join()

