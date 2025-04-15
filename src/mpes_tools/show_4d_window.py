import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QAction, QFileDialog, QSlider, QGridLayout,QHBoxLayout, QSizePolicy,QLabel
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import h5py
from mpes_tools.Gui_3d import Gui_3d
import xarray as xr
from mpes_tools.hdf5 import load_h5
from IPython.core.getipython import get_ipython
from mpes_tools.double_click_handler import SubplotClickHandler

class show_4d_window(QMainWindow):
    def __init__(self,data_array: xr.DataArray):
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
        self.canvases = []
        self.click_handlers=[]
        self.axis_list=[]
        plt.ioff()
        for i in range(2):
            for j in range(2):
                graph_window = QWidget()
                graph_layout = QVBoxLayout()
                graph_window.setLayout(graph_layout)

                # Create a figure and canvas for the graph
                figure, axis = plt.subplots(figsize=(10, 10))
                plt.close(figure)
                canvas = FigureCanvas(figure)
                handler = SubplotClickHandler(axis, self.external_callback)
                canvas.mpl_connect("button_press_event", handler.handle_double_click)
                self.click_handlers.append(handler)
                graph_layout.addWidget(canvas)
                self.axis_list.append(axis)
                self.canvases.append(canvas)
                
                
                slider_layout= QHBoxLayout()
                slider_layout_2= QHBoxLayout()
                # Create a slider widget
                slider1 = QSlider(Qt.Horizontal)
                slider1.setRange(0, 100)
                slider1.setValue(0)
                slider1_label = QLabel("0")
                
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
        self.ph= None
        self.pxv=None
        self.pyh=None
        
        
        open_graphe_action = QAction("Energy", self)
        open_graphe_action.triggered.connect(self.open_graph_kxkydt)
        open_graphx_action = QAction("kx_cut", self)
        open_graphx_action.triggered.connect(self.open_graph_kyedt)
        open_graphy_action = QAction("ky_cut", self)
        open_graphy_action.triggered.connect(self.open_graph_kxedt)
        
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
        self.load_data(data_array)

    def closeEvent(self, event):
        # Remove references to graphs and canvases to prevent lingering objects
        self.graphs = []
        self.canvases = []
        self.axis_list = []
        
        # Update window state
        self.window_open = False
        event.accept()

    def external_callback(self, ax):
        # print(f"External callback: clicked subplot ({i},{j})")
        if ax==self.graphs[0].gca():
            content= f"""
data='your data_array'
#the energy plot
data.loc[
    {{
        '{self.axes[2]}': slice(
            {self.data_array[self.axes[2]][self.slider1[0].value()].item()},
            {self.data_array[self.axes[2]][self.slider1[0].value() + self.slider2[0].value()].item()}
        ),
        '{self.axes[3]}': slice(
            {self.data_array[self.axes[3]][self.slider3[0].value()].item()},
            {self.data_array[self.axes[3]][self.slider3[0].value() + self.slider4[0].value()].item()}
        )
    }}
].mean(dim=('{self.axes[2]}', '{self.axes[3]}')).T

            """
        elif ax==self.graphs[1].gca():
            content= f"""
data='your data_array'
#the ky plot
data.loc[
    {{
        '{self.axes[1]}': slice(
            {self.data_array[self.axes[1]][self.slider1[1].value()].item()},
            {self.data_array[self.axes[1]][self.slider1[1].value() + self.slider2[1].value()].item()}
        ),
        '{self.axes[3]}': slice(
            {self.data_array[self.axes[3]][self.slider3[1].value()].item()},
            {self.data_array[self.axes[3]][self.slider3[1].value() + self.slider4[1].value()].item()}
        )
    }}
].mean(dim=('{self.axes[1]}', '{self.axes[3]}')).T
            """
        elif ax==self.axis_list[2]:
            content= f"""
data='your data_array'
#the kx plot
data.loc[
    {{
        '{self.axes[0]}': slice(
            {self.data_array[self.axes[0]][self.slider1[2].value()].item()},
            {self.data_array[self.axes[0]][self.slider1[2].value() + self.slider2[2].value()].item()}
        ),
        '{self.axes[3]}': slice(
            {self.data_array[self.axes[3]][self.slider3[2].value()].item()},
            {self.data_array[self.axes[3]][self.slider3[2].value() + self.slider4[2].value()].item()}
        )
    }}
].mean(dim=('{self.axes[0]}', '{self.axes[3]}')).T
            """
        elif ax==self.axis_list[3]:
            content= f"""
data='your data_array'
#the kx,ky plot
data.loc[
    {{
        '{self.axes[1]}': slice(
            {self.data_array[self.axes[1]][self.slider1[3].value()].item()},
            {self.data_array[self.axes[1]][self.slider1[3].value() + self.slider2[3].value()].item()}
        ),
        '{self.axes[0]}': slice(
            {self.data_array[self.axes[0]][self.slider3[3].value()].item()},
            {self.data_array[self.axes[0]][self.slider3[3].value()+ self.slider4[3].value()].item()}
        )
    }}
].mean(dim=('{self.axes[1]}', '{self.axes[0]}'))
            """
        shell = get_ipython()
        payload = dict(
            source='set_next_input',
            text=content,
            replace=False,
        )
        shell.payload_manager.write_payload(payload, single=False)
        shell.run_cell('pass')
        print('results extracted!')

    def open_graph_kxkydt(self):
        E1=self.data_array[self.axes[2]][self.slider1[0].value()].item()
        E2=self.data_array[self.axes[2]][self.slider1[0].value()+self.slider2[0].value()+1].item()
        data_kxkydt = self.data_array.loc[{self.axes[2]:slice(E1,E2)}].mean(dim=(self.axes[2]))
        graph_window=Gui_3d(data_kxkydt, self.slider3[0].value(), self.slider4[0].value(),'METIS')
        # Show the graph window
        graph_window.show()
        self.graph_windows.append(graph_window)

    def open_graph_kxedt(self):
        ky1=self.data_array[self.axes[1]][self.slider1[1].value()].item()
        ky2=self.data_array[self.axes[1]][self.slider1[1].value()+self.slider2[1].value()+1].item()
        data_kxedt = self.data_array.loc[{self.axes[1]:slice(ky1,ky2)}].mean(dim=(self.axes[1]))
        graph_window = Gui_3d(data_kxedt, self.slider3[1].value(), self.slider4[1].value(),'METIS')
        # Show the graph window
        graph_window.show()
        self.graph_windows.append(graph_window)

    def open_graph_kyedt(self):
        kx1=self.data_array[self.axes[0]][self.slider1[2].value()].item()
        kx2=self.data_array[self.axes[0]][self.slider1[2].value()+self.slider2[2].value()+1].item()
        data_kyedt = self.data_array.loc[{self.axes[0]:slice(kx1,kx2)}].mean(dim=(self.axes[0]))
        print(type(data_kyedt))
        graph_window = Gui_3d(data_kyedt, self.slider3[2].value(), self.slider4[2].value(),'METIS')
        # Show the graph window
        
        graph_window.show()
        self.graph_windows.append(graph_window)
        
    def load_data(self, data_array: xr.DataArray):
        self.data_array = data_array
        self.axes = data_array.dims
        # print('theaxissss',self.axes)
        self.slider1[0].setRange(0,len(self.data_array.coords[self.axes[2]])-1)
        self.slider1[1].setRange(0,len(self.data_array.coords[self.axes[0]])-1)
        self.slider1[2].setRange(0,len(self.data_array.coords[self.axes[1]])-1)
        self.slider1[3].setRange(0,len(self.data_array.coords[self.axes[0]])-1)
        self.slider3[3].setRange(0,len(self.data_array.coords[self.axes[1]])-1)
        self.slider3[0].setRange(0,len(self.data_array.coords[self.axes[3]])-1)
        self.slider3[1].setRange(0,len(self.data_array.coords[self.axes[3]])-1)
        self.slider3[2].setRange(0,len(self.data_array.coords[self.axes[3]])-1)
        
        self.slider_labels[0].setText(self.axes[2])
        self.slider_labels[1].setText("Δ"+self.axes[2])
        self.slider_labels[2].setText(self.axes[3])
        self.slider_labels[3].setText("Δ"+self.axes[3])
        
        self.slider_labels[4].setText(self.axes[1])
        self.slider_labels[5].setText("Δ"+self.axes[1])
        self.slider_labels[6].setText(self.axes[3])
        self.slider_labels[7].setText("Δ"+self.axes[3])

        self.slider_labels[8].setText(self.axes[0])
        self.slider_labels[9].setText("Δ"+self.axes[0])
        self.slider_labels[10].setText(self.axes[3])
        self.slider_labels[11].setText("Δ"+self.axes[3])
        
        self.slider_labels[12].setText(self.axes[1])
        self.slider_labels[13].setText("Δ"+self.axes[1])
        self.slider_labels[14].setText(self.axes[0])
        self.slider_labels[15].setText("Δ"+self.axes[0])
        
        
        self.update_energy(self.slider1[0].value(),self.slider2[0].value(),self.slider3[0].value(), self.slider4[0].value())

        self.update_ky(self.slider1[1].value(), self.slider2[1].value(),self.slider3[1].value(), self.slider4[1].value())
    
        self.update_kx(self.slider1[2].value(), self.slider2[2].value(),self.slider3[2].value(), self.slider4[2].value())
        
        self.update_dt(self.slider1[3].value(), self.slider2[3].value(), self.slider3[3].value(), self.slider4[3].value())
    
    
    def update_energy(self,Energy,dE,te,dte):
        self.ce_state=True
        E1=self.data_array[self.axes[2]][Energy].item()
        E2=self.data_array[self.axes[2]][Energy+dE].item()
        te1=self.data_array[self.axes[3]][te].item()
        te2=self.data_array[self.axes[3]][te+dte].item()

        ax=self.graphs[0].gca()
        ax.cla() 
        data_avg=self.data_array.loc[{self.axes[2]:slice(E1,E2), self.axes[3]:slice(te1,te2)}].mean(dim=(self.axes[2], self.axes[3]))
        self.im=data_avg.T.plot(ax=ax,cmap='terrain', add_colorbar=False)
        ax.set_title(f'energy: {E1:.2f}, E+dE: {E2:.2f} , t: {te1:.2f}, t+dt: {te2:.2f}')
        
        self.ev = ax.axvline(x=self.data_array.coords[self.axes[1]][self.slider1[2].value()].item(), color='r', linestyle='--')
        self.eh = ax.axhline(y=self.data_array.coords[self.axes[1]][self.slider1[1].value()].item(), color='r', linestyle='--')
        self.pxv = self.graphs[0].gca().axvline(x=self.data_array.coords[self.axes[1]][self.slider1[3].value()].item(), color='b', linestyle='--')
        self.pyh = self.graphs[0].gca().axhline(y=self.data_array.coords[self.axes[0]][self.slider3[3].value()].item(), color='b', linestyle='--')
        self.graphs[0].tight_layout()
        self.graphs[0].canvas.draw_idle()
        
    def update_ky(self,ypos,dy,ty,dty):
        
        y1=self.data_array[self.axes[1]][ypos].item()
        y2=self.data_array[self.axes[1]][ypos+dy].item()
        ty1=self.data_array[self.axes[3]][ty].item()
        ty2=self.data_array[self.axes[3]][ty+dty].item()
        
        ax=self.graphs[1].gca()
        ax.cla() 
        self.data_array.loc[{self.axes[1]:slice(y1,y2), self.axes[3]:slice(ty1,ty2)}].mean(dim=(self.axes[1], self.axes[3])).T.plot(ax=ax,cmap='terrain', add_colorbar=False)
        ax.set_title(f'ky: {y1:.2f}, ky+dky: {y2:.2f} , t: {ty1:.2f}, t+dt: {ty2:.2f}')
        self.yh = ax.axhline(y=self.data_array.coords[self.axes[2]][self.slider1[0].value()].item(), color='r', linestyle='--')

        self.graphs[1].tight_layout()
        self.graphs[1].canvas.draw_idle()
        
        
    def update_kx(self,xpos,dx,tx,dtx):
        x1=self.data_array[self.axes[0]][xpos].item()
        x2=self.data_array[self.axes[0]][xpos+dx].item()
        tx1=self.data_array[self.axes[3]][tx].item()
        tx2=self.data_array[self.axes[3]][tx+dtx].item()
        
        ax=self.graphs[2].gca()
        ax.cla() 
        self.data_array.loc[{self.axes[0]:slice(x1,x2), self.axes[3]:slice(tx1,tx2)}].mean(dim=(self.axes[0], self.axes[3])).T.plot(ax=ax,cmap='terrain', add_colorbar=False)
        ax.set_title(f'kx: {x1:.2f}, kx+dkx: {x2:.2f} , t: {tx1:.2f}, t+dt: {tx2:.2f}')
        self.xh = ax.axhline(y=self.data_array.coords[self.axes[2]][self.slider1[0].value()].item(), color='r', linestyle='--')
        
        self.graphs[2].tight_layout()
        self.graphs[2].canvas.draw_idle()
    
    
    def update_dt(self,yt,dyt,xt,dxt):
        yt1=self.data_array[self.axes[1]][yt].item()
        yt2=self.data_array[self.axes[1]][yt+dyt].item()
        xt1=self.data_array[self.axes[0]][xt].item()
        xt2=self.data_array[self.axes[0]][xt+dxt].item()
        
        ax=self.graphs[3].gca()
        ax.cla() 
        self.data_array.loc[{self.axes[1]:slice(yt1,yt2), self.axes[0]:slice(xt1,xt2)}].mean(dim=(self.axes[1], self.axes[0])).plot(ax=ax,cmap='terrain', add_colorbar=False)
        ax.set_title(f'ky: {yt1:.2f}, ky+dky: {yt2:.2f} , kx: {xt1:.2f}, kx+dkx: {xt2:.2f}')
        self.ph = ax.axhline(y=self.data_array.coords[self.axes[2]][self.slider1[0].value()].item(), color='r', linestyle='--')
        self.graphs[3].tight_layout()
        self.graphs[3].canvas.draw_idle()
        

    def slider_changed(self, value):
        sender = self.sender()  # Get the slider that emitted the signal
        index = self.sliders.index(sender)  # Find the index of the slider
        
        # self.slider_labels[index].setText(str(value))  # Update the corresponding label text
        base = self.slider_labels[index].text().split(':')[0]
        self.slider_labels[index].setText(f"{base}: {value}")

        if index in range(0,4):
            # ax = self.graphs[2].gca()
            if self.xh in self.graphs[2].gca().lines:
                self.xh.remove()
            if self.yh in self.graphs[1].gca().lines:
                self.yh.remove()
            if self.ph in self.graphs[3].gca().lines:
                self.ph.remove()
            self.xh = self.graphs[2].gca().axhline(y=self.data_array.coords[self.axes[2]][self.slider1[0].value()].item(), color='r', linestyle='--')
            self.yh = self.graphs[1].gca().axhline(y=self.data_array.coords[self.axes[2]][self.slider1[0].value()].item(), color='r', linestyle='--')
            self.ph = self.graphs[3].gca().axhline(y=self.data_array.coords[self.axes[2]][self.slider1[0].value()].item(), color='r', linestyle='--')
            # self.graphs[2].tight_layout()
            self.graphs[2].canvas.draw_idle()
            self.graphs[1].canvas.draw_idle()
            self.graphs[3].canvas.draw_idle()
            self.update_energy(self.slider1[0].value(),self.slider2[0].value(),self.slider3[0].value(), self.slider4[0].value())
            
        elif index in range(4,8):
            if self.eh is not None:
                self.eh.remove()
           
            self.eh = self.graphs[0].gca().axhline(y=self.data_array.coords[self.axes[0]][self.slider1[1].value()].item(), color='r', linestyle='--')
            self.graphs[0].canvas.draw_idle()
            self.update_ky(self.slider1[1].value(), self.slider2[1].value(),self.slider3[1].value(), self.slider4[1].value())
        elif index in range (8,12):
            ax = self.graphs[0].gca()
            if self.ev in ax.lines:
                self.ev.remove()
            self.ev = self.graphs[0].gca().axvline(x=self.data_array.coords[self.axes[1]][self.slider1[2].value()].item(), color='r', linestyle='--')
            self.graphs[0].canvas.draw_idle()
            self.update_kx(self.slider1[2].value(), self.slider2[2].value(),self.slider3[2].value(), self.slider4[2].value())
        elif index in range (12,16):
            if self.pxv in self.graphs[0].gca().lines:
                self.pxv.remove()
            if self.pyh in self.graphs[0].gca().lines:
                self.pyh.remove()
            self.pyh = self.graphs[0].gca().axhline(y=self.data_array.coords[self.axes[1]][self.slider1[3].value()].item(), color='b', linestyle='--')
            self.pxv = self.graphs[0].gca().axvline(x=self.data_array.coords[self.axes[0]][self.slider3[3].value()].item(), color='b', linestyle='--')
            self.graphs[0].canvas.draw_idle()
            self.update_dt(self.slider1[3].value(), self.slider2[3].value(), self.slider3[3].value(), self.slider4[3].value())

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = show_4d_window()
    window.show()
    sys.exit(app.exec_())
