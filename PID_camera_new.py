import cv2
import time
import math
import numpy as np
import picamera2 as pc2
from InvertedESC import ESC
from ESC_Manager import ESC_Manager
import pigpio

pg = pigpio.pi()

camera = pc2.Picamera2()
camera_config = camera.create_preview_configuration()
camera.configure(camera_config)
#camera.start_preview(pc2.Preview.DRM)
camera.start()
time.sleep(0.1)

Kpt, Kit, Kdt = 0.0075, 0.0005, 0.0005
#Kpt, Kit, Kdt = 0.1, 0.05, 0.05

Kp_v, Ki_v, Kd_v = 0.1, 0.002, 0.002

dt = 0.08                
BASE_SPEED = 0.1  
MAX_SPEED = 0.4        
TARGET_DIST_PIXELS = 10.0      

I_theta = 0.0
prev_error_theta = 0.0

I_dist_v = 0.0
prev_error_dist_v = 0.0

FR = ESC(5)  
FL = ESC(6)  
BR = ESC(27) 
BL = ESC(22)
manager = ESC_Manager([FR, FL, BR, BL])
manager.UpdateESCS([0,0,0,0])
print("Motors Initialized! Starting autonomous navigation...")
time.sleep(2)

def setspeeds(fl, fr, bl, br):
    manager.UpdateESCS([fr, fl, br, bl], MAX_SPEED)

print("Setup complete! Starting Loop...")

while True:
    start_time = time.perf_counter()
    print_num= 0
    image = camera.capture_array()
    key = cv2.waitKey(1) & 0xFF 
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, thresh = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY_INV)
    mask = cv2.erode(thresh, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    v = 0.15
    w = 0.0

    if len(contours) > 0.5:
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)

        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

            center_x = image.shape[1] // 2
            center_y = image.shape[0] // 2
            
            #error_theta = math.degrees(math.atan2(cy - center_y, cx - center_x)) 
            #error_theta = math.atan2(cy - center_y, cx - center_x)
            error_theta = (cx - center_x) / 10
            print(f"Error theta: {error_theta:.2f}  Yerr:{cy-center_y:.2f} Xerr: {cx-center_x:.2f}              ")
            print_num = print_num+1

            P_theta = error_theta
            I_theta += error_theta * dt
            D_theta = (error_theta - prev_error_theta) / dt
     
            w = Kpt*P_theta + Kit*I_theta + Kdt*D_theta 
            prev_error_theta = error_theta
          
            dist = math.sqrt((cx - center_x)**2 + (cy - center_y)**2)
            error_dist = dist - TARGET_DIST_PIXELS
            
         
            P_dist_v = error_dist
            I_dist_v += error_dist * dt
            D_dist_v = (error_dist - prev_error_dist_v) / dt
            
            #v = Kp_v*P_dist_v + Ki_v*I_dist_v + Kd_v*D_dist_v + BASE_SPEED
            prev_error_dist_v = error_dist
            v = 0.15
            
            
            '''
            max_abs_speed = max(abs(fl), abs(fr), abs(bl), abs(br), 1.0)
        
            fl /= max_abs_speed
            fr /= max_abs_speed
            bl /= max_abs_speed
            br /= max_abs_speed
            '''
        print("i see a line!!!                        ") 
        print_num = print_num+1

    else:
        print("i dont see a line                      ")
        print_num = print_num+1
        #setspeeds(0, 0, 0, 0)
        I_theta = 0.0
        I_dist_v = 0.0
        v = 0.15
        w = 0.0

    
    #cv2.imshow("img", image)
    '''
    if key == ord('q'):
        setspeeds(0, 0, 0, 0)
        print(f"FR: {FR.getThrottle():.2f} FL: {FL.getThrottle():.2f} BR: {BR.getThrottle():.2f} BL: {BL.getThrottle():.2f}           ") 
        print_num = print_num+1
        break
    else:
    '''
    fl = v - w
    fr = v + w
    bl = v  - w
    br = v + w

    print(f"FR: {fr:.2f} FL: {fl:.2f} BR: {br:.2f} BL: {bl:.2f}                       ")
    print_num = print_num + 1
    setspeeds(fl, fr, bl, br)
    print(f"FR: {FR.getThrottle():.2f} FL: {FL.getThrottle():.2f} BR: {BR.getThrottle():.2f} BL: {BL.getThrottle():.2f}           ")
    print_num = print_num+1

    print(f"Omega: {w}                             ")
    print_num = print_num+1
    end_time = time.perf_counter()
    print(f"Execution time: {end_time-start_time}          ")
    print_num = print_num+1
    for i in range(print_num):
        print("\033[F", end="\r")
    time.sleep(dt)

cv2.destroyAllWindows()