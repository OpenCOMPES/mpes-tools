import sys
from PyQt5.QtWidgets import QApplication,QMainWindow, QVBoxLayout, QWidget, QCheckBox, QAction, QSlider, QHBoxLayout, QLabel,QLineEdit,QPushButton
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
from matplotlib.lines import Line2D
import json
import pickle
from mpes_tools.fit_panel import fit_panel
from IPython.core.getipython import get_ipython

import xarray as xr

#graphic window showing a 2d map controllable with sliders for the third dimension, with cursors showing cuts along the x direction for MDC and y direction for EDC
# Two vertical cursors and two horizontal cursors are defined in the main graph with each same color for the cursors being horizontal and vertical intercept each other in a dot so one can move either each cursor or the dot itself which will move both cursors. 
class Gui_3d(QMainWindow):  
    def __init__(self,data_array: xr.DataArray,t,dt,technique):
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
        # plt.ioff()
        # add the checkboxes for EDC and MDC integration and the button to save the results
        self.checkbox_e = QCheckBox("Integrate_energy")
        self.checkbox_e.stateChanged.connect(self.checkbox_e_changed)
        
        self.checkbox_k = QCheckBox("Integrate_k")
        self.checkbox_k.stateChanged.connect(self.checkbox_k_changed)

        self.save_button = QPushButton('Extract results', self)
        self.save_button.clicked.connect(self.create_new_cell)
        # self.save_button.clicked.connect(self.save_results)
        
        #create the layout
        h_layout = QHBoxLayout()
        self.cursor_label=[]
        self.cursor_inputs = []
        cursors_names=['yellow_vertical', 'yellow_horizontal','green_vertical', 'green_horizontal']
        for i in range(4):
            sub_layout = QVBoxLayout()
            # label = QLabel(f"Cursor {i+1}:")
            label=QLabel(cursors_names[i])
            input_field = QLineEdit()
            input_field.setPlaceholderText("Value")
            input_field.setFixedWidth(80)
            input_field.editingFinished.connect(lambda i=i: self.main_graph_cursor_changed(i))
            self.cursor_inputs.append(input_field)
            self.cursor_label.append(label)
            sub_layout.addWidget(label)
            sub_layout.addWidget(input_field)
            h_layout.addLayout(sub_layout)

        checkbox_layout= QHBoxLayout()
        # Add the canvas to the layout
        checkbox_layout.addWidget(self.checkbox_e)
        checkbox_layout.addWidget(self.checkbox_k)
        layout.addLayout(checkbox_layout)
        layout.addLayout(h_layout)
        layout.addWidget(self.canvas)
        layout.addWidget(self.save_button)
        
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
        
        # Create a layout for the central widget
        slider_layout.addWidget(self.slider1)
        slider_layout.addWidget(self.slider1_label)
        slider_layout.addWidget(self.slider2)
        slider_layout.addWidget(self.slider2_label)
        layout.addLayout(slider_layout)

        #define the data_array
        self.data=data_array
        self.axis=[data_array.coords[dim].data for dim in data_array.dims]
        if technique == 'Phoibos':
            self.axis[1]=self.axis[1]-21.7
            self.data = self.data.assign_coords(Ekin=self.data.coords['Ekin'] -21.7)

        # define the cut for the spectra of the main graph
        self.data2D_plot=self.data.isel({self.data.dims[2]:slice(t, t+dt+1)}).sum(dim=self.data.dims[2])
        
        #Initialize the relevant prameters
        self.t=t
        self.dt=dt
        self.active_cursor = None
        self.Line1=None
        self.Line2=None
        self.cursor_vert1 = []
        self.cursor_horiz1 = []
        self.cursor_vert2 =[]
        self.cursor_horiz2 = []
        self.integrated_edc=None
        self.integrated_mdc=None
        
        # sliders for the delay
        self.slider1.setRange(0,len(self.axis[2])-1)
        self.slider1_label.setText(self.data.dims[2]+": 0")
        self.slider2_label.setText("Δ"+self.data.dims[2]+": 0")
        
        self.slider1.valueChanged.connect(self.slider1_changed)
        self.slider2.valueChanged.connect(self.slider2_changed)
        
        #run the main code to show the graphs and cursors
        self.show_graphs(t,dt)
        
        #create a menu for the fit panel
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
        
        print(data_array.dims)

    def create_new_cell(self):
        content = f"""
# Code generated by GUI for the following parameters:
import matplotlib.pyplot as plt

# data= 'your data_array'
data=V1
data = data.assign_coords(Ekin=data.coords['Ekin'] -21.7)
time1={self.axis[2][self.slider1.value()]}
time2={self.axis[2][self.slider1.value()+self.slider2.value()]}
t={self.slider1.value()}
dt={self.slider2.value()}
data2D_plot=data.isel({{data.dims[2]:slice(t, t+dt+1)}}).sum(dim=data.dims[2])
yellowline_edc_energy={self.dot1.center[1]}
greenline_edc_energy={self.dot2.center[1]}
yellowline_mdc_momentum={self.dot1.center[0]}
greenline_mdc_momentum={self.dot2.center[0]}
#plot Data_2d between t and t+dt
fig,ax=plt.subplots(1,1,figsize=(12,8))
data2D_plot.plot(ax=ax, cmap='terrain', add_colorbar=False)
#plot EDC yellow and green
fig,ax=plt.subplots(1,1,figsize=(12,8))
data2D_plot.sel({{data.dims[0]:yellowline_edc_energy}}, method='nearest').plot(ax=ax,color='orange')
data2D_plot.sel({{data.dims[0]:greenline_edc_energy}}, method='nearest').plot(ax=ax,color='green')
#plot integrated EDC
fig,ax=plt.subplots(1,1,figsize=(12,8))
data2D_plot.sel({{data.dims[0]:slice(min(greenline_edc_energy,yellowline_edc_energy), max(greenline_edc_energy,yellowline_edc_energy))}}).sum(dim=data.dims[0]).plot(ax=ax)
#plot MDC yellow and green
fig,ax=plt.subplots(1,1,figsize=(12,8))
data2D_plot.sel({{data.dims[1]:yellowline_mdc_momentum}}, method='nearest').plot(ax=ax,color='orange')
data2D_plot.sel({{data.dims[1]:greenline_mdc_momentum}}, method='nearest').plot(ax=ax,color='green')
#plot integrated MDC
fig,ax=plt.subplots(1,1,figsize=(12,8))
data2D_plot.sel({{data.dims[1]:slice(min(greenline_mdc_momentum,yellowline_mdc_momentum), max(greenline_mdc_momentum,yellowline_mdc_momentum))}}).sum(dim=data.dims[1]).plot(ax=ax)
#plot integrated intensity in the box between the cursors
fig,ax=plt.subplots(1,1,figsize=(12,8))
x0,y0=({self.dot1.center[0]},{self.dot1.center[1]})
x1,y1=({self.dot2.center[0]},{self.dot2.center[1]})
x0, x1 = sorted([x0, x1])
y0, y1 = sorted([y0, y1])
data.loc[{{data.dims[0]: slice(y0, y1), data.dims[1]: slice(x0, x1)}}].sum(dim=(data.dims[0], data.dims[1])).plot(ax=ax)

        """
        shell = get_ipython()
        payload = dict(
            source='set_next_input',
            text=content,
            replace=False,
        )
        shell.payload_manager.write_payload(payload, single=False)
        print('results extracted!')
    def save_results(self):#save the relevant results in a .pkl file which can be accessed easily for Jupyter Notebook workflow
        print('res')
        results = {
            'integrated_edc': self.integrated_edc,
            'integrated_mdc': self.integrated_mdc,
            'yellowline_edc': self.data2D_plot.sel({self.data.dims[0]:self.dot1.center[1]}, method='nearest'), 
            'greenline_edc': self.data2D_plot.sel({self.data.dims[0]:self.dot2.center[1]}, method='nearest'),
            'yellowline_mdc': self.data2D_plot.sel({self.data.dims[1]: self.dot1.center[0]}, method='nearest'),
            'greenline_mdc': self.data2D_plot.sel({self.data.dims[1]: self.dot2.center[0]}, method='nearest'),
            'current_spectra': self.data2D_plot,
            'intensity_box': self.int,
            'yellow_vertical': self.dot1.center[0],
            'yellow_horizontal': self.dot1.center[1],
            'green_vertical': self.dot2.center[0],
            'green_horizontal': self.dot2.center[1],
            'delay1':self.axis[2][self.slider1.value()],
            'delay2':self.axis[2][self.slider1.value()+self.slider2.value()]
        }
        with open('gui_results.pkl', 'wb') as f:
            pickle.dump(results, f)
        # with open('gui_results.json', 'w') as f:
        #     json.dump(results, f)
        print("Results saved!")
                  
    def main_graph_cursor_changed(self, index): #set manually the values for the cursors in the main graph
        value = self.cursor_inputs[index].text()
        value=float(value)
        if index ==0: 
            self.cursor_vert1.set_xdata([value, value])
            self.dot1.center = (value,self.dot1.center[1])
            base = self.cursor_label[0].text().split(':')[0]
            self.cursor_label[0].setText(f"{base}: {value:.2f}")
        elif index ==1:
            self.cursor_horiz1.set_ydata([value, value])
            self.dot1.center = (self.dot1.center[0], value)
            base = self.cursor_label[1].text().split(':')[0]
            self.cursor_label[1].setText(f"{base}: {value:.2f}")
        elif index ==2: 
            self.cursor_vert2.set_xdata([value, value])
            self.dot2.center = (value,self.dot2.center[1])
            base = self.cursor_label[2].text().split(':')[0]
            self.cursor_label[2].setText(f"{base}: {value:.2f}")
        elif index ==3:
            self.cursor_horiz2.set_ydata([value, value])
            self.dot2.center = (self.dot2.center[0], value)
            base = self.cursor_label[3].text().split(':')[0]
            self.cursor_label[3].setText(f"{base}: {value:.2f}")
        # self.change_pixel_to_arrayslot()
        self.update_show(self.slider1.value(),self.slider2.value())
        try:
            num = float(value)
            # print(f"Cursor {index+1} changed to: {num}")
            # Update graph logic here
        except ValueError:
            print("Invalid input!")
        
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
    def checkbox_e_changed(self, state): # Checkbox for integrating the EDC between the cursors
        if state == Qt.Checked:
            self.integrate_E()
        else:
            self.update_show(self.slider1.value(),self.slider2.value())
    def checkbox_k_changed(self, state): # Checkbox for integrating the MDC between the cursors
        if state == Qt.Checked:
            self.integrate_k()
        else:
            self.update_show(self.slider1.value(),self.slider2.value())

    
    def fit_energy_panel(self,event): # open up the fit panel for the EDC 
        graph_window=fit_panel(self.data,self.dot1.center[1], self.dot2.center[1], self.t, self.dt, self.data.dims[1])
        graph_window.show()
        self.graph_windows.append(graph_window)
    def fit_momentum_panel(self,event): # open up the fit panel for the MDC
        graph_window=fit_panel(self.data,self.dot1.center[0], self.dot2.center[0], self.t, self.dt, self.data.dims[0])
        graph_window.show()
        self.graph_windows.append(graph_window)
    def fit_box_panel(self,event): # open up the fit panel for the intensity box
        graph_window=fit_panel(self.int,0,0, self.t, self.dt, 'box')
        graph_window.show()
        self.graph_windows.append(graph_window)
        
    
    def show_graphs(self, t, dt): # This is where the updates after changing the sliders happen
    
        def integrate_E(): # integrate EDC between the two cursors in the main graph
            self.axs[1, 0].clear()
            # plt.draw()
    
            x_min = min(self.dot2.center[1], self.dot1.center[1])
            x_max = max(self.dot2.center[1], self.dot1.center[1])
            
            # self.data2D_plot.isel({self.data.dims[0]:slice(x_min, x_max)}).sum(dim=self.data.dims[0]).plot(ax=self.axs[1,0])
            self.integrated_edc=self.data2D_plot.sel({self.data.dims[0]:slice(x_min, x_max)}).sum(dim=self.data.dims[0])
            self.integrated_edc.plot(ax=self.axs[1,0])
            self.fig.canvas.draw_idle()
    
        def integrate_k(): # integrate MDC between the two cursors in the main graph
            self.axs[0, 1].clear()
            # plt.draw()
    
            x_min = min(self.dot1.center[0], self.dot2.center[0])
            x_max = max(self.dot1.center[0], self.dot2.center[0])
            print (x_min, x_max)
            # self.data2D_plot.isel({self.data.dims[1]:slice(x_min, x_max)}).sum(dim=self.data.dims[1]).plot(ax=self.axs[0,1])
            self.integrated_mdc=self.data2D_plot.sel({self.data.dims[1]:slice(x_min, x_max)}).sum(dim=self.data.dims[1])
            self.integrated_mdc.plot(ax=self.axs[0,1])
            self.fig.canvas.draw_idle()
    
        def box(): # generate the intensity graph between the four cursors in the main graph
            self.axs[1, 1].clear()
            
            x0,y0=self.dot1.center
            x1,y1=self.dot2.center
    
            # Ensure (x0, y0) is the top-left corner and (x1, y1) is the bottom-right
            x0, x1 = sorted([x0, x1])
            y0, y1 = sorted([y0, y1])
    
            self.int = self.data.loc[{self.data.dims[0]: slice(y0, y1), self.data.dims[1]: slice(x0, x1)}].sum(dim=(self.data.dims[0], self.data.dims[1]))
            if x0 != x1 and y0 != y1:
                
                self.int.plot(ax=self.axs[1,1])
                self.dot, = self.axs[1, 1].plot([self.axis[2][self.slider1.value()]], [self.int[self.slider1.value()]], 'ro', markersize=8)
                self.fig.canvas.draw_idle()
    
        def update_show(t, dt): # update the main graph as well as the relevant EDC and MDC cuts. Also the box intensity
            self.axs[0, 1].clear()
            self.axs[1, 0].clear()
            #update the main graph/ spectra
            self.data2D_plot=self.data.isel({self.data.dims[2]:slice(t, t+dt+1)}).sum(dim=self.data.dims[2])
            im.set_array(self.data2D_plot)
            # show the cuts for the EDC and MDC
            if self.checkbox_e.isChecked() and self.checkbox_k.isChecked():
                integrate_E()
                integrate_k()
            elif self.checkbox_e.isChecked():
                integrate_E()
                self.data2D_plot.sel({self.data.dims[1]:self.dot1.center[0]}, method='nearest').plot(ax=self.axs[0, 1], color='orange')
                self.data2D_plot.sel({self.data.dims[1]:self.dot2.center[0]}, method='nearest').plot(ax=self.axs[0, 1], color='green')
                
            elif self.checkbox_k.isChecked():
                integrate_k()
                self.data2D_plot.sel({self.data.dims[0]:self.dot1.center[1]}, method='nearest').plot(ax=self.axs[1, 0], color='orange')
                self.data2D_plot.sel({self.data.dims[0]:self.dot2.center[1]}, method='nearest').plot(ax=self.axs[1, 0], color='green')
                
            else: 
                self.data2D_plot.sel({self.data.dims[0]:self.dot1.center[1]}, method='nearest').plot(ax=self.axs[1,0],color='orange')
                self.data2D_plot.sel({self.data.dims[0]:self.dot2.center[1]}, method='nearest').plot(ax=self.axs[1,0],color='green')
                self.data2D_plot.sel({self.data.dims[1]:self.dot1.center[0]}, method='nearest').plot(ax=self.axs[0,1],color='orange')
                self.data2D_plot.sel({self.data.dims[1]:self.dot2.center[0]}, method='nearest').plot(ax=self.axs[0,1],color='green')

            
            box() # update the intensity box graph
            time1 = self.axis[2][t]
            timedt1 = self.axis[2][t + dt]
            self.axs[0, 0].set_title(f't: {time1:.2f}, t+dt: {timedt1:.2f}')
            self.fig.canvas.draw_idle()
            plt.draw()
        
        # plot the main graph
        im = self.data2D_plot.plot(ax=self.axs[0, 0], cmap='terrain', add_colorbar=False)
        
        # define the initial positions of the cursors in the main graph
        
        initial_x = 0
        initial_y = 0
        initial_x2 = 0.5
        initial_y2 = 0.5
        ax = self.axs[0, 0]
        # define the lines for the cursors
        ymin, ymax = self.axs[0, 0].get_ylim()
        xmin, xmax = self.axs[0, 0].get_ylim()
        ymin, ymax = 5 * ymin, 5 * ymax
        xmin, xmax = 5 * xmin, 5 * xmax
        self.cursor_vert1 = Line2D([initial_x, initial_x], [ymin, ymax], color='yellow', linewidth=2, picker=10, linestyle='--')
        self.cursor_horiz1 = Line2D([xmin, xmax], [initial_y, initial_y], color='yellow', linewidth=2, picker=10, linestyle='--')
        self.cursor_vert2 = Line2D([initial_x2, initial_x2], [ymin, ymax], color='green', linewidth=2, picker=10, linestyle='--')
        self.cursor_horiz2 = Line2D([xmin, xmax], [initial_y2, initial_y2], color='green', linewidth=2, picker=10, linestyle='--')
        
        # show the initial values of the cursors 
        base = self.cursor_label[0].text().split(':')[0]
        self.cursor_label[0].setText(f"{base}: {initial_x:.2f}")
        base = self.cursor_label[1].text().split(':')[0]
        self.cursor_label[1].setText(f"{base}: {initial_x:.2f}")
        base = self.cursor_label[2].text().split(':')[0]
        self.cursor_label[2].setText(f"{base}: {initial_x2:.2f}")
        base = self.cursor_label[3].text().split(':')[0]
        self.cursor_label[3].setText(f"{base}: {initial_y2:.2f}")
        
        # define the dots that connect the cursors
        self.dot1 = Circle((initial_x, initial_y), radius=0.05, color='yellow', picker=10)
        self.dot2 = Circle((initial_x2, initial_y2), radius=0.05, color='green', picker=10)
        
        # add the lines and the cursors to the main graph
        ax.add_line(self.cursor_vert1)
        ax.add_line(self.cursor_horiz1)
        ax.add_patch(self.dot1)
        ax.add_line(self.cursor_vert2)
        ax.add_line(self.cursor_horiz2)
        ax.add_patch(self.dot2)
    
        # self.change_pixel_to_arrayslot()
        
        # define the integrated EDC and MDC 
        x_min = min(self.dot2.center[1], self.dot1.center[1])
        x_max = max(self.dot2.center[1], self.dot1.center[1])
        self.integrated_edc=self.data2D_plot.sel({self.data.dims[0]:slice(x_min, x_max)}).sum(dim=self.data.dims[0])
        x_min = min(self.dot1.center[0], self.dot2.center[0])
        x_max = max(self.dot1.center[0], self.dot2.center[0])
        self.integrated_mdc=self.data2D_plot.sel({self.data.dims[1]:slice(x_min, x_max)}).sum(dim=self.data.dims[1])

        plt.draw()
        update_show(self.slider1.value(),self.slider2.value()) 
        self.fig.canvas.draw_idle()
        self.active_cursor = None
        def on_pick(event): # function to pick up the cursors or the dots
            if event.artist == self.cursor_vert1:
                self.active_cursor = self.cursor_vert1
            elif event.artist == self.cursor_horiz1:
                self.active_cursor = self.cursor_horiz1
            elif event.artist == self.dot1:
                self.active_cursor = self.dot1
            elif event.artist == self.cursor_vert2:
                self.active_cursor = self.cursor_vert2
            elif event.artist == self.cursor_horiz2:
                self.active_cursor = self.cursor_horiz2
            elif event.artist == self.dot2:
                self.active_cursor = self.dot2
            elif event.artist == self.Line1:
                self.active_cursor =self. Line1
            elif event.artist == self.Line2:
                self.active_cursor =self. Line2
        self.active_cursor=None
        def on_motion(event): # function to move the cursors or the dots
            if self.active_cursor is not None and event.inaxes == ax:
                if self.active_cursor == self.cursor_vert1:
                    self.cursor_vert1.set_xdata([event.xdata, event.xdata])
                    self.dot1.center = (event.xdata, self.dot1.center[1])
                    base = self.cursor_label[0].text().split(':')[0]
                    self.cursor_label[0].setText(f"{base}: {event.xdata:.2f}")
                elif self.active_cursor == self.cursor_horiz1:
                    self.cursor_horiz1.set_ydata([event.ydata, event.ydata])
                    self.dot1.center = (self.dot1.center[0], event.ydata)
                    base = self.cursor_label[1].text().split(':')[0]
                    self.cursor_label[1].setText(f"{base}: {event.ydata:.2f}")
                elif self.active_cursor == self.dot1:
                    self.dot1.center = (event.xdata, event.ydata)
                    self.cursor_vert1.set_xdata([event.xdata, event.xdata])
                    self.cursor_horiz1.set_ydata([event.ydata, event.ydata])
                    base = self.cursor_label[0].text().split(':')[0]
                    self.cursor_label[0].setText(f"{base}: {event.xdata:.2f}")
                    base = self.cursor_label[1].text().split(':')[0]
                    self.cursor_label[1].setText(f"{base}: {event.ydata:.2f}")
                elif self.active_cursor == self.cursor_vert2:
                    self.cursor_vert2.set_xdata([event.xdata, event.xdata])
                    self.dot2.center = (event.xdata, self.dot2.center[1])
                    base = self.cursor_label[2].text().split(':')[0]
                    self.cursor_label[2].setText(f"{base}: {event.xdata:.2f}")
                elif self.active_cursor == self.cursor_horiz2:
                    self.cursor_horiz2.set_ydata([event.ydata, event.ydata])
                    self.dot2.center = (self.dot2.center[0], event.ydata)
                    base = self.cursor_label[3].text().split(':')[0]
                    self.cursor_label[3].setText(f"{base}: {event.ydata:.2f}")
                elif self.active_cursor == self.dot2:
                    self.dot2.center = (event.xdata, event.ydata)
                    self.cursor_vert2.set_xdata([event.xdata, event.xdata])
                    self.cursor_horiz2.set_ydata([event.ydata, event.ydata])
                    base = self.cursor_label[2].text().split(':')[0]
                    self.cursor_label[2].setText(f"{base}: {event.xdata:.2f}")
                    base = self.cursor_label[3].text().split(':')[0]
                    self.cursor_label[3].setText(f"{base}: {event.ydata:.2f}")
                self.fig.canvas.draw_idle()
                plt.draw()
                
                # self.change_pixel_to_arrayslot()
                update_show(self.slider1.value(),self.slider2.value()) 
               
            
        def on_release(event):# function to release the selected object
            self.active_cursor = None
            
        self.fig.canvas.mpl_connect('pick_event', on_pick)
        self.fig.canvas.mpl_connect('motion_notify_event', on_motion)
        self.fig.canvas.mpl_connect('button_release_event', on_release)
       
        
        self.update_show=update_show
        self.integrate_E=integrate_E
        self.integrate_k=integrate_k

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = GraphWindow()
#     window.show()
#     sys.exit(app.exec_()) 