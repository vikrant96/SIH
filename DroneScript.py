import math
import time
import threading
from Render import *
import cv2

class Simulator:
    def __init__(self, coordinates, drone_list, velocity, toc, server, grid, grid_pts, w, h):
        self.coordinates = coordinates
        self.drone_list = drone_list
        self.timeToClick = toc
        self.velocity = velocity
        self.serverLoc = server
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

    def sim_loop(self):
        t1 = time.time()
        time.sleep(0.1)
        for drone in self.drone_list:
            drone.renderer = self.render_object
            drone.update_grid = self.update_grid
        while True:
            print("next")
            dt = time.time() - t1;
            t1 = time.time()
            self.render_object.render_grid(self.grid_pts, self.width, self.height)
            for drone in self.drone_list:
                drone.update(dt)
            self.render_object.show()

#   class Drone (threading.Thread):
#     renderer = None
#     colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (102, 0, 102), (255, 0, 255)]
#
#     def __init__(self, droneID, gridLocation, gridDimension, server, velocity, toc):
#         threading.Thread.__init__(self)
#         self.droneID = droneID
#         self.gridLocation = gridLocation
#         self.renderer = GenGrid(gridDimension[0],gridDimension[1]);
#         self.serverLoc = server
#         self.velocity = velocity
#         self.toc = toc
#
#     def run(self):
#         # update function
#         for i in range(0,len(self.gridLocation)):
#             print("thread {} running".format(self.droneID))
#             if (i == 0):
#                 startPos = self.gridLocation[i][1]
#                 distance = math.sqrt((startPos[1] - self.serverLoc[1]) ** 2 + (startPos[0] - self.serverLoc[0]) ** 2)
#                 timeToReach = distance / self.velocity
#                 time.sleep(timeToReach)
#             else:
#                 nextPos = self.gridLocation[i][1]
#                 currPos = self.gridLocation[i-1][1]
#                 distance = math.sqrt((currPos[1] - nextPos[1]) ** 2 + (currPos[0] - nextPos[0]) ** 2)
#                 timeToFly = distance / self.velocity
#                 time.sleep(timeToFly + self.toc)
#
#             self.renderer.initCircleRender(self.gridLocation[i][1],self.colors[self.droneID-1])
#             cv2.imshow("map",self.renderer.map_image)
#             if(cv2.waitKey(0) == 32):
#                 break


