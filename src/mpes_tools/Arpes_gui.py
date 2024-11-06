import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QAction, QFileDialog, QSlider, QGridLayout,QHBoxLayout, QSizePolicy,QLabel
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import h5py
from mpes_tools.additional_window import GraphWindow
import xarray as xr
from .hdf5 import load_h5


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget for the graph and slider
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QGridLayout()
        central_widget.setLayout(layout)

        # Create four graphs and sliders
        self.graphs = []
        self.slider1 = []
        self.slider2 = []
        self.slider3 = []
        self.slider4 = []
        self.sliders = []
        self.slider_labels = []

        plt.ioff()

        for i in range(2):
            for j in range(2):
                graph_window = QWidget()
                graph_layout = QVBoxLayout()
                graph_window.setLayout(graph_layout)

                # Create a figure and canvas for the graph
                figure, axis = plt.subplots(figsize=(20, 20))
                canvas = FigureCanvas(figure)
                graph_layout.addWidget(canvas)

                slider_layout= QHBoxLayout()
                slider_layout_2= QHBoxLayout()
                # Create a slider widget
                slider1 = QSlider(Qt.Horizontal)
                slider1.setRange(0, 100)
                slider1.setValue(0)
                slider1_label = QLabel("0")
                # slider.valueChanged.connect(self.slider_changed)
                # Set the size of the slider
                
                # default_size = slider1.sizeHint()
                # print(f"Default size of the slider: {default_size.width()}x{default_size.height()}")
                
                slider2 = QSlider(Qt.Horizontal)
                slider2.setRange(0, 10)
                slider2.setValue(0)
                slider2_label = QLabel("0")
                
                
                
                slider3 = QSlider(Qt.Horizontal)
                slider3.setRange(0, 100)
                slider3.setValue(0)
                slider3_label = QLabel("0")
                
                slider4 = QSlider(Qt.Horizontal)
                slider4.setRange(0, 10)
                slider4.setValue(0)
                slider4_label = QLabel("0")
                
                slider1.setFixedSize(200, 12)  # Change the width and height as needed
                slider2.setFixedSize(200, 12)  # Change the width and height as needed
                slider3.setFixedSize(200, 12)  # Change the width and height as needed
                slider4.setFixedSize(200, 12)  # Change the width and height as needed
                
                slider_layout.addWidget(slider1)
                slider_layout.addWidget(slider1_label)
                slider_layout.addWidget(slider2)
                slider_layout.addWidget(slider2_label)
                
                slider_layout_2.addWidget(slider3)
                slider_layout_2.addWidget(slider3_label)
                slider_layout_2.addWidget(slider4)
                slider_layout_2.addWidget(slider4_label)
                # slider2.valueChanged.connect(self.slider_changed)

                # Add the slider to the layout
                graph_layout.addLayout(slider_layout)
                graph_layout.addLayout(slider_layout_2)
                # graph_layout.addWidget(slider3)
                # graph_layout.addWidget(slider2)

                layout.addWidget(graph_window, i, j)
                self.graphs.append(figure)
                self.slider1.append(slider1)
                self.slider2.append(slider2)
                self.slider3.append(slider3)
                self.slider4.append(slider4)
                self.sliders.extend([slider1, slider2,slider3, slider4])
                self.slider_labels.extend([slider1_label, slider2_label,slider3_label, slider4_label])
        for slider in self.slider1:   
            slider.valueChanged.connect(self.slider_changed)
        for slider in self.slider2:   
            slider.valueChanged.connect(self.slider_changed)
        for slider in self.slider3:   
            slider.valueChanged.connect(self.slider_changed)
        for slider in self.slider4:   
            slider.valueChanged.connect(self.slider_changed)
            
        self.xv = None
        self.yv = None
        self.ev = None
        self.eh = None
        
        # print(self.sliders)
        # Create a menu bar
        menu_bar = self.menuBar()

        # Create a 'File' menu
        file_menu = menu_bar.addMenu("File")

        # Create actions for opening a file and exiting
        open_file_action = QAction("Open File", self)
        open_file_action.triggered.connect(self.open_file_dialoge)
        file_menu.addAction(open_file_action)
        
        open_graphe_action = QAction("Energy", self)
        open_graphe_action.triggered.connect(self.open_graph_energy)
        open_graphy_action = QAction("ky_cut", self)
        open_graphy_action.triggered.connect(self.open_graph_y_cut)
        open_graphx_action = QAction("kx_cut", self)
        open_graphx_action.triggered.connect(self.open_graph_x_cut)
        
        menu_bar = self.menuBar()

        # Create a 'Graph' menu
        graph_menu = menu_bar.addMenu("Graph")

        # Add the actions to the menu
        graph_menu.addAction(open_graphe_action)
        graph_menu.addAction(open_graphx_action)
        graph_menu.addAction(open_graphy_action)
        # file_menu.addAction(open_graph_action)
        self.graph_windows = []
        self.ce=None

        self.show()

    def open_graph_energy(self):
        print('energy')
        self.dataet=np.zeros((len(self.data_array.coords[self.axes[0]]),len(self.data_array.coords[self.axes[1]]),len(self.data_array.coords[self.axes[3]])))
        # self.axet=np.zeros((len(self.data_array.coords[self.axes[0]]),len(self.data_array.coords[self.axes[1]]),len(self.data_array.coords[self.axes[3]])))
        self.axet=[self.data_array.coords[self.axes[0]],self.data_array.coords[self.axes[1]],self.data_array.coords[self.axes[3]]]
        # self.axet[0]=self.data_array.coords[self.axes[0]]
        # self.axet[1]=self.data_array.coords[self.axes[1]] 
        # self.axet[2]=self.data_array.coords[self.axes[3]]
        
        for i in range(self.slider1[0].value(),self.slider1[0].value()+self.slider2[0].value()+1):
            self.dataet += self.data_updated[:, :, i,:]
        # if not self.graph_window:
        #     self.graph_window = GraphWindow(self.dataet,self.axet,self.slider3[0].value(),self.slider4[0].value())
        graph_window= GraphWindow(self.dataet,self.axet,self.slider3[0].value(),self.slider4[0].value())
        # Show the graph window
        graph_window.show()
        self.graph_windows.append(graph_window)
    def open_graph_x_cut(self):
        self.dataxt=np.zeros((len(self.data_array.coords[self.axes[0]]),len(self.self.data_array.coords[self.axes[2]]),len(self.data_array.coords[self.axes[3]])))
        # self.axet=np.zeros((len(self.data_array.coords[self.axes[0]]),len(self.data_array.coords[self.axes[1]]),len(self.data_array.coords[self.axes[3]])))
        self.axxt=[self.data_array.coords[self.axes[0]],self.self.data_array.coords[self.axes[2]],self.data_array.coords[self.axes[3]]]
        # self.axet[0]=self.data_array.coords[self.axes[0]]
        # self.axet[1]=self.data_array.coords[self.axes[1]] 
        # self.axet[2]=self.data_array.coords[self.axes[3]]
        # print(self.dataxt.shape)
        for i in range(self.slider1[1].value(),self.slider1[1].value()+self.slider2[1].value()+1):
            self.dataxt += self.data_updated[:, i, :,:]
        graph_window = GraphWindow(self.dataxt,self.axxt,self.slider3[1].value(),self.slider4[1].value())
        # Show the graph window
        graph_window.show()
        self.graph_windows.append(graph_window)
    def open_graph_y_cut(self):
        self.datayt=np.zeros((len(self.data_array.coords[self.axes[1]]),len(self.self.data_array.coords[self.axes[2]]),len(self.data_array.coords[self.axes[3]])))
        # self.axet=np.zeros((len(self.data_array.coords[self.axes[0]]),len(self.data_array.coords[self.axes[1]]),len(self.data_array.coords[self.axes[3]])))
        self.axyt=[self.data_array.coords[self.axes[1]],self.self.data_array.coords[self.axes[2]],self.data_array.coords[self.axes[3]]]
        # self.axet[0]=self.data_array.coords[self.axes[0]]
        # self.axet[1]=self.data_array.coords[self.axes[1]] 
        # self.axet[2]=self.data_array.coords[self.axes[3]]
        # print(self.dataxt.shape)
        for i in range(self.slider1[2].value(),self.slider1[2].value()+self.slider2[2].value()+1):
            self.datayt += self.data_updated[i, :, :,:]
        graph_window = GraphWindow(self.datayt,self.axyt,self.slider3[2].value(),self.slider4[2].value())
        # Show the graph window
        graph_window.show()
        self.graph_windows.append(graph_window)
    def open_graph_xy_cut(self):
        self.datapt=np.zeros((len(self.data_array.coords[self.axes[0]]),len(self.data_array.coords[self.axes[1]]),len(self.data_array.coords[self.axes[3]])))
        # self.axet=np.zeros((len(self.data_array.coords[self.axes[0]]),len(self.data_array.coords[self.axes[1]]),len(self.data_array.coords[self.axes[3]])))
        self.axpt=[self.data_array.coords[self.axes[0]],self.data_array.coords[self.axes[1]],self.data_array.coords[self.axes[3]]]
        # self.axet[0]=self.data_array.coords[self.axes[0]]
        # self.axet[1]=self.data_array.coords[self.axes[1]] 
        # self.axet[2]=self.data_array.coords[self.axes[3]]
        # print(self.dataxt.shape)
        for i in range(self.slider1[2].value(),self.slider1[2].value()+self.slider2[2].value()+1):
            self.datayt += self.data_updated[i, :, :,:]
        graph_window = GraphWindow(self.datayt,self.axyt,self.slider3[2].value(),self.slider4[2].value())
        # Show the graph window
        graph_window.show()
        self.graph_windows.append(graph_window)
    def open_file_dialoge(self):
        # Open file dialog to select a .h5 file
        file_path, _ = QFileDialog.getOpenFileName(self, "Open hdf5", "", "h5 Files (*.h5)")
        print(file_path)
        if file_path:
            data_array = load_h5(file_path)

            self.load_data(data_array)

    def load_data(self, data_array: xr.DataArray):
        self.data_array = data_array
        self.axes = data_array.dims

        self.slider1[0].setRange(0,len(self.data_array.coords[self.axes[2]])-1)
        self.slider1[1].setRange(0,len(self.data_array.coords[self.axes[0]])-1)
        self.slider1[2].setRange(0,len(self.data_array.coords[self.axes[1]])-1)
        self.slider1[3].setRange(0,len(self.data_array.coords[self.axes[0]])-1)
        self.slider3[3].setRange(0,len(self.data_array.coords[self.axes[1]])-1)
        self.slider3[0].setRange(0,len(self.data_array.coords[self.axes[3]])-1)
        self.slider3[1].setRange(0,len(self.data_array.coords[self.axes[3]])-1)
        self.slider3[2].setRange(0,len(self.data_array.coords[self.axes[3]])-1)

        self.update_energy(self.slider1[0].value(),self.slider2[0].value() , self.slider1[1].value(), self.slider2[1].value())
        
        # self.ce= update_color(self.im,self.graphs[0],self.graphs[0].gca())
        # self.ce.slider_plot.on_changed(self.ce.update)
        
        self.update_ky(self.slider1[2].value(), self.slider2[2].value(), self.slider3[0].value(), self.slider4[0].value())
    
        self.update_kx(self.slider3[1].value(), self.slider4[1].value(), self.slider3[2].value(), self.slider4[2].value())
        
        self.update_dt(self.slider1[3].value(), self.slider3[3].value(), self.slider2[3].value(), self.slider4[3].value())
        # Plot the data
        # self.plot_data2([self.data_array.coords[self.axes[0]],self.data_array.coords[self.axes[1]]],self.data[:,:,100,10],graph[0])
        # self.plot_data2([self.data_array.coords[self.axes[1]],self.self.data_array.coords[self.axes[2]]],self.data[40,:,:,10],self.ax01,self.fig01,self.canvas01,self.axes[0])
        # self.plot_data2([self.data_array.coords[self.axes[0]],self.self.data_array.coords[self.axes[2]]],self.data[:,40,:,10],self.ax10,self.fig10,self.canvas10,self.axes[1])
        # self.plot_data2([self.self.data_array.coords[self.axes[2]],self.data_array.coords[self.axes[3]]],self.data[40,40,:,:],self.ax11,self.fig11,self.canvas11,'time')
    
    def update_energy(self,Energy,dE,te,dte):
        self.ce_state=True
        E1=self.data_array[self.axes[2]][Energy].item()
        E2=self.data_array[self.axes[2]][Energy+dE].item()
        te1=self.data_array[self.axes[3]][te].item()
        te2=self.data_array[self.axes[3]][te+dte].item()

        self.graphs[0].clear()
        ax=self.graphs[0].gca()

        self.im=self.data_array.loc[{self.axes[2]:slice(E1,E2), self.axes[3]:slice(te1,te2)}].mean(dim=(self.axes[2], self.axes[3])).T.plot(ax=ax)
        
        self.ev = ax.axvline(x=self.data_array.coords[self.axes[0]][self.slider1[1].value()], color='r', linestyle='--')
        self.eh = ax.axhline(y=self.data_array.coords[self.axes[1]][self.slider1[2].value()], color='r', linestyle='--')
        
        self.graphs[0].tight_layout()
        self.graphs[0].canvas.draw()
        
    def update_ky(self,ypos,dy,ty,dty):
        
        y1=self.data_array[self.axes[1]][ypos].item()
        y2=self.data_array[self.axes[1]][ypos+dy].item()
        ty1=self.data_array[self.axes[3]][ty].item()
        ty2=self.data_array[self.axes[3]][ty+dty].item()
        
        self.graphs[1].clear()
        ax=self.graphs[1].gca()
        self.data_array.loc[{self.axes[1]:slice(y1,y2), self.axes[3]:slice(ty1,ty2)}].mean(dim=(self.axes[1], self.axes[3])).T.plot(ax=ax)
        
        self.yv = ax.axvline(x=self.data_array.coords[self.axes[2]][self.slider1[0].value()], color='r', linestyle='--')

        self.graphs[1].tight_layout()
        self.graphs[1].canvas.draw()
        
        
    def update_kx(self,xpos,dx,tx,dtx):
        x1=self.data_array[self.axes[0]][xpos].item()
        x2=self.data_array[self.axes[0]][xpos+dx].item()
        tx1=self.data_array[self.axes[3]][tx].item()
        tx2=self.data_array[self.axes[3]][tx+dtx].item()
        
        self.graphs[2].clear()
        ax=self.graphs[2].gca()
        self.data_array.loc[{self.axes[0]:slice(x1,x2), self.axes[3]:slice(tx1,tx2)}].mean(dim=(self.axes[0], self.axes[3])).T.plot(ax=ax)

        self.xv = ax.axvline(x=self.data_array.coords[self.axes[2]][self.slider1[0].value()], color='r', linestyle='--')
        
        self.graphs[2].tight_layout()
        self.graphs[2].canvas.draw()
    
    
    def update_dt(self,yt,xt,dyt,dxt):
        yt1=self.data_array[self.axes[1]][yt].item()
        yt2=self.data_array[self.axes[1]][yt+dyt].item()
        xt1=self.data_array[self.axes[0]][xt].item()
        xt2=self.data_array[self.axes[0]][xt+dxt].item()
        
        self.graphs[3].clear()
        ax=self.graphs[3].gca()
        self.data_array.loc[{self.axes[1]:slice(yt1,yt2), self.axes[0]:slice(xt1,xt2)}].mean(dim=(self.axes[1], self.axes[0])).plot(ax=ax)

        self.graphs[3].tight_layout()
        self.graphs[3].canvas.draw()

    def slider_changed(self, value):
        sender = self.sender()  # Get the slider that emitted the signal
        index = self.sliders.index(sender)  # Find the index of the slider
        
        self.slider_labels[index].setText(str(value))  # Update the corresponding label text

        if index in range(0,4):
            # self.ce.slider_plot.on_changed(self.ce.update)
            self.update_energy(self.slider1[0].value(),self.slider2[0].value(),self.slider3[0].value(), self.slider4[0].value())
            # self.update_line()
        elif index in range(4,8):
            self.update_ky(self.slider1[1].value(), self.slider2[1].value(),self.slider3[1].value(), self.slider4[1].value())
        elif index in range (8,12):
            self.update_kx(self.slider1[2].value(), self.slider2[2].value(),self.slider3[2].value(), self.slider4[2].value())
        elif index in range (12,16):
            self.update_dt(self.slider1[3].value(), self.slider3[3].value(), self.slider2[3].value(), self.slider4[3].value())

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
