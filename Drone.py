import math

class Drone:

    def __init__(self, drone_id, drone_color, drone_location, drone_start_pos):
        self.id = drone_id
        self.color = drone_color
        self.locations = drone_location
        self.start_pos = drone_start_pos
        self.velocity = 5
        self.renderer = None
        self.start = True
        self.update_grid = None

    def _get_distance(self, pt1, pt2):
        return math.sqrt((pt1[1] - pt2[1]) ** 2 + (pt1[0] - pt2[0]) ** 2)

    def update(self, dt):
        if self.start:
            self.curr_loc = self.locations[0][1]
            self.locations.pop(0)
            self.start = False

        # render next point on the list
        render_loc = None
        index = self.locations[0][0]
        next_loc = self.locations[0][1]
        dist = self.velocity * dt
        if next_loc[0] - self.curr_loc[0] != 0:
            slope = (next_loc[1] - self.curr_loc[1]) / (next_loc[0] - self.curr_loc[0])
            print(slope)
            theta = math.atan(slope)
            print(theta)
        else:
            if next_loc[1] > self.curr_loc[1]:
                print("bcbcbc")
                theta = math.pi / 2
            else:
                print("bcbcbc")
                theta = - math.pi / 2
        i_loc = (self.curr_loc[0] + (dist * math.cos(theta)), self.curr_loc[1] + (dist * math.sin(theta)))
        if self._get_distance(i_loc, self.curr_loc) > self._get_distance(next_loc, self.curr_loc):
            render_loc = next_loc
            self.update_grid(index)
            self.locations.pop(0)
        else:
            render_loc = i_loc

        print("drone{}, cur: {}, next {}".format(self.id, render_loc, next_loc))
        self.renderer.render_points([[render_loc[0], render_loc[1], self.color],])
        self.curr_loc = render_loc




