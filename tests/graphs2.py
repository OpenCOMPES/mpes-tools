import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QGridLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class showgraphs(QMainWindow):
    def __init__(self, x, y_arrays):
        super().__init__()
        self.setWindowTitle("Multiple Array Plots")
        self.setGeometry(100, 100, 800, 600)

        # Store x and y data
        self.x = x
        self.y_arrays = y_arrays
        self.num_plots = len(y_arrays)

        # Create a central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QGridLayout(central_widget)

        # Create and add buttons and plots for each y array in a 3x3 layout
        for i, y in enumerate(y_arrays):
            # Create a button to show the plot in a new window
            button = QPushButton(f"Show Plot {i+1}")
            button.setFixedSize(80, 30)  # Set a fixed size for the button
            button.clicked.connect(lambda checked, y=y, index=i+1: self.show_plot(y, index))

            # Calculate grid position
            row = (i // 3) * 2  # Each function will take 2 rows: one for the plot, one for the button
            col = i % 3

            # Add the plot canvas to the grid
            layout.addWidget(self.create_plot_widget(y, f"Plot {i+1}"), row, col)  # Plot in a 3x3 grid
            layout.addWidget(button, row + 1, col)  # Button directly below the corresponding plot

    def create_plot_widget(self, y, title):
        """Creates a plot widget for displaying a function."""
        figure, ax = plt.subplots()
        ax.plot(self.x, y)
        ax.set_title(title)
        ax.grid(True)
        ax.set_xlabel('x')
        ax.set_ylabel('y')

        # Create a FigureCanvas to embed in the Qt layout
        canvas = FigureCanvas(figure)
        return canvas  # Return the canvas so it can be used in the layout

    def show_plot(self, y, index):
        """Show the plot in a new window."""
        figure, ax = plt.subplots()
        ax.plot(self.x, y)
        ax.set_title(f"Plot {index}")
        ax.grid(True)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        plt.show()  # Show the figure in a new window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # # Example data: Define x and multiple y arrays
    # x = np.linspace(-10, 10, 400)
    # y_arrays = [
    #     np.sin(x),
    #     np.cos(x),
    #     np.tan(x),
    #     np.exp(x / 10),
    #     x**2,
    #     x**3,
    #     np.abs(x),
    #     np.log(x + 11),  # Shift to avoid log(0)
    #     np.sqrt(x + 11)  # Shift to avoid sqrt of negative
    # ]
    
    main_window = showgraphs()
    main_window.show()
    sys.exit(app.exec_())
