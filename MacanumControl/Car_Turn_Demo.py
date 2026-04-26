import sys
import time
import signal

# Add TurboPi path safely
TURBOPI_PATH = '/home/pi/TurboPi/'
if TURBOPI_PATH not in sys.path:
    sys.path.append(TURBOPI_PATH)

import HiWonderSDK.mecanum as mecanum

# Ensure Python 3
if sys.version_info.major < 3:
    print('Please run this program with Python 3!')
    sys.exit(1)

class RotationController:
    def __init__(self):
        self.running = True
        self.chassis = mecanum.MecanumChassis()
        # Register Ctrl+C handler
        signal.signal(signal.SIGINT, self.stop)

    def stop(self, signum=None, frame=None):
        """Gracefully stop the robot"""
        if self.running:
            print('\nClosing...')
            self.running = False
            self.chassis.set_velocity(0, 0, 0)

    def rotation_pattern(self):
        """Clockwise and counterclockwise rotation"""
        try:
            movements = [
                (0, 90, 0.3),   # Clockwise rotation
                (0, 90, -0.3)   # Counterclockwise rotation
            ]

            while self.running:
                for speed, angle, yaw in movements:
                    if not self.running:
                        break

                    self.chassis.set_velocity(speed, angle, yaw)
                    time.sleep(3)

        except Exception as e:
            print(f"Error: {e}")

        finally:
            self.shutdown()

    def shutdown(self):
        """Ensure motors stop"""
        self.chassis.set_velocity(0, 0, 0)
        print('Robot safely stopped')


if __name__ == '__main__':
    print('Rotation Demo - Press Ctrl+C to stop')

    controller = RotationController()
    controller.rotation_pattern()