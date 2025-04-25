from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,QHBoxLayout
from superqt import QRangeSlider
from PyQt5.QtCore import Qt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys

class colorscale_slider(QWidget):
    def __init__(self, layout, imshow_artist,canvas, limits=None):
        super().__init__()

        self.im = imshow_artist
        self.canvas = canvas
        self.colorbar = None  # Optional: set this externally if you want to update a colorbar
        if limits is None:
            self.data = imshow_artist.get_array().data
            self.vmin, self.vmax = float(np.min(self.data)), float(np.max(self.data))
        else: 
            self.vmin,self.vmax= limits
        if self.vmin==self.vmax:
            self.vmax += 0.1
        self.cmin, self.cmax = 10, 1e5

        # Slider Widget
        slider_widget = QWidget()
        slider_layout = QVBoxLayout(slider_widget)

        self.slider = QRangeSlider(Qt.Vertical)
        self.slider.setFixedWidth(15)
        self.slider.setMinimum(int(1 * self.cmin))
        self.slider.setMaximum(int(1* self.cmax))
        self.slider.setValue([self.new_values(self.vmin), self.new_values(self.vmax)])
        # self.slider.valueChanged.connect(self.update_clim)
        self.slider.valueChanged.connect(lambda value: self.update_clim(value))

        self.label = QLabel(f"{self.vmin:.2f} to {self.vmax:.2f}")
        # self.label = QLabel(' ')
        slider_layout.addWidget(self.label)
        slider_layout.addWidget(self.slider)

        # New horizontal layout: slider left, canvas right
        h_container = QWidget()
        h_layout = QHBoxLayout(h_container)
        h_layout.addWidget(slider_widget)
        h_layout.addWidget(self.canvas)
        h_layout.addWidget(self.canvas, stretch=1)

        layout.insertWidget(0, h_container)

    def new_values(self, x):
        a = (self.cmax - self.cmin) / (self.vmax - self.vmin)
        b = self.vmax * self.cmin - self.vmin * self.cmax
        return int(a * x + b)

    def inverse(self, x):
        a = (self.cmax - self.cmin) / (self.vmax - self.vmin)
        b = self.vmax * self.cmin - self.vmin * self.cmax
        return (x - b) / a

    def update_clim(self, value):
        vmin, vmax = self.inverse(value[0]), self.inverse(value[1])
        self.im.set_clim(vmin, vmax)
        self.label.setText(f" {vmin:.2f} to {vmax:.2f}")
        if self.colorbar:
            self.colorbar.update_normal(self.im)
        self.canvas.draw_idle()
