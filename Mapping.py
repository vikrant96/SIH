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


def get_grid_distribution(gridPoints, timeOfFlight, timeToClick, velocity, serverLoc, serverRange, colors):
    # get new range and tof based on buffer %
    # considering buffer of 10%
    tof = 0.9 * timeOfFlight
    allocated = 0
    serverRange = 0.9 * serverRange
    distribution = {}
    startPositions = []
    droneList = []
    drones = 0
    grid_pts = copy.copy(gridPoints)

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
                if(math.sqrt((grid_pt.coordinate[1] - lastDronePos[1])**2 + (grid_pt.coordinate[0] - lastDronePos[0])**2) < serverRange):
                    startPos = grid_pt.coordinate
                    startPositions.append(startPos)
                    break

        # get distance and time for travel
        distance = math.sqrt((startPos[1] - serverLoc[1])**2 + (startPos[0] - serverLoc[0])**2)
        timeToTravel = distance / velocity
        timeToMap = tof - 2*timeToTravel
        if(timeToMap < 0):
            print("Drones inefficient to map such a large area. Increase battery :p")
            break

        # list of locations
        distribution[drones] = [[(-1, -1), serverLoc]]

        for grid_pt in gridPoints:
            if grid_pt.allocated:
                continue
            if math.sqrt((grid_pt.coordinate[1] - serverLoc[1])**2 + (grid_pt.coordinate[0] - serverLoc[0])**2) < serverRange and drones == 1 and timeToMap > 2:
                distribution[drones].append([grid_pt.index, grid_pt.coordinate])
                grid_pt.color = colors[drones-1]
                timeToMap -= timeToClick
                grid_pt.allocated = True
                allocated += 1
            elif drones != 1:
                for j in range(0,len(distribution[drones-1])):
                    print("dist {} ".format(distribution[drones-1][j]))
                    indices_, loc_ = distribution[drones-1][j]
                    if(math.sqrt((grid_pt.coordinate[1] - loc_[1])**2 + (grid_pt.coordinate[0] - loc_[0])**2) < serverRange and timeToMap > 2):
                        distribution[drones].append([grid_pt.index, grid_pt.coordinate])
                        grid_pt.color = colors[drones-1]
                        timeToMap -= timeToClick
                        grid_pt.allocated = True
                        allocated += 1
                        print(len(gridPoints))
                        break

        drone = Drone(drones, colors[drones-1], None, startPos)
        droneList.append(drone)

        # print time left for drone one
        print("Drone {}: \nStart Pos: {} \ndistance: {} \nTime taken: {}".format(drones,startPos,distance,tof - timeToMap))

    print(grid_pts)
    print(distribution)
    return droneList, distribution, grid_pts

def arrangeGrid(dist):
    arrangedGrid = {}

    # print("Transpose: {}".format(transpose))
    # print("Alternate grid: {}".format(arrangedGrid))

    for k,v in dist.items():
        locations = v
        transposeIndividual = {}
        alternateGrid = []
        start = locations[0][0]

        # get columns
        for listObj in locations:
            indices,loc = listObj
            transposeIndividual.setdefault(indices[0], []).append(listObj)

        # get alternate
        alternateGrid = alternate(transposeIndividual)

        # print(alternateGrid)

        arrangedGrid[k] = alternateGrid

    return arrangedGrid

def alternate(transpose):
    alternateGrid = []
    i = 0
    for k,v in transpose.items():
        if(i%2 == 0):
            for listObj in v:
                alternateGrid.append(listObj)
            i+=1
        else:
            for item in v[::-1]:
                alternateGrid.append(item)
            i+=1

    return alternateGrid

def add_transparency(self, distribution):
    for k, v in distribution.items():
        color = self.colors[k-1]
        for index, loc_ in v:
            self.grid_list.append([loc_[0],loc_[1],color,0.2])


def main():
    # parameters
    coordinates = [[0,0],[0,100],[100,100],[100,0]]
    overlap = 2.5
    imgWidth = 10
    imgHeight = 10
    timeOfFlight = 200
    serverLoc = (0,0)
    timeToClick = 2
    velocity = 15
    range_ = 30
    gridDimension = (100,100)
    colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (102, 0, 102), (255, 0, 255), (215, 220, 55), (205, 100, 155), (155, 200, 255)]

    # print grid array
    gridPoints = getGridPoints(coordinates, overlap, imgWidth, imgHeight)
    print(gridPoints)

    # get distribution
    drone_list, distribution, gridPoints = get_grid_distribution(gridPoints, timeOfFlight, timeToClick, velocity, serverLoc, range_, colors)
    print(distribution)
    # get arranged grid per drone
    arrangedDist = arrangeGrid(distribution)

    for k in arrangedDist.keys():
        arrangedDist[k].insert(0, [(-1, -1), serverLoc])
        arrangedDist[k].append([(-1, -1), serverLoc])

    for k,v in arrangedDist.items():
        drone_list[k-1].locations = v

    # generate grid
    # grid = GenGrid(gridDimension[0],gridDimension[1])
    # grid.set_distribution(distribution)
    # grid.initRectRender(imgWidth,imgHeight)

    # Simulation init

    # Ds = DroneSystem(arrangedDist,drones,velocity,timeToClick,serverLoc,gridDimension)
    sim = Simulator(arrangedDist, drone_list, velocity, timeToClick, serverLoc, gridDimension, gridPoints, imgWidth, imgHeight)
    sim.sim_loop()


if __name__== "__main__":
  main()