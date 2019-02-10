
class StupidAlgorithm:

    def __init__(self):
        self.prefer_left = True
        self.reverse_count = 0
        self.steer_count = 0

    def get_move(self, map, car):
        """Get next car move based on current world state."""
        if self.reverse_count:  # More reversing to do - go straight back
            if not all([map.is_clear(car.to_world(s)) for s in (car.back_right, car.back_left)]):
                # Obstacle behind - stop reversing
                self.reverse_count = 0
                return 0, 0
            self.reverse_count -= 1
            return -1, -1 if self.prefer_left else 1
        fs = car.to_world(car.front_sensor)
        frs = car.to_world(car.front_right)
        fls = car.to_world(car.front_left)
        rs = car.to_world(car.right_sensor)
        ls = car.to_world(car.left_sensor)
        if not all([map.is_clear(x) for x in [fs, frs, fls]]):  # Obstacle on emergency brake sensor
            if map.is_clear(fs) and map.is_clear(frs):
                self.prefer_left = False
            elif map.is_clear(fs) and map.is_clear(fls):
                self.prefer_left = True
            elif any([map.is_wall(x) for x in [fs, frs, fls]]):  # Obstacle is wall, so switch preferred direction
                self.prefer_left = True if car.rot > 0 else False
            self.reverse_count = 50
            self.steer_count = 50
            return 0, 0
        if self.steer_count:  # Steer count means there was an obstacle and we reversed, so try turning
            self.steer_count -= 1
            return 1, -1 if self.prefer_left else 1
        # Otherwise, move toward goal line
        if not map.is_clear(rs):  # Obstacle on outer sensor but not emergency brake sensor
            return 1, -1
        elif not map.is_clear(ls):
            return 1, 1
        elif car.rot > 0.001:  # No obstacles? straighten up
            return 1, -1
        elif car.rot < -0.001:
            return 1, 1
        # No obstacle, car already straight - full speed ahead
        return 1, 0
