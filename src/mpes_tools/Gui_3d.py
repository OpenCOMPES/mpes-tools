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

import xarray as xr


class Gui_3d(QMainWindow):  #graphic window showing a 2d map controllable with sliders for the third dimension, with cursors showing cuts along the x direction for MDC and y direction for EDC
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

        self.save_button = QPushButton('Save Results', self)
        self.save_button.clicked.connect(self.save_results)
        
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
        # layout.addWidget(self.checkbox_cursors)
        
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
        self.square_coords = [[0, 0], [0, 0]]  # To store the coordinates of the dots
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
        
        self.t=t
        self.dt=dt
        self.data_t=self.data.isel({self.data.dims[2]:slice(t, t+dt+1)}).sum(dim=self.data.dims[2])
        self.cursor_vert1 = []
        self.cursor_horiz1 = []
        self.cursor_vert2 =[]
        self.cursor_horiz2 = []
        self.integrated_edc=None
        self.integrated_mdc=None
        
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
        
        print(data_array.dims)

    

    def save_results(self):
        results = {
            'integrated_edc': self.integrated_edc,
            'integrated_mdc': self.integrated_mdc,
            'yellowline_edc': self.data_t.isel({self.data.dims[0]:self.square_coords[0][1]}),
            'greenline_edc': self.data_t.isel({self.data.dims[0]:self.square_coords[1][1]}),
            'yellowline_mdc': self.data_t.isel({self.data.dims[1]: int(self.square_coords[0][0])}),
            'greenline_mdc': self.data_t.isel({self.data.dims[1]: int(self.square_coords[1][0])}),
            'current_spectra': self.data_t,
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
        
    def results_3d(self):
        def integrated_edc(self):
            return self.integrated_edc
        def integrated_mdc(self):
            return self.integrated_mdc
        def yellowline_edc(self):
            return self.data_t.isel({self.data.dims[0]:self.square_coords[0][1]})
        def greenline_edc(self):
            return self.data_t.isel({self.data.dims[0]:self.square_coords[1][1]})
        def yellowline_mdc(self):
            return self.data_t.isel({self.data.dims[1]: int(self.square_coords[0][0])})
        def greenline_mdc(self):
            return self.data_t.isel({self.data.dims[1]: int(self.square_coords[1][0])})
        def current_spectra(self):
            return self.data_t
        def intensity_box(self):
            return self.int
        def yellow_vertical(self):
            return self.dot1.center[0]
        def yellow_horizontal(self):
            return self.dot1.center[1]
        def green_vertical(self):
            return self.dot2.center[0]
        def green_horizontal(self):
            return self.dot2.center[1]
        
        
    def main_graph_cursor_changed(self, index):
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
        self.change_pixel_to_arrayslot()
        self.update_show(self.slider1.value(),self.slider2.value())
        try:
            num = float(value)
            # print(f"Cursor {index+1} changed to: {num}")
            # Update graph logic here
        except ValueError:
            print("Invalid input!")
    def change_pixel_to_arrayslot(self):# convert the value of the pixel to the value of the slot in the data
        if self.dot1.center[0] is not None and self.dot1.center[1] is not None and self.dot2.center[0] is not None and self.dot2.center[1] is not None: 
            x1_pixel=int((self.dot1.center[0] - self.axis[1][0]) / (self.axis[1][-1] - self.axis[1][0]) * (self.axis[1].shape[0] - 1) + 0.5)
            y1_pixel=int((self.dot1.center[1] - self.axis[0][0]) / (self.axis[0][-1] - self.axis[0][0]) * (self.axis[0].shape[0] - 1) + 0.5)
            self.square_coords[0]=[x1_pixel,y1_pixel]
            x2_pixel=int((self.dot2.center[0] - self.axis[1][0]) / (self.axis[1][-1] - self.axis[1][0]) * (self.axis[1].shape[0] - 1) + 0.5)
            y2_pixel=int((self.dot2.center[1] - self.axis[0][0]) / (self.axis[0][-1] - self.axis[0][0]) * (self.axis[0].shape[0] - 1) + 0.5)
            self.square_coords[1]=[x2_pixel,y2_pixel]
        
    def slider1_changed(self,value): # change the slider controlling the third dimension
        # self.slider1_label.setText(str(value))
        print(value)
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
        print(state)
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
    
            # self.data_t.isel({self.data.dims[0]:slice(x_min, x_max)}).sum(dim=self.data.dims[0]).plot(ax=self.axs[1,0])
            self.integrated_edc=self.data_t.isel({self.data.dims[0]:slice(x_min, x_max)}).sum(dim=self.data.dims[0])
            self.integrated_edc.plot(ax=self.axs[1,0])
            self.fig.canvas.draw()
    
        def integrate_k(): # integrate MDC between the two cursors in the main graph
            self.axs[0, 1].clear()
            plt.draw()
    
            x_min = int(min(self.square_coords[0][0], self.square_coords[1][0]))
            x_max = int(max(self.square_coords[0][0], self.square_coords[1][0])) + 1
    
            # self.data_t.isel({self.data.dims[1]:slice(x_min, x_max)}).sum(dim=self.data.dims[1]).plot(ax=self.axs[0,1])
            self.integrated_mdc=self.data_t.isel({self.data.dims[1]:slice(x_min, x_max)}).sum(dim=self.data.dims[1])
            self.integrated_mdc.plot(ax=self.axs[0,1])
            self.fig.canvas.draw()
    
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
                
                self.int.plot(ax=self.axs[1,1])
                self.dot, = self.axs[1, 1].plot([self.axis[2][self.slider1.value()]], [self.int[self.slider1.value()]], 'ro', markersize=8)
                self.fig.canvas.draw_idle()
    
        def update_show(t, dt): # update the main graph as well as the relevant EDC and MDC cuts. Also the box intensity
            self.axs[0, 1].clear()
            self.axs[1, 0].clear()
            self.data_t=self.data.isel({self.data.dims[2]:slice(t, t+dt+1)}).sum(dim=self.data.dims[2])
            im.set_array(self.data_t)
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
   
        # im6 = self.axs[0, 0].imshow(self.data_t.data, extent=[self.axis[1][0], self.axis[1][-1], self.axis[0][0], self.axis[0][-1]], origin='lower',cmap='terrain', aspect='auto')
        im = self.data.isel({self.data.dims[2]:slice(t, t+dt+1)}).sum(dim=self.data.dims[2]).plot(ax=self.axs[0, 0], cmap='terrain', add_colorbar=False)
        
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
        self.cursor_vert1 = Line2D([initial_x, initial_x], [ymin, ymax], color='yellow', linewidth=2, picker=10, linestyle='--')
        self.cursor_horiz1 = Line2D([xmin, xmax], [initial_y, initial_y], color='yellow', linewidth=2, picker=10, linestyle='--')
        self.cursor_vert2 = Line2D([initial_x2, initial_x2], [ymin, ymax], color='green', linewidth=2, picker=10, linestyle='--')
        self.cursor_horiz2 = Line2D([xmin, xmax], [initial_y2, initial_y2], color='green', linewidth=2, picker=10, linestyle='--')
        
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
    
        self.change_pixel_to_arrayslot()
        
        x_min = int(min(self.square_coords[1][1], self.square_coords[0][1]))
        x_max = int(max(self.square_coords[1][1], self.square_coords[0][1])) + 1
        self.integrated_edc=self.data_t.isel({self.data.dims[0]:slice(x_min, x_max)}).sum(dim=self.data.dims[0])
        x_min = int(min(self.square_coords[0][0], self.square_coords[1][0]))
        x_max = int(max(self.square_coords[0][0], self.square_coords[1][0])) + 1
        self.integrated_mdc=self.data_t.isel({self.data.dims[1]:slice(x_min, x_max)}).sum(dim=self.data.dims[1])
        
        ax.add_line(self.cursor_vert1)
        ax.add_line(self.cursor_horiz1)
        ax.add_patch(self.dot1)
        ax.add_line(self.cursor_vert2)
        ax.add_line(self.cursor_horiz2)
        ax.add_patch(self.dot2)
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
                self.fig.canvas.draw()
                plt.draw()
                
                self.change_pixel_to_arrayslot()
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
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = GraphWindow()
#     window.show()
#     sys.exit(app.exec_()) 