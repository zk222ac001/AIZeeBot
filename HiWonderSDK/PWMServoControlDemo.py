#!/usr/bin/python3
# coding=utf8

import sys

sys.path.append("/home/pi/TurboPi/")

import time
import signal
import threading
import ros_robot_controller_sdk as rrc

if sys.version_info.major == 2:
    print("Please run this program with Python 3!")
    sys.exit(0)

print("""
**********************************************************
******** Hiwonder Raspberry Pi Expansion Board ********
************** PWM Servo Control Example **************
**********************************************************
----------------------------------------------------------
Official website: https://www.hiwonder.com
Online mall: https://hiwonder.tmall.com
----------------------------------------------------------
Tips:
 * Press Ctrl+C to stop the program. If it fails, try multiple times.
----------------------------------------------------------
""")

board = rrc.Board()
start = True


# Cleanup before program exit
def Stop(signum, frame):
    global start

    start = False
    print("Shutting down...")


signal.signal(signal.SIGINT, Stop)

if __name__ == "__main__":
    while True:
        # Set Servo 1 pulse width to 1100, move time 1000 ms
        board.pwm_servo_set_position(1, [[1, 1100]])
        time.sleep(1)

        # Set Servo 1 pulse width to 1500, move time 1000 ms
        board.pwm_servo_set_position(1, [[1, 1500]])
        time.sleep(1)

        # Set Servo 1 pulse width to 1900 and Servo 2 pulse width to 1000
        board.pwm_servo_set_position(1, [[1, 1900], [2, 1000]])
        time.sleep(1)

        # Set Servo 1 pulse width to 1500 and Servo 2 pulse width to 2000
        board.pwm_servo_set_position(1, [[1, 1500], [2, 2000]])
        time.sleep(1)

        if not start:
            # Return both servos to center position
            board.pwm_servo_set_position(1, [[1, 1500], [2, 1500]])
            time.sleep(1)

            print("Program stopped.")
            break
