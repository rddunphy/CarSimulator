#!/usr/bin/python3

import argparse
import math
import time

import matplotlib.pyplot as plt
from matplotlib import animation
import numpy
import png

from carsim_algorithms import *


# GLOBALS

# Increase for smaller turning circle:
steering_factor = 0.01

# Margin from edge of map for placing car
margin = 50

# Distance from top of image considered goal
goal_line = 80


class Map:
    def __init__(self, img):
        r = png.Reader(filename=img)
        self.w, self.h, px, _ = r.read_flat()
        ch = int(round(len(px) / (self.w * self.h)))
        self.px = numpy.array(px).reshape((self.h, self.w, ch))

    def is_wall(self, pos):
        return not any((self.is_line(pos), self.is_clear(pos)))

    def is_line(self, pos):
        p = self.px[int(pos.imag)][int(pos.real)]
        return all((p[0] >= 127, p[1] < 127, p[2] < 127))

    def is_clear(self, pos):
        p = self.px[int(pos.imag)][int(pos.real)]
        return all((p[0] >= 127, p[1] >= 127, p[2] >= 127))


class Car:
    def __init__(self, pos):
        self.pos = pos
        self.width = 50
        self.length = 80
        self.rot = 0
        self.front_left = complex(-self.width / 2, -self.length / 2)
        self.front_right = complex(self.width / 2, -self.length / 2)
        self.back_left = complex(-self.width / 2, self.length / 2)
        self.back_right = complex(self.width / 2, self.length / 2)
        self.left_sensor = complex(-self.width / 2 - 10, -self.length / 2)
        self.right_sensor = complex(self.width / 2 + 10, -self.length / 2)
        self.front_sensor = complex(0, -self.length / 2 - 10)
        self.back_sensor = complex(0, self.length / 2 + 5)
        self.sensors = (self.front_sensor, self.back_right, self.back_left, self.front_right, self.front_left,
                        self.left_sensor, self.right_sensor)

    def to_world(self, p):
        """Takes a point relative to the centre of the car (in driving direction) and calculates the world coordinates,
        based on the current position and angle of the car"""
        return self.pos + p * complex(math.cos(self.rot), math.sin(self.rot))

    def move(self, speed, steer):
        """Update position and angle of car.

        :param speed: In range [-1; 1], -1 is backwards, 1 is forwards, 0 is no movement
        :param steer: In range [-1; 1], -1 is hard left, 1 is hard right, 0 is straight
        """
        self.rot += steer * steering_factor * abs(speed)
        if self.rot < -math.pi:
            self.rot += 2*math.pi
        elif self.rot > math.pi:
            self.rot -= 2*math.pi
        self.pos = self.to_world(complex(0, -speed))


def _plt_patch_list(map, car, ax):
    corner = car.to_world(car.front_left)
    shapes = [
        plt.Circle((car.pos.real, car.pos.imag), radius=3, color='g'),
        plt.Rectangle((corner.real, corner.imag), car.width, car.length,
                      angle=math.degrees(car.rot), linewidth=2, edgecolor='g', facecolor='none')
    ]
    sensors = [car.to_world(s) for s in car.sensors]
    shapes += [plt.Circle((p.real, p.imag), radius=7, color='m' if map.is_clear(p) else 'c') for p in sensors]
    return [ax.add_patch(shape) for shape in shapes]


def _end_animation(count):
    print("Number of steps: {}".format(count))
    time.sleep(2)
    exit(0)


def _plt_animate(frame, map, car, alg, ax):
    speed, dir = alg.get_move(map, car)
    car.move(speed, dir)
    if car.pos.imag <= goal_line:
        _end_animation(frame)
    return _plt_patch_list(map, car, ax)


def main(img, start_x, start_y):
    map = Map(img)
    if start_x < 0:
        start_x = map.w / 2
    if start_y < 0:
        start_y = map.h - margin
    if start_x < margin or start_y < margin or start_x > map.w - margin or start_y > map.h - margin:
        print("Start coordinates out of bounds - need to be at least {}px within the edge of the image. "
              "(x: [{}; {}], y: [{}; {}])".format(margin, margin, map.w - margin, margin, map.h - margin))
        exit(1)
    start_pos = complex(start_x, start_y)
    fig, ax = plt.subplots(1)
    ax.imshow(map.px)
    car = Car(start_pos)
    alg = StupidAlgorithm()
    _ = animation.FuncAnimation(fig, _plt_animate, fargs=(map, car, alg, ax), interval=10, blit=True)
    plt.show()


def get_args():
    parser = argparse.ArgumentParser("Simulate obstacle avoiding car")
    parser.add_argument("file", type=str, nargs='?', help="Path to a PNG image of the map", default="maps/default_map.png")
    parser.add_argument("-x", type=int, help="X coordinate to start at", default=-1)
    parser.add_argument("-y", type=int, help="Y coordinate to start at", default=-1)
    args = parser.parse_args()
    return args.file, args.x, args.y


if __name__ == '__main__':
    main(*get_args())
