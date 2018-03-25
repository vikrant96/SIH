import math
import time
import threading
from Render import *
import cv2
from Utility import *


def best_fit(X, Y):

    xbar = sum(X)/len(X)
    ybar = sum(Y)/len(Y)
    n = len(X) # or len(Y)

    numer = sum([xi*yi for xi,yi in zip(X, Y)]) - n * xbar * ybar
    denum = sum([xi**2 for xi in X]) - n * xbar**2

    b = numer / denum
    a = ybar - b * xbar

    print('best fit line:\ny = {:.2f} + {:.2f}x'.format(a, b))

    return a, b


def _get_intersection(pt1, center, radius):
    # get slope of line
    y1 = math.sqrt(radius ** 2 - (pt1[0] - center[0]) ** 2) + center[1]
    y2 = -math.sqrt(radius ** 2 - (pt1[0] - center[0]) ** 2) + center[1]
    return (pt1[0], y1) if y1 > y2 else (pt1[0], y2)

class Simulator:
    def __init__(self, drone_list, velocity, toc, server_loc, drone_range, grid, grid_pts, w, h):
        self.drone_list = drone_list
        self.timeToClick = toc
        self.velocity = velocity
        self.server_loc = server_loc
        self.drone_range = drone_range
        self.gridDimension = grid
        self.grid_pts = grid_pts
        self.width = w
        self.height = h
        self.colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (102, 0, 102), (255, 0, 255)]
        self.render_object = GenGrid(self.gridDimension[0], self.gridDimension[1])

    def update_grid(self, indices):
        for i, point in enumerate(self.grid_pts):
            if point.index == indices:
                self.grid_pts[i].foc = 0.6
                self.grid_pts[i].completed = True

    def generate_relay(self, time):
        # get nearest grid location for next time
        grid_locations = []
        drange = self.drone_range * 0.9  # TODO store as constants in a class
        for drone in self.drone_list:
            grid_locations.append(sorted(drone.locations, key=lambda x: abs(x.estimated_time - time))[0])

        # get relay points
        relay_points = [self.server_loc]

        for i, grid_pt in enumerate(grid_locations):
            # check if inside range
            vec = (grid_pt.coordinate[0] - relay_points[i][0], grid_pt.coordinate[1] - relay_points[i][1])
            mag = math.sqrt(vec[0] ** 2 + vec[1] ** 2)
            if mag < drange:
                #push it in y
                relay_points.append(_get_intersection(grid_pt.coordinate, relay_points[i], drange))
            else:
                vec = (vec[0] / mag, vec[1] / mag)
                relay_points.append((relay_points[i][0] + vec[0] * drange, relay_points[i][1] + vec[1] * drange))

        # # line
        # a, b = best_fit([self.server_loc[0], ] * len(grid_locations) + [pt.coordinate[0] for pt in grid_locations],
        #                 [self.server_loc[1], ] * len(grid_locations) + [pt.coordinate[1] for pt in grid_locations])
        #
        # # get cuts on the line at a distance of range
        # pt2 = (grid_locations[0].coordinate[0], a + b * grid_locations[0].coordinate[0])
        # vec = (pt2[0] - self.server_loc[0], pt2[1] - self.server_loc[1])
        # mag = math.sqrt(vec[0] ** 2 + vec[1] ** 2)
        # vec = (vec[0] / mag, vec[1] / mag)
        #
        # # get scaling factor for relays
        # last_y_pt = self.server_loc[1] + vec[1] * (len(grid_locations)) * drange
        # last_x_pt = self.server_loc[0] + vec[0] * (len(grid_locations)) * drange
        # scale_factor_y = self.gridDimension[1] / last_y_pt
        #
        # scale_factor_x = (self.gridDimension[0] - abs(self.server_loc[0])) / abs(last_x_pt - self.server_loc[0])
        # print(scale_factor_x)
        #
        # # generate relay points
        # relay_points = []
        # for i in range(len(grid_locations)):
        #     relay_points.append((self.server_loc[0] + vec[0] * (i + 1) * drange * scale_factor_x * scale_factor_y,
        #                          self.server_loc[1] + vec[1] * (i + 1) * drange * scale_factor_x * scale_factor_y))

        return grid_locations, relay_points

    def sim_loop(self):
        ttime = 0
        t1 = time.time()
        time.sleep(0.1)
        for drone in self.drone_list:
            drone.renderer = self.render_object
            drone.update_grid = self.update_grid
        f = True
        relaytime = 20
        relay, linepoints = self.generate_relay(relaytime)
        while True:
            dt = time.time() - t1
            t1 = time.time()
            ttime += dt
            #print(ttime)
            if f:
                self.render_object.render_grid(self.grid_pts, self.width, self.height)
                f = False

            # recompute relay
            if ttime > relaytime:
                relaytime += 10
                relay, linepoints = self.generate_relay(relaytime)

            # draw relay and linepoints
            self.render_object.render_points([[r.coordinate[0], r.coordinate[1], (0, 0, 0)] for r in relay])
            self.render_object.render_points([[l[0], l[1], (255, 255, 255)] for l in linepoints])

            # update drones
            for drone in self.drone_list:
                drone.update(dt)
            self.render_object.show()
