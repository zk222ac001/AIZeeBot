#!/usr/bin/python3
# coding=utf8

import sys
import time
import signal

sys.path.append("/home/pi/TurboPi/")
import ros_robot_controller_sdk as rrc

if sys.version_info.major == 2:
    print("Please run this program with Python 3!")
    sys.exit(0)

print("""
**********************************************************
******** Hiwonder Raspberry Pi Expansion Board ********
**************** Motor Control Example ****************
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

    # Stop all motors
    board.set_motor_duty([[1, 0], [2, 0], [3, 0], [4, 0]])


signal.signal(signal.SIGINT, Stop)

if __name__ == "__main__":
    while True:
        # Set Motor 1 speed to 35
        board.set_motor_duty([[1, 35]])
        time.sleep(0.2)

        # Set Motor 1 speed to 90
        board.set_motor_duty([[1, 90]])
        time.sleep(0.2)

        if not start:
            # Stop all motors
            board.set_motor_duty([[1, 0], [2, 0], [3, 0], [4, 0]])
            print("Program stopped.")
            break
