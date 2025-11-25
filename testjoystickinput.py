import struct
import time

JS_EVENT_BUTTON = 0x01  # button pressed/released
JS_EVENT_AXIS   = 0x02  # joystick moved
JS_EVENT_INIT   = 0x80  # initial state

# js_event struct = uint32 time, int16 value, uint8 type, uint8 number
EVENT_FORMAT = "IhBB"
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

jsdev = open('/dev/input/js0', 'rb')

print("Reading from /dev/input/js0...")

while True:
    ev = jsdev.read(EVENT_SIZE)
    if not ev:
        continue

    time_ms, value, etype, number = struct.unpack(EVENT_FORMAT, ev)

    # Ignore initialization events
    if etype & JS_EVENT_INIT:
        continue

    if etype & JS_EVENT_BUTTON:
        print(f"Button {number}: {'pressed' if value else 'released'}")

    elif etype & JS_EVENT_AXIS:
        print(f"Axis {number} value: {value}")

    time.sleep(0.01)
