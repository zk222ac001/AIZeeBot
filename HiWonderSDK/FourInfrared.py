#!/usr/bin/python3
# coding=utf8

import time
import smbus

# 4-channel line tracking sensor usage example

class FourInfrared:

    def __init__(self, address=0x78, bus=1):
        self.address = address
        self.bus = smbus.SMBus(bus)

    def readData(self, register=0x01):
        value = self.bus.read_byte_data(self.address, register)
        return [True if value & v > 0 else False for v in [0x01, 0x02, 0x04, 0x08]]


if __name__ == "__main__":
    line = FourInfrared()

    while True:
        data = line.readData()

        # True indicates a black line is detected; False indicates no black line is detected
        print(
            "Sensor1:", data[0],
            " Sensor2:", data[1],
            " Sensor3:", data[2],
            " Sensor4:", data[3]
        )

        time.sleep(0.5)