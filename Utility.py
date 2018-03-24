import math


def get_distance(pt1, pt2):
    return math.sqrt((pt1[1] - pt2[1]) ** 2 + (pt1[0] - pt2[0]) ** 2)

class GridPoint:
    def __init__(self, index, coordinate, factor_of_completion, color, allocated):
        self.index = index
        self.coordinate = coordinate
        self.color = color
        self.foc = factor_of_completion
        self.allocated = allocated
        self.distance_from_server = None

    def __str__(self):
        return "{0},{1},{2},{3},{4}".format(self.index, self.coordinate, self.color, self.foc, self.allocated)

    def set_distance_from_server(self, server_loc):
        self.distance_from_server = get_distance(server_loc, self.coordinate)
