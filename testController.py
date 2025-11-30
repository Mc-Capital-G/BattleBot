import time
from Controller import Controller

js = Controller("/dev/input/js0")

while True:
    js.printButtons()
    time.sleep(0.01)