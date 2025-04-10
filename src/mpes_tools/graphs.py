import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QGridLayout,QSlider,QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class showgraphs(QMainWindow):
    def __init__(self, x, y_arrays,names,list_axis,list_plot_fits):
        super().__init__()
        self.setWindowTitle("Multiple Array Plots")
        self.setGeometry(100, 100, 800, 600)

        # Store x and y data
        self.dim=x.dims[0]
        self.x = x.data
        self.y_arrays = y_arrays
        self.num_plots = len(y_arrays)
        self.list_plot_fits=list_plot_fits
        self.list_axis=list_axis
        # Create a central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QGridLayout(central_widget)
        
        
        # print(len(x),len(list_plot_fits))
        # print(list_plot_fits[0])
        slider = QSlider()
        slider.setOrientation(1)  # 1 = Qt.Horizontal
        slider.setMinimum(0)
        slider.setMaximum(len(x)-1)  # Adjust as needed
        slider.setValue(0)  # Default value
        slider.valueChanged.connect(self.update_parameter)  # Function to update parameter
        
        self.slider_label = QLabel(f"{x.dims[0]}:0")
        
        self.figure, self.axis = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.slider_label)
        vbox.addWidget(slider)
        
        layout.addLayout(vbox, 0, 0)  # Place in top-left
        self.update_parameter(0)
        # Create and add buttons and plots for each y array in a 3x3 layout
        for i, y in enumerate(y_arrays):
            # Create a button to show the plot in a new window
            button = QPushButton(f"Show Plot {i+1}")
            button.setFixedSize(80, 30)  # Set a fixed size for the button
            button.clicked.connect(lambda checked, y=y, index=i+1: self.show_plot(y, index, names[i]))

            # Calculate grid position
            row = ((i+1) // 3) * 2   # Each function will take 2 rows: one for the plot, one for the button
            col = (i+1) % 3

            # Add the plot canvas to the grid
            layout.addWidget(self.create_plot_widget(y, f"Plot {i+1}_"+names[i]), row, col)  # Plot in a 3x3 grid
            layout.addWidget(button, row + 1, col)  # Button directly below the corresponding plot
        
    def create_plot_widget(self, y, title):
        """Creates a plot widget for displaying a function."""
        figure, ax = plt.subplots()
        ax.plot(self.x, y)
        ax.set_title(title)
        ax.grid(True)
        ax.set_xlabel(self.dim)
        # ax.set_ylabel('y')

        # Create a FigureCanvas to embed in the Qt layout
        canvas = FigureCanvas(figure)
        return canvas  # Return the canvas so it can be used in the layout

    def show_plot(self, y, index, name):
        """Show the plot in a new window."""
        figure, ax = plt.subplots()
        ax.plot(self.x, y)
        ax.set_title(f"Plot {index}_"+ name)
        ax.grid(True)
        ax.set_xlabel(self.dim)
        # ax.set_ylabel('y')
        plt.show()  # Show the figure in a new window
    def update_parameter(self, value):
        base = self.slider_label.text().split(':')[0]
        print("self.x:", self.x)
        print("Slider value:", value)
        self.slider_label.setText(f"{base}: {self.x[value]:.2f}")
        self.axis.clear()
        
        self.axis.plot(self.list_axis[0][0],self.list_plot_fits[value][0][0],'o', label='data')
        self.axis.plot(self.list_axis[1][0],self.list_plot_fits[value][1][0],'r--', label='fit')
        self.axis.legend()
        self.figure.tight_layout()
        self.canvas.draw()
    def create_plot_widget1(self,x_data, y_data, title, return_axes=False):
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        import matplotlib.pyplot as plt
    
        fig, ax = plt.subplots()
        canvas = FigureCanvas(fig)  
    
        ax.plot(x_data,y_data)
        ax.set_title(title)
    
        if return_axes:
            return canvas, ax  # Allow updating later
        return canvas

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    main_window = showgraphs()
    main_window.show()
    sys.exit(app.exec_())
