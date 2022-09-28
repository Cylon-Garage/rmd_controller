import serial
import serial.rs485
import struct
from typing import Union


def check_sum(data: bytearray) -> int:
    return sum(data) % 255


class RMD:
    def __init__(self, port: str, id: int = 1, baudrate: int = 115200) -> None:
        self.id = id
        self.serial = serial.Serial(port, baudrate=baudrate, timeout=0.5)

    def check_response_header(self, header, command):
        if header[0] != 0x3E:
            self.serial.reset_input_buffer()
            print('response head byte mismatch')

        if (check_sum(header[:4]) != header[4]):
            print('response header checksum mismatch')

        if header[2] == self.id or header[1] == command:
            return header[3]

        return None

    def send_command(self, command: int, data: bytearray = None) -> bytes:
        data_len = len(data) if data is not None else 0
        total_len = 5 + data_len + 1 if data is not None else 5

        message = bytearray(total_len)
        message[0] = 0x3E
        message[1] = command
        message[2] = self.id
        message[3] = data_len
        message[4] = check_sum(message[:4])
        if data is not None:
            message[5:-1] = data
            message[-1] = check_sum(message[5:-1])
        self.serial.reset_input_buffer()
        self.serial.write(message)

        resp_header = self.serial.read(5)
        resp_len = self.check_response_header(resp_header, command)

        if resp_len is not None:
            resp = self.serial.read(resp_len + 1)
            if (check_sum(resp[:-1]) != resp[-1]):
                print('response data checksum mismatch %u vs %u' %
                      (check_sum(resp[:-1]), resp[-1]))
            return resp[:-1]
        return None

    def read_status(self):
        resp = self.send_command(0x9A)
        temp, _, voltage, _, _, error = struct.unpack('<BBHBBB', resp)
        voltage /= 10
        print(temp, voltage, error)

    def clear_errors(self) -> None:
        self.send_command(0x9B)

    def read_encoder(self):
        resp = self.send_command(0x90)
        pos, t1, t2 = struct.unpack('<HHH', resp)
        print(pos, t1, t2)

    def read_model(self):
        resp = self.send_command(0x12)
        driver, motor, hw_ver, fw_ver = struct.unpack('<20s20sBB', resp)

        driver = driver.decode().rstrip('\x00')
        motor = motor.decode().rstrip('\x00')
        hw_ver = round(hw_ver / 10.0, 3)
        fw_ver = round(fw_ver / 10.0, 3)

        print(driver, motor, hw_ver, fw_ver)


if __name__ == '__main__':
    rmd = RMD('/dev/ttyUSB0', id=1, baudrate=115200)
    # rmd.read_model()
    # rmd.read_status()
    rmd.read_encoder()
