import sys
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QTextEdit, QLineEdit,QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QLabel, QAction, QCheckBox, QPushButton, QListWidget, QTableWidget, QTableWidgetItem, QTableWidget, QCheckBox, QSplitter
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QHBoxLayout, QCheckBox, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
from lmfit.models import ExpressionModel,Model
from lmfit import CompositeModel, Model
from lmfit.lineshapes import gaussian, step
import inspect
from mpes_tools.movable_vertical_cursors_graph import MovableCursors
from mpes_tools.make_model import make_model
from mpes_tools.graphs import showgraphs




class fit_panel_single(QMainWindow):
    def __init__(self,data):
        super().__init__()

        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 1500, 800)
        
        # Create a menu bar
        menu_bar = self.menuBar()

        # Create a 'View' menu
        view_menu = menu_bar.addMenu("View")

        # Create actions for showing and hiding the graph window
        clear_graph_action = QAction("Show Graph", self)
        clear_graph_action.triggered.connect(self.clear_graph_window)
        view_menu.addAction(clear_graph_action)

        # Store references to graph windows to prevent garbage collection
        self.graph_windows = []

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QHBoxLayout()
        central_widget.setLayout(layout)

        # Create a splitter for two panels
        splitter = QSplitter(Qt.Horizontal)

        # Create a left panel widget and its layout
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        # Create a right panel widget and its layout
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        # Add the panels to the splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        self.figure, self.axis = plt.subplots()
        plt.close(self.figure)
        self.canvas = FigureCanvas(self.figure)
        # Create two checkboxes
        self.checkbox0 = QCheckBox("Cursors")
        self.checkbox0.stateChanged.connect(self.checkbox0_changed)
        

        # Create two checkboxes
        self.checkbox1 = QCheckBox("Multiply with Fermi Dirac")
        self.checkbox1.stateChanged.connect(self.checkbox1_changed)

        self.checkbox2 = QCheckBox("Convolve with a Gaussian")
        self.checkbox2.stateChanged.connect(self.checkbox2_changed)
        
        self.checkbox3 = QCheckBox("add background offset")
        self.checkbox3.stateChanged.connect(self.checkbox3_changed)

        
        self.guess_button = QPushButton("Guess")
        self.guess_button.clicked.connect(self.button_guess_clicked)
        
        bigger_layout = QVBoxLayout()
        bigger_layout.addWidget(self.guess_button)
        # Create a QListWidget
        self.list_widget = QListWidget()
        self.list_widget.addItems(["linear","Lorentz", "Gauss", "sinusoid","constant","jump"])
        self.list_widget.setMaximumSize(120,150)
        self.list_widget.itemClicked.connect(self.item_selected)

        self.add_button = QPushButton("add")
        self.add_button.clicked.connect(self.button_add_clicked)
        
        self.remove_button = QPushButton("remove")
        self.remove_button.clicked.connect(self.button_remove_clicked)
        

        self.graph_button = QPushButton("clear graph")
        self.graph_button.clicked.connect(self.clear_graph_window)
        
        self.fit_button = QPushButton("Fit")
        self.fit_button.clicked.connect(self.fit)


        
        left_buttons=QVBoxLayout()
        left_sublayout=QHBoxLayout()
        
        left_buttons.addWidget(self.add_button)
        left_buttons.addWidget(self.remove_button)
        left_buttons.addWidget(self.graph_button)
        left_buttons.addWidget(self.fit_button)

        
        left_sublayout.addWidget(self.list_widget)
        left_sublayout.addLayout(left_buttons) 

        # Add widgets to the left layout
        left_layout.addWidget(self.canvas)
        left_layout.addWidget(self.checkbox0)
        left_layout.addLayout(left_sublayout) 
        
        
        self.text_equation = QTextEdit()
        # self.text_equation.setMinimumSize(50, 50)  # Set minimum size
        self.text_equation.setMaximumSize(500, 30)  # Set maximum size
        
        # Create a table widget for the right panel
        self.table_widget = QTableWidget(0, 4)  # 6 rows and 4 columns (including the special row)
        self.table_widget.setHorizontalHeaderLabels(['min', 'value', 'max', 'fix'])
        # self.table_widget.setVerticalHeaderLabels(['Row 1', 'The ROW', 'Row 2', 'Row 3', 'Row 4', 'Row 5'])
        self.table_widget.itemChanged.connect(self.table_item_changed)
        self.table_widget.setMaximumSize(700,500)
        # Add checkboxes to the last column of the table, except for the special row
        for row in range(6):
            if row != 1:  # Skip 'The ROW'
                checkbox_widget = QWidget()
                checkbox_layout = QHBoxLayout()
                checkbox_layout.setAlignment(Qt.AlignCenter)
                checkbox = QCheckBox()
                checkbox_layout.addWidget(checkbox)
                checkbox_widget.setLayout(checkbox_layout)
                self.table_widget.setCellWidget(row, 3, checkbox_widget)

        # Set 'The ROW' with uneditable empty cells
        for col in range(4):
            # if col == 3:  # Skip the checkbox column for 'The ROW'
            #     continue
            item = QTableWidgetItem('')
            item.setFlags(Qt.ItemIsEnabled)  # Make cell uneditable
            self.table_widget.setItem(1, col, item)

        # Add the table to the right layout
        checkboxes=QVBoxLayout()
        top_lay = QHBoxLayout()
        above_table=QVBoxLayout()
        checkboxes.addWidget(self.checkbox1)
        checkboxes.addWidget(self.checkbox2)
        checkboxes.addWidget(self.checkbox3)
        top_lay.addWidget(self.text_equation)
        top_lay.addLayout(checkboxes)
        above_table.addLayout(top_lay)
        above_table.addLayout(bigger_layout)
        right_layout.addLayout(above_table)
        right_layout.addWidget(self.table_widget)

        # Add the splitter to the main layout
        layout.addWidget(splitter)
        def zero(x):
            return 0
        self.equation= None
        self.mod= Model(zero)
        self.total_function=zero
        self.function_before_Fermi= zero
        self.function_before_convoluted= zero
        self.update_text_edit_boxes()
        self.i=0
        
        self.function_list=[]
        self.function_names_list=[]
        self.cursor_handler = None
        self.FD_state = False
        self.CV_state = False
        self.t0_state = False
        self.offset_state = False
        self.data=data
        self.y=data
        self.dim=data.dims[0]
        self.plot_graph()

    def plot_graph(self):
        self.axis.clear()
        self.y.plot(ax=self.axis)
        if self.checkbox0.isChecked():
            if self.cursor_handler is None:
                self.cursor_handler = MovableCursors(self.axis)
            else:
                self.cursor_handler.redraw()
        self.figure.tight_layout()
        self.canvas.draw()
    def update_text_edit_boxes(self):
        self.text_equation.setPlaceholderText("Top Right Text Edit Box")
    
    def offset_function (self,x,offset):
        return 0*x+offset    
    def constant (self,x,A):
        return 0*x+A
    def linear (self,x,a,b):
        return a*x+b
    def lorentzian(self,x, A, x0, gamma):
        c=0.0000
        return A / (1 + ((x - x0) / (gamma+c)) ** 2)
    def fermi_dirac(self,x, mu, T):
        kb = 8.617333262145 * 10**(-5)  # Boltzmann constant in eV/K
        return 1 / (1 + np.exp((x - mu) / (kb * T)))
    def gaussian(self,x,A, x0, gamma):
        return A* np.exp(-(x -x0)**2 / (2 * gamma**2))
    def gaussian_conv(self,x,sigma):
        return  np.exp(-(x)**2 / (2 * sigma**2))
    def jump(self,x, mid):
        """Heaviside step function."""
        o = np.zeros(x.size)
        imid = max(np.where(x <= mid)[0])
        o[imid:] = 1.0
        return o
    def jump2(self,x, mid,Amp):
        """Heaviside step function."""
        o = np.zeros(x.size)
        imid = max(np.where(x <= mid)[0])
        o[:imid] = Amp
        return o

    def centered_kernel(self,x, sigma):
        mean = x.mean()
        return np.exp(-(x-mean)**2/(2*sigma/2.3548200)**2)

    def convolve(self,arr, kernel):
        """Simple convolution of two arrays."""
        npts = min(arr.size, kernel.size)
        pad = np.ones(npts)
        tmp = np.concatenate((pad*arr[0], arr, pad*arr[-1]))
        out = np.convolve(tmp, kernel/kernel.sum(), mode='valid')
        noff = int((len(out) - npts) / 2)
        return out[noff:noff+npts]
    
    
    def convolution(x, func, *args, sigma=1.0):
            N = 20  # Assuming N is intended to be a local variable here
            x_step = x[1] - x[0]
            
            # Create the shifted input signal 'y' for convolution
            y = np.zeros(N + len(x))
            for i in range(N):
                y[i] = x[0] - (N - i) * x_step
            y[N:] = x  # Append the original signal x to y
            
            # Create the Gaussian kernel
            x_gauss = np.linspace(-0.5, 0.5, len(x))
            gaussian_values = np.exp(-0.5 * (x_gauss / sigma)**2) / (sigma * np.sqrt(2 * np.pi))
            
            # Evaluate the function values with parameters
            function_values = func(x, *args)
            
            # Perform convolution
            convolution_result = np.convolve(function_values, gaussian_values, mode='same')
            
            return convolution_result[N-1:-1]
    

    def clear_graph_window(self):
        self.axis.clear()
        self.plot_graph()
        
    def checkbox0_changed(self, state):
        if state == Qt.Checked:
            if self.cursor_handler is None:
                self.cursor_handler = MovableCursors(self.axis)
                self.canvas.draw()
            else:
                self.cursor_handler.redraw()
        else:
            self.cursor_handler.remove()
    
    def checkbox1_changed(self, state):
        if self.CV_state== True:
            pos=2
        else:
            pos=0
        if state == Qt.Checked:
            self.FD_state = True
            self.update_equation()
            self.table_widget.insertRow(pos)
            label_item = QTableWidgetItem("Fermi")
            self.table_widget.setVerticalHeaderItem(pos, label_item)
            for col in range(4):
                item = QTableWidgetItem('')
                item.setFlags(Qt.ItemIsEnabled)  # Make cell uneditable
                self.table_widget.setItem(pos, col, item)
                item.setBackground(QBrush(QColor('grey')))
            c=self.table_widget.rowCount()
            self.table_widget.insertRow(pos+1)
            label_item1 = QTableWidgetItem("Fermi level")
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout()
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(lambda state, row= pos+1: self.handle_checkbox_state_change(state, row))
            # print('thecount',c+1)
            checkbox_layout.addWidget(checkbox)
            checkbox_widget.setLayout(checkbox_layout)
            self.table_widget.setCellWidget(pos+1, 3, checkbox_widget)
            self.table_widget.setVerticalHeaderItem(pos+1, label_item1)
            
            self.table_widget.insertRow(pos+2)
            label_item2 = QTableWidgetItem("Temperature")
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout()
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(lambda state, row= pos+2: self.handle_checkbox_state_change(state, row))
            checkbox_layout.addWidget(checkbox)
            checkbox_widget.setLayout(checkbox_layout)
            self.table_widget.setCellWidget(pos+2, 3, checkbox_widget)
            self.table_widget.setVerticalHeaderItem(pos+2, label_item2)
        else:
            self.FD_state = False
            self.update_equation()
            # print("Checkbox 1 is unchecked")
            
            self.table_widget.removeRow(pos)
            self.table_widget.removeRow(pos)
            self.table_widget.removeRow(pos)
            
    def checkbox2_changed(self, state):
        if state == Qt.Checked:
            self.CV_state = True
            
            self.update_equation()

            self.table_widget.insertRow(0)
            label_item = QTableWidgetItem("Convolution")
            self.table_widget.setVerticalHeaderItem(0, label_item)
            # self.table_widget.setVerticalHeaderItem(0, new_row_name)
            for col in range(4):
                item = QTableWidgetItem('')
                item.setFlags(Qt.ItemIsEnabled)  # Make cell uneditable
                self.table_widget.setItem(0, col, item)
                item.setBackground(QBrush(QColor('grey')))
                
            self.table_widget.insertRow(1)
            label_item1 = QTableWidgetItem("sigma")
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout()
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(lambda state, row= 1: self.handle_checkbox_state_change(state, row))
            checkbox_layout.addWidget(checkbox)
            checkbox_widget.setLayout(checkbox_layout)
            self.table_widget.setCellWidget(1, 3, checkbox_widget)
            self.table_widget.setVerticalHeaderItem(1, label_item1)
            
        else:
            self.CV_state = False
            self.update_equation()
            # print("Checkbox 1 is unchecked")
            
            self.table_widget.removeRow(0)
            self.table_widget.removeRow(0)
    def checkbox3_changed(self, state):
        if state == Qt.Checked:
            self.offset_state=True
        else:
            self.offset_state=False
        
    def item_selected(self, item):
        # print(f"Selected: {item.text()}")
        if item.text() == 'Lorentz':
            self.function_selected = self.lorentzian
        elif item.text() == 'Gauss':
            self.function_selected = self.gaussian 
        elif item.text()=='linear':
            self.function_selected =self.linear
        elif item.text()=='constant':
            self.function_selected =self.constant
        elif item.text()=='jump':
            self.function_selected =self.jump2
        
    def button_guess_clicked(self):
        cursors= self.cursor_handler.cursors()
        self.y_f=self.y.isel({self.dim:slice(cursors[0], cursors[1])})
        self.x_f=self.y_f[self.dim]
        max_value= self.y_f.data.max()
        min_value= self.y_f.data.min()
        mean_value= self.y_f.data.mean()
        max_arg=self.y_f.data.argmax()
        # print(self.x_f[max_arg].item())
        for row in range(self.table_widget.rowCount()):
            header_item = self.table_widget.verticalHeaderItem(row)
            if "A" in header_item.text():
                self.params[header_item.text()].set(value=max_value)
                item = QTableWidgetItem(str(max_value))
                self.table_widget.setItem(row, 1, item)
            elif "x0" in header_item.text():
                self.params[header_item.text()].set(value=self.x_f[max_arg].item())
                item = QTableWidgetItem(str(self.x_f[max_arg].item()))
                self.table_widget.setItem(row, 1, item)
            elif "gamma" in header_item.text():
                self.params[header_item.text()].set(value=0.2)
                item = QTableWidgetItem(str(0.2))
                self.table_widget.setItem(row, 1, item)

            
    
    def button_remove_clicked(self):
        if self.i>0:
            self.i-=1
        current_row_count = self.table_widget.rowCount()
        sig = inspect.signature(self.function_list[-1])
        params = sig.parameters
        
        for p in range(len(params)):
            self.table_widget.removeRow(current_row_count-1-p)    
            
        self.function_list.remove(self.function_list[-1])
        self.function_names_list.remove(self.function_names_list[-1])
        self.update_equation()
        self.create()

    def button_add_clicked(self):
        def zero(x):
            return 0
        
        
        self.i+=1
        self.function_list.append(self.function_selected)
        self.function_names_list.append(self.list_widget.currentItem().text())
        j=0
        for p in self.function_list:
            current_function=Model(p,prefix='f'+str(j)+'_')
            j+=1
            
        
        current_row_count = self.table_widget.rowCount()
        
        self.table_widget.insertRow(current_row_count)
        new_row_name = QTableWidgetItem(self.list_widget.currentItem().text())
        self.table_widget.setVerticalHeaderItem(current_row_count, new_row_name)
        for col in range(4):
            item = QTableWidgetItem('')
            item.setFlags(Qt.ItemIsEnabled)  # Make cell uneditable
            self.table_widget.setItem(current_row_count, col, item)
            item.setBackground(QBrush(QColor('grey')))
        c=current_row_count
        for p in range(len(current_function.param_names)):

            self.table_widget.insertRow(c+p+1)
            # print(current_function.param_names[p])
            new_row_name = QTableWidgetItem(current_function.param_names[p])
            self.table_widget.setVerticalHeaderItem(c+p+1, new_row_name)
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout()
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(lambda state, row=c + p + 1: self.handle_checkbox_state_change(state, row))
            checkbox_layout.addWidget(checkbox)
            checkbox_widget.setLayout(checkbox_layout)
            self.table_widget.setCellWidget(c+p+1, 3, checkbox_widget)
        
        self.update_equation()
        self.create()
        
    def update_equation(self):
        self.equation=''
        # print('names',self.function_names_list)
        for j,n in enumerate(self.function_names_list):
            if len(self.function_names_list)==1:
                self.equation= n
            else:
                if j==0:
                    self.equation= n
                else:
                    self.equation+= '+' + n
        if self.FD_state:
            self.equation= '('+ self.equation+ ')* Fermi_Dirac'
        self.text_equation.setPlainText(self.equation)
        # print('equation',self.equation)
    

    def table_item_changed(self, item):
        # print(f"Table cell changed at ({item.row()}, {item.column()}): {item.text()}")
        header_item = self.table_widget.verticalHeaderItem(item.row())
        # print('theeeeeeitem=',item.text())
        
    def handle_checkbox_state_change(self,state,row):
        if state == Qt.Checked:
            header_item = self.table_widget.verticalHeaderItem(row)
            
        else:
            header_item = self.table_widget.verticalHeaderItem(row)
    def create(self):
        def zero(x):
            return 0
        cursors= self.cursor_handler.cursors()
        self.y_f=self.y.isel({self.dim:slice(cursors[0], cursors[1])})
        self.x_f=self.y_f[self.dim]
        # print(self.y_f)
        if self.offset_state==True:
            self.params['offset'].set(value=self.y_f.data.min())
        list_axis=[[self.y[self.dim]],[self.x_f]]
        self.mod= Model(zero)
        j=0
        for f in self.function_list:
            self.mod+=Model(f,prefix='f'+str(j)+'_')
            j+=1
        if self.FD_state == True:
            self.mod= self.mod* Model(self.fermi_dirac)
        if self.CV_state == True:
            self.mod = CompositeModel(self.mod, Model(self.centered_kernel), self.convolve)
        if self.offset_state==True:
            self.mod= self.mod+Model(self.offset_function)
        m1=make_model(self.mod, self.table_widget)
        self.mod=m1.current_model()
        self.params=m1.current_params()
    def fit(self):
        
        def zero(x):
            return 0
        self.mod= Model(zero)
        cursors= self.cursor_handler.cursors()
        j=0
        for f in self.function_list:
            self.mod+=Model(f,prefix='f'+str(j)+'_')
            j+=1
        if self.FD_state == True:
            self.mod= self.mod* Model(self.fermi_dirac)
        if self.CV_state == True:
            self.mod = CompositeModel(self.mod, Model(self.centered_kernel), self.convolve)
        if self.offset_state==True:
            self.mod= self.mod+Model(self.offset_function)
        m1=make_model(self.mod, self.table_widget)
        self.mod=m1.current_model()
        self.params=m1.current_params()
        self.y_f=self.y.isel({self.dim:slice(cursors[0], cursors[1])})
        self.x_f=self.y_f[self.dim]
        if self.offset_state==True:
            self.params['offset'].set(value=self.y_f.data.min())
        # print(self.params)
        out = self.mod.fit(self.y_f, self.params, x=self.x_f)
        print(out.fit_report(min_correl=0.25))
        self.axis.plot(self.x_f,out.best_fit,color='red',label='fit')
        self.figure.tight_layout()
        self.canvas.draw()
        
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = fit_panel_single()
    window.show()
    sys.exit(app.exec_())
