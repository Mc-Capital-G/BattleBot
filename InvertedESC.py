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

    def __init__(self, GPIO_PIN: int, pigpio_daemon: pigpio.pi):
        self.pin = GPIO_PIN
        self.throttle = 0.0

        self.gpio = pigpio_daemon
        self.gpio.set_mode(self.pin, pigpio.OUTPUT)

        self.wave_table = {}
        self.build_wave_table()
        self.gpio.wave_send_repeat(self.wave_table[1500])
    
    def build_wave_table(self):
        for microseconds in range(ESC.MIN_WIDTH, ESC.MAX_WIDTH + 1, ESC.WAVE_TABLE_RES):
            signal_low = microseconds
            signal_high = ESC.FRAME_TIME - microseconds

            wave = [pigpio.pulse(0, 1 << self.pin, signal_low), pigpio.pulse(1 << self.pin, 0, signal_high)]

            self.gpio.wave_clear()
            self.gpio.wave_add_generic(wave)
            self.wave_table[microseconds] = self.gpio.wave_create()
    
    def SetThrottle(self, value: float):
        if abs(value) > 1:
            if value > 0: self.throttle = 1.0
            if value < 0: self.throttle = -1.0
            return
        self.throttle = value

        wave_id = ESC.MIN_WIDTH + (((self.throttle + 1) * (ESC.MAX_WIDTH - ESC.MIN_WIDTH)) / 2)
        wave_id = round(wave_id / ESC.WAVE_TABLE_RES) * ESC.WAVE_TABLE_RES
        self.gpio.wave_send_repeat(self.wave_table[wave_id])
        
    
    def getThrottle(self):
        return self.throttle