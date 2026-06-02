import time
import signal
import ros_robot_controller_sdk as rrc

print('''
**********************************************************
******** Hiwonder Raspberry Pi Expansion Board ********
*************** RGB Light Control Example ***************
**********************************************************
----------------------------------------------------------
Official website: https://www.hiwonder.com
Online mall: https://hiwonder.tmall.com
----------------------------------------------------------
Tips:
 * Press Ctrl+C to stop the program. If it fails, try multiple times.
----------------------------------------------------------
''')

start = True

# Cleanup before program exit
def Stop(signum, frame):
    global start

    start = False
    print('Shutting down...')

board = rrc.Board()

# Turn off all RGB LEDs initially
board.set_rgb([[1, 0, 0, 0], [2, 0, 0, 0]])

signal.signal(signal.SIGINT, Stop)

while True:
    # Set both LEDs to red
    board.set_rgb([[1, 255, 0, 0], [2, 255, 0, 0]])
    time.sleep(1)

    # Set both LEDs to green
    board.set_rgb([[1, 0, 255, 0], [2, 0, 255, 0]])
    time.sleep(1)

    # Set both LEDs to blue
    board.set_rgb([[1, 0, 0, 255], [2, 0, 0, 255]])
    time.sleep(1)

    # Set both LEDs to yellow
    board.set_rgb([[1, 255, 255, 0], [2, 255, 255, 0]])
    time.sleep(1)

    if not start:
        # Turn off all LEDs
        board.set_rgb([[1, 0, 0, 0], [2, 0, 0, 0]])
        print('Program stopped.')
        break