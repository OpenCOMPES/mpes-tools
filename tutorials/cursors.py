import numpy as np
import h5py
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons, Button

class cursors():
    def __init__(self,fig,ax,axis,x1,x2):
        self.rax_ce = plt.axes([0.52, 0.36, 0.05, 0.03])
        self.cb_ce = CheckButtons(self.rax_ce, ['Cursors_energy'], [False])
        # cb_roi.on_clicked(on_checkbox_change)
        self.cb_ce.on_clicked(self.integrate_checkbox)  
        self.fig=fig
        self.ax=ax
        self.axis=axis
        self.cursorlinev1=x1
        self.cursorlinev2=x2
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.active_cursor=None
        self.v1_pixel=int((self.cursorlinev1 - self.axis[0]) / (self.axis[-1] - self.axis[0]) * (self.axis.shape[0] - 1) + 0.5)
        self.v2_pixel=int((self.cursorlinev2 - self.axis[0]) / (self.axis[-1] - self.axis[0]) * (self.axis.shape[0] - 1) + 0.5)
    # def show(self):
    def integrate_checkbox(self,label):
        if label == 'Cursors_energy':
                if self.cb_ce.get_status()[0]:
                    self.Line1=self.ax.axvline(x=self.cursorlinev1, color='red', linestyle='--',linewidth=2, label='Vertical Line',picker=10)
                    self.Line2=self.ax.axvline(x=self.cursorlinev2, color='red', linestyle='--',linewidth=2, label='Vertical Line',picker=10)
                    plt.draw()
                    self.fig.canvas.draw()
                else:
                    
                    self.Line1.remove()
                    self.Line2.remove()
                    plt.draw()
                    self.fig.canvas.draw()
    def on_pick(self,event):
        
        if event.artist == self.Line1:
            self.active_cursor =self. Line1
        elif event.artist == self.Line2:
            self.active_cursor =self. Line2
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
            self.fig.canvas.draw()
            plt.draw()
            self.v1_pixel=int((self.cursorlinev1 - self.axis[0]) / (self.axis[-1] - self.axis[0]) * (self.axis.shape[0] - 1) + 0.5)
            self.v2_pixel=int((self.cursorlinev2 - self.axis[0]) / (self.axis[-1] - self.axis[0]) * (self.axis.shape[0] - 1) + 0.5)
            # print(self.v1_pixel,self.v2_pixel)
    def on_release(self,event):
        # global self.active_cursor
        self.active_cursor = None
    def give_position(self):
        return self.v1_pixel,self.v2_pixel
        
        # rax_ce = plt.axes([0.52, 0.36, 0.05, 0.03])
        # cb_ce = CheckButtons(rax_ce, ['Cursors_energy'], [False])
        # # cb_roi.on_clicked(on_checkbox_change)
        # cb_ce.on_clicked(integrate_checkbox)      
        # # Connect pick and motion events
        # self.fig.canvas.mpl_connect('pick_event', on_pick)
        # self.fig.canvas.mpl_connect('motion_notify_event', on_motion)
        # self.fig.canvas.mpl_connect('button_release_event', on_release)