import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QDialog, QLineEdit, QPushButton, QHBoxLayout, QLabel,QCheckBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class AxisEditor:
    def __init__(self, canvas, is2d=None):
        self.canvas = canvas
        self.ax = canvas.figure.axes[0]
        self.cid = self.canvas.mpl_connect('button_press_event', self.on_click)
        self.activation_x=False
        self.activation_y=False
        self.is2d=is2d
        if is2d is not None:
            self.original_x=self.ax.get_xlim()
            self.original_y=self.ax.get_ylim()

    def get_limits(self,ax):
        all_x=[]
        all_y=[]
        if len(ax.lines)>0:
            for line in ax.lines:
                x = line.get_xdata()
                y = line.get_ydata()
    
            if len(x) > 0 and len(y) > 0:
                all_x.append(x)
                all_y.append(y)
        x_all = np.concatenate(all_x)
        y_all = np.concatenate(all_y)
        xlim = [np.min(x_all), np.max(x_all)]
        ylim = [np.min(y_all), np.max(y_all)]    
        return xlim, ylim
    def on_click(self, event):
        
        if not event.dblclick:
            return
        bbox = self.ax.get_window_extent(self.canvas.renderer)

        margin = 30
        x, y = event.x, event.y
        near_xaxis = bbox.y0 - margin < y < bbox.y0 + margin
        near_yaxis = bbox.x0 - margin < x < bbox.x0 + margin

        if near_xaxis:
            axis = "x"
            old_min, old_max = self.ax.get_xlim()
            self.activation_x=True
        elif near_yaxis:
            axis = "y"
            old_min, old_max = self.ax.get_ylim()
            self.activation_y=True
        else:
            return

        dialog = MinMaxDialog(axis, old_min, old_max)
        if dialog.exec_():
            new_min, new_max = dialog.get_values()
            if not dialog.isitautoscaled():
                if new_min is not None and new_max is not None:
                    if axis == "x":
                        self.ax.set_xlim(new_min, new_max)
                    else:
                        self.ax.set_ylim(new_min, new_max)
                    self.canvas.draw_idle()
            else:
                if axis == "x":
                    self.activation_x=False
                    if self.is2d is not None:
                        self.ax.set_xlim(self.original_x)
                    else:
                        self.ax.set_xlim(self.get_limits(self.ax)[0])
                else:
                    self.activation_y=False
                    if self.is2d is not None:
                        self.ax.set_xlim(self.original_y)
                    else:
                        self.ax.set_xlim(self.get_limits(self.ax)[1])

                self.canvas.draw_idle()
    def activation_x(self):
        return self.activation_x
    def activation_y(self):
        return self.activation_y
class MinMaxDialog(QDialog):
    def __init__(self, axis_name, old_min, old_max):
        super().__init__()
        self.setWindowTitle(f"Set {axis_name}-axis limits")
        layout = QVBoxLayout()
        
        self.autoscale=False
        
        self.checkbox = QCheckBox("Autoscale")
        self.checkbox.stateChanged.connect(self.checkbox_autoscale)
        layout.addWidget(self.checkbox)
        self.min_edit = QLineEdit(str(old_min))
        self.max_edit = QLineEdit(str(old_max))

        layout.addWidget(QLabel(f"{axis_name}-axis min:"))
        layout.addWidget(self.min_edit)
        layout.addWidget(QLabel(f"{axis_name}-axis max:"))
        layout.addWidget(self.max_edit)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def checkbox_autoscale(self,state):
        if self.checkbox.isChecked():
            self.autoscale=True
        else:
            self.autoscale=False
    def isitautoscaled(self):
        return self.autoscale
    def get_values(self):
        try:
            return float(self.min_edit.text()), float(self.max_edit.text())
        except ValueError:
            return None, None
    

