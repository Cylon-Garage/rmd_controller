import serial
import serial.rs485
import struct
import time
from typing import Literal, NamedTuple, Tuple, Optional, Union

DEBOUNCE = 0.01


def check_sum(data: bytearray) -> int:
    return sum(data) % 256


class MotorParams:
    def __init__(self,
                 position_kp: int = 100,
                 position_ki: int = 100,
                 speed_kp: int = 40,
                 speed_ki: int = 14,
                 torque_kp: int = 0,
                 torque_ki: int = 0) -> None:

        self.position_kp = position_kp
        self.position_ki = position_ki
        self.speed_kp = speed_kp
        self.speed_ki = speed_ki
        self.torque_kp = torque_kp
        self.torque_ki = torque_ki

    def get_params(self) -> Tuple[int, int, int, int, int, int]:
        return (self.position_kp,
                self.position_ki,
                self.speed_kp,
                self.speed_ki,
                self.torque_kp,
                self.torque_ki)

    def get_params_bytes(self) -> bytes:
        params = bytearray(6)
        params[0] = self.position_kp
        params[1] = self.position_ki
        params[2] = self.speed_kp
        params[3] = self.speed_ki
        params[4] = self.torque_kp
        params[5] = self.torque_ki
        return params

    def print_params(self):
        print(self.get_params())


class RMD:

    def __init__(self, port: str, id: int = 1, baudrate: int = 115200) -> None:
        self.id = id
        self.serial = serial.Serial(port, baudrate=baudrate, timeout=0.5)
        self.last_cmd_time = time.time() - DEBOUNCE * 1.1
        pid_params = self.read_pid_parameters()
        self.motor_params = MotorParams(*pid_params)

    def check_response_header(self, header: bytes, command: int) -> Union[int, None]:
        if header[0] != 0x3E:
            self.serial.reset_input_buffer()
            print('response head byte mismatch')

        if (check_sum(header[:4]) != header[4]):
            print('response header checksum mismatch')

        if header[2] == self.id or header[1] == command:
            return header[3]

        return

    def send_command(self, command: int, data: bytearray = None) -> Union[bytes, None]:
        now = time.time()
        if (now - self.last_cmd_time) < DEBOUNCE:
            return

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
        self.last_cmd_time = now

        resp_header = self.serial.read(5)
        resp_len = self.check_response_header(resp_header, command)

        if resp_len is not None:
            resp = self.serial.read(resp_len + 1)
            return resp[:-1]
        return None

    def uppack_run_response(self, resp: bytes) -> Tuple[Union[int, None], Union[int, None], Union[int, None], Union[int, None]]:
        temp, power, speed, position = None, None, None, None
        if resp is not None:
            temp, power, speed, position = struct.unpack('<bhhH', resp)
            print(temp, power, speed, position)
        return temp, power, speed, position

    def read_pid_parameters(self) -> Tuple[int, int, int, int, int, int]:
        resp = self.send_command(0x30)
        position_kp, position_ki, speed_kp, speed_ki, torque_kp, torque_ki = struct.unpack(
            '<6B', resp)
        return position_kp, position_ki, speed_kp, speed_ki, torque_kp, torque_ki

    def write_pid_parameters(self, position_kp: int = None, position_ki: int = None, speed_kp: int = None, speed_ki: int = None, torque_kp: int = None, torque_ki: int = None, rom: bool = False) -> None:
        arg_keys = [i for i in locals().keys() if i in
                    ['position_kp', 'position_ki', 'speed_kp', 'speed_ki', 'torque_kp', 'torque_ki']]
        for key in arg_keys:
            value = locals()[key]
            if value is not None:
                setattr(self.motor_params, key, value)

        data = self.motor_params.get_params_bytes()
        resp = self.send_command(0x32 if rom else 0x31, data)
        position_kp, position_ki, speed_kp, speed_ki, torque_kp, torque_ki = struct.unpack(
            '<6B', resp)

        print('motor params changed to:\n\tposition_kp:%u\n\tposition_ki:%u\n\tspeed_kp:%u\n\tspeed_ki:%u\n\ttorque_kp:%u\n\ttorque_ki:%u' % (
            position_kp, position_ki, speed_kp, speed_ki, torque_kp, torque_ki))

    def read_encoder(self) -> None:
        resp = self.send_command(0x90)
        pos, t1, t2 = struct.unpack('<HHH', resp)
        print(pos, t1, t2)

    def read_multi_loop_angle(self) -> None:
        resp = self.send_command(0x92)
        angle = struct.unpack('<q', resp)[0] / 100
        print(angle)

    def read_status(self) -> None:
        resp = self.send_command(0x9A)
        temp, _, voltage, _, _, error = struct.unpack('<BBHBBB', resp)
        voltage /= 10
        print(temp, voltage, error)

    def clear_errors(self) -> None:
        resp = self.send_command(0x9B)
        temp, _, voltage, _, _, error = struct.unpack('<BBHBBB', resp)
        voltage /= 10
        print(temp, voltage, error)

    def motor_shutdown(self) -> None:
        resp = self.send_command(0x80)

    def motor_stop(self) -> None:
        resp = self.send_command(0x81)
        print('motor off')

    def motor_on(self) -> None:
        resp = self.send_command(0x88)
        print('motor on')

    def run_torque(self, value: int) -> None:
        resp = self.send_command(0xA0, struct.pack('<h', value))
        temp, power, speed, position = struct.unpack('<bhhH', resp)

    def run_torque2(self, value: int) -> None:
        resp = self.send_command(0xA1, struct.pack('<h', value))
        temp, power, speed, position = struct.unpack('<bhhH', resp)

    def run_position1(self, position: int) -> None:
        resp = self.send_command(0xA3, struct.pack('<q', position))
        temp, power, speed, position = self.uppack_run_response(resp)

    def run_position2(self, position: int) -> None:
        speed = 100
        resp = self.send_command(0xA4, struct.pack('<ql', position, speed))
        temp, power, speed, position = self.uppack_run_response(resp)

    def run_increment1(self, angle: int) -> None:
        resp = self.send_command(0xA7, struct.pack('<h', angle))
        temp, power, speed, position = self.uppack_run_response(resp)

    def read_model(self) -> None:
        resp = self.send_command(0x12)
        driver, motor, hw_ver, fw_ver = struct.unpack('<20s20sBB', resp)

        driver = driver.decode().rstrip('\x00')
        motor = motor.decode().rstrip('\x00')
        hw_ver = round(hw_ver / 10.0, 3)
        fw_ver = round(fw_ver / 10.0, 3)

        print(driver, motor, hw_ver, fw_ver)


if __name__ == '__main__':
    rmd = RMD('/dev/ttyUSB0', id=1, baudrate=115200)
    # rmd.write_pid_parameters(position_ki=100)
    rmd.read_model()
    # rmd.read_status()
    # rmd.read_encoder()
    # rmd.run_torque(-150)
    # rmd.run_torque2(150)
    # rmd.run_torque(0)
    # rmd.read_multi_loop_angle()
    # rmd.run_position1(0)
    # rmd.run_position1(180 * 100)
    # rmd.read_encoder()
    # rmd.run_position1(180 * 100)
    # rmd.run_position2(180 * 100)
