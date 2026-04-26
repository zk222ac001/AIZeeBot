import enum
import time
import queue  # queue → thread-safe communication between threads
import struct # struct → pack/unpack binary data (important for serial communication)
import serial # serial → communication via UART (PySerial)
import threading
import logging

# =========================
# LOGGING
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Board")

# =========================
# ENUMS
# =========================

class PacketControllerState(enum.IntEnum):
    STARTBYTE1 = 0  # waiting for 0xAA
    STARTBYTE2 = 1  # waiting for 0x55
    FUNCTION = 2    # function type (SYS, MOTOR)
    LENGTH = 3      # data length
    DATA = 4        # actual payload
    CHECKSUM = 5    # checksum byte for data integrity - CRC validation


class PacketFunction(enum.IntEnum):
    SYS = 0    # system data (e.g., battery)
    MOTOR = 3  # motor control data
    NONE = 12  # invalid function type (used for error handling)


# =========================
# CRC8 (USE YOUR FULL TABLE)
# =========================

crc8_table = [
    0, 94, 188, 226, 97, 63, 221, 131, 194, 156, 126, 32, 163, 253, 31, 65,
    157, 195, 33, 127, 252, 162, 64, 30, 95, 1, 227, 189, 62, 96, 130, 220,
    35, 125, 159, 193, 66, 28, 254, 160, 225, 191, 93, 3, 128, 222, 60, 98,
    190, 224, 2, 92, 223, 129, 99, 61, 124, 34, 192, 158, 29, 67, 161, 255,
    70, 24, 250, 164, 39, 121, 155, 197, 132, 218, 56, 102, 229, 187, 89, 7,
    219, 133, 103, 57, 186, 228, 6, 88, 25, 71, 165, 251, 120, 38, 196, 154,
    101, 59, 217, 135, 4, 90, 184, 230, 167, 249, 27, 69, 198, 152, 122, 36,
    248, 166, 68, 26, 153, 199, 37, 123, 58, 100, 134, 216, 91, 5, 231, 185,
    140, 210, 48, 110, 237, 179, 81, 15, 78, 16, 242, 172, 47, 113, 147, 205,
    17, 79, 173, 243, 112, 46, 204, 146, 211, 141, 111, 49, 178, 236, 14, 80,
    175, 241, 19, 77, 206, 144, 114, 44, 109, 51, 209, 143, 12, 82, 176, 238,
    50, 108, 142, 208, 83, 13, 239, 177, 240, 174, 76, 18, 145, 207, 45, 115,
    202, 148, 118, 40, 171, 245, 23, 73, 8, 86, 180, 234, 105, 55, 213, 139,
    87, 9, 235, 181, 54, 104, 138, 212, 149, 203, 41, 119, 244, 170, 72, 22,
    233, 183, 85, 11, 136, 214, 52, 106, 43, 117, 151, 201, 74, 20, 246, 168,
    116, 42, 200, 150, 21, 75, 169, 247, 182, 232, 10, 84, 215, 137, 107, 53
]


def checksum_crc8(data):
    check = 0
    for b in data:
        check = crc8_table[check ^ b]
    return check & 0xFF

# =========================
# BOARD CLASS
# =========================

class Board:    
    # Default serial port (Raspberry Pi UART)
    # High baudrate (1 Mbps)
    def __init__(self, device="/dev/ttyAMA0", baudrate=1000000, timeout=1):
        self.running = True
        self.enable_recv = False

        self.frame = []
        self.recv_count = 0
        self.state = PacketControllerState.STARTBYTE1

        # SERIAL INIT
        try:
            # Initialize serial port with specified parameters
            self.port = serial.Serial(
                port=device,
                baudrate=baudrate,
                timeout=timeout
            )
            # Opens UART connection and configures RTS/DTR for proper operation with the board
            self.port.rts = False
            self.port.dtr = False
            logger.info(f"Connected to {device}")
        except Exception as e:
            logger.error(f"Serial init failed: {e}")
            raise

        # QUEUE FOR RECEIVED DATA
        self.sys_queue = queue.Queue(maxsize=10)

        # THREAD
        self.thread = threading.Thread(target=self.recv_task, daemon=True)
        self.thread.start()

    # =========================
    # CONTROL
    # =========================

    def stop(self):
        self.running = False
        if self.port.is_open:
            self.port.close()
        logger.info("Board stopped")
    
    # Enable or disable reception of data from the board (e.g., battery status)
    def enable_reception(self, enable=True):
        self.enable_recv = enable

    # =========================
    # WRITE
    # =========================
    # Helper function to construct and send packets to the board
    def buf_write(self, func, data):
        # Packet structure: [0xAA, 0x55, function, length, data..., checksum]
        buf = [0xAA, 0x55, int(func), len(data)]
        # Append data bytes to the buffer
        buf.extend(data)
        # Calculate and append checksum for data integrity
        buf.append(checksum_crc8(bytes(buf[2:])))
        # Send the packet over the serial port  if self.port.is_open:
        self.port.write(bytearray(buf))

    # =========================
    # MOTOR CONTROL
    # =========================

    def set_motor_duty(self, dutys):
        data = [0x05, len(dutys)]
        for motor_id, value in dutys:
            data.extend(struct.pack("<Bf", int(motor_id - 1), float(value)))
        self.buf_write(PacketFunction.MOTOR, data)

    # =========================
    # READ
    # =========================
    # Get battery voltage (in millivolts) from the board. 
    # Returns None if no data is available.
    def get_battery(self):
        # Only attempt to read if reception is enabled
        if not self.enable_recv:
            return None
        try:
            # Attempt to get data from the queue with a timeout to avoid blocking indefinitely
            data = self.sys_queue.get(timeout=0.1)
            # Unpack the battery voltage from the received data (assuming it's a 16-bit unsigned integer)
            return struct.unpack('<H', data[1:])[0]
        except queue.Empty:
            return None

    # =========================
    # RECEIVER
    # =========================

    def recv_task(self):
        while self.running:

            if not self.enable_recv:
                time.sleep(0.01)
                continue

            try:
                data = self.port.read(self.port.in_waiting or 1)
            except Exception as e:
                logger.error(f"Serial read error: {e}")
                continue

            for byte in data:

                if self.state == PacketControllerState.STARTBYTE1:
                    if byte == 0xAA:
                        self.state = PacketControllerState.STARTBYTE2

                elif self.state == PacketControllerState.STARTBYTE2:
                    if byte == 0x55:
                        self.state = PacketControllerState.FUNCTION
                    else:
                        self.state = PacketControllerState.STARTBYTE1

                elif self.state == PacketControllerState.FUNCTION:
                    if byte >= PacketFunction.NONE:
                        self.state = PacketControllerState.STARTBYTE1
                        continue
                    self.frame = [byte, 0]
                    self.state = PacketControllerState.LENGTH

                elif self.state == PacketControllerState.LENGTH:
                    if byte > 64:  # safety limit
                        self.state = PacketControllerState.STARTBYTE1
                        continue
                    self.frame[1] = byte
                    self.recv_count = 0
                    self.state = PacketControllerState.DATA

                elif self.state == PacketControllerState.DATA:
                    self.frame.append(byte)
                    self.recv_count += 1

                    if self.recv_count >= self.frame[1]:
                        self.state = PacketControllerState.CHECKSUM

                elif self.state == PacketControllerState.CHECKSUM:
                    if checksum_crc8(bytes(self.frame)) == byte:
                        try:
                            self.sys_queue.put_nowait(bytes(self.frame[2:]))
                        except queue.Full:
                            pass
                    else:
                        logger.warning("Checksum failed")

                    self.state = PacketControllerState.STARTBYTE1

    # =========================
    # DEBUG
    # =========================

    def __del__(self):
        self.stop()


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    board = Board()
    board.enable_reception(True)

    logger.info("START")

    try:
        board.set_motor_duty([[1, -50], [2, 50]])
        time.sleep(1)
        board.set_motor_duty([[1, 0], [2, 0]])

        while True:
            battery = board.get_battery()
            if battery:
                logger.info(f"Battery: {battery}")
            time.sleep(0.1)

    except KeyboardInterrupt:
        logger.info("Stopping...")
        board.stop()


'''
his code is a robot control + communication system:
✅ What it does:
Talks to hardware via UART
Sends motor commands
Receives system data (battery)
Uses CRC for safety
Runs async receiver thread
Implements packet parsing state machine
'''
