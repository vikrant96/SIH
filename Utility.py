
class GridPoint:
    def __init__(self, index, coordinate, factor_of_completion, color, allocated):
        self.index = index
        self.coordinate = coordinate
        self.color = color
        self.foc = factor_of_completion
        self.allocated = allocated

    def __str__(self):
        return "{0},{1},{2},{3},{4}".format(self.index, self.coordinate, self.color, self.foc, self.allocated)
