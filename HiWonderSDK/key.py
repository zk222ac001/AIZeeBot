#!/usr/bin/env python3
# encoding:utf-8

import time
import gpiod

try:
    key1_pin = 13
    chip = gpiod.Chip("gpiochip4")

    key1 = chip.get_line(key1_pin)
    key1.request(
        consumer="key1",
        type=gpiod.LINE_REQ_DIR_IN,
        flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
    )

    key2_pin = 23
    key2 = chip.get_line(key2_pin)
    key2.request(
        consumer="key2",
        type=gpiod.LINE_REQ_DIR_IN,
        flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
    )

    while True:
        # Display key states
        print(
            "\rkey1: {} key2: {}".format(key1.get_value(), key2.get_value()),
            end="",
            flush=True,
        )
        time.sleep(0.001)

    chip.close()

except:
    print("The buttons are occupied by the hw_button_scan service.")
    print("Stop the service before running this program:")
    print("sudo systemctl stop hw_button_scan.service")
