import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import CheckButtons, Button
import h5py
# import mplcursors
from matplotlib.widgets import  Button, CheckButtons
from lmfit.models import ExpressionModel
class fit_osc:
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
        
        self.rax = plt.axes([plc[0]-0.15, plc[1], 0.05, 0.03])
        self.cb = CheckButtons(self.rax, ['two_sin'], [True])
        # cb_roi.on_clicked(on_checkbox_change)
        self.cb.on_clicked(self.whichfit)  
        
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
    def fit(self,event):
        
        # mod = ExpressionModel('off +  exp(-b*x) * (A1*sin(x*2*np.pi*fr1+ph1)+A2*sin(x*2*np.pi*fr2+ph2)+A3*sin(x*2*np.pi*fr3+ph3))')
        # mod = ExpressionModel('off +  exp(-b*x) * (A1*sin(0.001*x*2*3.1415*fr1+ph1)+A2*sin(0.001*x*2*3.1415*fr2+ph2)+A3*sin(0.001*x*2*3.1415*fr3+ph3))')
        # def FD(x, A, mu, T):
        #     c=0.02
        #     kb=1.38*10^(-23)
        #     return A / (1 + exp(-(x-mu)/(kb*T)))
        def exponential(x, a, b, x0 ,e):
            return (a-e) * (np.exp(-b * (x-x0))) + e
        def sinusoidal(x,A,fr,f):
            return A*np.sin(2*np.pi*fr*0.001*x+f)
        # def onesindecay(x,a,b,x0,e,A,fr,f):
        #     return exponential(x,a,b,x0,e)*sinusoidal(x-x0,A,fr,f)+e
        def onesindecay(x,a,b,x0,e,A,fr,f):
            return np.exp(-b*(x))*(sinusoidal(x,A,fr,f))
        def twosindecay(x,a,b,x0,e,A,fr,f,A2,fr2,f2):
            return np.exp(-b*(x))*(sinusoidal(x,A,fr,f)+sinusoidal(x, A2, fr2, f2))
        def threesindecay(x,a,b,x0,e,A,fr,f,A2,fr2,f2,A3,fr3,f3):
            return np.exp(-b*(x))*(sinusoidal(x,A,fr,f)+sinusoidal(x, A2, fr2, f2)+sinusoidal(x, A3, fr3, f3))
        def fermi_dirac(x, A, mu, T,off):
            kb = 8.617333262145 * 10**(-5)  # Boltzmann constant in eV/K
            return A / (1 + np.exp((x - mu) / (kb * T)))+off
        def gaussian(x, mu, sigma):
            return 0.1* np.exp(-(x - mu)**2 / (2 * sigma**2))
        self.data=self.data_or[self.v1_pixel:self.v2_pixel,:]
        # self.axis=self.data[:,0]
        self.fit_plot=np.zeros_like(self.data[:,1])
        fit_example=np.zeros_like(self.data[:,1])
        
        f0=1.4
        # self.w0=2*np.pi*f0
        f1=3.1
        f2=4.1
        # self.w1=2*np.pi*f1
        
        max=np.max(self.data[:-2,1])
        max_index=np.argmax(self.data[:-2,1])
        # min_index=np.argmin(self.data)
        max_index=np.argmax(self.data[:-2,1])
        # print('max_ind=',max_index)
        min_index=np.argmin(self.data[max_index:-2,1])
        min=np.min(self.data[max_index:-1,1])
        mean=np.mean(self.data[:-2,1])
        
        
        if self.fit_twosin:
        ###onesin
            # p0=[1,np.abs(5/(self.data[max_index,0]-self.data[-2,0])),self.data[max_index,0],mean,np.abs(max-mean),f0,0]
            # # params_bounds=([max*0.8,np.abs(5/(self.data[max_index,0]-self.data[min_index,0]))*0.1,-np.inf,-np.inf,np.abs((max-min)/10),0.5*self.w0,-np.inf]
            # #                ,[max*2,np.abs(5/(self.data[max_index,0]-self.data[min_index,0]))*10,np.inf,np.inf,np.abs((max-min)),2*self.w0,np.inf])
            # params, covariance = curve_fit(onesindecay, self.data[:,0], self.data[:,1], p0)
            # self.fit_plot=onesindecay(self.data[:,0],*params)
            # fit_example=onesindecay(self.data[:,0],*p0)
            mod = ExpressionModel('off +  exp(-b*x) * (A1*sin(0.001*x*2*3.1415*fr1+ph1)+A2*sin(0.001*x*2*3.1415*fr2+ph2))')
            params = mod.make_params(off=mean, b=np.abs(5/(self.data[max_index,0]-self.data[-2,0])), A1=np.abs(max-mean)/2, fr1=0.5,ph1=0,A2=np.abs(max-mean)/2, fr2=3.1,ph2=0)
            # params['A2'].set(value=0, vary=False, expr='')
            # params['fr1'].set(value=1.35, vary=True, expr='')
            params['fr1'].set(value=4.2, vary=True, expr='')
            params['fr2'].set(value=3.1, vary=True, expr='')
            
            params['b'].set(value=0, vary=False, expr='')
            # out = mod.fit(self.data[:,1], params, x=self.data[:,0],method='nelder')
            out = mod.fit(self.data[:,1], params, x=self.data[:,0])
            dely = out.eval_uncertainty(sigma=3)
            print(out.fit_report(min_correl=0.25))
        else:
        ###twosin
            # p0=[1,np.abs(5/(self.data[max_index,0]-self.data[-2,0])),self.data[max_index,0],mean,np.abs(max-mean),f0,0,np.abs(max-mean)/2,f1,0]
            # params, covariance = curve_fit(twosindecay, self.data[:,0], self.data[:,1], p0)
            # self.fit_plot=twosindecay(self.data[:,0],*params)
            # fit_example=twosindecay(self.data[:,0],*p0)
        ###threesin    
            # p0=[1,np.abs(5/(self.data[max_index,0]-self.data[-2,0])),self.data[max_index,0],mean,np.abs(max-mean),f0,0,np.abs(max-mean)/2,f1,0,np.abs(max-mean),f2,0]
            # params, covariance = curve_fit(threesindecay, self.data[:,0], self.data[:,1], p0)
            # self.fit_plot=threesindecay(self.data[:,0],*params)
            # fit_example=threesindecay(self.data[:,0],*p0)
            mod = ExpressionModel('off +  exp(-b*x) * (A1*sin(0.001*x*2*3.1415*fr1+ph1)+A2*sin(0.001*x*2*3.1415*fr2+ph2)+A3*sin(0.001*x*2*3.1415*fr3+ph3))')
            params = mod.make_params(off=mean, b=np.abs(5/(self.data[max_index,0]-self.data[-2,0])), A1=np.abs(max-mean)/2, fr1=0.5,ph1=0,A2=np.abs(max-mean)/2, fr2=3.1,ph2=0,A3=np.abs(max-mean)/2, fr3=4.1,ph3=0)
            # params['A1'].min=0
            # params['A2'].min=0
            # params['A3'].min=0
            # params['ph1'].min=-3.1415
            # params['ph1'].max=3.1415
            # params['ph2'].min=-3.1415
            # params['ph2'].max=3.1415
            # params['ph3'].min=-3.1415
            # params['ph3'].max=3.1415
            # params['A2'].set(value=0, vary=False, expr='')
            # params['fr1'].set(value=1.35, vary=True, expr='')
            params['fr1'].set(value=1.3, vary=True, expr='')
            params['fr2'].set(value=3.1, vary=True, expr='')
            params['fr3'].set(value=4.1, vary=True, expr='')
            params['b'].set(value=0, vary=False, expr='')
            # out = mod.fit(self.data[:,1], params, x=self.data[:,0],method='nelder')
            out = mod.fit(self.data[:,1], params, x=self.data[:,0])
            dely = out.eval_uncertainty(sigma=3)
            print(out.fit_report(min_correl=0.25))
        # print('p0= ',p0)
        # print('params= ',params)
        self.fig1, self.axs = plt.subplots(2, 1, figsize=(12, 5))
        print('001')
        # plt.figure(figsize=(12, 6))
        self.axs[0].plot(self.data[:,0],self.data[:,1],color='blue',label='data')
        # self.axs.plot(self.data[:,0],self.fit_plot,color='red') 
        self.axs[0].plot(self.data[:,0],out.best_fit,color='red',label='fit')
        self.axs[0].fill_between(self.data[:,0], out.best_fit-dely, out.best_fit+dely,
                    color="#8A8A8A", label=r'3-$\sigma$ band')
        if self.fit_twosin:
            # self.axs[0].set_title('frequency= '+ str(params[5])+' THz')
            self.axs[0].set_title('frequency 1= '+ str("{:.3f}".format(out.best_values['fr1']))+' THz'+ ', frequency 2= '+ str("{:.3f}".format(out.best_values['fr2']))+' THz')
            self.axs[1].errorbar([out.best_values['fr1'],out.best_values['fr2']],[np.abs(out.best_values['A1']),np.abs(out.best_values['A2'])],xerr=[out.params['fr1'].stderr,out.params['fr2'].stderr],yerr=[out.params['A1'].stderr,out.params['A2'].stderr],fmt='o',ecolor='red')
            
            self.axs[1].set_ylim(0,1.2*np.max([np.abs(out.best_values['A1']),np.abs(out.best_values['A2'])]))
        else:
            # self.axs.set_title('frequency 1= '+ str(params[5])+' THz'+ ', frequency 2= '+ str(params[8])+' THz')
            # self.axs.set_title('frequency 1= '+ str(params[5])+' THz'+ ', frequency 2= '+ str(params[8])+' THz'+ ', frequency 3= '+ str(params[11])+' THz')
            
            self.axs[0].set_title('frequency 1= '+ str("{:.3f}".format(out.best_values['fr1']))+' THz'+ ', frequency 2= '+ str("{:.3f}".format(out.best_values['fr2']))+' THz'+ ', frequency 3= '+ str("{:.3f}".format(out.best_values['fr3']))+' THz')
            
            # print([out.best_values['fr1'],out.best_values['fr2'],out.best_values['fr3']],[[out.best_values['A1']],out.best_values['A2'],out.best_values['A3']])
            # if params['A2'] != 0:
            self.axs[1].errorbar([out.best_values['fr1'],out.best_values['fr2'],out.best_values['fr3']],[np.abs(out.best_values['A1']),np.abs(out.best_values['A2']),np.abs(out.best_values['A3'])],xerr=[out.params['fr1'].stderr,out.params['fr2'].stderr,out.params['fr3'].stderr],yerr=[out.params['A1'].stderr,out.params['A2'].stderr,out.params['A3'].stderr],fmt='o',ecolor='red')
            # self.axs[1].errorbar([out.best_values['fr1'],out.best_values['fr3']],[np.abs(out.best_values['A1']),np.abs(out.best_values['A3'])],xerr=[out.params['fr1'].stderr,out.params['fr3'].stderr],yerr=[out.params['A1'].stderr,out.params['A3'].stderr],fmt='o',ecolor='red')
            self.axs[1].set_ylim(0,1.2*np.max([np.abs(out.best_values['A1']),np.abs(out.best_values['A2']),np.abs(out.best_values['A3'])]))
        
        
        self.axs[0].set_xlabel('time (fs)',fontsize=16,labelpad=14)
        self.axs[0].set_ylabel('Signal (a.u.)',fontsize=16,labelpad=14)
        self.axs[0].tick_params(axis='both',labelsize=16)
        self.axs[1].set_xlabel('Frequency modes(THz)',fontsize=16,labelpad=14)
        self.axs[1].set_ylabel('Amplitude (a.u.)',fontsize=16,labelpad=14)
        self.axs[1].tick_params(axis='both',labelsize=16)
        self.axs[1].set_xlim(0,8)
        self.axs[0].legend(fontsize=14)
        self.fig.canvas.draw()
        self.fig.show()
        
        # slider_ax1 = self.fig1.add_axes([0.1, 0.08, 0.3, 0.02])
        # slider_ax2 = self.fig1.add_axes([0.1, 0.06, 0.3, 0.02])
        # slider_ax3 = self.fig1.add_axes([0.1, 0.04, 0.3, 0.02])
        # slider_ax4 = self.fig1.add_axes([0.5, 0.08, 0.3, 0.02])
        # slider_ax5 = self.fig1.add_axes([0.5, 0.06, 0.3, 0.02])
        # slider_ax6 = self.fig1.add_axes([0.5, 0.04, 0.3, 0.02])
        # slider_ax7 = self.fig1.add_axes([0.1, 0.02, 0.3, 0.02])
        
        # slider_amp1 = Slider(slider_ax1, 'Amp1', 0, np.max(self.data[:,1])*5, valinit=params[4], valstep=np.max(self.data[:,1])/10,orientation='horizontal')
        # slider_fr1 = Slider(slider_ax2, 'fr1', 0, 10, valinit=params[5], valstep=0.1, orientation='horizontal')
        # slider_ph1 = Slider(slider_ax3, 'ph1', -3.1415,3.1415, valinit=params[6], valstep=0.1, orientation='horizontal')
        # slider_amp2 = Slider(slider_ax4, 'Amp2', 0, np.max(self.data[:,1])*5, valinit=params[7], valstep=np.max(self.data[:,1])/10,orientation='horizontal')
        # slider_fr2 = Slider(slider_ax5, 'fr2', 0, 10, valinit=params[8], valstep=0.1, orientation='horizontal')
        # slider_ph2 = Slider(slider_ax6, 'ph2', -3.1415,3.1415, valinit=params[9], valstep=0.1, orientation='horizontal')
        # slider_b = Slider(slider_ax7, 'b', 0,params[1]*1.4, valinit=params[1], valstep=params[1]/10, orientation='horizontal')
        
    
        
        # def update_amp1(val):
        #     update_graph(slider_amp1.val,slider_fr1.val,slider_ph1.val,slider_amp2.val,slider_fr2.val,slider_ph2.val,slider_b.val)
        # def update_fr1(val):
        #     update_graph(slider_amp1.val,slider_fr1.val,slider_ph1.val,slider_amp2.val,slider_fr2.val,slider_ph2.val,slider_b.val)
        # def update_ph1(val):
        #     update_graph(slider_amp1.val,slider_fr1.val,slider_ph1.val,slider_amp2.val,slider_fr2.val,slider_ph2.val,slider_b.val)
        # def update_amp2(val):
        #     update_graph(slider_amp1.val,slider_fr1.val,slider_ph1.val,slider_amp2.val,slider_fr2.val,slider_ph2.val,slider_b.val)
        # def update_fr2(val):
        #     update_graph(slider_amp1.val,slider_fr1.val,slider_ph1.val,slider_amp2.val,slider_fr2.val,slider_ph2.val,slider_b.val)
        # def update_ph2(val):
        #     update_graph(slider_amp1.val,slider_fr1.val,slider_ph1.val,slider_amp2.val,slider_fr2.val,slider_ph2.val,slider_b.val)    
        # def update_b(val):
        #     update_graph(slider_amp1.val,slider_fr1.val,slider_ph1.val,slider_amp2.val,slider_fr2.val,slider_ph2.val,slider_b.val)   
            
        # slider_amp1.on_changed(update_amp1)
        # slider_fr1.on_changed(update_fr1)
        # slider_ph1.on_changed(update_ph1)
        # slider_amp2.on_changed(update_amp2)
        # slider_fr2.on_changed(update_fr2)
        # slider_ph2.on_changed(update_ph2)
        # slider_b.on_changed(update_b)
        
        # def update_graph(amp1,fr1,ph1,amp2,fr2,ph2,b):
        #     self.axs.clear()
        #     # print(self.data[:,0])
        #     t_data = np.linspace(self.data[:,0].min(), self.data[:,0].max(), 300)
        #     example=(sinusoidal(t_data, amp1, fr1, ph1)+sinusoidal(t_data, amp2, fr2, ph2)+sinusoidal(t_data, params[10], params[11], params[12]))*np.exp(-b*(t_data))
        #     self.axs.plot(self.data[:,0],self.data[:,1],color='blue')
        #     # self.fit_plot=sinusoidal(self.data[:,0], amp1, fr1, ph1)
        #     # self.fit_plot=sinusoidal(self.data[:,0], amp1, fr1, ph1)+sinusoidal(self.data[:,0], amp2, fr2, ph2)
        #     # self.axs.plot(self.data[:,0],self.fit_plot,color='red')
        #     self.axs.plot(t_data,example,color='red')
        #     plt.title('frequency 1= '+ str(fr1)+' THz'+ ', frequency 2= '+ str(fr2)+' THz')
        
        # plt.draw()
        # #     plt.plot(self.ax2[0:self.N],self.sigma[0:self.N])
        # # self.axs.plot(self.data[:,0],self.data[:,1],color='blue')
        
        # # self.axs.plot(self.data[:,0],self.fit_plot,color='red')    
        # plt.figure(figsize=(12, 6))
        # plt.plot(self.data[:,0],fit_example,color='blue')
        # if self.fit_twosin:
        #     plt.title('frequency= '+ str(params[5])+' THz')
        # else:
        #     plt.title('frequency 1= '+ str(params[5])+' THz'+ ', frequency 2= '+ str(params[8])+' THz')
        # plt.draw()
        # plt.show()
        # self.fig.canvas.draw()
        # print('002')      
                
    def whichfit(self,label):
        if label == 'two_sin':
                if self.cb.get_status()[0]:
                    self.fit_twosin= True
                else:
                    self.fit_twosin = False
                             
       
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
            N=6000
            new_axis=np.linspace(self.data[:,0].min(),self.data[:,0].max(),N)
            new_data=np.interp(new_axis,self.data[:,0],self.data[:,1])

            # fft_lev=fft(new_axis, new_data, [0.08,0.96],self.fig, self.ax[1],'linewidth')
            
            fft_result = np.fft.fft(new_data)
            # fft_result = np.fft.fft(self.data[cursors(self.fig, self.ax,self.axis, 2, 10).v1_pixel:cursors(self.fig, self.ax,self.axis, 2, 10).v2_pixel])
            n = len(fft_result)
            # sampling_frequency = 2000  # Sample rate (Hz)
            frequencies = np.fft.fftfreq(len(fft_result), d=0.001*(new_axis[1] - new_axis[0]))
            # print((signal[1,0] - signal[0,0]))
            # print(frequencies)
            
            # fig=plt.figure(figsize=(8, 4))
            self.ax[1].clear()
            self.ax[1].plot(frequencies[0:int(len(frequencies)/2)], np.abs(fft_result)[0:int(len(frequencies)/2)])
            # plt.xlabel('Frequency (THz)')
            # plt.ylabel('Magnitude')
            # plt.title()
            # plt.ylim(-0.01, 0.1)
            self.ax[1].set_xlim(0,10)
            self.ax[1].set_ylim(-0.01, 1.2*np.max(np.abs(fft_result)[4:int(len(frequencies)/2)]))
            self.ax[1].set_xlabel('Frequency (THz)',fontsize=16,labelpad=14)
            self.ax[1].set_ylabel('Magnitude (a.u.)',fontsize=16,labelpad=14)
            self.ax[1].tick_params(axis='both',labelsize=16)
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