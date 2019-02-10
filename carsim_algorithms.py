import enum
import math


class StupidAlgorithm:

    def __init__(self, map, car):
        self.map = map
        self.car = car
        self.prefer_left = True
        self.reverse_count = 0
        self.steer_count = 0

    def get_move(self):
        """Get next car move based on current world state."""
        if self.reverse_count:  # More reversing to do - go straight back
            if not all([self.map.is_clear(self.car.to_world(s)) for s in (self.car.back_right, self.car.back_left)]):
                # Obstacle behind - stop reversing
                self.reverse_count = 0
                return 0, 0
            self.reverse_count -= 1
            return -1, -1 if self.prefer_left else 1
        fs = self.car.to_world(self.car.front_sensor)
        frs = self.car.to_world(self.car.front_right)
        fls = self.car.to_world(self.car.front_left)
        rs = self.car.to_world(self.car.right_sensor)
        ls = self.car.to_world(self.car.left_sensor)
        if not all([self.map.is_clear(x) for x in [fs, frs, fls]]):  # Obstacle on emergency brake sensor
            if self.map.is_clear(fs) and self.map.is_clear(frs):
                self.prefer_left = False
            elif self.map.is_clear(fs) and self.map.is_clear(fls):
                self.prefer_left = True
            elif any([self.map.is_wall(x) for x in [fs, frs, fls]]):  # Obstacle is wall, so switch preferred direction
                self.prefer_left = True if self.car.rot > 0 else False
            self.reverse_count = 50
            self.steer_count = 50
            return 0, 0
        if self.steer_count:  # Steer count means there was an obstacle and we reversed, so try turning
            self.steer_count -= 1
            return 1, -1 if self.prefer_left else 1
        # Otherwise, move toward goal line
        if not self.map.is_clear(rs):  # Obstacle on outer sensor but not emergency brake sensor
            return 1, -1
        elif not self.map.is_clear(ls):
            return 1, 1
        elif self.car.rot > 0.001:  # No obstacles? straighten up
            return 1, -1
        elif self.car.rot < -0.001:
            return 1, 1
        # No obstacle, car already straight - full speed ahead
        return 1, 0
