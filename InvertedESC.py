import pigpio

# This is a class designed to drive an ESC using inverted servo style pwm signals. 
# This is typically not needed, but if the output signal from your pi or microcontroller
# is getting inverted in an optocoupler or something, this will produce the correct inverted wave
# so that the inversion in the circuit creates a proper servo pwm signal.

class ESC:

    FRAME_TIME = 20000 # frame width of servo pulse (in microseconds)
    MAX_WIDTH = 2000 # maximum width of servo pulse (in mircoseconds)
    MIN_WIDTH = 1000 # minimum width of servo pulse (in microseconds)
    WAVE_TABLE_RES = 10 # amount of "steps" we have for waveform generation (in microseconds)
    MIN_THROTTLE = 0.09

    def __init__(self, GPIO_PIN: int):
        self.pin = GPIO_PIN
        self.throttle = 0.0

    
    def get_pwm_time(self):
        microseconds = ESC.MIN_WIDTH + (((self.throttle + 1) * (ESC.MAX_WIDTH - ESC.MIN_WIDTH)) / 2)
        microseconds = round(microseconds / ESC.WAVE_TABLE_RES) * ESC.WAVE_TABLE_RES
        signal_low = microseconds
            
        return signal_low
            
    def SetThrottle(self, value: float):
        if abs(value) > 1:
            if value > 0: self.throttle = 1.0
            if value < 0: self.throttle = -1.0
            return
        self.throttle = value
    
    def getThrottle(self):
        return self.throttle