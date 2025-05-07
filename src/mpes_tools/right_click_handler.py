from PyQt5.QtWidgets import QMenu
from matplotlib.backend_bases import MouseButton
from PyQt5.QtGui import QCursor

class RightClickHandler:
    def __init__(self, canvas, ax, show_popup=None):
        self.canvas = canvas
        self.ax = ax
        self.show_popup=show_popup

    def on_right_click(self, event):
        if event.button == MouseButton.RIGHT and event.inaxes == self.ax:
            if self.show_popup:
                self.show_popup(self.canvas,self.ax)