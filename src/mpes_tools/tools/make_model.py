import sys
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QTextEdit, QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QLabel, QAction, QCheckBox, QPushButton, QListWidget, QTableWidget, QTableWidgetItem, QTableWidget, QCheckBox, QSplitter
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QHBoxLayout, QCheckBox, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt



class make_model:
    # from matplotlib.widgets import CheckButtons, Button
    # %matplotlib qt
    
    def __init__(self,mod,table_widget):
        
        self.mod=mod
        self.params=mod.make_params()
        print('otherpalce',self.params)
        print('thefuuuuTable',table_widget)
        print('count',table_widget.rowCount())
        for row in range(table_widget.rowCount()):
            item = table_widget.item(row, 1)
            checkbox_widget = table_widget.cellWidget(row, 3)
            print('tableitenm=',item)
            if item is not None and item.text().strip():
                header_item = table_widget.verticalHeaderItem(item.row())
                checkbox=checkbox_widget.findChild(QCheckBox)
                print(header_item.text(),item.text())
                if header_item.text()== "Fermi level":
                    self.params['mu'].set(value=float(item.text()))
                    if table_widget.item(row, 0) is not None:
                        self.params['mu'].set(min=float(table_widget.item(row, 0).text()))
                    if table_widget.item(row, 2) is not None:
                        self.params['mu'].set(max=float(table_widget.item(row, 2).text()))
                    if checkbox.isChecked():
                        self.params['mu'].vary = False
                        
                elif header_item.text()== "Temperature":
                    self.params['T'].set(value=float(item.text()))
                    if table_widget.item(row, 0) is not None:
                        self.params['T'].set(min=float(table_widget.item(row, 0).text()))
                    if table_widget.item(row, 2) is not None:
                        self.params['T'].set(max=float(table_widget.item(row, 2).text()))
                    if checkbox.isChecked():
                        self.params['T'].vary = False
                elif header_item.text()== "sigma":
                    self.params['sigma'].set(value=float(item.text()))
                    self.params['sigma'].set(min=0)
                    if table_widget.item(row, 0) is not None:
                        self.params['sigma'].set(min=float(table_widget.item(row, 0).text()))
                    if table_widget.item(row, 2) is not None:
                        self.params['sigma'].set(max=float(table_widget.item(row, 2).text()))
                    if checkbox.isChecked():
                        self.params['sigma'].vary = False
                else:
                    self.params[header_item.text()].set(value=float(item.text()))
                    if table_widget.item(row, 0) is not None:
                        self.params[header_item.text()].set(min=float(table_widget.item(row, 0).text()))
                    if table_widget.item(row, 2) is not None:
                        self.params[header_item.text()].set(max=float(table_widget.item(row, 2).text()))
                    if checkbox.isChecked():
                        self.params[header_item.text()].vary = False
        
        
    def current_model(self):
        return self.mod
    def current_params(self):
        return self.params
                