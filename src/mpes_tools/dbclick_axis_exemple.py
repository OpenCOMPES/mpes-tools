import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QDialog, QLineEdit, QPushButton, QHBoxLayout, QLabel
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class AxisEditor:
    def __init__(self, canvas, ax):
        self.canvas = canvas
        self.ax = canvas.figure.axes[0]
        self.cid = self.canvas.mpl_connect('button_press_event', self.on_click)

    def on_click(self, event):

        if not event.dblclick:
            return

        bbox = self.ax.get_window_extent(self.canvas.renderer)

        margin = 30
        x, y = event.x, event.y
        near_xaxis = bbox.y0 - margin < y < bbox.y0 + margin
        near_yaxis = bbox.x0 - margin < x < bbox.x0 + margin

        if near_xaxis:
            axis = "x"
            old_min, old_max = self.ax.get_xlim()
        elif near_yaxis:
            axis = "y"
            old_min, old_max = self.ax.get_ylim()
        else:
            return

        dialog = MinMaxDialog(axis, old_min, old_max)
        if dialog.exec_():
            new_min, new_max = dialog.get_values()
            if new_min is not None and new_max is not None:
                if axis == "x":
                    self.ax.set_xlim(new_min, new_max)
                else:
                    self.ax.set_ylim(new_min, new_max)
                self.canvas.draw_idle()
class MinMaxDialog(QDialog):
    def __init__(self, axis_name, old_min, old_max):
        super().__init__()
        self.setWindowTitle(f"Set {axis_name}-axis limits")
        layout = QVBoxLayout()

        self.min_edit = QLineEdit(str(old_min))
        self.max_edit = QLineEdit(str(old_max))

        layout.addWidget(QLabel(f"{axis_name}-axis min:"))
        layout.addWidget(self.min_edit)
        layout.addWidget(QLabel(f"{axis_name}-axis max:"))
        layout.addWidget(self.max_edit)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_values(self):
        try:
            return float(self.min_edit.text()), float(self.max_edit.text())
        except ValueError:
            return None, None
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Axis Click Test")

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        self.canvas = FigureCanvas(Figure())
        layout.addWidget(self.canvas)

        self.ax = self.canvas.figure.add_subplot(111)
        self.ax.plot([0, 1, 2], [10, 20, 15])

        self.canvas.draw()  # Important to generate renderer for get_window_extent
        self.editor = AxisEditor(self.canvas, self.ax)  # Store reference!


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
