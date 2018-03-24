import math
import copy
from Drone import *
from Render import *
from DroneScript import *
from random import randint
from Utility import *


class XYCoordinate:
    x = 0
    y = 0

    def __init__(self,x_coordinate,y_coordinate):
        self.x = x_coordinate
        self.y = y_coordinate

    def getDistance(self,xycoordinate):
        return math.sqrt((xycoordinate.x - self.x)**2 + (xycoordinate.y - self.y))


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
    print("New overlap in x and y resp is: {}{:5}".format(d1,d2))

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


def get_grid_distribution_with_range(gridPoints, timeOfFlight, timeToClick, velocity, serverLoc, serverRange, colors):
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
        print("Drone {}: \nStart Pos: {} \ndistance: {} \nTime taken: {}".format(drones,startPos,distance,tof - timeToMap))

    print(gridPoints)
    print(distribution)
    return droneList, distribution, gridPoints


def shuffle_distribution(drone_list, grid_dimension, w, h):

    shuffle_renderer = GenGrid(grid_dimension[0], grid_dimension[1])
    n_drones = len(drone_list)
    for j in range(0, 5):
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
                    print("Drone{0}/{5} taking {1}/{4} from Drone{2} at iter {3}".format(i, len(take), i-1, j,
                            len(drone_list[i - 1].sorted_locations), len(drone.sorted_locations)))
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
                    print("Drone{0}/{5} taking {1}/{4} from Drone{2} at iter {3}".format(i, len(take), i + 1, j,
                            len(drone_list[i + 1].sorted_locations), len(drone.sorted_locations)))
                    drone_list[i + 1].set_locations(next_locs[int(num_extra_blocks / 2):])
                    curr_drone_locations = drone.sorted_locations
                    curr_drone_locations += take
                    drone.set_locations(curr_drone_locations)
        pr = ""
        for drone in drone_list:
            pr += " " + str(len(drone.sorted_locations))
        print(pr)
        grid_pts = []
        for drone in drone_list:
            grid_pts += drone.locations

        # render grid
        shuffle_renderer.render_grid(grid_pts, w, h)
        shuffle_renderer.show()
    # i = input()

def add_transparency(self, distribution):
    for k, v in distribution.items():
        color = self.colors[k-1]
        for index, loc_ in v:
            self.grid_list.append([loc_[0], loc_[1], color, 0.2])


def main():
    # parameters
    coordinates = [[0,0],[0,100],[100,100],[100,0]]
    overlap = 2.5
    imgWidth = 10
    imgHeight = 10
    timeOfFlight = 200
    serverLoc = (50,0)
    timeToClick = 2
    velocity = 10
    range_ = 30
    gridDimension = (100,100)
    colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (102, 0, 102), (255, 0, 255), (215, 220, 55), (205, 100, 155), (155, 200, 255)]

    # print grid array
    gridPoints = getGridPoints(coordinates, overlap, imgWidth, imgHeight)
    print(gridPoints)

    # get distribution
    drone_list, distribution, gridPoints = get_grid_distribution_with_range(gridPoints, timeOfFlight, timeToClick, velocity, serverLoc, range_, colors)
    print(distribution)

    # set locations for each drone
    for i, drone in enumerate(drone_list):
        drone.set_locations(distribution[i+1])

    # shuffle distribution for same time
    shuffle_distribution(drone_list, gridDimension, imgWidth, imgHeight)

    # Print est time for drones
    for drone in drone_list:
        print("Drone{0}, ETA,to,back: {1}".format(drone.id, drone.get_estimated_time()))

    sim = Simulator(drone_list, velocity, timeToClick, serverLoc, gridDimension, gridPoints, imgWidth, imgHeight)
    sim.sim_loop()


if __name__== "__main__":
  main()