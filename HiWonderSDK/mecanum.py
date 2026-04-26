import sys # sys → gives access to Python system-level functions
sys.path.append('/home/pi/TurboPi/') # tells Python where to find external modules

import math # math → provides mathematical functions like sin, cos, atan2, etc.
import time # time → allows for time-related functions like sleep
import HiWonderSDK.ros_robot_controller_sdk as rrc # rrc → custom module for controlling the robot's hardware

class MecanumChassis:
    def __init__(self, board=None, a=67, b=59, wheel_diameter=65, max_duty=100):
        self.board = board if board else rrc.Board() # Initialize the robot board (communication interface)
        self.a = a # a → distance from the center of the robot to the wheel along the x-axis
        self.b = b # b → distance from the center of the robot to the wheel along the y-axis
        self.wheel_diameter = wheel_diameter # wheel_diameter → diameter of the mecanum wheels in millimeters
        self.max_duty = max_duty # max_duty → maximum motor duty cycle

        self.velocity = 0 # velocity → current linear velocity of the robot in mm/s
        self.direction = 0 # direction → current movement direction in degrees (0–360)
        self.angular_rate = 0 # angular_rate → current rotational speed in degrees/s

    # =========================
    # INTERNAL HELPERS
    # =========================
    # Clamp motor speeds to the maximum duty cycle
    def _clamp(self, value):
        return max(-self.max_duty, min(self.max_duty, int(value)))
    
    # Normalize wheel speeds to ensure they do not exceed the maximum duty cycle 
    # while maintaining their ratios
    def _normalize(self, speeds):
        max_val = max(abs(v) for v in speeds)
        if max_val > self.max_duty:
            scale = self.max_duty / max_val
            speeds = [v * scale for v in speeds]
        return speeds

    # =========================
    # MOTOR CONTROL
    # =========================
    # Reset all motors to zero speed and clear internal state
    def reset_motors(self):
        self.board.set_motor_duty([[i, 0] for i in range(1, 5)])
        self.velocity = 0
        self.direction = 0
        self.angular_rate = 0
    
    # Set the robot's velocity, direction, and angular rate.
    def set_velocity(self, velocity, direction, angular_rate, fake=False):
        """
        velocity: mm/s
        direction: degrees (0–360)
        angular_rate: rotation speed
        """
        rad = math.radians(direction)
        vx = velocity * math.cos(rad)
        vy = velocity * math.sin(rad)
        vp = -angular_rate * (self.a + self.b)

        # Wheel speeds
        # v1 = front-left, v2 = front-right, v3 = rear-left, v4 = rear-right
        v1 = vy + vx - vp
        v2 = vy - vx + vp
        v3 = vy - vx - vp
        v4 = vy + vx + vp

        speeds = [v1, v2, v3, v4]

        # Normalize to safe range
        speeds = self._normalize(speeds)

        # Clamp values
        speeds = [self._clamp(v) for v in speeds]

        if fake:
            return speeds

        # Apply motor directions
        self.board.set_motor_duty([
            [1, -speeds[0]],
            [2,  speeds[1]],
            [3, -speeds[2]],
            [4,  speeds[3]]
        ])

        self.velocity = velocity
        self.direction = direction
        self.angular_rate = angular_rate

    # =========================
    # TRANSLATION (XY CONTROL)
    # =========================
    def translation(self, vx, vy, fake=False):
        """
        vx: velocity in x direction
        vy: velocity in y direction
        """
        velocity = math.hypot(vx, vy)  # better than sqrt(x^2 + y^2)

        # Use atan2 → handles all quadrants correctly
        direction = math.degrees(math.atan2(vy, vx)) % 360

        if fake:
            return velocity, direction

        return self.set_velocity(velocity, direction, 0)