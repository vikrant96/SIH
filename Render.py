import cv2
import numpy as np


class GenGrid:
    def __init__(self, width, height, path = './img.png'):
        self.map_width = width
        self.map_height = height
        self.path = path
        self.width_ratio = 0.0
        self.height_ratio = 0.0
        self.map_image = None
        self.output = None
        self.lat_long_mat = None
        self.grid_width = None
        self.grid_height = None
        self.grid_list = []

    def _set_map_image(self):
        self.map_image = cv2.imread(self.path)

    def show(self):
        if isinstance(self.output, type(None)):
            return
        cv2.waitKey(1)
        cv2.imshow("map", self.output)
        self.output = None


    def _draw_rect_on_map(self, x, y, w, h, color, alpha):
        x = x - w/2
        y = y - h/2
        if isinstance(self.output, type(None)):
            self.output = self.map_image.copy()
        overlay = self.output.copy()
        cv2.rectangle(overlay, (int(x * self.width_ratio), int(y * self.height_ratio)),
                      (int((x + w) * self.width_ratio), int((y + h) * self.height_ratio)), color, -1)
        cv2.addWeighted(overlay, alpha, self.output, 1 - alpha, 0, self.output)

    def render_grid(self, grid_list, w, h):
        if isinstance(self.map_image, type(None)):
            self._set_map_image()

        (height, width, channel) = self.map_image.shape
        self.width_ratio = width / float(self.map_width)
        self.height_ratio = height / float(self.map_height)
        for grid_pt in grid_list:
            self._draw_rect_on_map(grid_pt.coordinate[0], grid_pt.coordinate[1], w, h, grid_pt.color, grid_pt.foc)

    def render_points(self, point_list):
        """
        point_list is List of list, containg x,y, color where color is in the form (0,0,0)
        """
        (height, width, channel) = self.map_image.shape
        self.width_ratio = width / float(self.map_width)
        self.height_ratio = height / float(self.map_height)
        if isinstance(self.output, type(None)):
            self.output = self.map_image.copy()
        for point_x, point_y, color in point_list:
            cv2.circle(self.output, (int(point_x * self.width_ratio), int(point_y * self.height_ratio)), 3, color, 3)
