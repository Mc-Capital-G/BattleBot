import cv2
import time
import math
import numpy as np
import picamera2 as pc2
from InvertedESC import ESC
import pigpio

pg = pigpio.pi()

camera = pc2.Picamera2()
camera_config = camera.create_preview_configuration()
camera.configure(camera_config)
#camera.start_preview(pc2.Preview.DRM)
camera.start()
time.sleep(0.1)

Kpt, Kit, Kdt = 0.075, 0.0005, 0.0005

Kp_v, Ki_v, Kd_v = 0.1, 0.002, 0.002

dt = 0.05                      
BASE_SPEED = 0.3           
TARGET_DIST_PIXELS = 10.0      

I_theta = 0.0
prev_error_theta = 0.0

I_dist_v = 0.0
prev_error_dist_v = 0.0

FR = ESC(19, pg)  
FL = ESC(26, pg)  
BR = ESC(5, pg) 
BL = ESC(6, pg)  

def setspeeds(fl, fr, bl, br):

    FL.SetThrottle(fl)
    FR.SetThrottle(fr)
    BL.SetThrottle(bl)
    BR.SetThrottle(br)

print("Setup complete! Starting Loop...")

while True:

    image = camera.capture_array()
    key = cv2.waitKey(1) & 0xFF 
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, thresh = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY_INV)
    mask = cv2.erode(thresh, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    v, w = 0.0,  0.0 

    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)

        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

            center_x = image.shape[1] // 2
            center_y = image.shape[0] // 2
            
            error_theta = math.degrees(math.atan2(cy - center_y, cx - center_x)) 
            
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
            
            v = Kp_v*P_dist_v + Ki_v*I_dist_v + Kd_v*D_dist_v + BASE_SPEED
            prev_error_dist_v = error_dist
            
            fl = v - w
            fr = v + w
            bl = v  - w
            br = v + w
            
            max_abs_speed = max(abs(fl), abs(fr), abs(bl), abs(br), 1.0)
        
            fl /= max_abs_speed
            fr /= max_abs_speed
            bl /= max_abs_speed
            br /= max_abs_speed
            
            setspeeds(fl, fr, bl, br)

    else:
  
        setspeeds(0, 0, 0, 0)
        I_theta = 0.0
        I_dist_v = 0.0

    #cv2.imshow("img", image)

    if key == ord('q'):
        setspeeds(0, 0, 0, 0) 
        break
    
    print(f"FR: {FR.getThrottle():.2f} FL: {FL.getThrottle():.2f} BR: {BR.getThrottle():.2f} BL: {BL.getThrottle():.2f}           ", end='\r')

cv2.destroyAllWindows()