import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QGridLayout,QSlider,QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from IPython.core.getipython import get_ipython
from mpes_tools.double_click_handler import SubplotClickHandler
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import xarray as xr
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
        plt.close(self.figure)
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.slider_label)
        vbox.addWidget(slider)
        
        layout.addLayout(vbox, 0, 0)  # Place in top-left
        self.update_parameter(0)
        self.click_handlers=[]
        self.ax_list=[]
        self.data_list=[]
        # Create and add buttons and plots for each y array in a 3x3 layout
        for i, y in enumerate(y_arrays):
            # Create a button to show the plot in a new window
            button = QPushButton(f"Show Plot {i+1}")
            button.setFixedSize(80, 30)  # Set a fixed size for the button
            button.clicked.connect(lambda checked, y=y, index=i+1: self.show_plot(y, index, names[i]))
            data_array = xr.DataArray(
                data=y,
                dims=[self.dim],                # e.g., 'energy', 'time', etc.
                coords={self.dim: self.x},
                name=names[i]                      # Optional: give it a name (like the plot title)
            )
            self.data_list.append(data_array)
            # Calculate grid position
            row = ((i+1) // 3) * 2   # Each function will take 2 rows: one for the plot, one for the button
            col = (i+1) % 3
            widget,canvas,ax=self.create_plot_widget(data_array, f"Plot {i+1}_"+names[i])
            # Add the plot canvas to the grid
            
            layout.addWidget(widget, row, col)  # Plot in a 3x3 grid
            # layout.addWidget(self.create_plot_widget(y, f"Plot {i+1}_"+names[i]), row, col)  # Plot in a 3x3 grid
            layout.addWidget(button, row + 1, col)  # Button directly below the corresponding plot
            handler = SubplotClickHandler(ax, self.external_callback)
            canvas.mpl_connect("button_press_event", handler.handle_double_click)
            self.click_handlers.append(handler)
            self.ax_list.append(ax)
    def external_callback(self,ax):
        # print(f"External callback: clicked subplot ({i},{j})")
        for i, ax_item in enumerate(self.ax_list):
            if ax == ax_item:
                data = self.data_list[i]
                coords = {k: data.coords[k].values.tolist() for k in data.coords}
                dims = data.dims
                name = data.name if data.name else f"data_{i}"
                content = f"""
import xarray as xr
import numpy as np

data_array = xr.DataArray(
    data=np.array({data.values.tolist()}),
    dims={dims},
    coords={coords},
    name="{name}"
)
"""
                break
        shell = get_ipython()
        payload = dict(
            source='set_next_input',
            text=content,
            replace=False,
        )
        shell.payload_manager.write_payload(payload, single=False)
        # shell.run_cell("%gui qt")
        QApplication.processEvents()
        print('results extracted!')
        
    def create_plot_widget(self, data_array, title):
        """Creates a plot widget for displaying a function."""
        
        figure, ax = plt.subplots()
        plt.close(figure)
        data_array.plot(ax=ax)
        ax.set_title(title)
        # print('create_plot'+f"self.ax id: {id(ax)}")
        # Create a FigureCanvas to embed in the Qt layout
        canvas = FigureCanvas(figure)
        toolbar = NavigationToolbar(canvas, self)

        # Wrap canvas and toolbar in a widget with a layout
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
    
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        return widget,canvas,ax  # Return the canvas so it can be used in the layout

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
