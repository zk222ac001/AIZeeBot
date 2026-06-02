import time
import ros_robot_controller_sdk as rrc

print('''
**********************************************************
******** Function: Hiwonder Raspberry Pi Expansion Board, Buzzer Control Routine ********
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

# Sound at 1900 Hz for 0.1 seconds, then silence for 0.9 seconds, repeat once
board.set_buzzer(1900, 0.1, 0.9, 1)

time.sleep(2)

# Sound at 1000 Hz for 0.5 seconds, then silence for 0.5 seconds, repeat continuously
board.set_buzzer(1000, 0.5, 0.5, 0)

time.sleep(3)

# Turn off the buzzer
board.set_buzzer(1000, 0.0, 0.0, 1)