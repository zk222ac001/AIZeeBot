#!/usr/bin/python3
# coding=utf8

import sys
import time

sys.path.append('/home/pi/TurboPi/')
import HiwonderSDK.ros_robot_controller_sdk as rrc

if sys.version_info.major == 2:
    print('Please run this program with Python 3!')
    sys.exit(0)

print('''
**********************************************************
**************** PWM Servo and Motor Test ****************
**********************************************************
----------------------------------------------------------
Official website: https://www.hiwonder.com
Online mall: https://hiwonder.tmall.com
----------------------------------------------------------
Tips:
 * Press Ctrl+C to stop the program. If it fails, try multiple times.
----------------------------------------------------------
''')

board = rrc.Board()

# Test PWM Servo 1
board.pwm_servo_set_position(0.3, [[1, 1800]])
time.sleep(0.3)

board.pwm_servo_set_position(0.3, [[1, 1500]])
time.sleep(0.3)

board.pwm_servo_set_position(0.3, [[1, 1200]])
time.sleep(0.3)

board.pwm_servo_set_position(0.3, [[1, 1500]])
time.sleep(1.5)

# Test PWM Servo 2
board.pwm_servo_set_position(0.3, [[2, 1200]])
time.sleep(0.3)

board.pwm_servo_set_position(0.3, [[2, 1500]])
time.sleep(0.3)

board.pwm_servo_set_position(0.3, [[2, 1800]])
time.sleep(0.3)

board.pwm_servo_set_position(0.3, [[2, 1500]])
time.sleep(1.5)

# Test Motor 1
board.set_motor_duty([[1, -45]])
time.sleep(0.5)
board.set_motor_duty([[1, 0]])
time.sleep(1)

# Test Motor 2
board.set_motor_duty([[2, 45]])
time.sleep(0.5)
board.set_motor_duty([[2, 0]])
time.sleep(1)

# Test Motor 3
board.set_motor_duty([[3, -45]])
time.sleep(0.5)
board.set_motor_duty([[3, 0]])
time.sleep(1)

# Test Motor 4
board.set_motor_duty([[4, 45]])
time.sleep(0.5)
board.set_motor_duty([[4, 0]])
time.sleep(1)