import numpy as np
import h5py
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import CheckButtons, Button
from scipy.ndimage import rotate
import h5py
from matplotlib.widgets import Slider, Cursor, SpanSelector
# import mplcursors
from scipy.optimize import curve_fit
from matplotlib.widgets import Slider, Cursor, SpanSelector
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Circle
from save_data import save_data
from matplotlib.widgets import  Button, CheckButtons
from datetime import datetime
from cursors import cursors
from lmfit.models import ExpressionModel,Model
from bi_exponential_second import fit
class FFT_cursor:
    # from matplotlib.widgets import CheckButtons, Button
    # %matplotlib qt
    
    def __init__(self,data,plc,fig,ax,name): 
        # print('saveinit')
        self.fig=fig
        self.rax_ce = plt.axes([plc[0]-0.05, plc[1], 0.05, 0.03])
        # self.rax_ce = plt.axes([0.52, 0.36, 0.05, 0.03])
        # self.rax_ce = plt.axes([0.5,0.5, 0.05, 0.03])
        self.cb_ce = CheckButtons(self.rax_ce, ['Cursors'], [False])
        # cb_roi.on_clicked(on_checkbox_change)
        self.cb_ce.on_clicked(self.integrate_checkbox)  
        
       
        
        self.fit_twosin= True
        
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.data_or=data
        # self.axis=self.data_or[:,0]
        self.axis=data[:,0]
        self.cursorlinev1=self.axis[0]
        self.cursorlinev2=self.axis[-1]
        # self.data=data
        self.name=name
        self.Line1=None
        self.Line2=None
        # self.x1=x1
        # self.x2=x2
        self.ax=ax
        self.active_cursor=None
        self.v1_pixel=int((self.cursorlinev1 - self.axis[0]) / (self.axis[-1] - self.axis[0]) * (self.axis.shape[0] - 1) + 0.5)
        self.v2_pixel=int((self.cursorlinev2 - self.axis[0]) / (self.axis[-1] - self.axis[0]) * (self.axis.shape[0] - 1) + 0.5)
        
        self.data=self.data_or[self.v1_pixel:self.v2_pixel,:]
        self.size=[0.028,0.025]
        
        self.save_button = self.fig.add_axes( [plc[0]+self.size[0],plc[1]]+self.size)
        # self.save_button =plt.axes([0.78, 0.02, 0.1, 0.06])
        
        # # self.save_button=self.fig.add_axes([0.78, 0.02, 0.1, 0.06])
        # self.button_save = Button(self.save_button, 'fft')
        # self.button_save.on_clicked(lambda event: self.fft_data(event))
        self.size2=[0.08,0.04]
        self.fit_button = self.fig.add_axes( [plc[0]+self.size2[0],plc[1]]+self.size2)
        # # self.save_button =plt.axes([0.78, 0.02, 0.1, 0.06])
        
        # self.save_button=self.fig.add_axes([0.78, 0.02, 0.1, 0.06])
        self.button_fit = Button(self.fit_button, 'fit')
        self.button_fit.on_clicked(lambda event: self.fit(event))
        # self.button_save.on_clicked(lambda event: self.test_button(event))
        # plt.show()
        self.sub=None
        # self.name=name
        # print(self.data.shape,self.data2.shape)
        self.fit_plot=np.zeros_like(self.data[:,1])
        # self.fig1, self.axs = plt.subplots(1, 1, figsize=(12, 5))
        self.fig1 =[]
        self.axs =[]
        print('self.axissize=',self.axis.shape[0])
        print('self.axis=',self.axis)
    
        N=20000
        new_axis=np.linspace(self.data[:,0].min(),self.data[:,0].max(),N)
        new_data=np.interp(new_axis,self.data[:,0],self.data[:,1])
        
        # fft_lev=fft(new_axis, new_data, [0.08,0.96],self.fig, self.ax[1],'linewidth')
        # n1=4*len(fft_result)
        n1=4*len(new_axis)
        fft_result = np.fft.fft(new_data,n1)
        frequencies = np.fft.fftfreq(n1, d=0.001*(new_axis[1] - new_axis[0]))
        M=2
        self.ax[1].clear()
        self.ax[1].plot(frequencies[M:int(len(frequencies)/2)], np.abs(fft_result)[M:int(len(frequencies)/2)])
        self.ax[1].set_xlim(0,5)
        self.ax[1].set_ylim(-0.01, 1.2*np.max(np.abs(fft_result)[M:int(len(frequencies)/2)]))
        self.ax[1].set_xlabel('Frequency (THz)',fontsize=16,labelpad=14)
        self.ax[1].set_ylabel('Magnitude (a.u.)',fontsize=16,labelpad=14)
        self.ax[1].tick_params(axis='both',labelsize=16)
        # s_fft=save_data(new_frequencies[0:int(len(new_frequencies)/2)],np.abs(new_fft_result)[0:int(len(new_frequencies)/2)] ,self.name+'_fft', [0.2,0.46],self.fig)
        s_fft=save_data(frequencies[0:int(len(frequencies)/2)],np.abs(fft_result)[0:int(len(frequencies)/2)] ,self.name+'_fft', [0.2,0.46],self.fig)
        plt.grid()
        plt.show()
        
    def fit(self,event):
        def osc_exp(x,A,T,phi,tau):
            return A*np.exp(-x/tau)*np.sin(2*np.pi*x/T+phi)
        print(self.data)
        p0=[self.data[:,1].max()-self.data[:,1].min(),1000,0,500]
        # self.ax[0].plot(self.data[:,0], osc_exp(self.data[:,0],*p0),label='fitttt')
        # plt.show()    
        print(p0)
        params, covariance = curve_fit(osc_exp, self.data[:,0], self.data[:,1], p0)
        self.ax[0].plot(self.data[:,0], osc_exp(self.data[:,0],*params),label='fit')
        self.ax[0].legend()
        plt.show()    
        print([params[0],params[1],params[2],params[3]])   
        print([np.sqrt(np.diag(covariance))[0],np.sqrt(np.diag(covariance))[1],np.sqrt(np.diag(covariance))[2],np.sqrt(np.diag(covariance))[3]])
        print('frequency=', 1/params[1])
        fig,ax=  plt.subplots(1, 1, figsize=(12, 8))
        
        ax.plot(self.data_or[:,0],self.data_or[:,1] ,label='data',linewidth=4)
        ax.plot(self.data[:,0], osc_exp(self.data[:,0],*params),label='fit',color='red',linewidth=4)
        ax.set_xlabel('time (fs)',fontsize=28,labelpad=14)
        ax.set_ylabel('signal -background (eV)',fontsize=28,labelpad=14)
        ax.tick_params(axis='both',labelsize=20)
        ax.tick_params(axis='both', direction='in', length=10, width=3)
        # ax.set_xlabel('time (ps)',fontsize=28,labelpad=14)
        # ax.tick_params(axis='both',labelsize=14)

        plt.gca().xaxis.set_tick_params(top=True, labeltop=False)  # Enable ticks on the top
        plt.gca().yaxis.set_tick_params(right=True, labelright=False)  # Enable ticks on the right
        y_ticks = plt.gca().get_yticks()
        plt.yticks(y_ticks[::1]) 
       
        ax.spines['top'].set_linewidth(3)
        ax.spines['right'].set_linewidth(3)
        ax.spines['bottom'].set_linewidth(3)
        ax.spines['left'].set_linewidth(3)
        ax.legend(fontsize=20)
        
       
    def integrate_checkbox(self,label):
        if label == 'Cursors':
                if self.cb_ce.get_status()[0]:
                    self.Line1=self.ax[0].axvline(x=self.cursorlinev1, color='red', linestyle='--',linewidth=2, label='Vertical Line',picker=10)
                    self.Line2=self.ax[0].axvline(x=self.cursorlinev2, color='red', linestyle='--',linewidth=2, label='Vertical Line',picker=10)
                    plt.draw()
                    self.fig.canvas.draw()
                else:
                    
                    self.Line1.remove()
                    self.Line2.remove()
                    plt.draw()
                    self.fig.canvas.draw()
    def on_pick(self,event):
        
        if event.artist == self.Line1:
            self.active_cursor =self.Line1
        elif event.artist == self.Line2:
            self.active_cursor =self.Line2
    # self.active_cursor=None
    def on_motion(self,event):
        
        if self.active_cursor is not None and event.inaxes == self.ax[0]:
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
            # self.v1_pixel_1=int((self.cursorlinev1 - self.data[0,0]) / (self.data[-1,0] - self.data[0:0]) * (self.data[:,0].shape[0] - 1) + 0.5)
            # self.v2_pixel_1=int((self.cursorlinev2 - self.data[0,0]) / (self.data[-1,0] - self.data[0:0]) * (self.data[:,0].shape[0] - 1) + 0.5)
            def find_nearest_index(array, value):
                idx = (np.abs(array - value)).argmin()
                return idx
            self.v1_pixel=find_nearest_index(self.axis, self.cursorlinev1)
            self.v2_pixel=find_nearest_index(self.axis, self.cursorlinev2)
            
            self.data=self.data_or[self.v1_pixel:self.v2_pixel,:]
            
            N=20000
            new_axis=np.linspace(self.data[:,0].min(),self.data[:,0].max(),N)
            new_data=np.interp(new_axis,self.data[:,0],self.data[:,1])

            # fft_lev=fft(new_axis, new_data, [0.08,0.96],self.fig, self.ax[1],'linewidth')
            n1=4*len(new_axis)
            fft_result = np.fft.fft(new_data,n1)
            # fft_result = np.fft.fft(self.data[cursors(self.fig, self.ax,self.axis, 2, 10).v1_pixel:cursors(self.fig, self.ax,self.axis, 2, 10).v2_pixel])
            # n0 = len(fft_result)
            # n1=4*n0
            # sampling_frequency = 2000  # Sample rate (Hz)
            frequencies = np.fft.fftfreq(n1, d=0.001*(new_axis[1] - new_axis[0]))
            
            new_fft_result=np.fft.fft(new_data, n=n1)
            new_frequencies = np.fft.fftfreq(n1, d=0.001*(new_axis[1] - new_axis[0]))
            n=n1
            # print((signal[1,0] - signal[0,0]))
            # print(frequencies)
            
            # fig=plt.figure(figsize=(8, 4))
            M=2
            self.ax[1].clear()
            # self.ax[1].plot(frequencies[0:int(len(frequencies)/2)], np.abs(fft_result)[0:int(len(frequencies)/2)])
            # self.ax[1].plot(new_frequencies[0:n//2], np.abs(new_fft_result[:n//2]))
            self.ax[1].plot(frequencies[M:int(len(frequencies)/2)], np.abs(fft_result)[M:int(len(frequencies)/2)])
            # plt.xlabel('Frequency (THz)')
            # plt.ylabel('Magnitude')
            # plt.title()
            # plt.ylim(-0.01, 0.1)
            self.ax[1].set_xlim(0,5)
            # self.ax[1].set_ylim(-0.01, 1.2*np.max(np.abs(new_fft_result)[4:int(len(new_frequencies)/2)]))
            self.ax[1].set_ylim(-0.01, 1.2*np.max(np.abs(fft_result)[M:int(len(frequencies)/2)]))
            self.ax[1].set_xlabel('Frequency (THz)',fontsize=16,labelpad=14)
            self.ax[1].set_ylabel('Magnitude (a.u.)',fontsize=16,labelpad=14)
            self.ax[1].tick_params(axis='both',labelsize=16)
            # s_fft=save_data(new_frequencies[0:int(len(new_frequencies)/2)],np.abs(new_fft_result)[0:int(len(new_frequencies)/2)] ,self.name+'_fft', [0.2,0.46],self.fig)
            s_fft=save_data(frequencies[0:int(len(frequencies)/2)],np.abs(fft_result)[0:int(len(frequencies)/2)] ,self.name+'_fft', [0.2,0.46],self.fig)
            plt.grid()
            plt.show()
            
            # print('new_index=',idx,self.axis[idx])
            # self.v1_pixel=int((self.cursorlinev1 - self.axis[0]) / (self.axis[-1] - self.axis[0]) * (self.axis.shape[0] - 1) + 0.5)
            # self.v2_pixel=int((self.cursorlinev2 - self.axis[0]) / (self.axis[-1] - self.axis[0]) * (self.axis.shape[0] - 1) + 0.5)
            
            # print(self.v1_pixel, self.data[self.v1_pixel,0],self.v2_pixel, self.data[self.v2_pixel,0])
            # print((self.cursorlinev1 - self.axis[0]) / (self.axis[-1] - self.axis[0]) * (self.axis.shape[0] - 1) + 0.5)
            # print(self.v1_pixel_1, self.data[self.v1_pixel_1,0],self.v2_pixel_1, self.data[self.v2_pixel_1,0])
            
            # print(self.v1_pixel,self.v2_pixel)
    def on_release(self,event):
        # global self.active_cursor
        self.active_cursor = None    
    def test_button(self,event):
        print('test for save')
    # show()
# def show(self):
#     plt.show()