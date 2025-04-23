import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QGridLayout,QSlider,QLabel,QCheckBox
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from IPython.core.getipython import get_ipython
from mpes_tools.double_click_handler import SubplotClickHandler
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import xarray as xr
from mpes_tools.right_click_handler import RightClickHandler
from PyQt5.QtWidgets import QMenu
from PyQt5.QtGui import QCursor
class showgraphs(QMainWindow):
    def __init__(self, x, y_arrays,y_arrays_err,names,list_axis,list_plot_fits):
        super().__init__()
        self.setWindowTitle("Multiple Array Plots")
        self.setGeometry(100, 100, 800, 600)

        # Store x and y data
        self.dim=x.dims[0]
        self.x = x.data
        self.y_arrays = y_arrays
        self.y_arrays_err = y_arrays_err
        self.num_plots = len(y_arrays)
        self.list_plot_fits=list_plot_fits 
        self.list_axis=list_axis
        # Create a central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QGridLayout(central_widget)
        
        # print(len(x),len(list_plot_fits))
        # print(list_plot_fits[0])
        self.slider = QSlider()
        self.slider.setOrientation(1)  # 1 = Qt.Horizontal
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(x)-1)  # Adjust as needed
        self.slider.setValue(0)  # Default value
          # Function to update parameter
        
        self.slider_label = QLabel(f"{x.dims[0]}:0")
        
        self.figure, self.axis = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        plt.close(self.figure)
        
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        
        layout_plot = QVBoxLayout()
        layout_plot.addWidget(self.toolbar)  # assuming `layout` is your QVBoxLayout or similar
        layout_plot.addWidget(self.canvas) 
        
        widget_plot = QWidget()
        widget_plot.setLayout(layout_plot)
        
        vbox = QVBoxLayout()
        vbox.addWidget(widget_plot)
        vbox.addWidget(self.slider_label)
        vbox.addWidget(self.slider)
        
        layout.addLayout(vbox, 0, 0)  # Place in top-left
        
        self.click_handlers=[]
        self.handler_list=[]
        self.ax_list=[]
        self.data_list=[]
        self.cursor_list=[]
        # Create and add buttons and plots for each y array in a 3x3 layout
        for i, y in enumerate(y_arrays):
            # Create a button to show the plot in a new window
            
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
            widget,canvas,ax=self.create_plot_widget(data_array,y_arrays_err[i], names[i])
            # Add the plot canvas to the grid
            checkbox = QCheckBox(f"Show error bars {i+1}")
            checkbox.setFixedSize(120, 30)  # Adjust size if needed
            checkbox.stateChanged.connect(lambda state, data_array=data_array, y_err=y_arrays_err[i], index=i: self.show_err(state, data_array, y_err, index))
            
            layout.addWidget(widget, row, col)  # Plot in a 3x3 grid
            # layout.addWidget(self.create_plot_widget(y, f"Plot {i+1}_"+names[i]), row, col)  # Plot in a 3x3 grid
            layout.addWidget(checkbox, row + 1, col)  # Button directly below the corresponding plot
            handler = RightClickHandler(canvas, ax,self.show_pupup_window)
            canvas.mpl_connect("button_press_event", handler.on_right_click)
            self.handler_list.append(handler)
            # handler = SubplotClickHandler(ax, self.external_callback)
            # canvas.mpl_connect("button_press_event", handler.handle_double_click)
            # self.click_handlers.append(handler)
            self.ax_list.append(ax)
            self.cursor=ax.axvline(x=self.x[0], color='r', linestyle='--')
            self.cursor_list.append(self.cursor)
        self.update_parameter(0)
        self.slider.valueChanged.connect(self.update_parameter)
        
    def show_pupup_window(self,canvas,ax):
        # print(f"External callback: clicked subplot ({i},{j})")
        for i, ax_item in enumerate(self.ax_list):
            if ax == ax_item:
                data = self.data_list[i]
                coords = {k: data.coords[k].values.tolist() for k in data.coords}
                dims = data.dims
                name = data.name if data.name else f"data_{i}"
                menu = QMenu(canvas)
                action1 = menu.addAction(f"{data.name} plot")
                action = menu.exec_(QCursor.pos())
        
                if action == action1:
                    print(f'''
import xarray as xr
import numpy as np

data_array = xr.DataArray(
    data=np.array({data.values.tolist()}),
    dims={dims},
    coords={coords},
    name="{name}"
)
''')
                

        
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
        
    def create_plot_widget(self, data_array, y_err , title):
        """Creates a plot widget for displaying a function."""
        
        figure, ax = plt.subplots()
        plt.close(figure)
        
        # ax.errorbar(data_array[data_array.dims[0]].values, data_array.values, yerr=y_err, fmt='o', capsize=3)
        ax.plot(data_array[data_array.dims[0]].values, data_array.values,'o')
        # data_array.plot(ax=ax,fmt='o', capsize=3)
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

    def show_err(self,state,data_array,y_err,i):
        self.ax_list[i].clear()
        if state == Qt.Checked:
            self.ax_list[i].errorbar(data_array[data_array.dims[0]].values, data_array.values, yerr=y_err, fmt='o', capsize=3)
        else:
            self.ax_list[i].plot(data_array[data_array.dims[0]].values, data_array.values,'o')
            # data_array.plot(ax=self.ax_list[i], fmt='o', capsize=3)
        self.ax_list[i].set_title(data_array.name)
        self.cursor_list[i]=self.ax_list[i].axvline(x=self.x[self.slider.value()], color='r', linestyle='--')
        self.ax_list[i].figure.canvas.draw_idle()
            
    def update_parameter(self, value):
        for i, c in enumerate(self.cursor_list):
            if c is not None:
                c.remove()
            self.cursor_list[i]=self.ax_list[i].axvline(x=self.x[value], color='r', linestyle='--')
            self.ax_list[i].figure.canvas.draw_idle()
        base = self.slider_label.text().split(':')[0]
        self.slider_label.setText(f"{base}: {self.x[value]:.2f}")
        self.axis.clear()
        
        self.axis.plot(self.list_axis[0][0],self.list_plot_fits[value][0][0],'o', label='data')
        self.axis.plot(self.list_axis[1][0],self.list_plot_fits[value][1][0],'r--', label='fit')
        self.axis.legend()
        self.figure.tight_layout()
        self.canvas.draw()
    # def create_plot_widget1(self,x_data, y_data, title, return_axes=False):
    #     from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    #     import matplotlib.pyplot as plt
    
    #     fig, ax = plt.subplots()
    #     canvas = FigureCanvas(fig)  
    
    #     ax.plot(x_data,y_data)
    #     ax.set_title(title)
    
    #     if return_axes:
    #         return canvas, ax  # Allow updating later
    #     return canvas

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    main_window = showgraphs()
    main_window.show()
    sys.exit(app.exec_())
