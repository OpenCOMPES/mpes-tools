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
from mpes_tools.fit_panel_single import fit_panel_single
from IPython.core.getipython import get_ipython
from mpes_tools.double_click_handler import SubplotClickHandler
import xarray as xr
from mpes_tools.right_click_handler import RightClickHandler
from PyQt5.QtWidgets import QMenu,QGridLayout,QHBoxLayout, QSizePolicy,QLabel
from PyQt5.QtGui import QCursor
from mpes_tools.cursor_handler import Cursor_handler
from mpes_tools.dot_handler import Dot_handler
from mpes_tools.colorscale_slider_handler import colorscale_slider
from matplotlib.figure import Figure
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

        self.click_handlers = []
        self.handler_list = []
        # plt.ioff()
        # add the checkboxes for EDC and MDC integration and the button to save the results
        self.checkbox_e = QCheckBox("Integrate_energy")
        self.checkbox_e.stateChanged.connect(self.checkbox_e_changed)
        
        self.checkbox_k = QCheckBox("Integrate_k")
        self.checkbox_k.stateChanged.connect(self.checkbox_k_changed)

        
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
        
        self.canvases = []
        self.axes = []
        
        for i in range(4):
            fig = Figure(figsize=(10, 8))  # optional: smaller size per plot
            plt.close(fig)
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            self.canvases.append(canvas)
            self.axes.append(ax)
            
        canvas_layout = QGridLayout()

        canvas_layout.addWidget(self.canvases[0], 0, 0)
        canvas_layout.addWidget(self.canvases[1], 0, 1)
        canvas_layout.addWidget(self.canvases[2], 1, 0)
        canvas_layout.addWidget(self.canvases[3], 1, 1)

        checkbox_layout= QHBoxLayout()
        # Add the canvas to the layout
        checkbox_layout.addWidget(self.checkbox_e)
        checkbox_layout.addWidget(self.checkbox_k)
        layout.addLayout(checkbox_layout)
        layout.addLayout(h_layout)
        layout.addLayout(canvas_layout)
        
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


        for idx, ax in enumerate(self.axes):
            handler = RightClickHandler(self.canvases[idx], ax,self.show_pupup_window)
            self.canvases[idx].mpl_connect("button_press_event", handler.on_right_click)
            self.handler_list.append(handler)
        


        #define the data_array
        self.data=data_array
        self.axis=[data_array.coords[dim].data for dim in data_array.dims]
        if technique == 'Phoibos':
            self.axis[1]=self.axis[1]-21.7
            self.data = self.data.assign_coords(Ekin=self.data.coords['Ekin'] -21.7)

        # define the cut for the spectra of the main graph
        # self.data2D_plot=self.data.isel({self.data.dims[2]:slice(t, t+dt+1)}).mean(dim=self.data.dims[2])
        self.data2D_plot=self.data.sel({self.data.dims[2]:slice(self.axis[2][t], self.axis[2][t + dt])}).mean(dim=self.data.dims[2])
        
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
        
        # plot the main graph
        self.im = self.data2D_plot.plot(ax=self.axes[0], cmap='terrain', add_colorbar=False)
        self.axes[0].figure.colorbar(self.im, ax=self.axes[0])
        colorscale_slider(canvas_layout, self.im, self.axes[0].figure.canvas)
        
        # define the initial positions of the cursors in the main graph
        
        initial_x = 0
        initial_y = 0
        initial_x2 = 0.5
        initial_y2 = 0.5
        ax = self.axes[0]
        # define the lines for the cursors
        ymin, ymax = self.axes[0].get_ylim()
        xmin, xmax = self.axes[0].get_ylim()
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
        self.integrated_edc=self.data2D_plot.sel({self.data.dims[0]:slice(x_min, x_max)}).mean(dim=self.data.dims[0])
        x_min = min(self.dot1.center[0], self.dot2.center[0])
        x_max = max(self.dot1.center[0], self.dot2.center[0])
        self.integrated_mdc=self.data2D_plot.sel({self.data.dims[1]:slice(x_min, x_max)}).mean(dim=self.data.dims[1])
        self.active_handler = None
        self.edc_yellow, = self.axes[2].plot([], [], color='orange')
        self.edc_green, = self.axes[2].plot([], [], color='green')
        self.update_show() 
        self.update_all_canvases()
        self.cursor_dot_handler=[]
        self.cursors_list=[self.cursor_vert1, self.cursor_horiz1,self.cursor_vert2, self.cursor_horiz2]
        self.cursors_functions=[lambda:  self.changes_cursor_vertical_1(),lambda: self.changes_cursor_horizontal_1(), lambda: self.changes_cursor_vertical_2(),lambda: self.changes_cursor_horizontal_2()]
        self.dots_list=[self.dot1,self.dot2]
        self.dots_function=[lambda: self.changes_dot1(), lambda: self.changes_dot2()]
        for idx, c in enumerate(self.cursors_list):
            c_handler = Cursor_handler(self.canvases[0].figure,self.axes[0],c, self.cursors_functions[idx],parent=self)
            self.cursor_dot_handler.append(c_handler)
        for idx, d in enumerate(self.dots_list):
            d_handler = Dot_handler(self.canvases[0].figure,self.axes[0], d, self.dots_function[idx])
            self.cursor_dot_handler.append(d_handler)
    def update_all_canvases(self):
        for canvas in self.canvases:
            canvas.draw_idle()         
    def changes_cursor_vertical_1(self):
        x_val= self.cursor_vert1.get_xdata()[0]
        self.dot1.center = (x_val, self.dot1.center[1])
        base = self.cursor_label[0].text().split(':')[0]
        self.cursor_label[0].setText(f"{base}: {x_val:.2f}")
        self.update_mdc()
        self.box()
        self.update_all_canvases() 
    def changes_cursor_horizontal_1(self):
        y_val= self.cursor_horiz1.get_ydata()[0]
        self.dot1.center = (self.dot1.center[0],y_val)
        base = self.cursor_label[1].text().split(':')[0]
        self.cursor_label[1].setText(f"{base}: {y_val:.2f}")
        self.update_edc()
        self.box()
        self.update_all_canvases() 
    def changes_cursor_vertical_2(self):
        x_val= self.cursor_vert2.get_xdata()[0]
        self.dot2.center = (x_val, self.dot2.center[1])
        base = self.cursor_label[2].text().split(':')[0]
        self.cursor_label[2].setText(f"{base}: {x_val:.2f}")
        self.update_mdc()
        self.box()
        self.update_all_canvases() 
    def changes_cursor_horizontal_2(self):
        y_val= self.cursor_horiz2.get_ydata()[0]
        self.dot2.center = (self.dot2.center[0], y_val)
        base = self.cursor_label[3].text().split(':')[0]
        self.cursor_label[3].setText(f"{base}: {y_val:.2f}")
        self.update_edc()
        self.box()
        self.update_all_canvases() 
    def changes_dot1(self):
        x_val,y_val= self.dot1.center
        self.cursor_vert1.set_xdata([x_val,x_val])
        self.cursor_horiz1.set_ydata([y_val,y_val])
        base = self.cursor_label[0].text().split(':')[0]
        self.cursor_label[0].setText(f"{base}: {x_val:.2f}")
        base = self.cursor_label[1].text().split(':')[0]
        self.cursor_label[1].setText(f"{base}: {y_val:.2f}")
        self.update_edc()
        self.update_mdc()
        self.box()
        self.update_all_canvases() 
    def changes_dot2(self):
        x_val,y_val= self.dot2.center
        self.cursor_vert2.set_xdata([x_val,x_val])
        self.cursor_horiz2.set_ydata([y_val,y_val])
        base = self.cursor_label[2].text().split(':')[0]
        self.cursor_label[2].setText(f"{base}: {x_val:.2f}")
        base = self.cursor_label[3].text().split(':')[0]
        self.cursor_label[3].setText(f"{base}: {y_val:.2f}")
        self.update_edc()
        self.update_mdc()
        self.box()
        self.update_all_canvases() 
   
    def show_pupup_window(self,canvas,ax):
        if ax==self.axes[0]:
            menu = QMenu(canvas)
            action1 = menu.addAction("data_2D")
            action2 = menu.addAction("cursors")
    
            action = menu.exec_(QCursor.pos())
    
            if action == action1:
                print('data2D_plot=data.sel({data.dims[2]:slice('+f"{self.axis[2][self.slider1.value()]:.2f}"+', '+f"{self.axis[2][self.slider1.value()+self.slider2.value()+1]:.2f}"+')}).mean(dim=data.dims[2])' )
            elif action == action2:
                print('yellow_vertical,yellow_horizontal,green_vertical,green_horizontal= '+ f"{self.dot1.center[0]:.2f} ,{self.dot1.center[1]:.2f},{self.dot2.center[0]:.2f},{self.dot2.center[1]:.2f}")

        elif ax==self.axes[2]:
            menu = QMenu(canvas)
            action1 = menu.addAction("yellow_EDC")
            action2 = menu.addAction("green_EDC")
            action3 = menu.addAction("integrated_EDC")
    
            action = menu.exec_(QCursor.pos())
    
            if action == action1:
                print("data.sel({data.dims[2]: slice(" +
              f"{self.axis[2][self.slider1.value()]:.2f}, " +
              f"{self.axis[2][self.slider1.value() + self.slider2.value() + 1]:.2f}" +
              ")}).mean(dim=data.dims[2]).sel({data.dims[0]: " +
              f"{self.dot1.center[1]:.2f}" +
              "}, method='nearest')  # Yellow EDC")
            elif action == action2: 
                print("data.sel({data.dims[2]: slice(" +
              f"{self.axis[2][self.slider1.value()]:.2f}, " +
              f"{self.axis[2][self.slider1.value() + self.slider2.value() + 1]:.2f}" +
              ")}).mean(dim=data.dims[2]).sel({data.dims[0]: " +
              f"{self.dot2.center[1]:.2f}" +
              "}, method='nearest')  # Green EDC")
            elif action == action3: 
                print("data.sel({data.dims[2]: slice(" +
              f"{self.axis[2][self.slider1.value()]:.2f}, " +
              f"{self.axis[2][self.slider1.value() + self.slider2.value() + 1]:.2f}" +
              ")}).mean(dim=data.dims[2]).sel({data.dims[0]: slice(" +
              f"{min(self.dot1.center[1], self.dot2.center[1]):.2f}, " +
              f"{max(self.dot1.center[1], self.dot2.center[1]):.2f}" +
              ")}).mean(dim=data.dims[0])  # Integrated EDC")
        elif ax==self.axes[1]:
            menu = QMenu(canvas)
            action1 = menu.addAction("yellow_MDC")
            action2 = menu.addAction("green_MDC")
            action3 = menu.addAction("integrated_MDC")
    
            action = menu.exec_(QCursor.pos())
    
            if action == action1:
                print("data.sel({data.dims[2]: slice(" +
              f"{self.axis[2][self.slider1.value()]:.2f}, " +
              f"{self.axis[2][self.slider1.value() + self.slider2.value() + 1]:.2f}" +
              ")}).mean(dim=data.dims[2]).sel({data.dims[1]: " +
              f"{self.dot1.center[0]:.2f}" +
              "}, method='nearest')  # Yellow MDC")
            elif action == action2: 
                print("data.sel({data.dims[2]: slice(" +
              f"{self.axis[2][self.slider1.value()]:.2f}, " +
              f"{self.axis[2][self.slider1.value() + self.slider2.value() + 1]:.2f}" +
              ")}).mean(dim=data.dims[2]).sel({data.dims[1]: " +
              f"{self.dot2.center[0]:.2f}" +
              "}, method='nearest')  # Green MDC")

            elif action == action3: 
                print("data.sel({data.dims[2]: slice(" +
              f"{self.axis[2][self.slider1.value()]:.2f}, " +
              f"{self.axis[2][self.slider1.value() + self.slider2.value() + 1]:.2f}" +
              ")}).mean(dim=data.dims[2]).sel({data.dims[1]: slice(" +
              f"{min(self.dot1.center[0], self.dot2.center[0]):.2f}, " +
              f"{max(self.dot1.center[0], self.dot2.center[0]):.2f}" +
              ")}).mean(dim=data.dims[1])  # Integrated MDC")
        elif ax==self.axes[3]:
            menu = QMenu(canvas)
            action1 = menu.addAction("intensity box")
            action = menu.exec_(QCursor.pos())
    
            if action == action1:
                # Integrated intensity box
                print("data.loc[{data.dims[0]: slice(" +
              f"{min(self.dot1.center[1], self.dot2.center[1]):.2f}, " +
              f"{max(self.dot1.center[1], self.dot2.center[1]):.2f}" +
              "), data.dims[1]: slice(" +
              f"{min(self.dot1.center[0], self.dot2.center[0]):.2f}, " +
              f"{max(self.dot1.center[0], self.dot2.center[0]):.2f}" +
              ")}].mean(dim=(data.dims[0], data.dims[1]))  # Box integration")
                
   
                  
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
        self.update_show()
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
        self.data2D_plot=self.data.sel({self.data.dims[2]:slice(self.axis[2][self.slider1.value()], self.axis[2][self.slider1.value() + self.slider2.value()])}).mean(dim=self.data.dims[2])
        self.update_show()
        self.t=self.slider1.value()
    def slider2_changed(self,value): # change the slider controlling the third dimension for windowing
        # self.slider2_label.setText(str(value))
        base = self.slider2_label.text().split(':')[0]
        self.slider2_label.setText(f"{base}: {value}")
        self.data2D_plot=self.data.sel({self.data.dims[2]:slice(self.axis[2][self.slider1.value()], self.axis[2][self.slider1.value() + self.slider2.value()])}).mean(dim=self.data.dims[2])
        self.update_show()
        self.dt=self.slider2.value()
    def checkbox_e_changed(self, state): # Checkbox for integrating the EDC between the cursors
        self.update_edc()
        self.update_all_canvases()
    def checkbox_k_changed(self, state): # Checkbox for integrating the MDC between the cursors
        self.update_mdc()
        self.update_all_canvases()

    def fit_energy_panel(self,event): # open up the fit panel for the EDC 
        x_min = min(self.dot2.center[1], self.dot1.center[1])
        x_max = max(self.dot2.center[1], self.dot1.center[1])
        data_fit=self.data.sel({self.data.dims[0]:slice(x_min, x_max)}).mean(dim=self.data.dims[0])
        graph_window=fit_panel(data_fit, self.t, self.dt, self.data.dims[1])
        graph_window.show()
        self.graph_windows.append(graph_window)
    def fit_momentum_panel(self,event): # open up the fit panel for the MDC
        x_min = min(self.dot1.center[0], self.dot2.center[0])
        x_max = max(self.dot1.center[0], self.dot2.center[0])
        data_fit=self.data.sel({self.data.dims[1]:slice(x_min, x_max)}).mean(dim=self.data.dims[1])
        graph_window=fit_panel(data_fit, self.t, self.dt, self.data.dims[0])
        graph_window.show()
        self.graph_windows.append(graph_window)
    def fit_box_panel(self,event): # open up the fit panel for the intensity box
        graph_window=fit_panel_single(self.int)
        graph_window.show()
        self.graph_windows.append(graph_window)
    def update_edc(self):
        self.axes[2].clear()
        if self.checkbox_e.isChecked():
            self.integrate_E()
        else:
            self.edc_yellow=self.data2D_plot.sel({self.data.dims[0]:self.dot1.center[1]}, method='nearest')
            self.edc_green=self.data2D_plot.sel({self.data.dims[0]:self.dot2.center[1]}, method='nearest')
            self.edc_yellow.plot(ax=self.axes[2],color='orange')
            self.edc_green.plot(ax=self.axes[2],color='green')
    def update_mdc(self):
        self.axes[1].clear()
        if self.checkbox_k.isChecked():
            self.integrate_k()
        else:
            self.data2D_plot.sel({self.data.dims[1]:self.dot1.center[0]}, method='nearest').plot(ax=self.axes[1],color='orange')
            self.data2D_plot.sel({self.data.dims[1]:self.dot2.center[0]}, method='nearest').plot(ax=self.axes[1],color='green')
    
    def integrate_E(self): # integrate EDC between the two cursors in the main graph
        self.axes[2].clear()

        x_min = min(self.dot2.center[1], self.dot1.center[1])
        x_max = max(self.dot2.center[1], self.dot1.center[1])
        
        # self.data2D_plot.isel({self.data.dims[0]:slice(x_min, x_max)}).mean(dim=self.data.dims[0]).plot(ax=self.axes[2])
        self.integrated_edc=self.data2D_plot.sel({self.data.dims[0]:slice(x_min, x_max)}).mean(dim=self.data.dims[0])
        self.integrated_edc.plot(ax=self.axes[2])

    def integrate_k(self): # integrate MDC between the two cursors in the main graph
        self.axes[1].clear()

        x_min = min(self.dot1.center[0], self.dot2.center[0])
        x_max = max(self.dot1.center[0], self.dot2.center[0])

        # self.data2D_plot.isel({self.data.dims[1]:slice(x_min, x_max)}).mean(dim=self.data.dims[1]).plot(ax=self.axes[1])
        self.integrated_mdc=self.data2D_plot.sel({self.data.dims[1]:slice(x_min, x_max)}).mean(dim=self.data.dims[1])
        self.integrated_mdc.plot(ax=self.axes[1])

    def box(self): # generate the intensity graph between the four cursors in the main graph
        self.axes[3].clear()
        
        x0,y0=self.dot1.center
        x1,y1=self.dot2.center

        # Ensure (x0, y0) is the top-left corner and (x1, y1) is the bottom-right
        x0, x1 = sorted([x0, x1])
        y0, y1 = sorted([y0, y1])

        self.int = self.data.loc[{self.data.dims[0]: slice(y0, y1), self.data.dims[1]: slice(x0, x1)}].mean(dim=(self.data.dims[0], self.data.dims[1]))
        if x0 != x1 and y0 != y1:
            
            self.int.plot(ax=self.axes[3])
            self.dot, = self.axes[3].plot([self.axis[2][self.slider1.value()]], [self.int[self.slider1.value()]], 'ro', markersize=8)
            self.update_all_canvases()

    def update_show(self): # update the main graph as well as the relevant EDC and MDC cuts. Also the box intensity
        self.update_edc()
        self.update_mdc()
        self.im.set_array(self.data2D_plot)
        self.box() # update the intensity box graph
        time1 = self.axis[2][self.slider1.value()]
        timedt1 = self.axis[2][self.slider1.value() + self.slider2.value()]
        self.axes[0].set_title(f't: {time1:.2f}, t+dt: {timedt1:.2f}')
        self.update_all_canvases()


   
    


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = GraphWindow()
#     window.show()
#     sys.exit(app.exec_()) 