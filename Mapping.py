import math;
import copy;
from Render import *

class XYCoordinate:
    x = 0;
    y = 0;

    def __init__(self,x_coordinate,y_coordinate):
        self.x = x_coordinate;
        self.y = y_coordinate;

    def getDistance(self,xycoordinate):
        return math.sqrt((xycoordinate.x - self.x)**2 + (xycoordinate.y - self.y));


def getGridPoints(coordinates,overlap,imgWidth,imgHeight):
    #get length and breadth of the rectangle
    l = coordinates[2][0] - coordinates[1][0];
    b = coordinates[1][1] - coordinates[0][1];

    #get number of rectangles in l and b as n1 and n2 resp
    n1 = math.ceil((l - overlap) / (imgWidth - overlap));
    n2 = math.ceil((b - overlap) / (imgHeight - overlap));

    #get new overlaps
    d1 = (n1*imgWidth - l) / (n1 - 1);
    d2 = (n2*imgHeight - b) / (n2 - 1);

    #print new overlaps
    print("New overlap in x and y resp is: {}{:5}".format(d1,d2));

    #calculate grids
    gridPoints = [];

    #rows
    for i in range(0,n2):
        for j in range(0,n1):
            x = coordinates[0][0] + imgWidth/2 + j*(imgWidth - d1);
            y = coordinates[0][1] + imgHeight/2 + i*(imgHeight - d2);
            gridPoints.append([x,y]);

    return gridPoints;

def getGridDistribution(gridPoints, timeOfFlight, timeToClick, velocity, serverLoc, serverRange):
    #get new range and tof based on buffer %
    #considering buffer of 10%
    tof = 0.9 * timeOfFlight;
    serverRange = 0.9 * serverRange;
    distribution = {};
    startPositions = [];
    drones = 0;
    while(len(gridPoints) != 0):
        gridPointsCpy = copy.deepcopy(gridPoints);
        drones+=1;
        startPos = gridPointsCpy[0];

        #set start location for first drone
        if(drones == 1):
            for loc in gridPointsCpy:
                if(math.sqrt((loc[1] - serverLoc[1])**2 + (loc[0] - serverLoc[0])**2) < serverRange):
                    startPos = loc;
                    startPositions.append(startPos);
                    break;

        #set start location for rest of the drones
        if(drones > 1):
            lastDronePos = startPositions[-1];
            for loc in gridPointsCpy:
                if(math.sqrt((loc[1] - lastDronePos[1])**2 + (loc[0] - lastDronePos[0])**2) < serverRange):
                    startPos = loc;
                    startPositions.append(startPos);
                    break;

        #get distance and time for travel
        distance = math.sqrt((startPos[1] - serverLoc[1])**2 + (startPos[0] - serverLoc[0])**2)
        timeToTravel = distance / velocity;
        timeToMap = tof - 2*timeToTravel;
        if(timeToMap < 0):
            print("Drones inefficient to map such a large area. Increase battery :p");
            break;
        distribution[drones] = [];

        for i in range(0,len(gridPointsCpy)):
            loc = gridPointsCpy[i];
            if(math.sqrt((loc[1] - serverLoc[1])**2 + (loc[0] - serverLoc[0])**2) < serverRange and drones == 1 and timeToMap > 2):
                distribution[drones].append(loc);
                timeToMap -= timeToClick;
                gridPoints.remove(loc);
            elif(drones!=1):
                for loc_ in distribution[drones-1]:
                    if(math.sqrt((loc[1] - loc_[1])**2 + (loc[0] - loc_[0])**2) < serverRange and timeToMap > 2):
                        distribution[drones].append(loc);
                        timeToMap -= timeToClick;
                        gridPoints.remove(loc);
                        break;

        #print time left for drone one
        print("Drone {}: \nStart Pos: {} \ndistance: {} \nTime taken: {}".format(drones,startPos,distance,tof - timeToMap));

    print(distribution);
    return distribution;


def main():
    coordinates = [[0,0],[0,100],[100,100],[100,0]];

    #print grid array
    gridPoints = getGridPoints(coordinates,2.5,10,10);
    print(gridPoints);

    #get distribution
    distribution = getGridDistribution(gridPoints,200,2,15,[50,0],30);

    #generate grid
    grid = GenGrid(100, 100);
    grid.set_distribution(distribution);
    grid.initRender(10,10);


if __name__== "__main__":
  main()