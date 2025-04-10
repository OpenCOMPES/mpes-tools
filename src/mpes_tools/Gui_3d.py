from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QCheckBox, QAction, QSlider, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
from matplotlib.lines import Line2D

from mpes_tools.fit_panel import fit_panel

import xarray as xr


class GraphWindow(QMainWindow):  #graphic window showing a 2d map controllable with sliders for the third dimension, with cursors showing cuts along the x direction for MDC and y direction for EDC
    def __init__(self,data_array: xr.DataArray,t,dt,technique):
        global t_final
        super().__init__()

        self.setWindowTitle("Graph Window")
        self.setGeometry(100, 100, 1200, 1000)

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
        
        # self.slider1.setFixedSize(200, 12)  # Change the width and height as needed
        # self.slider2.setFixedSize(200, 12)  # Change the width and height as needed
        
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
        
        self.data=data_array
        self.axis=[data_array.coords[dim].data for dim in data_array.dims]
        # print(data_array.dims)
        if technique == 'Phoibos':
            self.axis[1]=self.axis[1]-21.7
            self.data = self.data.assign_coords(Ekin=self.data.coords['Ekin'] -21.7)
        
        self.dt=dt
        # self.datae=np.zeros((len(self.axis[0]),len(self.axis[1])))
        # Plot data
        self.data_t=self.data.isel({self.data.dims[2]:slice(t, t+dt+1)}).sum(dim=self.data.dims[2])
        # self.plot_graph(t,dt)
        self.ssshow(t,dt)
        self.slider1.setRange(0,len(self.axis[2])-1)
        self.slider1_label.setText(self.data.dims[2]+": 0")
        self.slider2_label.setText("Δ"+self.data.dims[2]+": 0")
        self.plot=np.zeros_like(self.data[1,:])
        
        self.slider1.valueChanged.connect(self.slider1_changed)
        self.slider2.valueChanged.connect(self.slider2_changed)
        t_final=self.axis[2].shape[0]
        
        menu_bar = self.menuBar()
        graph_menu1 = menu_bar.addMenu("Fit Panel")
        
        energy_panel_action = QAction('EDC',self)
        energy_panel_action.triggered.connect(self.fit_energy_panel)
        graph_menu1.addAction(energy_panel_action)
        
        momentum_panel_action = QAction('MDC',self)
        momentum_panel_action.triggered.connect(self.fit_momentum_panel)
        graph_menu1.addAction(momentum_panel_action)
        
        box_panel_action = QAction('box',self)
        box_panel_action.triggered.connect(self.fit_box_panel)
        graph_menu1.addAction(box_panel_action)
        
        self.graph_windows=[]
        self.t=t
        print(data_array.dims)
        # 
    def slider1_changed(self,value): # change the slider controlling the third dimension
        # self.slider1_label.setText(str(value))
        base = self.slider1_label.text().split(':')[0]
        self.slider1_label.setText(f"{base}: {self.data[self.data.dims[2]][value].item():.2f}")
        self.update_show(self.slider1.value(),self.slider2.value())
        self.t=self.slider1.value()
    def slider2_changed(self,value): # change the slider controlling the third dimension for windowing
        # self.slider2_label.setText(str(value))
        base = self.slider2_label.text().split(':')[0]
        self.slider2_label.setText(f"{base}: {value}")
        self.update_show(self.slider1.value(),self.slider2.value())
        self.dt=self.slider2.value()
    def checkbox_e_changed(self, state):
        if state == Qt.Checked:
            self.integrate_E()
        else:
            self.update_show(self.slider1.value(),self.slider2.value())
    def checkbox_k_changed(self, state):
        if state == Qt.Checked:
            self.integrate_k()
        else:
            self.update_show(self.slider1.value(),self.slider2.value())
    def checkbox_cursors_changed(self, state):
        if state == Qt.Checked:
            self.put_cursors()
        else:
            self.remove_cursors()
    # def plot_graph(self,t,dt):
        
    #     self.data_t=self.data.isel({self.data.dims[2]:slice(t, t+dt+1)}).sum(dim=self.data.dims[2])
    #     self.axs[0,0].imshow(self.data_t.data, extent=[self.axis[1][0], self.axis[1][-1], self.axis[0][0], self.axis[0][-1]], origin='lower',cmap='terrain',aspect='auto')
        
        
    #     self.axs[0,0].set_title('Sample Graph')
    #     self.axs[0,0].set_xlabel('E-Ef (eV)')
    #     self.axs[0,0].set_ylabel('Angle (degrees)')
    #     self.fig.tight_layout()
    #     self.canvas.draw()
    
    def fit_energy_panel(self,event): # open up the fit panel for the EDC 
        graph_window=fit_panel(self.data,self.square_coords[0][1], self.square_coords[1][1], self.t, self.dt, self.data.dims[1])
        graph_window.show()
        self.graph_windows.append(graph_window)
    def fit_momentum_panel(self,event): # open up the fit panel for the MDC
        graph_window=fit_panel(self.data,self.square_coords[0][0], self.square_coords[1][0], self.t, self.dt, self.data.dims[0])
        graph_window.show()
        self.graph_windows.append(graph_window)
    def fit_box_panel(self,event): # open up the fit panel for the intensity box
        graph_window=fit_panel(self.int,0,0, self.t, self.dt, 'box')
        graph_window.show()
        self.graph_windows.append(graph_window)
        
    
    def ssshow(self, t, dt): # This is where the updates after changing the sliders happen
        
            
        
        # c = self.data.shape[1] // 10 ** (len(str(self.data.shape[1])) - 1)
        
        def put_cursors(): # add cursors in the EDC graph
            # Adjust to use xarray's coords for axis referencing
            self.Line1 = axe.axvline(x=self.cursorlinev1, color='red', linestyle='--', linewidth=2, label='Vertical Line', picker=10)
            self.Line2 = axe.axvline(x=self.cursorlinev2, color='red', linestyle='--', linewidth=2, label='Vertical Line', picker=10)
            plt.draw()
            self.fig.canvas.draw()
    
        def remove_cursors(): # remoe cursors in the EDC graph
            self.Line1.remove()
            self.Line2.remove()
            plt.draw()
            self.fig.canvas.draw()
    
        def integrate_E(): # integrate EDC between the two cursors in the main graph
            self.axs[1, 0].clear()
            plt.draw()
    
            x_min = int(min(self.square_coords[1][1], self.square_coords[0][1]))
            x_max = int(max(self.square_coords[1][1], self.square_coords[0][1])) + 1
    
            self.data_t.isel({self.data.dims[0]:slice(x_min, x_max)}).sum(dim=self.data.dims[0]).plot(ax=self.axs[1,0])

    
        def integrate_k(): # integrate MDC between the two cursors in the main graph
            self.axs[0, 1].clear()
            plt.draw()
    
            x_min = int(min(self.square_coords[0][0], self.square_coords[1][0]))
            x_max = int(max(self.square_coords[0][0], self.square_coords[1][0])) + 1
    
            self.data_t.isel({self.data.dims[1]:slice(x_min, x_max)}).sum(dim=self.data.dims[1]).plot(ax=self.axs[0,1])
    
        def box(): # generate the intensity graph between the four cursors in the main graph
            self.int = np.zeros_like(self.axis[2])
            self.axs[1, 1].clear()
            x0, y0 = map(int, self.square_coords[0])
            x1, y1 = map(int, self.square_coords[1])
    
            # Ensure (x0, y0) is the top-left corner and (x1, y1) is the bottom-right
            x0, x1 = sorted([x0, x1])
            y0, y1 = sorted([y0, y1])
    
            self.int = self.data.isel({self.data.dims[0]: slice(y0, y1), self.data.dims[1]: slice(x0, x1)}).sum(dim=(self.data.dims[0], self.data.dims[1]))
            
            if x0 != x1 and y0 != y1:
                N = -1
                
                self.int.plot(ax=self.axs[1,1])
                self.dot, = self.axs[1, 1].plot([self.axis[2][self.slider1.value()]], [self.int[self.slider1.value()]], 'ro', markersize=8)
                self.fig.canvas.draw_idle()
    
        # def us(self): 
        #     update_show(self.slider1.value(), self.slider2.value())
    
        def update_show(t, dt): # update the main graph as well as the relevant EDC and MDC cuts. Also the box intensity
            self.axs[0, 1].clear()
            self.axs[1, 0].clear()
            self.data_t=self.data.isel({self.data.dims[2]:slice(t, t+dt+1)}).sum(dim=self.data.dims[2])
            im6.set_array(self.data_t)
            if self.checkbox_e.isChecked() and self.checkbox_k.isChecked():
                integrate_E()
                integrate_k()
            elif self.checkbox_e.isChecked():
                integrate_E()
                self.data_t.isel({self.data.dims[1]: int(self.square_coords[0][0])}).plot(ax=self.axs[0, 1], color='orange')
                self.data_t.isel({self.data.dims[1]:int(self.square_coords[1][0])}).plot(ax=self.axs[0, 1], color='green')
                
            elif self.checkbox_k.isChecked():
                integrate_k()
                self.data_t.isel({self.data.dims[0]:self.square_coords[0][1]}).plot(ax=self.axs[1, 0], color='orange')
                self.data_t.isel({self.data.dims[0]:self.square_coords[1][1]}).plot(ax=self.axs[1, 0], color='green')
                
            else:
                self.data_t.isel({self.data.dims[0]:self.square_coords[0][1]}).plot(ax=self.axs[1,0],color='orange')
                self.data_t.isel({self.data.dims[0]:self.square_coords[1][1]}).plot(ax=self.axs[1,0],color='green')
                self.data_t.isel({self.data.dims[1]:int(self.square_coords[0][0])}).plot(ax=self.axs[0,1],color='orange')
                self.data_t.isel({self.data.dims[1]:int(self.square_coords[1][0])}).plot(ax=self.axs[0,1],color='green')
                
                
    
            if self.checkbox_cursors.isChecked():
                self.Line1 = self.axs[1, 0].axvline(x=self.cursorlinev1, color='red', linestyle='--', linewidth=2, label='Vertical Line', picker=10)
                self.Line2 = self.axs[1, 0].axvline(x=self.cursorlinev2, color='red', linestyle='--', linewidth=2, label='Vertical Line', picker=10)
                plt.draw()
                self.fig.canvas.draw()
    
            box()
            time1 = self.axis[2][t]
            timedt1 = self.axis[2][t + dt]
            self.axs[0, 0].set_title(f't: {time1:.2f}, t+dt: {timedt1}')
            self.fig.canvas.draw()
            plt.draw()
        
        self.data.isel({self.data.dims[2]:slice(t, t+dt+1)}).sum(dim=self.data.dims[2])
        
        im6 = self.axs[0, 0].imshow(self.data_t.data, extent=[self.axis[1][0], self.axis[1][-1], self.axis[0][0], self.axis[0][-1]], origin='lower',cmap='terrain', aspect='auto')
        
        # define the cursors in the main graph
        
        initial_x = 0
        initial_y = 0
        initial_x2 = 0.5
        initial_y2 = 0.5
        ax = self.axs[0, 0]
        axe = self.axs[1, 0]
    
        ymin, ymax = self.axs[0, 0].get_ylim()
        xmin, xmax = self.axs[0, 0].get_ylim()
        ymin, ymax = 5 * ymin, 5 * ymax
        xmin, xmax = 5 * xmin, 5 * xmax
        cursor_vert1 = Line2D([initial_x, initial_x], [ymin, ymax], color='yellow', linewidth=2, picker=10, linestyle='--')
        cursor_horiz1 = Line2D([xmin, xmax], [initial_y, initial_y], color='yellow', linewidth=2, picker=10, linestyle='--')
        cursor_vert2 = Line2D([initial_x2, initial_x2], [ymin, ymax], color='green', linewidth=2, picker=10, linestyle='--')
        cursor_horiz2 = Line2D([xmin, xmax], [initial_y2, initial_y2], color='green', linewidth=2, picker=10, linestyle='--')
        
        # define the dots that connect the cursors
        dot1 = Circle((initial_x, initial_y), radius=0.05, color='yellow', picker=10)
        dot2 = Circle((initial_x2, initial_y2), radius=0.05, color='green', picker=10)
    
        if dot1.center[0] is not None and dot1.center[1] is not None and dot2.center[0] is not None and dot2.center[1] is not None:
            x1_pixel = int((dot1.center[0] - self.axis[1][0]) / (self.axis[1][-1] - self.axis[1][0]) * (self.axis[1].shape[0] - 1) + 0.5)
            y1_pixel = int((dot1.center[1] - self.axis[0][0]) / (self.axis[0][-1] - self.axis[0][0]) * (self.axis[0].shape[0] - 1) + 0.5)
            self.square_coords[0] = (x1_pixel, y1_pixel)
            x2_pixel = int((dot2.center[0] - self.axis[1][0]) / (self.axis[1][-1] - self.axis[1][0]) * (self.axis[1].shape[0] - 1) + 0.5)
            y2_pixel = int((dot2.center[1] - self.axis[0][0]) / (self.axis[0][-1] - self.axis[0][0]) * (self.axis[0].shape[0] - 1) + 0.5)
            self.square_coords[1] = (x2_pixel, y2_pixel)
    
        ax.add_line(cursor_vert1)
        ax.add_line(cursor_horiz1)
        ax.add_patch(dot1)
        ax.add_line(cursor_vert2)
        ax.add_line(cursor_horiz2)
        ax.add_patch(dot2)
    
        ax.set_xlabel('Energy (eV)')
        ax.set_ylabel('Momentum (1/A)')
        self.axs[0, 1].set_xlabel('Energy (eV)')
        self.axs[0, 1].set_ylabel('intensity (a.u.)')
        initial_xe=1
        
        axe.axvline(x=initial_xe, color='red', linestyle='--',linewidth=2, label='Vertical Line')
        axe.axvline(x=100, color='red', linestyle='--',linewidth=2, label='Vertical Line')
        axe.axhline(y=0, color='red', linestyle='--',linewidth=2, label='Horizontal Line')
        axe.axhline(y=100, color='red', linestyle='--',linewidth=2, label='Horizontal Line')
        plt.draw()
        update_show(self.slider1.value(),self.slider2.value()) 
        self.fig.canvas.draw()
        self.active_cursor = None
        def on_pick(event): # function to pick up the cursors or the dots
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
            elif event.artist == self.Line1:
                self.active_cursor =self. Line1
            elif event.artist == self.Line2:
                self.active_cursor =self. Line2
        self.active_cursor=None
        def on_motion(event): # function to move the cursors or the dots
            if self.active_cursor is not None and event.inaxes == ax:
                if self.active_cursor == cursor_vert1:
                    cursor_vert1.set_xdata([event.xdata, event.xdata])
                    dot1.center = (event.xdata, dot1.center[1])
                    # print(False)
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
                self.fig.canvas.draw()
                
                
                plt.draw()
                if dot1.center[0] is not None and dot1.center[1] is not None and dot2.center[0] is not None and dot2.center[1] is not None: # convert the value of the pixel to the value of the slot in the data
                    x1_pixel=int((dot1.center[0] - self.axis[1][0]) / (self.axis[1][-1] - self.axis[1][0]) * (self.axis[1].shape[0] - 1) + 0.5)
                    y1_pixel=int((dot1.center[1] - self.axis[0][0]) / (self.axis[0][-1] - self.axis[0][0]) * (self.axis[0].shape[0] - 1) + 0.5)
                    self.square_coords[0]=(x1_pixel,y1_pixel)
                    x2_pixel=int((dot2.center[0] - self.axis[1][0]) / (self.axis[1][-1] - self.axis[1][0]) * (self.axis[1].shape[0] - 1) + 0.5)
                    y2_pixel=int((dot2.center[1] - self.axis[0][0]) / (self.axis[0][-1] - self.axis[0][0]) * (self.axis[0].shape[0] - 1) + 0.5)
                    self.square_coords[1]=(x2_pixel,y2_pixel)
                    
                update_show(self.slider1.value(),self.slider2.value()) 
               
            elif self.active_cursor is not None and event.inaxes == axe:
                if self.active_cursor == self.Line1:
                    self.Line1.set_xdata([event.xdata, event.xdata])
                    self.cursorlinev1= event.xdata
                elif self.active_cursor == self.Line2:
                    self.Line2.set_xdata([event.xdata, event.xdata])
                    self.cursorlinev2= event.xdata
                self.fig.canvas.draw()
                plt.draw()
                self.v1_pixel=int((self.cursorlinev1 - self.axis[1][0]) / (self.axis[1][-1] - self.axis[1][0]) * (self.axis[1].shape[0] - 1) + 0.5)
                self.v2_pixel=int((self.cursorlinev2 - self.axis[1][0]) / (self.axis[1][-1] - self.axis[1][0]) * (self.axis[1].shape[0] - 1) + 0.5)
        def on_release(event):# function to release the selected object
            self.active_cursor = None
            
        self.fig.canvas.mpl_connect('pick_event', on_pick)
        self.fig.canvas.mpl_connect('motion_notify_event', on_motion)
        self.fig.canvas.mpl_connect('button_release_event', on_release)
       
        
        self.update_show=update_show
        self.integrate_E=integrate_E
        self.integrate_k=integrate_k
        self.put_cursors=put_cursors
        self.remove_cursors=remove_cursors
   