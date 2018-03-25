import math
from Utility import *


class Drone:

    def __init__(self, drone_id, drone_color, drone_velocity, server_loc):
        self.id = drone_id
        self.color = drone_color
        self.locations = None
        self.sorted_locations = None
        self.velocity = drone_velocity
        self.server_loc = server_loc
        self.renderer = None
        self.start = True
        self.update_grid = None
        self.curr_loc = None

        self.estimated_time = None
        self.travel_towards = None
        self.travel_back = None
        self.avg_time = None
        self.click_timer = None

        self.ttime = 0

    def set_locations(self, locations):
        for loc in locations:
            loc.color = self.color
        self.locations = locations
        for loc in locations:
            isinstance(loc.distance_from_server, float)
        self.sorted_locations = sorted(self.locations, key=lambda x: x.distance_from_server)
        self.arrange_grid()
        self.estimated_time, self.travel_towards, self.travel_back, self.avg_time = self.get_estimated_time()

    def get_estimated_time(self):
        time_ = 0
        last_loc = self.locations[0].coordinate
        travel_towards = get_distance(last_loc, self.locations[1].coordinate) / self.velocity
        travel_back = get_distance(last_loc, self.locations[-2].coordinate) / self.velocity

        for i, grid_pt in enumerate(self.locations):
            dist = get_distance(grid_pt.coordinate, last_loc)
            time_ += dist / self.velocity
            grid_pt.estimated_time = time_
            time_ += 2 if i != 0 else 0 # time to click TODO
            last_loc = grid_pt.coordinate

        avg_time = (time_ - travel_back - travel_towards - 2) / (len(self.locations) - 3)
        return time_, travel_towards, travel_back, avg_time

    def arrange_grid(self):
        arrangedGrid = {}

        # print("Transpose: {}".format(transpose))
        # print("Alternate grid: {}".format(arrangedGrid))
        transposeIndividual = {}

        for grid_pt in self.locations:
            # get columns
            indices = grid_pt.index
            transposeIndividual.setdefault(indices[0], []).append(grid_pt)


        # get alternate
        alternateGrid = self.alternate(transposeIndividual)

        alternateGrid.insert(0, GridPoint((-1, -1), self.server_loc, 0.2, 0.0, True))
        alternateGrid.append(GridPoint((-1, -1), self.server_loc, 0.2, 0.0, True))

        self.locations = alternateGrid

    def alternate(self, transpose):
        alternateGrid = []
        i = 0
        for k, v in transpose.items():
            if (i % 2 == 0):
                for grid_pt in v:
                    alternateGrid.append(grid_pt)
                i += 1
            else:
                for grid_pt in v[::-1]:
                    alternateGrid.append(grid_pt)
                i += 1

        return alternateGrid

    def update(self, dt):
        self.ttime += dt

        if self.start:
            self.curr_loc = self.locations[0].coordinate
            self.locations.pop(0)
            self.start = False

        if not isinstance(self.click_timer, type(None)):
            self.click_timer += dt
            self.renderer.render_points([[self.curr_loc[0], self.curr_loc[1], self.color], ])
            if self.click_timer > 2: # TODO time to click
                self.click_timer = None
            return

        # render next point on the list
        render_loc = None
        if len(self.locations) == 0:
            # print("Drone{} RTL".format(self.id))
            return

        index = self.locations[0].index
        next_loc = self.locations[0].coordinate
        dist = self.velocity * dt

        mag = (math.sqrt((next_loc[1] - self.curr_loc[1]) ** 2 + (next_loc[0] - self.curr_loc[0]) ** 2))

        if mag == 0:
            return

        unit_v_y = (next_loc[1] - self.curr_loc[1]) / mag
        unit_v_x = (next_loc[0] - self.curr_loc[0]) / mag

        i_loc = (self.curr_loc[0] + (dist * unit_v_x), self.curr_loc[1] + (dist * unit_v_y))
        if get_distance(i_loc, self.curr_loc) > get_distance(next_loc, self.curr_loc): # case when drone reached a loc
            print("Drone {0} Missed grid point by duration {1}".format(self.id,
                                                                       self.locations[0].estimated_time - self.ttime))
            render_loc = next_loc
            self.click_timer = 0
            self.update_grid(index)
            self.locations.pop(0)

            # print("popping: {}, list length: {}".format(self.locations.pop(0),len(self.locations)))
        else:
            render_loc = i_loc

        # print("drone{}, cur: {}, next {}".format(self.id, render_loc, next_loc))
        self.renderer.render_points([[render_loc[0], render_loc[1], self.color], ])
        self.curr_loc = render_loc
