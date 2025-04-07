from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QCheckBox, QAction, QSlider, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
from matplotlib.lines import Line2D

from mpes_tools.fi_panel6 import MainWindow

import xarray as xr

# %matplotlib qt

class GraphWindow(QMainWindow):
    def __init__(self,data_array: xr.DataArray,t,dt):
        global t_final
        super().__init__()

        self.setWindowTitle("Graph Window")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget for the graph
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        self.fig, self.axs = plt.subplots(2,2,figsize=(20,16))
        self.canvas = FigureCanvas(self.fig)
        
        self.checkbox_e = QCheckBox("Integrate_energy")
        self.checkbox_e.stateChanged.connect(self.checkbox_e_changed)
        
        self.checkbox_k = QCheckBox("Integrate_k")
        self.checkbox_k.stateChanged.connect(self.checkbox_k_changed)
        
        self.checkbox_cursors = QCheckBox("energy_cursors")
        self.checkbox_cursors.stateChanged.connect(self.checkbox_cursors_changed)
        checkbox_layout= QHBoxLayout()
        # Add the canvas to the layout
        checkbox_layout.addWidget(self.checkbox_e)
        checkbox_layout.addWidget(self.checkbox_k)
        layout.addLayout(checkbox_layout)
        layout.addWidget(self.canvas)
        layout.addWidget(self.checkbox_cursors)
        
        slider_layout= QHBoxLayout()
        self.slider1 = QSlider(Qt.Horizontal)
        self.slider1.setRange(0, 100)
        self.slider1.setValue(0)
        self.slider1_label = QLabel("0")
        
        self.slider2 = QSlider(Qt.Horizontal)
        self.slider2.setRange(0, 10)
        self.slider2.setValue(0)
        self.slider2_label = QLabel("0")
        
        self.slider1.setFixedSize(200, 12)  # Change the width and height as needed
        self.slider2.setFixedSize(200, 12)  # Change the width and height as needed
        
        slider_layout.addWidget(self.slider1)
        slider_layout.addWidget(self.slider1_label)
        slider_layout.addWidget(self.slider2)
        slider_layout.addWidget(self.slider2_label)
        layout.addLayout(slider_layout)
        # Create a layout for the central widget
        self.active_cursor = None
        self.cursorlinev1=1
        self.cursorlinev2=0
        # self.v1_pixel=None
        # self.v2_pixel=None
        self.Line1=None
        self.Line2=None
        self.square_artists = []  # To store the artists representing the dots
        self.square_coords = [(0, 0), (0, 0)]  # To store the coordinates of the dots
        self.square_count = 0  # To keep track of the number of dots drawn
        
        
        self.cid_press2= None
        self.line_artists=[]
        self.cid_press3 = None
        self.cid_press4 = None
        self.cid_press = None

        # Create a figure and canvas for the graph
        
        self.data_array=data_array
        self.axes = data_array.dims
        self.dt=dt
        # Plot data
        self.plot_graph(t,dt)
        self.ssshow(t,dt)
        self.slider1.setRange(0,len(self.data_array[self.axes[2]])-1)
        self.plot=np.zeros_like(self.data_array.loc[{self.axes[2]:slice(0,1)}].mean(dim=(self.axes[2]))[1,:])
        
        self.slider1.valueChanged.connect(self.slider1_changed)
        self.slider2.valueChanged.connect(self.slider2_changed)
        t_final=self.data_array[self.axes[2]].shape[0]
        
        
        fit_panel_action = QAction('Fit_Panel',self)
        fit_panel_action.triggered.connect(self.fit_panel)
        
        menu_bar = self.menuBar()

        # Create a 'Graph' menu
        
        graph_menu1 = menu_bar.addMenu("Fit Panel")
        
        graph_menu1.addAction(fit_panel_action)

        # Add the actions to the menu
        
        self.graph_windows=[]
        self.t=t
        
    def slider1_changed(self,value):
        self.slider1_label.setText(str(value))
        self.plot_graph(self.slider1.value(),self.slider2.value())
        # print(self.slider1.value(),self.slider2.value())
        self.update_show(self.slider1.value(),self.slider2.value())
        self.t=self.slider1.value()
        # self.us()
        # update_show(self.slider1.value(),self.slider2.value())

    def slider2_changed(self,value):
        self.slider2_label.setText(str(value))
        self.plot_graph(self.slider1.value(),self.slider2.value())
        self.update_show(self.slider1.value(),self.slider2.value())
        self.dt=self.slider2.value()
        # self.ssshow(self.slider1.value(),self.slider2.value()).update_show()
        # self.us()
        # update_show(self.slider1.value(),self.slider2.value())

    def checkbox_e_changed(self, state):
        if state == Qt.Checked:
            # print("Checkbox is checked")
            self.integrate_E()
        else:
            # print("Checkbox is unchecked")
            self.update_show(self.slider1.value(),self.slider2.value())

    def checkbox_k_changed(self, state):
        if state == Qt.Checked:
            # print("Checkbox is checked")
            self.integrate_k()
        else:
            # print("Checkbox is unchecked")
            self.update_show(self.slider1.value(),self.slider2.value())

    def checkbox_cursors_changed(self, state):
        if state == Qt.Checked:
            self.put_cursors()
            # self.integrate_k()
        else:
            # print("Checkbox is unchecked")
            self.remove_cursors()

    def plot_graph(self,t,dt):
        # Plot on the graph
        te1=self.data_array[self.axes[2]][t].item()
        te2=self.data_array[self.axes[2]][t+dt].item()
        ax = self.axs[0,0]

        self.data_array.loc[{self.axes[2]:slice(te1,te2)}].mean(dim=(self.axes[2])).T.plot(ax=ax)
        self.fig.tight_layout()
        self.canvas.draw()
    
    def fit_panel(self,event):
        print('forfit',len(self.plot),'axis',len(self.axis))
        graph_window=   MainWindow( self.data_o, self.axis,self.square_coords[0][1], self.square_coords[1][1],self.t,self.dt)
        graph_window.show()
        self.graph_windows.append(graph_window)
        
    def lz_fit(self, event):
        two_lz_fit(self.data_o, self.axis, self.square_coords[0][1], self.square_coords[1][1], 0, t_final, self.v1_pixel, self.v2_pixel,self.dt,self.a).fit()
    def fit(self, event):
        fit_4d(self.data_o, self.axis, self.square_coords[0][1], self.square_coords[1][1], 0, t_final, self.v1_pixel, self.v2_pixel,self.dt).fit()
    def fit_FD(self, event):
        fit_FD(self.data_o, self.axis, self.square_coords[0][1], self.square_coords[1][1], 0, t_final, self.v1_pixel, self.v2_pixel,self.dt).fit()
    def fit_FD_conv(self, event):
        # print('ax0test=',self.ax[0])
        # print('ax1test=',self.ax[1])
        
        fit_FD_lor_conv(self.data_o, self.axis, self.square_coords[0][1], self.square_coords[1][1], 0, t_final, self.v1_pixel, self.v2_pixel,self.dt).fit()
    def fit_FD_conv_2(self, event):
        
        f=fit_FD_conv(self.data_o, self.axis, self.square_coords[0][1], self.square_coords[1][1], 0, t_final, self.v1_pixel, self.v2_pixel,self.dt)
        f.show()

    def ssshow(self,t,dt):
        
        def put_cursors():
            self.Line1=axe.axvline(x=self.cursorlinev1, color='red', linestyle='--',linewidth=2, label='Vertical Line',picker=10)
            self.Line2=axe.axvline(x=self.cursorlinev2, color='red', linestyle='--',linewidth=2, label='Vertical Line',picker=10)
            plt.draw()
            self.fig.canvas.draw()
        def remove_cursors():
            self.Line1.remove()
            self.Line2.remove()
            plt.draw()
            self.fig.canvas.draw() 
                           
        def integrate_E():
            self.plote=np.zeros_like(self.data_array.loc[{self.axes[2]:slice(0,1)}].mean(dim=(self.axes[2]))[1,:])
            self.axs[1,0].clear()
            plt.draw()
            x_min = int(min(self.square_coords[1][1], self.square_coords[0][1]))
            x_max = int(max(self.square_coords[1][1], self.square_coords[0][1])) + 1
            for i in range(x_min, x_max):
                self.plote += self.data_array.loc[{self.axes[2]:slice(0,1)}].mean(dim=(self.axes[2]))[i, :]
            # if self.square_coords[1][1]<self.square_coords[0][1]:
            #     for i in range(self.square_coords[1][1],self.square_coords[0][1]+1):
            #          self.plot+=self.data[i,:]
            # elif self.square_coords[1][1]>self.square_coords[0][1]:
            #     for i in range(self.square_coords[0][1],self.square_coords[1][1]+1):
            #          self.plot+=self.data[i,:]
            # else: 
            #     self.plot+=self.data[self.square_coords[0][1],:]
                                                    
            self.axs[1, 0].plot(self.data_array[self.axes[1]][:],self.plote/abs(self.square_coords[0][1]-self.square_coords[1][1]),color='red') 
                
                # save_data(self.data_array[self.axes[1]], plot/abs(self.square_coords[0][1]-self.square_coords[1][1]),"EDC_time="+str(slider_t.val)+"_", [0.42,0.46],self.fig)        
        def integrate_k():
            self.plotk=np.zeros_like(self.data_array.loc[{self.axes[2]:slice(0,1)}].mean(dim=(self.axes[2]))[:,1])
            self.axs[0,1].clear()
            plt.draw()
            x_min = int(min(self.square_coords[0][0], self.square_coords[1][0]))
            x_max = int(max(self.square_coords[0][0], self.square_coords[1][0])) + 1
            for i in range(x_min, x_max):
                self.plotk += self.data_array.loc[{self.axes[2]:slice(0,1)}].mean(dim=(self.axes[2]))[:, i]
            # if self.square_coords[0][0]<self.square_coords[1][0]:
            #     for i in range(int(self.square_coords[0][0]),int(self.square_coords[1][0])+1):
            #         self.plot+=self.data[:,i] 
            # else:    
            #     for i in range(int(self.square_coords[1][0]),int(self.square_coords[0][0])+1):
            #         self.plot+=self.data[:,i]
            self.axs[0, 1].plot(self.plotk/abs(int(self.square_coords[0][0])-int(self.square_coords[1][0])),self.data_array[self.axes[0]][:],color='red')
            # plt.draw()    
        def box():
                self.int=np.zeros_like(self.data_array[self.axes[2]])
                self.axs[1,1].clear()
                if self.square_coords[1][1]<self.square_coords[0][1]:
                    if self.square_coords[0][0]<self.square_coords[1][0]:
                        for i in range(self.square_coords[1][1],self.square_coords[0][1]+1):
                            for j in range(int(self.square_coords[0][0]),int(self.square_coords[1][0])+1):
                                self.int+=self.data_array[i,j,:]
                                
                    else:
                        for i in range(self.square_coords[1][1],self.square_coords[0][1]+1):
                            for j in range(int(self.square_coords[1][0]),int(self.square_coords[0][0])+1):
                                self.int+=self.data_array[i,j,:]
                else:
                    if self.square_coords[0][0]<self.square_coords[1][0]:
                        for i in range(self.square_coords[0][1],self.square_coords[1][1]+1):
                            for j in range(int(self.square_coords[0][0]),int(self.square_coords[1][0])+1):
                                self.int+=self.data_array[i,j,:]
                    else:
                        for i in range(self.square_coords[0][1],self.square_coords[1][1]+1):
                            for j in range(int(self.square_coords[1][0]),int(self.square_coords[0][0])+1):
                                self.int+=self.data_array[i,j,:]
                if int(self.square_coords[1][1]) != int(self.square_coords[0][1]) and int(self.square_coords[0][0]) != int(self.square_coords[1][0]):
                    # self.axs[1,1].plot(plot/np.sqrt((self.square_coords[0][0])-int(self.square_coords[1][0])**2+(self.square_coords[0][1]-self.square_coords[1][1])**2),self.data_array[self.axes[2]])
                    # print(plot)
                    N=120
                    self.axs[1,1].plot(self.data_array[self.axes[2]][0:N],self.int[0:N])  
                          
        def update_show(t,dt):
            # print(self.data.shape)
            # print(self.data_array[self.axes[2]].shape)
            # print(self.square_coords)
            # self.data=np.zeros_like(self.data)
            print('update_Shopwwww')
            self.axs[0,1].clear()
            self.axs[1,0].clear()
            # if self.cursorlinev1 is not None and self.cursorlinev2 is not None:
            # if cb_ce.get_status()[0]:
            
            # for j in range(t, t+dt+1):
            #     self.data+=self.data_o[:,:,j]
            im6.set_array(self.data_array.loc[{self.axes[2]:slice(0,1)}].mean(dim=(self.axes[2])))
            if self.checkbox_e.isChecked() and self.checkbox_k.isChecked() :
                integrate_E()
                integrate_k()
            elif self.checkbox_e.isChecked():
                integrate_E()
                self.axs[0, 1].plot(self.data_array.loc[{self.axes[2]:slice(0,1)}].mean(dim=(self.axes[2]))[:,int(self.square_coords[0][0])],self.data_array[self.axes[0]][:],color='orange') 
                self.axs[0, 1].plot(self.data_array.loc[{self.axes[2]:slice(0,1)}].mean(dim=(self.axes[2]))[:,int(self.square_coords[1][0])],self.data_array[self.axes[0]][:],color='green')
                # self.axs[0, 1].plot(self.data[:,int(self.square_coords[0][0])],np.arange(self.data[:,self.square_coords[0][0]].shape[0]),color='orange') 
                # self.axs[0, 1].plot(self.data[:,int(self.square_coords[1][0])],np.arange(self.data[:,self.square_coords[0][0]].shape[0]),color='green')
            elif self.checkbox_k.isChecked():
                integrate_k()
                self.axs[1, 0].plot(self.data_array[self.axes[1]][:],self.data_array.loc[{self.axes[2]:slice(0,1)}].mean(dim=(self.axes[2]))[self.square_coords[0][1],:],color='orange')
                self.axs[1, 0].plot(self.data_array[self.axes[1]][:],self.data_array.loc[{self.axes[2]:slice(0,1)}].mean(dim=(self.axes[2]))[self.square_coords[1][1],:],color='green')
            else:
                self.axs[1, 0].plot(self.data_array[self.axes[1]][:],self.data_array.loc[{self.axes[2]:slice(0,1)}].mean(dim=(self.axes[2]))[self.square_coords[0][1],:],color='orange')
                self.axs[1, 0].plot(self.data_array[self.axes[1]][:],self.data_array.loc[{self.axes[2]:slice(0,1)}].mean(dim=(self.axes[2]))[self.square_coords[1][1],:],color='green')
                # self.axs[0, 1].plot(self.data[:,int(self.square_coords[0][0])],np.arange(self.data[:,int(self.square_coords[0][0])].shape[0]),color='orange') 
                # self.axs[0, 1].plot(self.data[:,int(self.square_coords[1][0])],np.arange(self.data[:,int(self.square_coords[0][0])].shape[0]),color='green')
                self.axs[0, 1].plot(self.data_array.loc[{self.axes[2]:slice(0,1)}].mean(dim=(self.axes[2]))[:,int(self.square_coords[0][0])],self.data_array[self.axes[0]][:],color='orange') 
                self.axs[0, 1].plot(self.data_array.loc[{self.axes[2]:slice(0,1)}].mean(dim=(self.axes[2]))[:,int(self.square_coords[1][0])],self.data_array[self.axes[0]][:],color='green')
                # save_data(self.axs[1], plot/abs(self.square_coords[0][1]-self.square_coords[1][1]),"EDC_time="+str(slider_t.val)+"_", [0.42,0.46],self.fig)
                # save_data(self.data_array[self.axes[1]], self.data[self.square_coords[0][1],:],"yellow, EDC_time="+str(slider_t.val)+"_", [0.42,0.46],self.fig)
                # save_data(self.data_array[self.axes[1]], self.data[self.square_coords[1][1],:],"green, EDC_time="+str(slider_t.val)+"_", [0.46,0.46],self.fig)
            if self.checkbox_cursors.isChecked():
                self.Line1=self.axs[1,0].axvline(x=self.cursorlinev1, color='red', linestyle='--',linewidth=2, label='Vertical Line',picker=10)
                self.Line2=self.axs[1,0].axvline(x=self.cursorlinev2, color='red', linestyle='--',linewidth=2, label='Vertical Line',picker=10)
                plt.draw()
                self.fig.canvas.draw()
            # print("update_show is called")
            # line_profile(self.data[self.square_coords[0][1],:], self.axis[3][:],self.fig).line_profile()
            # line_profile(self.data[self.square_coords[0][1],:], self.axis[3][:],self.fig)
            box()
            time1=self.data_array[self.axes[2]][t]
            timedt1=self.data_array[self.axes[2]][t+dt]
            # print( 'change')
            self.axs[0,0].set_title(f't: {time1:.2f}, t+dt: {timedt1}')
            im6.set_clim(vmin=self.data_array.loc[{self.axes[2]:slice(0,1)}].mean(dim=(self.axes[2])).min(), vmax=self.data_array.loc[{self.axes[2]:slice(0,1)}].mean(dim=(self.axes[2])).max())
            self.fig.canvas.draw()
            plt.draw() 
 
        
        ax = self.axs[0,0]
        im6 = self.data_array.loc[{self.axes[2]:slice(0,1)}].mean(dim=(self.axes[2])).T.plot(ax=ax)
       
        initial_x = 0
        initial_y = 0
        initial_x2 = 0.5
        initial_y2 = 0.5
        ax=self.axs[0,0]
        axe=self.axs[1,0]
        # Create cursor lines with larger pick radius
        cursor_vert1 = Line2D([initial_x, initial_x], [-200, len(self.data_array[self.axes[1]])+4000], color='yellow', linewidth=2, picker=10,linestyle='--')
        cursor_horiz1 = Line2D([-200, len(self.data_array[self.axes[0]])+4000], [initial_y, initial_y], color='yellow', linewidth=2, picker=10,linestyle='--')
        cursor_vert2 = Line2D([initial_x2, initial_x2], [-200, len(self.data_array[self.axes[1]])+4000], color='green', linewidth=2, picker=10,linestyle='--')
        cursor_horiz2 = Line2D([-200, len(self.data_array[self.axes[0]])+4000], [initial_y2, initial_y2], color='green', linewidth=2, picker=10,linestyle='--')
        # Create draggable dot at the intersection
        dot1 = Circle((initial_x, initial_y), radius=0.05, color='yellow', picker=10)
        dot2 = Circle((initial_x2, initial_y2), radius=0.05, color='green', picker=10)
        
        if dot1.center[0] is not None and dot1.center[1] is not None and dot2.center[0] is not None and dot2.center[1] is not None:
            x1_pixel=int((dot1.center[0] - self.data_array[self.axes[1]][0]) / (self.data_array[self.axes[1]][-1] - self.data_array[self.axes[1]][0]) * (self.data_array[self.axes[1]].shape[0] - 1) + 0.5)
            y1_pixel=int((dot1.center[1] - self.data_array[self.axes[0]][0]) / (self.data_array[self.axes[0]][-1] - self.data_array[self.axes[0]][0]) * (self.data_array[self.axes[0]].shape[0] - 1) + 0.5)
            self.square_coords[0]=(x1_pixel,y1_pixel)
            x2_pixel=int((dot2.center[0] - self.data_array[self.axes[1]][0]) / (self.data_array[self.axes[1]][-1] - self.data_array[self.axes[1]][0]) * (self.data_array[self.axes[1]].shape[0] - 1) + 0.5)
            y2_pixel=int((dot2.center[1] - self.data_array[self.axes[0]][0]) / (self.data_array[self.axes[0]][-1] - self.data_array[self.axes[0]][0]) * (self.data_array[self.axes[0]].shape[0] - 1) + 0.5)
            self.square_coords[1]=(x2_pixel,y2_pixel)
        # self.square_coords=[dot1.center,dot2.center]
        # Add cursor lines and dot to the plot
        ax.add_line(cursor_vert1)
        ax.add_line(cursor_horiz1)
        ax.add_patch(dot1)
        ax.add_line(cursor_vert2)
        ax.add_line(cursor_horiz2)
        ax.add_patch(dot2)
        
        ax.set_xlabel('Energy (eV)')
        ax.set_ylabel('Momentum (1/A)')
        self.axs[0,1].set_xlabel('Energy (eV)')
        self.axs[0,1].set_ylabel('intensity (a.u.)')
        initial_xe=1
        
        axe.axvline(x=initial_xe, color='red', linestyle='--',linewidth=2, label='Vertical Line')
        axe.axvline(x=100, color='red', linestyle='--',linewidth=2, label='Vertical Line')
        axe.axhline(y=0, color='red', linestyle='--',linewidth=2, label='Horizontal Line')
        axe.axhline(y=100, color='red', linestyle='--',linewidth=2, label='Horizontal Line')
        plt.draw()
        update_show(self.slider1.value(),self.slider2.value()) 
        self.fig.canvas.draw()
        # def update_cursors():
        self.active_cursor = None
        def on_pick(event):
            # global self.active_cursor
            if event.artist == cursor_vert1:
                self.active_cursor = cursor_vert1
            elif event.artist == cursor_horiz1:
                self.active_cursor = cursor_horiz1
            elif event.artist == dot1:
                self.active_cursor = dot1
            elif event.artist == cursor_vert2:
                self.active_cursor = cursor_vert2
            elif event.artist == cursor_horiz2:
                self.active_cursor = cursor_horiz2
            elif event.artist == dot2:
                self.active_cursor = dot2
            # elif event.artist == cursor_vert_e1:
            #     self.active_cursor = cursor_vert_e1
            elif event.artist == self.Line1:
                self.active_cursor =self. Line1
            elif event.artist == self.Line2:
                self.active_cursor =self. Line2
        self.active_cursor=None
        def on_motion(event):
            # global self.active_cursor
            if self.active_cursor is not None and event.inaxes == ax:
                if self.active_cursor == cursor_vert1:
                    cursor_vert1.set_xdata([event.xdata, event.xdata])
                    dot1.center = (event.xdata, dot1.center[1])
                    print(False)
                elif self.active_cursor == cursor_horiz1:
                    cursor_horiz1.set_ydata([event.ydata, event.ydata])
                    dot1.center = (dot1.center[0], event.ydata)
                elif self.active_cursor == dot1:
                    dot1.center = (event.xdata, event.ydata)
                    cursor_vert1.set_xdata([event.xdata, event.xdata])
                    cursor_horiz1.set_ydata([event.ydata, event.ydata])
                elif self.active_cursor == cursor_vert2:
                    cursor_vert2.set_xdata([event.xdata, event.xdata])
                    dot2.center = (event.xdata, dot2.center[1])
                elif self.active_cursor == cursor_horiz2:
                    cursor_horiz2.set_ydata([event.ydata, event.ydata])
                    dot2.center = (dot2.center[0], event.ydata)
                elif self.active_cursor == dot2:
                    dot2.center = (event.xdata, event.ydata)
                    cursor_vert2.set_xdata([event.xdata, event.xdata])
                    cursor_horiz2.set_ydata([event.ydata, event.ydata])
                # print(dot1.center) 
                self.fig.canvas.draw()
                
                
                plt.draw()
                if dot1.center[0] is not None and dot1.center[1] is not None and dot2.center[0] is not None and dot2.center[1] is not None:
                    x1_pixel=int((dot1.center[0] - self.data_array[self.axes[1]][0]) / (self.data_array[self.axes[1]][-1] - self.data_array[self.axes[1]][0]) * (self.data_array[self.axes[1]].shape[0] - 1) + 0.5)
                    y1_pixel=int((dot1.center[1] - self.data_array[self.axes[0]][0]) / (self.data_array[self.axes[0]][-1] - self.data_array[self.axes[0]][0]) * (self.data_array[self.axes[0]].shape[0] - 1) + 0.5)
                    self.square_coords[0]=(x1_pixel,y1_pixel)
                    x2_pixel=int((dot2.center[0] - self.data_array[self.axes[1]][0]) / (self.data_array[self.axes[1]][-1] - self.data_array[self.axes[1]][0]) * (self.data_array[self.axes[1]].shape[0] - 1) + 0.5)
                    y2_pixel=int((dot2.center[1] - self.data_array[self.axes[0]][0]) / (self.data_array[self.axes[0]][-1] - self.data_array[self.axes[0]][0]) * (self.data_array[self.axes[0]].shape[0] - 1) + 0.5)
                    self.square_coords[1]=(x2_pixel,y2_pixel)
                
                update_show(self.slider1.value(),self.slider2.value()) 
               
            elif self.active_cursor is not None and event.inaxes == axe:
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
                self.v1_pixel=int((self.cursorlinev1 - self.data_array[self.axes[1]][0]) / (self.data_array[self.axes[1]][-1] - self.data_array[self.axes[1]][0]) * (self.data_array[self.axes[1]].shape[0] - 1) + 0.5)
                self.v2_pixel=int((self.cursorlinev2 - self.data_array[self.axes[1]][0]) / (self.data_array[self.axes[1]][-1] - self.data_array[self.axes[1]][0]) * (self.data_array[self.axes[1]].shape[0] - 1) + 0.5)
                # print(self.v1_pixel,self.v2_pixel)
        def on_release(event):
            # global self.active_cursor
            self.active_cursor = None
            
        # Connect pick and motion events
        self.fig.canvas.mpl_connect('pick_event', on_pick)
        self.fig.canvas.mpl_connect('motion_notify_event', on_motion)
        self.fig.canvas.mpl_connect('button_release_event', on_release)
       
        
        self.update_show=update_show
        self.integrate_E=integrate_E
        self.integrate_k=integrate_k
        self.put_cursors=put_cursors
        self.remove_cursors=remove_cursors
   