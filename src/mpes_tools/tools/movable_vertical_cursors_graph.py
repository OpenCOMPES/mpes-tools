# movable_cursors.py

import numpy as np
import matplotlib.pyplot as plt

class MovableCursors:
    def __init__(self, ax):
        self.ax = ax
        line = self.ax.lines[0] 
        self.active_cursor=None

        self.axis = line.get_xdata()
        
        self.cursorlinev1=self.axis[int(len(self.axis)/4)]
        self.cursorlinev2=self.axis[int(3*len(self.axis)/4)]
        # Create initial cursors (at the middle of the plot)
        # self.v1_cursor = self.ax.axvline(x=5, color='r', linestyle='--', label='Cursor X')
        # self.v2_cursor = self.ax.axhline(y=0, color='g', linestyle='--', label='Cursor Y')
        
        self.Line1=self.ax.axvline(x=self.cursorlinev1, color='red', linestyle='--',linewidth=2, label='Vertical Line',picker=10)
        self.Line2=self.ax.axvline(x=self.cursorlinev2, color='red', linestyle='--',linewidth=2, label='Vertical Line',picker=10)

        # Connect mouse events for the canvas of the axes
        self.ax.figure.canvas.mpl_connect('pick_event', self.on_pick)
        self.ax.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.ax.figure.canvas.mpl_connect('button_release_event', self.on_release)

    def on_pick(self,event):
        
        if event.artist == self.Line1:
            self.active_cursor =self.Line1
        elif event.artist == self.Line2:
            self.active_cursor =self.Line2
    # self.active_cursor=None
    def on_motion(self,event):
        
        if self.active_cursor is not None and event.inaxes == self.ax:
            if self.active_cursor == self.Line1:
                self.Line1.set_xdata([event.xdata, event.xdata])
                self.cursorlinev1= event.xdata
            elif self.active_cursor == self.Line2:
                self.Line2.set_xdata([event.xdata, event.xdata])
                self.cursorlinev2= event.xdata
            # print(dot1.center) 
            # print(self.cursorlinev1,self.cursorlinev2)
            self.ax.figure.canvas.draw()
            plt.draw()
            def find_nearest_index(array, value):
                idx = (np.abs(array - value)).argmin()
                return idx
            self.v1_pixel=find_nearest_index(self.axis, self.cursorlinev1)
            self.v2_pixel=find_nearest_index(self.axis, self.cursorlinev2)
            
            # self.v1_pixel=int((self.cursorlinev1 - self.axis[0]) / (self.axis[-1] - self.axis[0]) * (self.axis.shape[0] - 1) + 0.5)
            # self.v2_pixel=int((self.cursorlinev2 - self.axis[0]) / (self.axis[-1] - self.axis[0]) * (self.axis.shape[0] - 1) + 0.5)
            print(self.v1_pixel,self.v2_pixel)
            
            # print(self.v1_pixel,self.v2_pixel)
    def on_release(self,event):
        # global self.active_cursor
        self.active_cursor = None    
    def remove(self):
        self.cursorlinev1= self.Line1.get_xdata()[0]
        self.cursorlinev2= self.Line2.get_xdata()[0]
        self.Line1.remove()
        self.Line2.remove()
        # plt.draw()
        self.ax.figure.canvas.draw()
        
    def redraw(self):
        # print(self.cursorlinev1,self.cursorlinev2)
        self.Line1=self.ax.axvline(x=self.cursorlinev1, color='red', linestyle='--',linewidth=2, label='Vertical Line',picker=10)
        self.Line2=self.ax.axvline(x=self.cursorlinev2, color='red', linestyle='--',linewidth=2, label='Vertical Line',picker=10)
        # plt.draw()
        self.ax.figure.canvas.draw()
    def cursors(self):
        return [self.v1_pixel,self.v2_pixel]        