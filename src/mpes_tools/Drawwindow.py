import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, \
    QHBoxLayout, QSizePolicy,QSlider,QLabel
# from k_path_4d_4 import drawKpath

class DrawWindow(QMainWindow):
    def __init__(self,data,s1,s2,s3,s4):
        super().__init__()

        # Set the title and size of the main window
        self.setWindowTitle("PyQt5 Matplotlib Example")
        self.setGeometry(100, 100, 800, 600)
        self.data_array=data
        print(data['E'][0])
        # Create the main layout
        main_layout = QVBoxLayout()

        # Create a widget to hold the layout
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        # Create a horizontal layout for the top row
        top_row_layout = QHBoxLayout()


        # Create top left graph
        self.figure1, self.axis1 = plt.subplots()
        self.canvas1 = FigureCanvas(self.figure1)
        top_row_layout.addWidget(self.canvas1)

        # Create bottom right graph
        self.figure2, self.axis2 = plt.subplots()
        self.canvas2 = FigureCanvas(self.figure2)
        top_row_layout.addWidget(self.canvas2)
        
        layout = QVBoxLayout()
        
        slider_layout= QHBoxLayout()
        self.slider1 = QSlider(Qt.Horizontal)
        self.slider1.setRange(0, len(data['E'].data))
        self.slider1.setValue(s1)
        self.slider1_label = QLabel("0")
        
        self.slider2 = QSlider(Qt.Horizontal)
        self.slider2.setRange(0, 10)
        self.slider2.setValue(s2)
        self.slider2_label = QLabel("0")
        
        self.slider1.setFixedSize(200, 12)  # Change the width and height as needed
        self.slider2.setFixedSize(200, 12)  # Change the width and height as needed
        
        slider_layout.addWidget(self.slider1)
        slider_layout.addWidget(self.slider1_label)
        slider_layout.addWidget(self.slider2)
        slider_layout.addWidget(self.slider2_label)
        # layout.addLayout(slider_layout)
        slider_layout2= QHBoxLayout()
        self.slider3 = QSlider(Qt.Horizontal)
        self.slider3.setRange(0, 100)
        self.slider3.setValue(s3)
        self.slider3_label = QLabel("0")
        
        self.slider4 = QSlider(Qt.Horizontal)
        self.slider4.setRange(0, 10)
        self.slider4.setValue(s4)
        self.slider4_label = QLabel("0")
        
        self.slider3.setFixedSize(200, 12)  # Change the width and height as needed
        self.slider4.setFixedSize(200, 12)  # Change the width and height as needed
        
        slider_layout2.addWidget(self.slider3)
        slider_layout2.addWidget(self.slider3_label)
        slider_layout2.addWidget(self.slider4)
        slider_layout2.addWidget(self.slider4_label)
        
        # layout.addLayout(slider_layout2)
        
        self.slider1.valueChanged.connect(self.slider1_changed)
        self.slider2.valueChanged.connect(self.slider2_changed)
        self.slider3.valueChanged.connect(self.slider3_changed)
        self.slider4.valueChanged.connect(self.slider4_changed)
        

        main_layout.addLayout(top_row_layout)
        main_layout.addLayout(slider_layout)
        main_layout.addLayout(slider_layout2)
        

        # Set size policy for the graph widgets
        self.canvas1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.update_energy(s1, s2, s3, s4)
        # self.d=drawKpath(data, axis, fig, ax, ax2, linewidth, slider, N)

        # Plot data
        # self.plot_graphs()
        # self.update_text_edit_boxes()
        
    def slider1_changed(self,value):
        self.slider1_label.setText(str(value))
        print(value)
        self.update_energy(self.slider1.value(),self.slider2.value() , self.slider3.value(), self.slider4.value())
    def slider2_changed(self,value):
        self.slider2_label.setText(str(value))
        self.update_energy(self.slider1.value(),self.slider2.value() , self.slider3.value(), self.slider4.value())
    def slider3_changed(self,value):
        self.slider3_label.setText(str(value))
        self.update_energy(self.slider1.value(),self.slider2.value() , self.slider3.value(), self.slider4.value())
    def slider4_changed(self,value):
        self.slider4_label.setText(str(value))
        # self.plot_graph(self.slider1.value(),self.slider2.value())
        # print(self.slider1.value(),self.slider2.value())
        # self.update_show(self.slider1.value(),self.slider2.value())
        self.update_energy(self.slider1.value(),self.slider2.value() , self.slider3.value(), self.slider4.value())
        
    def update_energy(self,Energy,dE,te,dte):
        
        # self.ce_state=True
        E1=self.data_array['E'][Energy].item()
        # print(Energy,E1)
        E2=self.data_array['E'][Energy+dE].item()
        te1=self.data_array['dt'][te].item()
        te2=self.data_array['dt'][te+dte].item()
        # print(E1,E2,te1)
        self.figure1.clear()
        ax = self.figure1.add_subplot(111)  # Recreate the axis on the figure
        self.im=self.data_array.sel(E=slice(E1,E2), dt=slice(te1,te2)).mean(dim=("E", "dt")).plot(ax=ax)
        # ax.set_title('Loaded Data')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        # self.graphs[0].tight_layout()
        self.figure1.canvas.draw()
        # self.ev = self.graphs[0].gca().axvline(x=self.axis[0][self.slider1[1].value()], color='r', linestyle='--')
        # self.eh = self.graphs[0].gca().axhline(y=self.axis[1][self.slider1[2].value()], color='r', linestyle='--')
        

    def plot_graphs(self):
        # Plot on the top left graph
        x1 = np.linspace(0, 10, 100)
        y1 = np.sin(x1)
        self.axis1.plot(x1, y1)
        self.axis1.set_title('Top Left Graph')
        self.axis1.set_xlabel('X')
        self.axis1.set_ylabel('Y')

        # Plot on the bottom right graph
        x2 = np.linspace(0, 10, 100)
        y2 = np.cos(x2)
        self.axis2.plot(x2, y2)
        self.axis2.set_title('Bottom Right Graph')
        self.axis2.set_xlabel('X')
        self.axis2.set_ylabel('Y')

        # Update the canvas
        self.canvas1.draw()
        self.canvas2.draw()

    # def update_text_edit_boxes(self):
    #     # self.text_edit_top_right.setPlaceholderText("Top Right Text Edit Box")
    #     self.text_edit_bottom_left.setPlaceholderText("Bottom Left Text Edit Box")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DrawWindow()
    window.show()
    sys.exit(app.exec_())
