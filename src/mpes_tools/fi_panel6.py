import sys
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QTextEdit, QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QLabel, QAction, QCheckBox, QPushButton, QListWidget, QTableWidget, QTableWidgetItem, QTableWidget, QCheckBox, QSplitter
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
from sum_functions import create_sum_function
from multiplication_function import create_x_function
from numpy import loadtxt
from movable_vertical_cursors_graph import MovableCursors
from make_model import make_model
from graphs2 import showgraphs



class MainWindow(QMainWindow):
    def __init__(self,data,axis,c1,c2,t,dt):
        super().__init__()

        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 1500, 800)
        
        # Create a menu bar
        menu_bar = self.menuBar()

        # Create a 'View' menu
        view_menu = menu_bar.addMenu("View")

        # Create actions for showing and hiding the graph window
        show_graph_action = QAction("Show Graph", self)
        show_graph_action.triggered.connect(self.show_graph_window)
        view_menu.addAction(show_graph_action)

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
        self.canvas = FigureCanvas(self.figure)
        # Create two checkboxes
        self.checkbox0 = QCheckBox("Cursors")
        self.checkbox0.stateChanged.connect(self.checkbox0_changed)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(axis[2])-1)
        self.slider.setValue(t)
        self.slider.valueChanged.connect(self.update_label)
        self.slider2 = QSlider(Qt.Horizontal)
        self.slider2.setMinimum(0)
        self.slider2.setMaximum(10)
        self.slider2.setValue(dt)
        self.slider2.valueChanged.connect(self.update_label2)
 
        self.label = QLabel("Slider Value: {t}")
        self.label2 = QLabel("Slider Value: {dt}")

        # Create two checkboxes
        self.checkbox1 = QCheckBox("Multiply with Fermi Dirac")
        self.checkbox1.stateChanged.connect(self.checkbox1_changed)

        self.checkbox2 = QCheckBox("Convolve with a Gaussian")
        self.checkbox2.stateChanged.connect(self.checkbox2_changed)

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
        self.graph_button.clicked.connect(self.show_graph_window)
        
        self.fit_button = QPushButton("Fit")
        self.fit_button.clicked.connect(self.fit)
        
        self.fitall_button = QPushButton("Fit all")
        self.fitall_button.clicked.connect(self.fit_all)
        
        left_buttons=QVBoxLayout()
        left_sublayout=QHBoxLayout()
        
        left_buttons.addWidget(self.add_button)
        left_buttons.addWidget(self.remove_button)
        left_buttons.addWidget(self.graph_button)
        left_buttons.addWidget(self.fit_button)
        left_buttons.addWidget(self.fitall_button)
        
        left_sublayout.addWidget(self.list_widget)
        left_sublayout.addLayout(left_buttons) 

        # Add widgets to the left layout
        left_layout.addWidget(self.canvas)
        left_layout.addWidget(self.checkbox0)
        left_layout.addWidget(self.slider)
        left_layout.addWidget(self.label)
        left_layout.addWidget(self.slider2)
        left_layout.addWidget(self.label2)
        left_layout.addLayout(left_sublayout) 
        
        # left_layout.addWidget(self.list_widget)
        # left_layout.addWidget(self.add_button)
        # left_layout.addWidget(self.remove_button)
        # left_layout.addWidget(self.graph_button)
        # left_layout.addWidget(self.fit_button)
        # left_layout.addWidget(self.fitall_button)
        
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
        checkboxes.addWidget(self.checkbox1)
        checkboxes.addWidget(self.checkbox2)
        top_lay.addWidget(self.text_equation)
        top_lay.addLayout(checkboxes)
        right_layout.addLayout(top_lay)
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
        # Add a button to activate cursors
        # self.add_cursors_button = QPushButton("Add Movable Cursors", self)
        # self.add_cursors_button.clicked.connect(self.add_movable_cursors)
        # right_layout.addWidget(self.add_cursors_button)

        # To hold the MovableCursors instance
        self.cursor_handler = None
        self.FD_state = False
        self.CV_state = False
        print('data=',data.shape,'axs',len(axis),'axis1',len(axis[0]),'axis2',len(axis[1]),'axis3',len(axis[2]))
        self.axs=axis
        self.data_t=np.zeros((data.shape[1],data.shape[2]))
        x_min = int(min(c1, c2))
        x_max = int(max(c1, c2)) + 1
        print('xmin=',x_min,'xmax=',x_max)
        for i in range(x_min, x_max):
            self.data_t += data[i, :,:]
        print('data_t',self.data_t.shape)
        self.t=t
        self.dt=dt
        print(t,dt)
        self.slider.setValue(self.t)
        self.slider2.setValue(self.dt)
        self.plot_graph(t,dt)
        self.fit_results=[]
        
    # def add_movable_cursors(self):
    #     if self.cursor_handler is None:
    #         # Initialize and add the cursors to the existing plot
    #         self.cursor_handler = MovableCursors(self.axis)
    #         self.canvas.draw()

    def plot_graph(self,t,dt):
        # Sample data
        # self.x = np.linspace(-5,5,100)
        # self.y = np.linspace(10,100,100)
        self.y=np.zeros((self.data_t.shape[0]))
        print('thecomp',self.y.shape,self.data_t[:,1].shape)
        # data = loadtxt('C:/Users/admin-nisel131/Documents/CVS_TR_flatband_fig/EDC_time=0_2024-05-08_093401_6994.txt')
        self.axis.clear()
        # self.x= data[:,0]   
        # self.y= data[:,1]
        self.x=self.axs[1][:]
        for i in range(0,dt+1):
            self.y +=self.data_t[:,t+i]
        
        
        self.axis.plot(self.x, self.y, 'bo', label='Data')

        self.axis.set_title('Sample Graph')
        self.axis.set_xlabel('X')
        self.axis.set_ylabel('Y')
        self.axis.legend()
        self.figure.tight_layout()
        self.canvas.draw()
        print('sliders=',self.slider.value(),self.slider2.value())
    def update_text_edit_boxes(self):
        self.text_equation.setPlaceholderText("Top Right Text Edit Box")
    
    def constant (self,x,b):
        return 0*x+b
    def linear (self,x,a,b):
        return a*x+b
    def lorentzian(self,x, A, x0, gamma):
        c=0.0002
        return A / (1 + ((x - x0) / (gamma+c)) ** 2)
    # def fermi_dirac(self,x, mu, T,off):
    #     kb = 8.617333262145 * 10**(-5)  # Boltzmann constant in eV/K
    #     return 1 / (1 + np.exp((x - mu) / (kb * T)))+off
    def fermi_dirac(self,x, mu, T):
        kb = 8.617333262145 * 10**(-5)  # Boltzmann constant in eV/K
        return 1 / (1 + np.exp((x - mu) / (kb * T)))
    def gaussian(self,x,A, mu, sigma):
        return A* np.exp(-(x - mu)**2 / (2 * sigma**2))
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
    
    
    def convolve(self, arr, kernel):
        """Simple convolution of two arrays."""
        npts = min(arr.size, kernel.size)
        pad = np.ones(npts)
        tmp = np.concatenate((pad*arr[0], arr, pad*arr[-1]))
        out = np.convolve(tmp, kernel, mode='valid')
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
    
    # def convolution(self,x,sigma,f):
    #     global N
    #     xmax=x[-1]
    #     xmin=x[0]
    #     N=20
    #     y=np.zeros(N+len(x))
    #     x_step=x[1]-x[0]
    #     for i in range(0,N):
    #         y[i]=x[0]-(N-i)*x_step
    #     for i in range(0,len(x)):
    #         y[i+N]=x[i]
    #     x_gauss = np.linspace(-0.5, 0.5, len(self.ax))
    #     gaussian_values = self.gaussian(x_gauss, 0, sigma)
    #     # function_values = 
    #     convolution = np.convolve( function_values, gaussian_values, mode='same')
    #     return convolution[N-1:-1]
    
    def show_graph_window(self):
        # Create a new graph window and show it
        # graph_window = GraphWindow()
        # graph_window.show()
        
        # # Store a reference to the window to prevent it from being garbage collected
        # self.graph_windows.append(graph_window)
        self.axis.clear()
        self.plot_graph(self.t,self.dt)
        
        
    def update_label(self, value):
        self.label.setText(f"Slider Value: {value}")
        self.t=self.slider.value()
        self.plot_graph(self.t,self.dt)
    def update_label2(self, value):
        self.label2.setText(f"Slider Value: {value}")
        self.dt=self.slider2.value()
        self.plot_graph(self.t,self.dt)
    
    def checkbox0_changed(self, state):
        # MovableCursors(self.axis)
        if state == Qt.Checked:
            if self.cursor_handler is None:
                # Initialize and add the cursors to the existing plot
                self.cursor_handler = MovableCursors(self.axis)
                self.canvas.draw()
            else:
                self.cursor_handler.redraw()
        else:
            self.cursor_handler.remove()
            # self.cursor_handler= None
    
    def checkbox1_changed(self, state):
        if self.CV_state== True:
            pos=2
        else:
            pos=0
        if state == Qt.Checked:
            self.FD_state = True
            self.update_equation()
            # pos=0
            
            print("Checkbox 1 is checked")
            # new_row_name = QTableWidgetItem('Fermi')
            self.table_widget.insertRow(pos)
            label_item = QTableWidgetItem("Fermi")
            # label_item.setTextAlignment(0x0004 | 0x0080)  # Align center
            self.table_widget.setVerticalHeaderItem(pos, label_item)
            # self.table_widget.setVerticalHeaderItem(0, new_row_name)
            for col in range(4):
                item = QTableWidgetItem('')
                item.setFlags(Qt.ItemIsEnabled)  # Make cell uneditable
                self.table_widget.setItem(pos, col, item)
                item.setBackground(QBrush(QColor('grey')))
            c=self.table_widget.rowCount()
            self.table_widget.insertRow(pos+1)
            label_item1 = QTableWidgetItem("Fermi level")
            # label_item1.setTextAlignment(0x0004 | 0x0080)  # Align center
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout()
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox = QCheckBox()
            # checkbox.stateChanged.connect(self.handle_checkbox_state_change)
            checkbox.stateChanged.connect(lambda state, row= pos+1: self.handle_checkbox_state_change(state, row))
            print('thecount',c+1)
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
            # checkbox.stateChanged.connect(self.handle_checkbox_state_change)
            checkbox.stateChanged.connect(lambda state, row= pos+2: self.handle_checkbox_state_change(state, row))
            checkbox_layout.addWidget(checkbox)
            checkbox_widget.setLayout(checkbox_layout)
            self.table_widget.setCellWidget(pos+2, 3, checkbox_widget)
            # label_item2.setTextAlignment(0x0004 | 0x0080)  # Align center
            self.table_widget.setVerticalHeaderItem(pos+2, label_item2)
            
            
            
        else:
            self.FD_state = False
            self.update_equation()
            print("Checkbox 1 is unchecked")
            
            self.table_widget.removeRow(pos)
            self.table_widget.removeRow(pos)
            self.table_widget.removeRow(pos)
            
    def checkbox2_changed(self, state):
        if state == Qt.Checked:
            self.CV_state = True
            
            self.update_equation()
           
           
            print("Checkbox 1 is checked")
            # new_row_name = QTableWidgetItem('Fermi')
            self.table_widget.insertRow(0)
            label_item = QTableWidgetItem("Convolution")
            # label_item.setTextAlignment(0x0004 | 0x0080)  # Align center
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
            # checkbox.stateChanged.connect(self.handle_checkbox_state_change)
            checkbox.stateChanged.connect(lambda state, row= 1: self.handle_checkbox_state_change(state, row))
            checkbox_layout.addWidget(checkbox)
            checkbox_widget.setLayout(checkbox_layout)
            self.table_widget.setCellWidget(1, 3, checkbox_widget)
            # label_item1.setTextAlignment(0x0004 | 0x0080)  # Align center
            self.table_widget.setVerticalHeaderItem(1, label_item1)
            
            # self.table_widget.insertRow(2)
            # label_item2 = QTableWidgetItem("Temperature")
            # # label_item2.setTextAlignment(0x0004 | 0x0080)  # Align center
            # self.table_widget.setVerticalHeaderItem(2, label_item2)
            
            
            
        else:
            self.CV_state = False
            self.update_equation()
            print("Checkbox 1 is unchecked")
            
            self.table_widget.removeRow(0)
            self.table_widget.removeRow(0)
            # self.table_widget.removeRow(0)

    def item_selected(self, item):
        print(f"Selected: {item.text()}")
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
        # print(self.list_widget.currentItem().text())
    
    def button_remove_clicked(self):
        if self.i>0:
            self.i-=1
        # self.mod=
        # print('removal')
        current_row_count = self.table_widget.rowCount()
        print(current_row_count)
        sig = inspect.signature(self.function_list[-1])
        params = sig.parameters
        
        for p in range(len(params)):
            # print('p=',p)
            # print('count=',current_row_count-1-p)
            self.table_widget.removeRow(current_row_count-1-p)    
            
        self.function_list.remove(self.function_list[-1])
        self.function_names_list.remove(self.function_names_list[-1])
        self.update_equation()

    def button_add_clicked(self):
        # print(self.cursor_handler.cursors())
        def zero(x):
            return 0
        
        
        self.i+=1
        self.function_list.append(self.function_selected)
        self.function_names_list.append(self.list_widget.currentItem().text())
       
        print('the list=',self.function_list,'iten',self.function_list[0])
        print('listlength=',len(self.function_list))
        j=0
        for p in self.function_list:
            # j=0
            print('j==',j)
            current_function=Model(p,prefix='f'+str(j)+'_')
            j+=1
            
        
        current_row_count = self.table_widget.rowCount()
        
        self.table_widget.insertRow(current_row_count)
        # self.table_widget.setVerticalHeaderLabels([self.list_widget.currentItem().text()])
        new_row_name = QTableWidgetItem(self.list_widget.currentItem().text())
        self.table_widget.setVerticalHeaderItem(current_row_count, new_row_name)
        for col in range(4):
            item = QTableWidgetItem('')
            item.setFlags(Qt.ItemIsEnabled)  # Make cell uneditable
            self.table_widget.setItem(current_row_count, col, item)
            item.setBackground(QBrush(QColor('grey')))
        c=current_row_count
        # self.table_widget.insertRow(1)
        # self.table_widget.insertRow(2)
        for p in range(len(current_function.param_names)):
            # c+=1
            # print(c+p+1)
            self.table_widget.insertRow(c+p+1)
            print(current_function.param_names[p])
            new_row_name = QTableWidgetItem(current_function.param_names[p])
            self.table_widget.setVerticalHeaderItem(c+p+1, new_row_name)
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout()
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox = QCheckBox()
            # checkbox.stateChanged.connect(self.handle_checkbox_state_change)
            checkbox.stateChanged.connect(lambda state, row=c + p + 1: self.handle_checkbox_state_change(state, row))
            checkbox_layout.addWidget(checkbox)
            checkbox_widget.setLayout(checkbox_layout)
            self.table_widget.setCellWidget(c+p+1, 3, checkbox_widget)
            # self.table_widget.setVerticalHeaderLabels([Model(self.function_selected).param_names[p]])
        # print(self.Mod.param_names)
        # params['A'].set(value=1.35, vary=True, expr='')
        
        self.update_equation()
        # print(self.params)
        
    def update_equation(self):
        self.equation=''
        print('names',self.function_names_list)
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
        print('equation',self.equation)
    

    def table_item_changed(self, item):
        print(f"Table cell changed at ({item.row()}, {item.column()}): {item.text()}")
        header_item = self.table_widget.verticalHeaderItem(item.row())
        # print(header_item.text())
        print('theeeeeeitem=',item.text())
        
    def handle_checkbox_state_change(self,state,row):
        if state == Qt.Checked:
            print("Checkbox is checked")
            print(row)
            header_item = self.table_widget.verticalHeaderItem(row)
            # self.params[header_item.text()].vary = False
            
        else:
            print("Checkbox is unchecked")
            header_item = self.table_widget.verticalHeaderItem(row)
            # self.params[header_item.text()].vary = True
    def fit(self):
        
        def zero(x):
            return 0
        self.mod= Model(zero)
        j=0
        for f in self.function_list:
            self.mod+=Model(f,prefix='f'+str(j)+'_')
            j+=1
        if self.FD_state == True:
            self.mod= self.mod* Model(self.fermi_dirac)
        if self.CV_state == True:
            # self.mod=CompositeModel(self.mod, Model(self.gaussian_conv), self.convolve)
            self.mod=CompositeModel(self.mod, Model(self.gaussian_conv), self.convolve)
            # self.mod=CompositeModel(Model(self.jump), Model(gaussian), self.convolve)
            
        m1=make_model(self.mod, self.table_widget)
        self.mod=m1.current_model()
        # self.mod = CompositeModel(m1.current_model(), Model(gaussian), self.convolve)
        self.params=m1.current_params()
        # self.params=self.mod.make_params()
        cursors= self.cursor_handler.cursors()
        self.x_f=self.x[cursors[0]:cursors[1]]
        self.y_f=self.y[cursors[0]:cursors[1]]
        print(self.params)
        # params['b'].set(value=0, vary=True, expr='')
        # out = mod.fit(self.data[:,1], params, x=self.data[:,0],method='nelder')
        out = self.mod.fit(self.y_f, self.params, x=self.x_f)
        # dely = out.eval_uncertainty(sigma=3)
        print(out.fit_report(min_correl=0.25))
        self.axis.plot(self.x_f,out.best_fit,color='red',label='fit')
        # self.axis.plot(self.x_f,1e5*self.gaussian_conv(self.x_f,out.best_values['sigma']))
    def fit_all(self):
        self.fit_results=[]
        def zero(x):
            return 0
        self.mod= Model(zero)
        j=0
        for f in self.function_list:
            self.mod+=Model(f,prefix='f'+str(j)+'_')
            j+=1
        if self.FD_state == True:
            self.mod= self.mod* Model(self.fermi_dirac)
        if self.CV_state == True:
            # self.mod=CompositeModel(self.mod, Model(self.gaussian_conv), self.convolve)
            self.mod=CompositeModel(self.mod, Model(self.gaussian_conv), self.convolve)
        m1=make_model(self.mod, self.table_widget)
        self.mod=m1.current_model()
        self.params=m1.current_params()
        for pname, par in self.params.items():
            print('the paramsnames or',pname, par)
            setattr(self, pname, np.zeros((len(self.axs[2]))))
            # self.pname=np.zeros((len(self.axs[2])))
        cursors= self.cursor_handler.cursors()
        for i in range(len(self.axs[2])-self.dt):
            self.y=np.zeros((self.data_t.shape[0]))
            for j in range (self.dt+1):
                self.y+= self.data_t[:,i+j]
            self.x_f=self.x[cursors[0]:cursors[1]]
            self.y_f=self.y[cursors[0]:cursors[1]]
            # print(self.params)
            # params['b'].set(value=0, vary=True, expr='')
            # out = mod.fit(self.data[:,1], params, x=self.data[:,0],method='nelder')
            self.axis.clear()
            out = self.mod.fit(self.y_f, self.params, x=self.x_f)
            # dely = out.eval_uncertainty(sigma=3)
            # print(out.fit_report(min_correl=0.25))
            self.axis.plot(self.x,self.y, 'bo', label='Data')
            self.axis.plot(self.x_f,out.best_fit,color='red',label='fit')
            for pname, par in self.params.items():
                array=getattr(self, pname)
                array[i]=out.best_values[pname]
                setattr(self, pname,array)
        if self.dt>0:
            self.axs[2]=self.axs[2][:-self.dt]
            for pname, par in self.params.items():
                self.fit_results.append(getattr(self, pname)[:-self.dt])
        else:
            for pname, par in self.params.items():
                self.fit_results.append(getattr(self, pname))
        print('fit_results',len(self.fit_results))
        print('thelengthis=',self.fit_results[0].shape)
        
            
        sg=showgraphs(self.axs[2], self.fit_results)
        sg.show()
        self.graph_windows.append(sg)
        # pname='T'
        # print(getattr(self, pname))
            # out.best_values['A1']
            # self.axis.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
