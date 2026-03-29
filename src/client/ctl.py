from datetime import datetime
from pathlib import Path

import numpy as np
import serial

MAX_SIZE = 4 * 1024 * 1024


class Control:
    def __init__(
        self: str, serial_path, x_min, x_max, y_min, y_max, z_min=None, z_max=None
    ):
        self.step = 1
        self.path = None
        self.plot_data = []
        self._speed = 500

        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.z_min = z_min
        self.z_max = z_max

        self.x = None
        self.y = None
        self.z = None

        self.serial_path = serial_path

    # moves positional device to specified location in 2d
    def move_2D(self, x, y):
        if self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max:
            with serial.Serial(self.serial_path, 115200, timeout=2) as printer:
                printer.reset_input_buffer()
                print("Move started.")

                printer.write(b"G90\n")
                printer.readline()

                gcode = f"G0 X{round(x,1)} Y{round(y,1)} F{self._speed}\n"
                printer.write(gcode.encode())
                printer.readline()

                printer.write(b"M400\n")
                while printer.readline().decode().strip() != "ok":
                    print("waiting for move to finish")

                print("Move finished.")

                self.x = x
                self.y = y
        else:
            print("! Move out of the boundary. !")

    # moves positional device to specified location in 3d
    def move_3D(self, x, y, z):
        if (
            self.x_min <= x <= self.x_max
            and self.y_min <= y <= self.y_max
            and self.z_min <= z <= self.z_max
        ):
            with serial.Serial(self.serial_path, 115200, timeout=2) as printer:
                printer.reset_input_buffer()
                print("Move started.")

                printer.write(b"G90\n")
                printer.readline()

                gcode = f"G0 X{round(x,1)} Y{round(y,1)} Z{round(z,1)} F{self._speed}\n"
                printer.write(gcode.encode())
                printer.readline()

                printer.write(b"M400\n")
                while printer.readline().decode().strip() != "ok":
                    print("waiting for move to finish")

                print("Move finished.")

                self.x = x
                self.y = y
                self.z = z
        else:
            print("! Move out of the boundary. !")

    def get_pos(self):
        return self.x, self.y, self.z
