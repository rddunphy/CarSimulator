#!/usr/bin/python3

import argparse
import time

import matplotlib.pyplot as plt
from matplotlib import animation
import numpy
import png


class Coords:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Map:
    def __init__(self, img):
        r = png.Reader(filename=img)
        self.w, self.h, px, _ = r.read_flat()
        self.px = numpy.array(px).reshape((self.h, self.w, 3))

    def is_wall(self, pos):
        return not self.is_line(pos) and not self.is_clear(pos)

    def is_line(self, pos):
        p = self.px[pos.y][pos.x]
        return p[0] >= 127 and p[1] < 127 and p[2] < 127

    def is_clear(self, pos):
        p = self.px[pos.y][pos.x]
        return p[0] >= 127 and p[1] >= 127 and p[2] >= 127


dash = True
prefer_left = True

counter = 0


def next_pos(map, pos):
    global dash, prefer_left
    if dash:
        next = Coords(pos.x, pos.y - 1)
        if not map.is_clear(next):
            dash = False
        return next
    if map.is_line(pos):
        if prefer_left:
            next = Coords(pos.x - 1, pos.y + 1)
        else:
            next = Coords(pos.x + 1, pos.y + 1)
        if not map.is_clear(next):
            next = Coords(pos.x, pos.y + 1)
    else:
        if prefer_left:
            next = Coords(pos.x - 1, pos.y - 1)
        else:
            next = Coords(pos.x + 1, pos.y - 1)
        if map.is_clear(next):
            dash = True
    if map.is_wall(next):
        prefer_left = not prefer_left
        return pos
    else:
        return next

def next_pos2(map, pos):
    global dash, prefer_left
    if dash:
        next = Coords(pos.x, pos.y - 1)
        if(all(map.is_clear(Coords(pos.x, pos.y - n)) for n in range(10))):
            prefer_left = pos.x > map.w / 2
        if not map.is_clear(next):
            dash = False
        return next
    if map.is_line(pos):
        if prefer_left:
            next = Coords(pos.x - 1, pos.y + 1)
        else:
            next = Coords(pos.x + 1, pos.y + 1)
        if not map.is_clear(next):
            next = Coords(pos.x, pos.y + 1)
    else:
        if prefer_left:
            next = Coords(pos.x - 1, pos.y - 1)
        else:
            next = Coords(pos.x + 1, pos.y - 1)
        if map.is_clear(next):
            dash = True
    if map.is_wall(next):
        prefer_left = not prefer_left
        return pos
    else:
        return next


def main(img, pos):
    map = Map(img)
    fig, ax = plt.subplots(1)
    ax.imshow(map.px)

    def plt_circle_patch(p):
        return [ax.add_patch(plt.Circle((p.x, p.y), radius=20, linewidth=2, edgecolor='g', facecolor='none'))]

    def plt_init():
        return plt_circle_patch(pos)

    def plt_anim(_, pos):
        p = next_pos2(map, pos)
        pos.x = p.x
        pos.y = p.y
        global counter
        counter += 1
        if pos.y <= 30:
            print(counter)
            time.sleep(2)
            exit()
        return plt_circle_patch(pos)

    _ = animation.FuncAnimation(fig, plt_anim, init_func=plt_init, fargs=(pos,), interval=10, blit=True)
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Simulate obstacle avoiding car")
    parser.add_argument("--file", type=str, help="Path to a PNG image of the map", default="maps/test_map.png")
    parser.add_argument("-x", type=int, help="X coordinate to start at", default=200)
    parser.add_argument("-y", type=int, help="Y coordinate to start at", default=1100)
    args = parser.parse_args()
    main(args.file, Coords(args.x, args.y))
