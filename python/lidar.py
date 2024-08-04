#!/usr/bin/env python3
import time

from enum import Enum
import serial


class Deframer:
    class State(Enum):
        HEADER_1 = 1
        HEADER_2 = 2
        COLLECT = 3

    def __init__(self, callback):
        self.state = self.State.HEADER_1
        self.index = 0
        self.length = 0
        self.data = bytearray(60)
        self.callback = callback

    def add_data(self, b):
        self.data[self.index] = b
        self.index = self.index + 1

    def process(self, b):
        match self.state:
            case self.State.HEADER_1:
                self.index = 0
                if b == 0x55:
                    self.add_data(b)
                    self.state = self.State.HEADER_2

            case self.State.HEADER_2:
                if b == 0xAA:
                    self.add_data(b)
                    self.length = 60
                    self.state = self.State.COLLECT
                else:
                    self.state = self.State.HEADER_1
                    self.process(b)

            case self.State.COLLECT:
                if self.index < self.length:
                    self.add_data(b)
                if self.index == self.length:
                    # done, invoke callback
                    self.callback(self.data, self.length)
                    self.state = self.State.HEADER_1


def full_frame_callback(data, length):
    ts = time.time()
    line = f"{ts:10.3f}:"

    for b in data:
        item = f' {b:02x}'
        line = line + item

    fsa = (data[6] + (data[7] << 8)) / 64.0 - 640
    lsa = (data[56] + (data[57] << 8)) / 64.0 - 640
    print(f"{line} = {fsa:6.2f}...{lsa:6.2f}")

    angle = fsa
    step = (lsa - fsa) / 16 if angle >= 0.0 else (360 + lsa - fsa) / 16
    line = ""
    idx = 8
    for i in range(16):
        v = data[idx] + (data[idx + 1] << 8) & 0xFFF
        v = max(0, v)
        idx = idx + 3
        line = line + f" {v:05d}"
        # print(f"{angle:.2f},{v}")
        angle = angle + step


def main():
    deframer = Deframer(full_frame_callback)
    with serial.Serial("/dev/ttyUSB0", 230400, timeout=1) as ser:
        while True:
            data = ser.read(size=16)
            for b in data:
                deframer.process(b)


if __name__ == "__main__":
    main()
