#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/TurboPi/')
import time
import signal
import HiWonderSDK.mecanum as mecanum

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)
    
print('Car Forward Demo, press Ctrl+C to close the running program, please try multiple times if failed')

chassis = mecanum.MecanumChassis()

start = True
# process program before closing
def Stop(signum, frame):
    global start
    start = False
    print('Closed...')    
    chassis.set_velocity(0,0,0)  # close all motors
    

signal.signal(signal.SIGINT, Stop)

if __name__ == '__main__':
    while start:
        chassis.set_velocity(50,90,0) # robot motion control function, linbear velocity 50(0~100), heading angle 90(0~360), yaw rate 0(-2~2))
        time.sleep(1)
        
    chassis.set_velocity(0,0,0)  # close all motors
    print('Closed')