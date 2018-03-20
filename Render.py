import cv2
import numpy as np


class GenGrid:
    def __init__(self, width, height):
        self.map_width = width
        self.map_height = height
        self.width_ratio = 0.0
        self.height_ratio = 0.0
        self.map_image = None
        self.lat_long_mat = None
        self.grid_width = None
        self.grid_height = None
        self.grid_list = []
        self.colors = [(0,0,255),(0,255,0),(255,0,0),(102,0,102),(255,0,255)]

    def _set_map_image(self, path):
        self.map_image = cv2.imread(path)

    def _show_map(self):
        cv2.imshow("map", self.map_image)
        cv2.waitKey()
        cv2.destroyAllWindows()

    def _draw_rect_on_map(self, x, y, w, h, color, alpha):
        x = x - w/2;
        y = y - h/2;
        overlay = self.map_image.copy()
        output = self.map_image.copy()
        cv2.rectangle(overlay, (int(x * self.width_ratio), int(y * self.height_ratio)),
                      (int((x + w) * self.width_ratio), int((y + h) * self.height_ratio)), color, -1)
        cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
        self.map_image = output

    def render_grid(self, path, grid_list, w, h):
        self._set_map_image(path)
        (height, width, channel) = self.map_image.shape
        self.width_ratio = width / float(self.map_width)
        self.height_ratio = height / float(self.map_height)
        for x, y, color, factor_of_completion in grid_list:
            self._draw_rect_on_map(x, y, w, h, color, factor_of_completion)
        self._show_map()

    def set_distribution(self,distribution):
        for k,v in distribution.items():
            color = self.colors[k-1]
            for loc_ in v:
                self.grid_list.append([loc_[0],loc_[1],color,0.5])

    def initRender(self,w,h):
        self.render_grid("./img.png", self.grid_list, w, h)

