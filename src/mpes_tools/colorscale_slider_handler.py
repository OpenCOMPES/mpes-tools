from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,QHBoxLayout,QGridLayout,QLineEdit,QCheckBox
from superqt import QRangeSlider
from PyQt5.QtCore import Qt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys

class colorscale_slider(QWidget):
    def __init__(self, layout, imshow_artist,canvas, limits=None):
        super().__init__()
        self.case=False
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
        if self.vmax<10:
            self.cmin, self.cmax = 10*self.vmin, 10*self.vmax
            print(self.cmin, self.cmax)
            self.case=True
        else:
            self.cmin, self.cmax=self.vmin,self.vmax
        # Slider Widget
        slider_widget = QWidget()
        slider_layout = QVBoxLayout(slider_widget)
        
        self.checkbox_autoscale = QCheckBox("Auto")
        self.checkbox_autoscale.stateChanged.connect(self.autoscale)
        
        self.input_vmax = QLineEdit()
        self.input_vmax.setPlaceholderText("Value")
        self.input_vmax.setFixedWidth(40)
        self.input_vmax.editingFinished.connect(self.value_change_vmax)
        self.input_vmin = QLineEdit()
        self.input_vmin.setPlaceholderText("Value")
        self.input_vmin.setFixedWidth(40)
        self.input_vmin.editingFinished.connect(self.value_change_vmin)
        self.slider = QRangeSlider(Qt.Vertical)
        self.slider.setFixedWidth(15)
        self.slider.setMinimum(int(1 * self.cmin))
        self.slider.setMaximum(int(1.5* self.cmax))
        self.slider.setValue([float(self.vmin),float(self.vmax)])
        if self.case :
            self.slider.setValue([self.new_values(self.vmin), self.new_values(self.vmax)])
        self.slider.valueChanged.connect(lambda value: self.update_clim(value))
        # self.vmin_label = QLabel(f"{self.vmin:.2e}")
        # self.vmax_label = QLabel(f"{self.vmax:.2e}")
        self.vmin_label = QLabel("")
        self.vmax_label = QLabel("")
        slider_layout.addWidget(self.checkbox_autoscale)
        slider_layout.addWidget(self.input_vmax)
        slider_layout.addWidget(self.vmax_label)
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.vmin_label)
        slider_layout.addWidget(self.input_vmin)

        # New horizontal layout: slider left, canvas right
        h_container = QWidget()
        h_layout = QHBoxLayout(h_container)
        h_layout.addWidget(slider_widget)
        h_layout.addWidget(self.canvas)
        h_layout.addWidget(self.canvas, stretch=1)
        if isinstance(layout, QGridLayout):
            layout.addWidget(h_container,0,0)
        else:
            layout.insertWidget(0, h_container)
    def autoscale(self,state):
        if self.checkbox_autoscale.isChecked():
            self.data = self.im.get_array().data
            self.vmin, self.vmax=float(np.min(self.data)), float(np.max(self.data))
            self.im.set_clim(self.vmin, self.vmax)
            self.slider.setValue([self.vmin,self.vmax])
            self.slider.setMaximum(self.vmax)
            self.slider.setMinimum(self.vmin)
            self.canvas.draw_idle()
    def value_change_vmax(self):
        value=float(self.input_vmax.text())
        self.vmax=value
        self.cmax=self.vmax
        if self.case :
            self.cmax =  10*self.vmax
        self.slider.setMaximum(int(1.0* self.cmax))
    def value_change_vmin(self):
        value=float(self.input_vmin.text())
        self.vmin=value
        self.cmin=self.vmin
        if self.case :
            self.cmin= 10*self.vmin
        self.slider.setMinimum(int(1 * self.cmin))
    def new_values(self, x):
        a = (self.cmax - self.cmin) / (self.vmax - self.vmin)
        b = (self.vmax * self.cmin - self.vmin * self.cmax)/(self.vmax-self.vmin)
        return int(a * x + b)

    def inverse(self, x):
        a = (self.cmax - self.cmin) / (self.vmax - self.vmin)
        b = (self.vmax * self.cmin - self.vmin * self.cmax)/(self.vmax-self.vmin)
        return (x - b) / a

    def update_clim(self, value):
        vmin, vmax = value
        if self.case:
            vmin, vmax = self.inverse(value[0]), self.inverse(value[1])
        self.im.set_clim(vmin, vmax)
        self.vmin_label.setText(f" {vmin:.2e}")
        self.vmax_label.setText(f"{vmax:.2e}")
        if self.colorbar:
            self.colorbar.update_normal(self.im)
        self.canvas.draw_idle()
