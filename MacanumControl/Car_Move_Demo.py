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

class DriftController:
    def __init__(self):
        self.running = True
        self.chassis = mecanum.MecanumChassis()

        # Register Ctrl+C handler
        signal.signal(signal.SIGINT, self.stop)

    def stop(self, signum=None, frame=None):
        # Function triggered when Ctrl+C is pressed.
        # signum = signal number
        # frame = current execution frame
        """Graceful shutdown"""
        if self.running:
            print('\nClosing...')
            self.running = False
            self.chassis.set_velocity(0, 0, 0)

    def drift_pattern(self):
        """Drifting movement pattern"""
        try:
            while self.running:
                # Speed = 50 (0–100)
                # Direction = 90° (typically left)
                # Rotation = 0 (no spin)
                movements = [
                    (50, 90, 0),
                    # Move forward (0° direction). No rotation.
                    (50, 0, 0),
                    # Move right (270° direction). No rotation.
                    (50, 270, 0),
                    # Move backward (180° direction). No rotation.
                    (50, 180, 0)
                ]

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
        """Ensure motors stop"""
        self.chassis.set_velocity(0, 0, 0)
        print('Robot safely stopped')


if __name__ == '__main__':
    print('Car Drifting Demo - Press Ctrl+C to stop')

    controller = DriftController()
    controller.drift_pattern()
    
'''
🧠 Big Picture
Your program does:
Initialize robot
Run a continuous loop
Move in 4 directions:
Left → Forward → Right → Backward
Repeat pattern
Stop when Ctrl+C is pressed
'''
    