import numpy as np
import h5py
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import CheckButtons, Button
from scipy.ndimage import rotate
import h5py
# import mplcursors
from matplotlib.widgets import Slider, Cursor, SpanSelector


class update_color():
    def __init__(self,im,fig,ax):
        # self.slider_plot=s
        self.im=im
        self.fig=fig
        ax_position=ax.get_position()
        # print(ax.get_position())
        x0, y0, width, height = ax_position.bounds

        # Print the coordinates
        # print("Lower-left coordinate (x0, y0):", x0, y0)
        # print("Upper-right coordinate (x1, y1):", x0 + width, y0 + height)
        self.cbar = plt.colorbar(im, ax=ax)
        # self.cbar.ax.set_position([0.43, 0.31, 0.01, 0.8])
        # self.ax_slider = fig.add_axes([0.42, 0.56, 0.01, 0.30], facecolor='lightgoldenrodyellow')
        self.cbar.ax.set_position([x0 + width +0.013, y0-0.08, 0.01, 0.5])
        self.ax_slider = fig.add_axes([x0 + width +0.006, y0 + 0.03, 0.01, 0.30], facecolor='lightgoldenrodyellow')
        self.slider_plot = Slider(self.ax_slider, '', -1.5, 1.5, valinit=0.0,valstep=0.01,orientation='vertical')
        self.original_vmax = im.norm.vmax
        # self.slider_plot.on_changed(self.update)
    def update(self,val):
        # print('whathbdjfs')
        self.im.norm.vmax = 10**(self.slider_plot.val) * self.original_vmax
        
        # self.fig.canvas.draw_idle()
    def slider (self):
        self.slider_plot.on_changed(self.update)
    def sprint(self,val):
        print('somethign', self.slider_plot)
        # self.fig.canvas.draw_idle()
        # print('slider')    
        
