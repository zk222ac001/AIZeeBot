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

class SlantController:
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

    def slant_pattern(self):
        """Slanted (diagonal) movement pattern"""
        try:
            # Diagonal directions
            movements = [
                (50, 45, 0),    # Forward-right
                (50, 315, 0),   # Forward-left
                (50, 225, 0),   # Backward-left
                (50, 135, 0)    # Backward-right
            ]

            while self.running:
                for speed, angle, yaw in movements:
                    if not self.running:
                        break
                    
                    self.chassis.set_velocity(speed, angle, yaw)
                    time.sleep(1)

        except Exception as e:
            print(f"Error: {e}")

        finally:
            self.shutdown()

    def shutdown(self):
        """Ensure motors are stopped"""
        self.chassis.set_velocity(0, 0, 0)
        print('Robot safely stopped')

# Main execution
if __name__ == '__main__':
    print('Car Slant Demo - Press Ctrl+C to stop')

    controller = SlantController()
    controller.slant_pattern()