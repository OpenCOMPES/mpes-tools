import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QAction, QFileDialog, QSlider, QGridLayout,QHBoxLayout, QSizePolicy,QLabel, QGridLayout, QPushButton, QFileDialog
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import h5py
from mpes_tools.Gui_3d import Gui_3d
import xarray as xr
from mpes_tools.hdf5 import load_h5
from mpes_tools.show_4d_window import show_4d_window
import os
from PyQt5.QtGui import QPixmap

class ARPES_Analyser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ARPES_Analyser")
        self.setGeometry(100, 100, 400, 300)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QGridLayout()
        central_widget.setLayout(layout)
        N=256
        
        # Get the directory of the current script
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Build full path to image files in the same folder
        image1_path = os.path.join(base_path, "METIS.png")
        image2_path = os.path.join(base_path, "Phoibos.png")

        # --- First Button + Image ---
        vbox1 = QVBoxLayout()
        label_img1 = QLabel()
        pixmap1 = QPixmap(image1_path)  # 🔁 Replace with your image path
        label_img1.setPixmap(pixmap1.scaled(N, N, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        label_img1.setAlignment(Qt.AlignCenter)

        self.btn_open_h5 = QPushButton("Open File H5")
        self.btn_open_h5.clicked.connect(self.open_file_dialoge)

        vbox1.addWidget(label_img1)
        vbox1.addWidget(self.btn_open_h5)

        # --- Second Button + Image ---
        vbox2 = QVBoxLayout()
        label_img2 = QLabel()
        pixmap2 = QPixmap(image2_path)  # 🔁 Replace with your image path
        label_img2.setPixmap(pixmap2.scaled(N, N, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        label_img2.setAlignment(Qt.AlignCenter)

        self.btn_open_phoibos = QPushButton("Open File Phoibos")
        self.btn_open_phoibos.clicked.connect(self.open_file_phoibos)

        vbox2.addWidget(label_img2)
        vbox2.addWidget(self.btn_open_phoibos)

        # Add the vbox layouts to the main grid layout
        layout.addLayout(vbox1, 0, 0)
        layout.addLayout(vbox2, 0, 1)

        self.graph_windows = []
        self.ce = None

        self.show()


        
    def open_file_phoibos(self):
        # ... existing code ...
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Data Files (*.npz *.nxs)")
        if file_path:
            if file_path.endswith('.npz'):
                loaded_data = np.load(file_path)
                V1 = xr.DataArray(loaded_data['data_array'], 
                                dims=['Angle', 'Ekin','delay'], 
                                coords={'Angle': loaded_data['Angle'], 
                                       'Ekin': loaded_data['Ekin'],
                                       'delay': loaded_data['delay']})
            elif file_path.endswith('.nxs'):
                with h5py.File(file_path, 'r') as f:
                    # Ajuste os caminhos dos dados de acordo com a estrutura do seu arquivo NeXus
                    # Isso é um exemplo - você precisa adaptar para a estrutura específica do seu arquivo
                    data_array = f['/entry/data/data'][:]  # Ajuste o caminho conforme necessário
                    angle = f['/entry/data/angular0'][:]      # Ajuste o caminho conforme necessário
                    energy = f['/entry/data/energy'][:]    # Ajuste o caminho conforme necessário
                    delay = f['/entry/data/delay'][:]      # Ajuste o caminho conforme necessário
                    
                    V1 = xr.DataArray(data_array,
                                    dims=['Angle', 'Ekin', 'delay'],
                                    coords={'Angle': angle,
                                           'Ekin': energy,
                                           'delay': delay})

        axis=[V1['Angle'],V1['Ekin']-21.7,V1['delay']]
        graph_window= Gui_3d(V1,0,0,'Phoibos')
        graph_window.show()
        self.graph_windows.append(graph_window)

    def open_file_dialoge(self):
        # Open file dialog to select a .h5 file
        file_path, _ = QFileDialog.getOpenFileName(self, "Open hdf5", "", "h5 Files (*.h5)")
        print(file_path)
        if file_path:
            data_array = load_h5(file_path)
            graph_4d = show_4d_window(data_array)
            graph_4d.show()
            self.graph_windows.append(graph_4d)
            # self.load_data(data_array)

    

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ARPES_Analyser()
    window.show()
    sys.exit(app.exec_())
