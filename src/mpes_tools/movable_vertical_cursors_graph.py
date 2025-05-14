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
        
        def find_nearest_index(array, value):
            idx = (np.abs(array - value)).argmin()
            return idx
        self.v1_pixel=find_nearest_index(self.axis, self.cursorlinev1)
        self.v2_pixel=find_nearest_index(self.axis, self.cursorlinev2)

        
        self.Line1=self.ax.axvline(x=self.cursorlinev1, color='red', linestyle='--',linewidth=2, label='Vertical Line',picker=10)
        self.Line2=self.ax.axvline(x=self.cursorlinev2, color='red', linestyle='--',linewidth=2, label='Vertical Line',picker=10)
        self.ax.figure.canvas.draw()
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
            self.ax.figure.canvas.draw()
            plt.draw()
            def find_nearest_index(array, value):
                idx = (np.abs(array - value)).argmin()
                return idx
            self.v1_pixel=find_nearest_index(self.axis, self.cursorlinev1)
            self.v2_pixel=find_nearest_index(self.axis, self.cursorlinev2)
            
            # print(self.v1_pixel,self.v2_pixel)
    def on_release(self,event):
        # global self.active_cursor
        self.active_cursor = None    
    def remove(self):
        self.cursorlinev1= self.Line1.get_xdata()[0]
        self.cursorlinev2= self.Line2.get_xdata()[0]
        self.Line1.remove()
        self.Line2.remove()
        self.ax.figure.canvas.draw()
    def redraw(self):
        # print(self.cursorlinev1,self.cursorlinev2)
        self.Line1=self.ax.axvline(x=self.cursorlinev1, color='red', linestyle='--',linewidth=2, label='Vertical Line',picker=10)
        self.Line2=self.ax.axvline(x=self.cursorlinev2, color='red', linestyle='--',linewidth=2, label='Vertical Line',picker=10)
        self.ax.figure.canvas.draw()
    def cursors(self):
        return [self.v1_pixel,self.v2_pixel]   
    def move(self):
        self.Line1.set_xdata([self.cursorlinev1, self.cursorlinev1])
        self.Line2.set_xdata([self.cursorlinev2, self.cursorlinev2])
        self.ax.figure.canvas.draw()

        