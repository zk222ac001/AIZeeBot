#!/usr/bin/env python3
# encoding:utf-8

import time
import gpiod

try:
    print("LED blinking at 0.1-second intervals")

    led1_pin = 16  # Blue LED
    led2_pin = 26

    chip = gpiod.Chip("gpiochip4")

    led1 = chip.get_line(led1_pin)
    led1.request(consumer="led1", type=gpiod.LINE_REQ_DIR_OUT)

    led2 = chip.get_line(led2_pin)
    led2.request(consumer="led2", type=gpiod.LINE_REQ_DIR_OUT)

    while True:
        led1.set_value(0)
        led2.set_value(0)
        time.sleep(0.1)

        led1.set_value(1)
        led2.set_value(1)
        time.sleep(0.1)

except:
    print("The LEDs are occupied by the hw_wifi service.")
    print("Comment out the related code in the service configuration.")
    print("Then restart the service with:")
    print("sudo systemctl restart hw_wifi.service")
