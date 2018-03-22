import math
import time
import threading
from Render import *
import cv2

class DroneSystem:
    coordinates = {}
    numberOfDrones = 0
    velocity = 0
    serverLoc = ()
    gridDimensions = ()
    timeToClick = 0
    start = True
    startTime = 0
    drones = []

    def __init__(self,coordinates,drones,velocity,toc,server,grid):
        self.coordinates = coordinates
        self.numberOfDrones = drones
        self.timeToClick = toc
        self.velocity = velocity
        self.serverLoc = server
        self.gridDimension = grid
        #Initialize renderer and render all the drones at the server location
        self.initialize()

    def initialize(self):
        self.startTime = time.time()

        #start drones for mapping
        for i in range(0, self.numberOfDrones):
            self.drones.append(Drone(i + 1, self.coordinates[i + 1], self.gridDimension, self.serverLoc, self.velocity, self.timeToClick))

        #start threads
        for t in self.drones:
            t.start()


    def returnDrone(self,drone):
        print("Drone {} has returned to base!".format(drone))


class Drone (threading.Thread):
    renderer = None
    colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (102, 0, 102), (255, 0, 255)]

    def __init__(self, droneID, gridLocation, gridDimension, server, velocity, toc):
        threading.Thread.__init__(self)
        self.droneID = droneID
        self.gridLocation = gridLocation
        self.renderer = GenGrid(gridDimension[0],gridDimension[1]);
        self.serverLoc = server
        self.velocity = velocity
        self.toc = toc

    def run(self):
        # update function
        for i in range(0,len(self.gridLocation)):
            print("thread {} running".format(self.droneID))
            if (i == 0):
                startPos = self.gridLocation[i][1]
                distance = math.sqrt((startPos[1] - self.serverLoc[1]) ** 2 + (startPos[0] - self.serverLoc[0]) ** 2)
                timeToReach = distance / self.velocity
                time.sleep(timeToReach)
            else:
                nextPos = self.gridLocation[i][1]
                currPos = self.gridLocation[i-1][1]
                distance = math.sqrt((currPos[1] - nextPos[1]) ** 2 + (currPos[0] - nextPos[0]) ** 2)
                timeToFly = distance / self.velocity
                time.sleep(timeToFly + self.toc)

            self.renderer.initCircleRender(self.gridLocation[i][1],self.colors[self.droneID-1])
            cv2.imshow("map",self.renderer.map_image)
            #cv2.waitKey(0)
