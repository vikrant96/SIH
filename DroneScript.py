import math
import time
import threading
from Render import *
from Drone import  *
from Utility import *


def getGridPoints(coordinates, overlap, imgWidth, imgHeight):
    # get length and breadth of the rectangle
    l = coordinates[2][0] - coordinates[1][0]
    b = coordinates[1][1] - coordinates[0][1]

    # get number of rectangles in l and b as n1 and n2 resp
    n1 = math.ceil((l - overlap) / (imgWidth - overlap))
    n2 = math.ceil((b - overlap) / (imgHeight - overlap))

    # get new overlaps
    d1 = (n1*imgWidth - l) / (n1 - 1)
    d2 = (n2*imgHeight - b) / (n2 - 1)

    # print new overlaps
    #print("New overlap in x and y resp is: {}{:5}".format(d1,d2))

    # calculate grids
    grid_points = []

    # rows
    for i in range(0, n2):
        for j in range(0, n1):
            x = coordinates[0][0] + imgWidth/2 + j*(imgWidth - d1)
            y = coordinates[0][1] + imgHeight/2 + i*(imgHeight - d2)
            # grid_points.append([(j, i), (x, y), 0.5, None])
            grid_pt = GridPoint((j, i), (x, y), 0.2, None, False)
            grid_points.append(grid_pt)

    # arrange grid items
    # gridPoints = arrangeGrid(gridPoints,n1,n2)

    return grid_points


def get_grid_distribution_with_range(num_drones, gridPoints, timeOfFlight, timeToClick, velocity, serverLoc, serverRange, colors):
    # get new range and tof based on buffer %
    # considering buffer of 10%
    tof = 0.9 * timeOfFlight
    allocated = 0
    serverRange = 0.9 * serverRange
    distribution = {}
    startPositions = []
    droneList = []
    drones = 0

    while allocated != len(gridPoints):
        drones+=1

        if drones == num_drones:
            distribution[drones] = []
            for grid_pt in gridPoints:
                if not grid_pt.allocated:
                    distribution[drones].append(grid_pt)
            drone = Drone(drones, colors[drones - 1], velocity, serverLoc)
            droneList.append(drone)
            break

        startPos = gridPoints[0].coordinate

        # set start location for first drone
        if(drones == 1):
            for grid_pt in gridPoints:
                if(math.sqrt((grid_pt.coordinate[1] - serverLoc[1])**2 + (grid_pt.coordinate[0] - serverLoc[0])**2) < serverRange):
                    startPos = grid_pt.coordinate
                    startPositions.append(startPos)
                    break

        # set start location for rest of the drones
        if(drones > 1):
            lastDronePos = startPositions[-1]
            for grid_pt in gridPoints:
                if get_distance(lastDronePos, grid_pt.coordinate) < serverRange:
                    startPos = grid_pt.coordinate
                    startPositions.append(startPos)
                    break

        # get distance and time for travel
        distance = get_distance(startPos, serverLoc)
        timeToTravel = distance / velocity
        timeToMap = tof - 2*timeToTravel
        if(timeToMap < 0):
            print("Drones inefficient to map such a large area. Increase battery :p")
            break

        # list of locations
        distribution[drones] = []

        # setting distance from server
        for grid_pt in gridPoints:
            grid_pt.set_distance_from_server(serverLoc)

        for grid_pt in gridPoints:
            if grid_pt.allocated:
                continue
            if grid_pt.distance_from_server < serverRange and drones == 1 and timeToMap > 2:
                distribution[drones].append(grid_pt)
                grid_pt.color = colors[drones-1]
                timeToMap -= timeToClick
                grid_pt.allocated = True
                allocated += 1
            elif drones != 1:
                for j in range(0,len(distribution[drones-1])):
                    dist_obj = distribution[drones-1][j]
                    loc_ = dist_obj.coordinate
                    if math.sqrt((grid_pt.coordinate[1] - loc_[1])**2 + (grid_pt.coordinate[0] - loc_[0])**2) < serverRange and timeToMap > 2:
                        distribution[drones].append(grid_pt)
                        grid_pt.color = colors[drones-1]
                        timeToMap -= timeToClick
                        grid_pt.allocated = True
                        allocated += 1
                        break

        # create drones
        drone = Drone(drones, colors[drones-1], velocity, serverLoc)
        droneList.append(drone)

        # print time left for drone one
        #print("Drone {}: \nStart Pos: {} \ndistance: {} \nTime taken: {}".format(drones,startPos,distance,tof - timeToMap))

    if drones < num_drones:
        while drones == num_drones:
            drones += 1
            drone = Drone(drones, colors[drones - 1], velocity, serverLoc)
            droneList.append(drone)
            distribution[drones] = []
    #print(gridPoints)
    #
    # print(distribution)
    return droneList, distribution, gridPoints


def shuffle_distribution(drone_list, grid_dimension, w, h):

    shuffle_renderer = GenGrid(grid_dimension[0], grid_dimension[1])
    n_drones = len(drone_list)
    for j in range(0, 10):
        for i, drone in enumerate(drone_list):
            time_prev = drone_list[i-1].estimated_time if i-1 >= 0 else float('-inf')
            time_next = drone_list[i+1].estimated_time if i+1 < n_drones else float('-inf')
            if drone.estimated_time < time_prev or drone.estimated_time < time_next:
                if time_prev > time_next:
                    prev_locs = drone_list[i-1].sorted_locations
                    num_extra_blocks = int((time_prev - drone.estimated_time) / drone_list[i-1].avg_time)
                    if int(num_extra_blocks / 2) == 0:
                        continue
                    take = prev_locs[-int(num_extra_blocks / 2): ]
                    #print("Drone{0}/{5} taking {1}/{4} from Drone{2} at iter {3}".format(i, len(take), i-1, j,
                    #        len(drone_list[i - 1].sorted_locations), len(drone.sorted_locations)))
                    drone_list[i-1].set_locations(prev_locs[:-int(num_extra_blocks / 2)])
                    curr_drone_locations = drone.sorted_locations
                    curr_drone_locations += take
                    drone.set_locations(curr_drone_locations)
                else:
                    next_locs = drone_list[i + 1].sorted_locations
                    num_extra_blocks = int((time_next - drone.estimated_time) // drone_list[i + 1].avg_time)
                    if int(num_extra_blocks / 2) == 0:
                        continue
                    take = next_locs[:int(num_extra_blocks / 2)]
                    #print("Drone{0}/{5} taking {1}/{4} from Drone{2} at iter {3}".format(i, len(take), i + 1, j,
                    #        len(drone_list[i + 1].sorted_locations), len(drone.sorted_locations)))
                    drone_list[i + 1].set_locations(next_locs[int(num_extra_blocks / 2):])
                    curr_drone_locations = drone.sorted_locations
                    curr_drone_locations += take
                    drone.set_locations(curr_drone_locations)
        pr = ""
        for drone in drone_list:
            pr += " " + str(len(drone.sorted_locations))
        #print(pr)
        grid_pts = []
        for drone in drone_list:
            grid_pts += drone.locations

        # render grid
        #shuffle_renderer.render_grid(grid_pts, w, h)
        #shuffle_renderer.show()
    # i = input()



def add_transparency(self, distribution):
    for k, v in distribution.items():
        color = self.colors[k-1]
        for index, loc_ in v:
            self.grid_list.append([loc_[0], loc_[1], color, 0.2])


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

            # scaling of the relay points
            last_x = relay_points[-1][0]
            last_y = relay_points[-1][1]

            scale_x = last_x / self.gridDimension[0]
            scale_y = last_y / self.gridDimension[1]


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
                # f = False

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


def main():
    # parameters
    coordinates = [[0,0],[0,100],[200,100],[200,0]]
    overlap = 2.5
    imgWidth = 10
    imgHeight = 10
    timeOfFlight = 200
    serverLoc = (50,0)
    timeToClick = 2
    velocity = 30
    range_ = 30
    num_drones = 5
    gridDimension = (200,100)
    colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (102, 0, 102), (255, 0, 255), (215, 220, 55), (205, 100, 155), (155, 200, 255), (233, 12, 33), (123, 45, 111)]

    # print grid array
    gridPoints = getGridPoints(coordinates, overlap, imgWidth, imgHeight)
    #print(gridPoints)

    # get distribution
    drone_list, distribution, gridPoints = get_grid_distribution_with_range(num_drones, gridPoints, timeOfFlight, timeToClick, velocity, serverLoc, range_, colors)
    #print(distribution)

    # set locations for each drone
    for i, drone in enumerate(drone_list):
        drone.set_locations(distribution[i+1])

    # shuffle distribution for same time
    shuffle_distribution(drone_list, gridDimension, imgWidth, imgHeight)

    # Print est time for drones
    for drone in drone_list:
        print("Drone{0}, ETA,to,back: {1}".format(drone.id, drone.get_estimated_time()))

    sim = Simulator(drone_list, velocity, timeToClick, serverLoc, range_, gridDimension, gridPoints, imgWidth, imgHeight)
    sim.sim_loop()


if __name__== "__main__":
  main()