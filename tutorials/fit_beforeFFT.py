import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import  Button, CheckButtons
from datetime import datetime
from cursors import cursors
from scipy.optimize import curve_fit
from save_data import save_data
from cursors_FFT_2 import FFT_cursor
class fit():
    def __init__(self,data,plc,fig,ax,name): 
        # print('saveinit')
        self.fig=fig
        self.rax_ce = plt.axes([plc[0]-0.05, plc[1], 0.05, 0.03])
        # self.rax_ce = plt.axes([0.52, 0.36, 0.05, 0.03])
        # self.rax_ce = plt.axes([0.5,0.5, 0.05, 0.03])
        self.cb_ce = CheckButtons(self.rax_ce, ['Cursors'], [False])
        # cb_roi.on_clicked(on_checkbox_change)
        self.cb_ce.on_clicked(self.integrate_checkbox)  
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.data=data
        self.axis=self.data[:,0]
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
        
        self.size=[0.028,0.025]
        
        self.save_button = self.fig.add_axes( [plc[0]+self.size[0],plc[1]]+self.size)
        # self.save_button =plt.axes([0.78, 0.02, 0.1, 0.06])
        
        # self.save_button=self.fig.add_axes([0.78, 0.02, 0.1, 0.06])
        self.button_save = Button(self.save_button, 'fft')
        self.button_save.on_clicked(lambda event: self.fft_data(event))
        self.size2=[0.08,0.04]
        self.fit_button = self.fig.add_axes( [plc[0]+self.size2[0],plc[1]]+self.size2)
        # self.save_button =plt.axes([0.78, 0.02, 0.1, 0.06])
        
        # self.save_button=self.fig.add_axes([0.78, 0.02, 0.1, 0.06])
        self.button_fit = Button(self.fit_button, 'fit')
        self.button_fit.on_clicked(lambda event: self.fit_dexp(event))
        # self.button_save.on_clicked(lambda event: self.test_button(event))
        # plt.show()
        self.sub=None
        # self.name=name
        
    def fit_dexp(self,event):
        def double_exponential(x, a, b, c, d,e):
            return a * np.exp(-b * x) + c * np.exp(-d * x)+e
        def exponential(x, a, b, x0 ,e):
            return (a-e) * (np.exp(-b * (x-x0))) + e
        
        print('Begin fit')
        
        # if j==1:
        # for k in range(j,j+dp+1)    
        mean=np.mean(self.data[self.v1_pixel:self.v2_pixel,1])
        min=np.min(self.data[self.v1_pixel:self.v2_pixel,1])
        max=np.max(self.data[self.v1_pixel:self.v2_pixel,1])
        max_index=np.argmax(self.data[:-2,1])
        print('max_ind=',max_index)
        min_index=np.argmin(self.data[max_index:-2,1])
        # xb=
        # print(max,min,mean)
        # p0=[max/2,self.data[self.v1_pixel,0],max/2,self.data[self.v1_pixel,0],min]
        # print(p0)
        # params, covariance = curve_fit(double_exponential, self.data[self.v1_pixel:self.v2_pixel,0], self.data[self.v1_pixel:self.v2_pixel,1], p0)
        # # print(params)
        
        # a,b,c,d,e =params
        # self.fit= double_exponential(self.data[:,0], a, b, c, d,e)
        
        # p0=[max,0.001,self.data[self.v1_pixel,0],min]
        p0=[max,0.001,self.data[self.v1_pixel,0],min]
        print(p0)
        # self.test=exponential(self.data[self.v1_pixel:self.v2_pixel,0], p0[0],p0[1],p0[2],p0[3])
        # print(self.test)
        # fig=plt.figure(figsize=(8, 4))
        # plt.plot(self.data[self.v1_pixel:self.v2_pixel,0],self.test)
        # self.ax.plot(self.data[self.v1_pixel:self.v2_pixel,0],self.test)
        params, covariance = curve_fit(exponential, self.data[self.v1_pixel:self.v2_pixel,0], self.data[self.v1_pixel:self.v2_pixel,1], p0)
        a,b,x0,e=params
        print(self.data[:,0].shape)
        print(params)
        # print('calculated b=',np.abs(1/(self.data[max_index,0]-self.data[min_index,0])) )
        print('calculated b=',np.abs(5/(self.data[max_index,0]-self.data[min_index,0])) )
        self.fit= exponential(self.data[self.v1_pixel:self.v2_pixel,0], a, b, x0 ,e)
        self.ax.plot(self.data[self.v1_pixel:self.v2_pixel,0],self.fit)
        self.ax.set_title(self.name)
        # self.ax.set_xlabel('time (fs)')
        # self.ax_set_ylabel('linewidth (eV)')
        plt.show()
        # fig=plt.figure(figsize=(8, 4))
        # plt.plot(self.data[self.v1_pixel:self.v2_pixel,0],self.data[self.v1_pixel:self.v2_pixel,1]-self.fit-min-np.min(self.fit))
        # plt.show()
        
        self.sub=np.zeros_like(self.data[self.v1_pixel:self.v2_pixel,1]).astype( dtype=np.float64)
        self.sub=self.data[self.v1_pixel:self.v2_pixel,1]-self.fit-min+np.min(self.fit)
        self.new_ax=self.data[self.v1_pixel:self.v2_pixel,0]
        self.sub_f= self.sub-self.sub.mean()
        # fig=plt.figure(figsize=(8, 4))
        # plt.plot(self.new_ax,self.sub)
        # plt.show()
    def fft_data(self,event):
        # print('save')
        # current_time = datetime.now()
        
        # Format the datetime object as a string
        # current_time_str = current_time.strftime("%Y-%m-%d_%H%M%S")
        # file_path = "C:/Users/admin-nisel131/Documents/CVS_TR_flatband_fig/"+ self.name + current_time_str +".txt"
        # file_path = name+".txt"
        # self.data_saved = np.column_stack((self.axis, self.data))
        # np.savetxt(file_path, self.data_saved, fmt='%.5f', delimiter='\t')  
        # signal=self.data
        
        # fig,ax= plt.subplots(1, 1, figsize=(10, 5))

        # ax.plot(self.axis[0:48],self.data[0:48])
        # plt.show()
        # print(self.x1,self.x2)
        # c=cursors(self.fig, self.ax,self.axis, 2, 10) 
        # print(c.v1_pixel,c.v2_pixel)
        
        # fft_result = np.fft.fft(self.data[self.v1_pixel:self.v2_pixel,1])
        # fft_result = np.fft.fft(self.sub)
        fft_result = np.fft.fft(abs(self.sub_f))
        print(fft_result)
        # fft_result = np.fft.fft(self.data[cursors(self.fig, self.ax,self.axis, 2, 10).v1_pixel:cursors(self.fig, self.ax,self.axis, 2, 10).v2_pixel])
        n = len(fft_result)
        # sampling_frequency = 2000  # Sample rate (Hz)
        frequencies = np.fft.fftfreq(len(fft_result), d=0.001*(self.axis[1] - self.axis[0]))
        # print((signal[1,0] - signal[0,0]))
        # print(frequencies)
        # new_fft_result=
        # fig=plt.figure(figsize=(8, 4))
        fig, ax = plt.subplots(2, 1, figsize=(12, 8))
        # plt.plot(frequencies[0:int(len(frequencies)/2)], np.abs(fft_result)[0:int(len(frequencies)/2)])
        print(self.data[self.v1_pixel:self.v2_pixel,0].shape,self.sub.shape)
        print(self.data[self.v1_pixel:self.v2_pixel,0])
        print(self.sub_f)
        
        # ax[0,0].plot(self.data[self.v1_pixel:self.v2_pixel,0],self.sub)
        ax[0].plot(self.new_ax,self.sub_f)
        ax[1].plot(frequencies[0:int(len(frequencies)/2)], np.abs(fft_result)[0:int(len(frequencies)/2)])
        ax[0].set_xlabel('time (fs)',fontsize=16,labelpad=15)
        ax[0].set_ylabel('Signal (a.u)',fontsize=16,labelpad=15)
        ax[1].set_xlabel('frequency (THz)',fontsize=16,labelpad=15)
        ax[1].set_ylabel('Magnitude',fontsize=16,labelpad=15)
        ax[0].tick_params(axis='both',labelsize=16)
        ax[1].tick_params(axis='both',labelsize=16)
        ax[0].set_title('Backround substructed_'+ self.name +' & fft')
        def get_data_from_ax(ax):
            lines = ax.get_lines()
            x_data = []
            y_data = []
            
            for line in lines:
                x_data.append(line.get_xdata())
                y_data.append(line.get_ydata())
                
            return x_data, y_data

        # Get data from the ax
        x_data, y_data = get_data_from_ax(ax[1])
        
        s_signal=save_data(self.new_ax, self.sub_f,self.name+'_signal', [0.02,0.46],fig)
        # s_fft=save_data(frequencies[0:int(len(frequencies)/2)],np.abs(fft_result)[0:int(len(frequencies)/2)] ,self.name+'_fft', [0.0,0.46],fig)
        s_fft=save_data(x_data,y_data ,self.name+'_fft', [0.0,0.46],fig)
        print('heeeeeeeeeeeeeeere')
        
        # ax[1].set_title('fft_linewidth')
        # plt.xlabel('Frequency (THz)')
        # plt.ylabel('Magnitude')
        # plt.title()
        ax[1].set_ylim(-0.01, 0.05)
        plt.grid()
        
        # new_data=np.zeros((self.sub.shape[0],2))
        # new_data[:,0]=self.new_ax
        # new_data[:,1]=self.sub
        # fit_osc(new_data, [0.5,0.95], fig, ax, 'name')
        # fit(new_data, [0.5,0.95], fig, ax, 'name')
        
        
        plt.draw()
        plt.show()
        fig.canvas.draw()
        # plt.show()
        new_data=np.zeros((self.sub.shape[0],2))
        new_data[:,0]=self.new_ax
        new_data[:,1]=self.sub-np.mean(self.sub)
        FFT_cursor(new_data, [0.5,0.95], fig, ax, self.name)
        
        # s_gamma_fft=save_data(frequencies[0:int(len(frequencies)/2)], np.abs(fft_result)[0:int(len(frequencies)/2)],"fft"+self.name, [0.84,0.87],fig)
    def integrate_checkbox(self,label):
        if label == 'Cursors':
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
            self.fig.canvas.draw()
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
    def test_button(self,event):
        print('test for save')