import sys # Gives access to Python system functions (like version info, paths, exit). 
import time # Provides time-related functions (like sleep).
import signal # Allows handling of signals (like SIGINT for graceful shutdown).

# Add TurboPi path safely
TURBOPI_PATH = '/home/pi/TurboPi/'
if TURBOPI_PATH not in sys.path:
    sys.path.append(TURBOPI_PATH)

import HiWonderSDK.mecanum as mecanum

# Ensure Python 3
if sys.version_info.major < 3:
    print('Please run this program with Python 3!')
    sys.exit(1)

class RobotController:
    def __init__(self):
        self.running = True
        self.chassis = mecanum.MecanumChassis()

        # Register signal handler
        signal.signal(signal.SIGINT, self.stop)

    def stop(self, signum=None, frame=None):
        """Gracefully stop the robot"""
        if self.running:
            print("\nStopping robot...")
            self.running = False
            self.chassis.set_velocity(0, 0, 0)

    def move_pattern(self):
        """Define robot movement pattern"""
        try:
            while self.running:
                # Move forward + slight rotation
                # Speed = 50, Direction = 180° (backward), Rotation = 0.3 (slight spin)
                self.chassis.set_velocity(50, 180, 0.3)
                time.sleep(3)
                
                if not self.running:
                    break

                # Move backward + opposite rotation
                # Speed = 50 , Direction = 0° (forward) , Rotation = -0.3 (opposite spin)
                self.chassis.set_velocity(50, 0, -0.3)
                time.sleep(3)

        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            self.shutdown()

    def shutdown(self):
        """Ensure motors are stopped"""
        self.chassis.set_velocity(0, 0, 0)
        print("Robot safely stopped.")


if __name__ == '__main__':
    print('Press Ctrl+C to stop the robot')
    
    controller = RobotController()
    controller.move_pattern()