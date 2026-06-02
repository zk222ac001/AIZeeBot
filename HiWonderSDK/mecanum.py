#!/usr/bin/python3
# coding=utf8

import math
import sys

sys.path.append("/home/pi/TurboPi/")

import HiwonderSDK.ros_robot_controller_sdk as rrc


class MecanumChassis:
    # A = 67  # mm
    # B = 59  # mm
    # WHEEL_DIAMETER = 65  # mm

    def __init__(self, board=None, a=67, b=59, wheel_diameter=65):
        self.board = board if board is not None else rrc.Board()
        self.a = a
        self.b = b
        self.wheel_diameter = wheel_diameter
        self.velocity = 0
        self.direction = 0
        self.angular_rate = 0

    def reset_motors(self):
        self.board.set_motor_duty([[1, 0], [2, 0], [3, 0], [4, 0]])
        self.velocity = 0
        self.direction = 0
        self.angular_rate = 0

    def set_velocity(self, velocity, direction, angular_rate, fake=False):
        """
        Use polar coordinates to control movement.

        motor1 v1|  up  |v2 motor2
                 |      |
        motor3 v3|      |v4 motor4

        :param velocity: mm/s
        :param direction: moving direction 0-360 degrees
        :param angular_rate: chassis rotation speed
        :param fake: calculate values without sending motor commands
        :return:
        """
        rad_per_deg = math.pi / 180
        vx = velocity * math.cos(direction * rad_per_deg)
        vy = velocity * math.sin(direction * rad_per_deg)
        vp = -angular_rate * (self.a + self.b)
        v1 = int(vy + vx - vp)
        v2 = int(vy - vx + vp)
        v3 = int(vy - vx - vp)
        v4 = int(vy + vx + vp)

        if fake:
            return

        self.board.set_motor_duty([[1, -v1], [2, v2], [3, -v3], [4, v4]])
        self.velocity = velocity
        self.direction = direction
        self.angular_rate = angular_rate

    def translation(self, velocity_x, velocity_y, fake=False):
        velocity = math.sqrt(velocity_x**2 + velocity_y**2)
        if velocity_x == 0:
            direction = 90 if velocity_y >= 0 else 270
        elif velocity_y == 0:
            direction = 0 if velocity_x > 0 else 180
        else:
            direction = math.atan(velocity_y / velocity_x)
            direction = direction * 180 / math.pi
            if velocity_x < 0:
                direction += 180
            elif velocity_y < 0:
                direction += 360

        if fake:
            return velocity, direction

        return self.set_velocity(velocity, direction, 0)
