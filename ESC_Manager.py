import pigpio
from InvertedESC import ESC

class ESC_Manager:

    def __init__(self, escs = list[ESC]):
        self.pg = pigpio.pi()
        self.escs = escs
        self.wid = -1
        '''
        for i in escs:
            self.pg.set_mode(i.pin, pigpio.OUTPUT)
            self.pg.write(i.pin, 0)
        '''

    def build_wave(self):
        #self.pg.wave_clear()

        on_times = []
        pins = []
        for i in self.escs:
            on_times.append(i.get_pwm_time())
            pins.append(i.pin)
        pair = list(zip(on_times, pins))
        pair = sorted(pair)
        on_times = [o for o, p in pair]
        pins = [p for o, p in pair]
        
        print(f"Pins: {pins}, On Times: {on_times}      ")
        wave = []
        # first section of all waveforms: all gpio pins we are controlling turn on
        gpiomask = 0
        for i in pins:
            gpiomask |= (1 << i)
        wave.append(pigpio.pulse(0, gpiomask, on_times[0]))

        #iteratively calculate how long to wait to turn off each pin
        gpiomask = (1 << pins[0])
        print(gpiomask)
        for i in range(0, len(on_times)):
            # Checks if gpio pin is already in the bitmask. 
            # If it is, we can assume it has been set properly and can continue the loop
            if (gpiomask & (1 << pins[i])) == gpiomask: continue
            else: gpiomask |= (1 << pins[i])
            for j in range(i+1, len(on_times)):
                if on_times[j] == on_times[i]: 
                    gpiomask |= (1 << on_times[j])
                else:
                    wave.append(pigpio.pulse(gpiomask, 0, on_times[j] - on_times[i]))
                    break
        print(gpiomask)
        wave.append(pigpio.pulse(0, 0, ESC.FRAME_TIME - 2*on_times[-1]))
        print(wave)
        self.pg.wave_add_generic(wave)
        self.wid = self.pg.wave_create()
        info = self.pg.wave_get_cbs()
        print(info)
        print(self.pg.wave_get_pulses())     # shows timing and bitmasks of each pulse
        print(self.pg.wave_get_max_pulses())

                
    def UpdateESCS(self, throttles: list[float]):
        for i in range(0, len(throttles)):
            self.escs[i].SetThrottle(throttles[i])
        self.build_wave()
        self.pg.wave_send_repeat(self.wid)


        