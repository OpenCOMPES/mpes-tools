import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QAction, QFileDialog, QSlider, QGridLayout,QHBoxLayout, QSizePolicy,QLabel
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import h5py
from matplotlib.widgets import CheckButtons, Button
from matplotlib.patches import Circle
from matplotlib.lines import Line2D
from additional_window import GraphWindow
from color_scale import update_color
import xarray as xr
from Drawwindow import DrawWindow
from h5toxarray import h5toxarray_loader
# from k_path_4d_4 import drawKpath

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
                slider4.setFixedSize(155, 10)  # Change the width and height as needed
                
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
        self.ph= None
        self.pxv=None
        self.pyh=None
        self.axis=[]
        # print(self.sliders)
        # Create a menu bar
        menu_bar = self.menuBar()

        # Create a 'File' menu
        file_menu = menu_bar.addMenu("File")

        # Create actions for opening a file and exiting
        open_file_action = QAction("Open File", self)
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)
        
        open_graphe_action = QAction("Energy", self)
        open_graphe_action.triggered.connect(self.open_graph_energy)
        open_graphy_action = QAction("kx_cut", self)
        open_graphy_action.triggered.connect(self.open_graph_y_cut)
        open_graphx_action = QAction("ky_cut", self)
        open_graphx_action.triggered.connect(self.open_graph_x_cut)
        
        menu_bar = self.menuBar()

        # Create a 'Graph' menu
        graph_menu = menu_bar.addMenu("Graph")

        # Add the actions to the menu
        graph_menu.addAction(open_graphe_action)
        graph_menu.addAction(open_graphx_action)
        graph_menu.addAction(open_graphy_action)
        
        open_draw_action = QAction("k-path", self)
        open_draw_action.triggered.connect(self.open_draw_k_path)
        
        draw_menu= menu_bar.addMenu("Draw path")
        draw_menu.addAction(open_draw_action)
        # file_menu.addAction(open_graph_action)
        self.graph_windows = []
        self.ce=None
        
    def open_draw_k_path(self):
        D=DrawWindow(self.data_array,self.slider1[0].value(),self.slider2[0].value() , self.slider1[1].value(), self.slider2[1].value())
        D.show()
        self.graph_windows.append(D)
    
    def open_graph_energy(self):
        print('energy')
        self.dataet=np.zeros((len(self.axis[0]),len(self.axis[1]),len(self.axis[3])))
        self.axet=[self.axis[0],self.axis[1],self.axis[3]]
        
        for i in range(self.slider1[0].value(),self.slider1[0].value()+self.slider2[0].value()+1):
            self.dataet += self.data_updated[:, :, i,:]
        graph_window= GraphWindow(self.dataet,self.axet,self.slider3[0].value(),self.slider4[0].value())
        
        graph_window.show()
        self.graph_windows.append(graph_window)
    def open_graph_x_cut(self):
        self.dataxt=np.zeros((len(self.axis[0]),len(self.axis[2]),len(self.axis[3])))
        self.axxt=[self.axis[0],self.axis[2],self.axis[3]]
        for i in range(self.slider1[1].value(),self.slider1[1].value()+self.slider2[1].value()+1):
            self.dataxt += self.data_updated[:, i, :,:]
        graph_window = GraphWindow(self.dataxt,self.axxt,self.slider3[1].value(),self.slider4[1].value())
        # Show the graph window
        graph_window.show()
        self.graph_windows.append(graph_window)
    def open_graph_y_cut(self):
        self.datayt=np.zeros((len(self.axis[1]),len(self.axis[2]),len(self.axis[3])))
        self.axyt=[self.axis[1],self.axis[2],self.axis[3]]
       
        for i in range(self.slider1[2].value(),self.slider1[2].value()+self.slider2[2].value()+1):
            self.datayt += self.data_updated[i, :, :,:]
        graph_window = GraphWindow(self.datayt,self.axyt,self.slider3[2].value(),self.slider4[2].value())
        # Show the graph window
        graph_window.show()
        self.graph_windows.append(graph_window)
    def open_graph_xy_cut(self):
        self.datapt=np.zeros((len(self.axis[0]),len(self.axis[1]),len(self.axis[3])))
        self.axpt=[self.axis[0],self.axis[1],self.axis[3]]
        
        for i in range(self.slider1[2].value(),self.slider1[2].value()+self.slider2[2].value()+1):
            self.datayt += self.data_updated[i, :, :,:]
        graph_window = GraphWindow(self.datayt,self.axyt,self.slider3[2].value(),self.slider4[2].value())
        # Show the graph window
        graph_window.show()
        self.graph_windows.append(graph_window)
    def open_file(self):
        # Open file dialog to select a .txt file
        # file_path, _ = QFileDialog.getOpenFileName(self, "Open Text File", "", "Text Files (*.txt)")
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Text File", "", "Text Files (*.h5)")
        print(file_path)
        if file_path:
            # Load data from the file
            # x, y = self.load_data(file_path)
            # self.axis,self.data_updated = self.load_data2(file_path)
            # Convert to an xarray.DataArray with named dimensions
            df = h5py.File(file_path, 'r')
            loader= h5toxarray_loader(df)
            self.data_array= loader.get_data_array()
            self.data_updated= loader.get_original_array()
            self.axis=[self.data_array['kx'].data,self.data_array['ky'].data,self.data_array['E'].data,self.data_array['dt'].data]
            
            # print(self.axis[2])
            self.slider1[0].setRange(0,len(self.data_array['E'].data)-1)
            self.slider1[1].setRange(0,len(self.data_array['kx'].data)-1)
            self.slider1[2].setRange(0,len(self.data_array['ky'].data)-1)
            self.slider1[3].setRange(0,len(self.data_array['kx'].data)-1)
            self.slider3[3].setRange(0,len(self.data_array['ky'].data)-1)
            self.slider3[0].setRange(0,len(self.data_array['dt'].data)-1)
            self.slider3[1].setRange(0,len(self.data_array['dt'].data)-1)
            self.slider3[2].setRange(0,len(self.data_array['dt'].data)-1)
            
            
            
            # self.update_plot(self.slider1[0].value(),self.slider2[0].value() , self.slider1[1].value(), self.slider2[0].value(), self.slider1[2].value(), self.slider2[2].value(), self.slider3[0].value(), self.slider4[0].value(),self.slider3[1].value(), self.slider4[1].value(), self.slider3[2].value(), self.slider4[2].value(), self.slider1[3].value(), self.slider3[3].value(), self.slider2[3].value(), self.slider4[3].value())
            self.update_energy(self.slider1[0].value(),self.slider2[0].value() , self.slider1[1].value(), self.slider2[1].value())
            
            # self.ce= update_color(self.im,self.graphs[0],self.graphs[0].gca())
            # self.ce.slider_plot.on_changed(self.ce.update)
            
            self.update_y(self.slider1[2].value(), self.slider2[2].value(), self.slider3[0].value(), self.slider4[0].value())
       
            self.update_x(self.slider3[1].value(), self.slider4[1].value(), self.slider3[2].value(), self.slider4[2].value())
            
            self.update_point(self.slider1[3].value(), self.slider3[3].value(), self.slider2[3].value(), self.slider4[3].value())
            
    def update_energy(self,Energy,dE,te,dte):
        E1=self.data_array['E'][Energy].item()
        # print(Energy,E1)
        E2=self.data_array['E'][Energy+dE].item()
        te1=self.data_array['dt'][te].item()
        te2=self.data_array['dt'][te+dte].item()
        
        self.graphs[0].clear()
        ax=self.graphs[0].gca()
        self.im=self.data_array.sel(E=slice(E1,E2), dt=slice(te1,te2)).mean(dim=("E", "dt")).T.plot(ax=ax)
        # ax.set_title('Loaded Data')
        ax.set_xlabel('kx')
        ax.set_ylabel('ky')
        ax.set_title(f'Energy: {E1:.2f}, dE: {E2-E1}')
        # self.graphs[0].tight_layout()
        self.graphs[0].canvas.draw()
        self.ev = self.graphs[0].gca().axvline(x=self.axis[1][self.slider1[2].value()], color='r', linestyle='--')
        self.eh = self.graphs[0].gca().axhline(y=self.axis[0][self.slider1[1].value()], color='r', linestyle='--')
        self.pxv = self.graphs[0].gca().axvline(x=self.axis[1][self.slider1[3].value()], color='b', linestyle='--')
        self.pyh = self.graphs[0].gca().axhline(y=self.axis[0][self.slider3[3].value()], color='b', linestyle='--')
        # if self.ce is not None:
        #     self.ce.slider_plot.on_changed(self.ce.update)
        
    def update_y(self,ypos,dy,ty,dty):
        
        y1=self.data_array['ky'][ypos].item()
        y2=self.data_array['ky'][ypos+dy].item()
        ty1=self.data_array['dt'][ty].item()
        ty2=self.data_array['dt'][ty+dty].item()
        
        self.graphs[1].clear()
        ax=self.graphs[1].gca()
        self.data_array.sel(ky=slice(y1,y2), dt=slice(ty1,ty2)).mean(dim=("ky", "dt")).plot(ax=ax)
        # ax.set_title('Loaded Data')
        
        ax.set_xlabel('Energy (eV)')
        ax.set_ylabel('kx (1/A)')
        ax.set_title(f'ky_pos: {y1:.2f}, dky: {y2-y1}')
        self.graphs[1].tight_layout()
        self.graphs[1].canvas.draw()
        self.yv = ax.axvline(x=self.axis[2][self.slider1[0].value()], color='r', linestyle='--')
        
    def update_x(self,xpos,dx,tx,dtx):
        x1=self.data_array['kx'][xpos].item()
        x2=self.data_array['kx'][xpos+dx].item()
        tx1=self.data_array['dt'][tx].item()
        tx2=self.data_array['dt'][tx+dtx].item()
        
        self.graphs[2].clear()
        ax=self.graphs[2].gca()
        self.data_array.sel(kx=slice(x1,x2), dt=slice(tx1,tx2)).mean(dim=("kx", "dt")).plot(ax=ax)
        # ax.set_title('Loaded Data')
        ax.set_xlabel('Energy (eV)')
        ax.set_ylabel('ky (1/A)')
        ax.set_title(f'kx_pos: {x1:.2f}, dkx: {x2-x1}')
        self.graphs[2].tight_layout()
        self.graphs[2].canvas.draw()
        self.xv = ax.axvline(x=self.axis[2][self.slider1[0].value()], color='r', linestyle='--')
    def update_point(self,xt,yt,dxt,dyt):
        yt1=self.data_array['ky'][yt].item()
        yt2=self.data_array['ky'][yt+dyt].item()
        xt1=self.data_array['kx'][xt].item()
        xt2=self.data_array['kx'][xt+dxt].item()
        
        self.graphs[3].clear()
        ax=self.graphs[3].gca()
        self.data_array.sel(kx=slice(xt1,xt2), ky=slice(yt1,yt2)).mean(dim=("kx", "ky")).plot(ax=ax)
        # ax.set_title('Loaded Data')
        ax.set_xlabel('time (fs)')
        ax.set_ylabel('Energy (eV)')
        ax.set_title(f'kx_pos: {xt1:.2f}, dkx: {xt2-xt1},ky_pos: {yt1:.2f}, dky: {yt2-yt1}')
        self.graphs[3].tight_layout()
        self.graphs[3].canvas.draw()
        self.ph = ax.axhline(y=self.axis[2][self.slider1[0].value()], color='r', linestyle='--')
    

    def load_data2(self, file_path):
        # Load data from the text file
        # r'C:\Users\admin-nisel131\Documents\\'
        # 'Scan130_scan130_Amine_100x100x300x50_spacecharge4_gamma850_amp_3p3.h5', 'r')
        df = h5py.File(file_path, 'r')
        # print(df.keys())
        print(df['axes'].keys())
        
        axis=[df['axes/ax0'][: ],df['axes/ax1'][: ],df['axes/ax2'][: ],df['axes/ax3'][: ]]
        # print(df['binned/BinnedData'].keys())
        data=df['binned/BinnedData']
        
        
        return axis,data

    def slider_changed(self, value):
        sender = self.sender()  # Get the slider that emitted the signal
        index = self.sliders.index(sender)  # Find the index of the slider
        # print(index)
        
        self.slider_labels[index].setText(str(value))  # Update the corresponding label text
        
        if index in range(0,4):
            
            self.update_energy(self.slider1[0].value(),self.slider2[0].value(),self.slider3[0].value(), self.slider4[0].value())
            # self.update_line()
            if self.xv is not None:
                self.xv.remove()
            if self.yv is not None:
                 self.yv.remove() 
            if self.ph is not None:
                 self.ph.remove() 
            
            self.xv = self.graphs[1].gca().axvline(x=self.axis[2][self.slider1[0].value()], color='r', linestyle='--')
            self.yv = self.graphs[2].gca().axvline(x=self.axis[2][self.slider1[0].value()], color='r', linestyle='--')
            self.ph = self.graphs[3].gca().axhline(y=self.axis[2][self.slider1[0].value()], color='r', linestyle='--')
        elif index in range(4,8):
            
            if self.eh is not None:
                self.eh.remove()
           
            self.eh = self.graphs[0].gca().axhline(y=self.axis[0][self.slider1[1].value()], color='r', linestyle='--')
            
            self.update_y(self.slider1[1].value(), self.slider2[1].value(),self.slider3[1].value(), self.slider4[1].value())
            print('here')
        elif index in range (8,12):
            if self.ev is not None:
                self.ev.remove()
            self.ev = self.graphs[0].gca().axvline(x=self.axis[1][self.slider1[2].value()], color='r', linestyle='--')
            self.update_x(self.slider1[2].value(), self.slider2[2].value(),self.slider3[2].value(), self.slider4[2].value())
        else: 
            if self.pxv is not None:
                self.pxv.remove()
            if self.pyh is not None:
                self.pyh.remove()
            self.update_point(self.slider1[3].value(), self.slider3[3].value(), self.slider2[3].value(), self.slider4[3].value())
            self.pxv = self.graphs[0].gca().axvline(x=self.axis[1][self.slider1[3].value()], color='b', linestyle='--')
            self.pyh = self.graphs[0].gca().axhline(y=self.axis[0][self.slider3[3].value()], color='b', linestyle='--')
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
