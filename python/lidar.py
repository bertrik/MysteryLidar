#!/usr/bin/env python3
import math
import time
from enum import Enum

import sdl2
import sdl2.ext
import serial


class FrameExtractor:
    class State(Enum):
        HEADER_1 = 1
        HEADER_2 = 2
        COLLECT = 3

    def __init__(self):
        self.state = self.State.HEADER_1
        self.index = 0
        self.length = 0
        self.data = bytearray(60)

    def add_data(self, b):
        self.data[self.index] = b
        self.index = self.index + 1

    def process(self, b):
        """ processes one byte, returns True if a full frame was received """
        match self.state:
            case self.State.HEADER_1:
                self.index = 0
                if b == 0x55:
                    self.add_data(b)
                    self.state = self.State.HEADER_2

            case self.State.HEADER_2:
                if b == 0xAA:
                    self.add_data(b)
                    self.length = len(self.data)
                    self.state = self.State.COLLECT
                else:
                    self.state = self.State.HEADER_1
                    self.process(b)

            case self.State.COLLECT:
                if self.index < self.length:
                    self.add_data(b)
                if self.index == self.length:
                    # done
                    self.state = self.State.HEADER_1
                    return True
        return False

    def get_data(self):
        return self.data


def dump_hex(data):
    ts = time.time()
    line = f"{ts:10.3f}:"
    for b in data:
        item = f' {b:02x}'
        line = line + item
    fsa = (data[6] + (data[7] << 8)) / 64.0 - 640
    lsa = (data[56] + (data[57] << 8)) / 64.0 - 640
    print(f"{line} = {fsa:6.2f}...{lsa:6.2f}")


last_angle = 0.0


def draw_plot(renderer, data):
    global last_angle

    fsa = (data[6] + (data[7] << 8)) / 64.0 - 640
    lsa = (data[56] + (data[57] << 8)) / 64.0 - 640
    angle = fsa
    if lsa < fsa:
        lsa = lsa + 360
    step = (lsa - fsa) / 16

    # clear if we started a new rotation
    if angle < last_angle:
        renderer.present()
        renderer.clear(sdl2.ext.Color(0, 0, 0))
    last_angle = angle

    points = []
    idx = 8
    for i in range(16):
        radians = math.radians(angle)
        angle = angle + step

        v = (data[idx] + (data[idx + 1] << 8)) & 0x3FFF
        idx = idx + 3
        distance = v / 12

        x = 400 + math.sin(radians) * distance
        y = 400 - math.cos(radians) * distance
        points.append((x, y))
    renderer.draw_point(points, sdl2.ext.Color(255, 255, 255))


def main():
    sdl2.ext.init()
    window = sdl2.ext.Window("LIDAR", size=(800, 800))
    window.show()
    renderer = sdl2.ext.Renderer(window)

    with serial.Serial("/dev/ttyUSB0", 230400, timeout=1) as ser:
        frame_extractor = FrameExtractor()
        while True:
            data = ser.read(size=16)
            for b in data:
                if frame_extractor.process(b):
                    frame_data = frame_extractor.get_data()
                    dump_hex(frame_data)
                    draw_plot(renderer, frame_data)


if __name__ == "__main__":
    main()
