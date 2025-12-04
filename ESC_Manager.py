import pigpio
from InvertedESC import ESC
import math

class ESC_Manager:

    def __init__(self, escs = list[ESC]):
        self.pg = pigpio.pi()
        self.escs = escs
        self.wid = -1
        self.gpiomask = 0
        
        for i in escs:
            self.pg.set_mode(i.pin, pigpio.OUTPUT)
            self.pg.write(i.pin, 1)
            self.gpiomask |= (1 << i.pin)
        #print("gpiomask:", format(self.gpiomask, "032b"))
        
        

    def build_wave(self):
        self.pg.wave_clear()

        on_times = []
        pins = []
        for i in self.escs:
            on_times.append(i.get_pwm_time())
            pins.append(i.pin)
        pair = list(zip(on_times, pins))
        pair = sorted(pair)
        on_times = [o for o, p in pair]
        pins = [p for o, p in pair]
        
        #print(f"Pins: {pins}, On Times: {on_times}      ")
        wave = []
        # first section of all waveforms: all gpio pins we are controlling turn on
        wave.append(pigpio.pulse(0, self.gpiomask, on_times[0]))

        #iteratively calculate how long to wait to turn off each pin
        for i in range(len(on_times)):
            if i == len(on_times)-1:
                wave.append(pigpio.pulse((1 << pins[i]), 0, ESC.FRAME_TIME - on_times[-1]))
            else:
                wave.append(pigpio.pulse((1 << pins[i]), 0, on_times[i+1] - on_times[i]))
            

        #old logic
        '''
        for i in range(0, len(on_times)):
            # Checks if gpio pin is already in the bitmask. 
            # If it is, we can assume it has been set properly and can continue the loop
            if (self.gpiomask & (1 << pins[i])) != 0: continue
            else: self.gpiomask |= (1 << pins[i])
            for j in range(i+1, len(on_times)):
                if on_times[j] == on_times[i]: 
                    self.gpiomask |= (1 << pins[j])
                else:
                    wave.append(pigpio.pulse(self.gpiomask, 0, on_times[j] - on_times[i]))
                    break
        wave.append(pigpio.pulse(self.gpiomask, 0, ESC.FRAME_TIME - 2*on_times[-1]))
        '''
        #print(f"GPIOMask: {bin(gpiomask)}    ")
        self.pg.wave_add_generic(wave)
        self.wid = self.pg.wave_create_and_pad(50)
        #print("\033[F\r\033[F\r")

                
    def UpdateESCS(self, throttles: list[float], max_speed_scalar = 1):
        for i in range(0, len(throttles)):
            #if throttles[i] > 1.0: throttles[i] = 1.0
            #elif throttles[i] < -1.0: throttles[i] = -1.0
            newthrottle = 0
            if throttles[i] > 0:
                newthrottle = ESC.MIN_THROTTLE + (((throttles[i] - ESC.MIN_THROTTLE) * (max_speed_scalar - ESC.MIN_THROTTLE)) / 2*math.pi )
            else:
                newthrottle = ESC.MIN_THROTTLE + (((throttles[i] - ESC.MIN_THROTTLE) * (max_speed_scalar - ESC.MIN_THROTTLE)) / (2*math.pi))
            self.escs[i].SetThrottle(newthrottle)
            #self.escs[i].SetThrottle(throttles[i]*max_speed_scalar)
        self.build_wave()
        self.pg.wave_send_repeat(self.wid)
        


        