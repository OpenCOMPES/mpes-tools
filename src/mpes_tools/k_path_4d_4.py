import numpy as np
import h5py
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import CheckButtons, Button
from scipy.ndimage import rotate
import h5py
# import mplcursors
from matplotlib.widgets import Slider, Cursor, SpanSelector
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Circle
from AdditionalInterface import AdditionalInterface
from AxisInteractor import AxisInteractor
from LinePixelGetter import LinePixelGetter
from update_plot_cut_4d import update_plot_cut
import json
import csv
from datetime import datetime

class drawKpath:
    # print(True)
    def __init__(self, data,axis,fig, ax,ax2,linewidth,slider,N):
      self.active_cursor=None
      self.dots_count=0
      self.ax=ax
      self.fig=fig
      self.dot1_x=0
      self.do1_y=0
      self.dot2_x=0
      self.do2_y=0
      self.cid_press=None
      self.linewidth=1
      self.line_artist=None
      self.cb_line=None
      self.button_update=None
      self.dot1=None
      self.dot2=None
      self.method_running = False
      self.pixels_along_line=[]
      self.number=N
      self.og_number=N
      self.dots_list=[]
      self.line_artist_list=[None]*N
      self.pixels_along_path=[None]*N
      # self.number=N
      self.is_drawn= False
      self.is_loaded= False
      self.new=False
      self.add_pressed=False
      self.lw=linewidth
      self.ax2=ax2
      self.data=data[:,:,:,slider]
      self.axis=axis
      self.pixels=[]
      self.slider=slider
      self.data2=data
      self.slider_ax7 = plt.axes([0.55, 0.14, 0.02, 0.3])
      self.slider_dcut= Slider(self.slider_ax7, 'dcut_kpath', 0, 15, valinit=1, valstep=1, orientation='vertical')
    # def update_plot_cut(self):
    #     update_plot_cut.update_plot_cut(self.data2[:,:,:,self.slider],self.ax2,self.pixels,self.lw)
    def isdrawn(self):
        return self.is_drawn
        
    
    def get_pixels(self):
        if self.pixels is not None:
            return self.pixels
    def get_pixels_along_line(self):
        if self.pixels_along_line is not None:
            return self.pixels_along_line
   
    def get_status(self):
        if self.cb_line is not None:
            return self.cb_line.get_status()[0]
        else:
            return False
    
    def draw(self):
        # print('beginning')
        def add_path(event):
            self.add_pressed= True
            
            for i in range (self.number):
                self.line_artist_list.append(None)
                self.pixels_along_path.append(None)
                # self.dots_list
            print('line list=', len(self.line_artist_list))
            self.number=self.number+self.og_number
            self.is_drawn=False
            self.dots_count=0
            self.cid_press = self.fig.canvas.mpl_connect('button_press_event', drawdots)
            
        def drawline(dot1,dot2,pos):
            self.pixels=[]
            if self.dots_count ==0 and self.line_artist_list[len(self.dots_list)-2] is not None :
                if not self.loaded:    
                    self.line_artist_list[len(self.dots_list)-2].remove()  # Remove the previous line if exists
                    print('test,code')
            # if self.dots_count==2:
            #     line = Line2D([self.dots_list[len(self.dots_list)].center[0], self.dots_list[len(self.dots_list)-1].center[0]], [self.dots_list[len(self.dots_list)].center[1], self.dots_list[len(self.dots_list)-1].center[1]], linewidth=self.linewidth, color='red')
            if self.dots_count==2 :
                line = Line2D([dot1.center[0], dot2.center[0]], [dot1.center[1], dot2.center[1]], linewidth=self.linewidth, color='red')
                
                self.ax.add_line(line)
                # print('movement',len(self.line_artist_list))
                print('currentline=',self.line_artist_list[pos])
                if self.line_artist_list[pos] is not None:
                    # print(pos,self.line_artist_list[pos].get_data())
                    self.line_artist_list[pos].remove()
                # if self.line_artist is not None:
                #     self.line_artist.remove()  # Remove the previous line if exists
                
                self.line_artist = line
                # self.line_artist_list.append(line)
                self.line_artist_list[pos]=line
                # print(pos,self.line_artist_list[pos].get_data())
                # x1=self.line_artist_list[pos].get_data()[0][1]
                # y1=self.line_artist_list[pos].get_data()[1][1]
                # x2= self.line_artist_list[pos].get_data()[0][0]
                # y2=self.line_artist_list[pos].get_data()[1][0]
                x1_pixel=int((self.line_artist_list[pos].get_data()[0][1] - self.axis[0][0]) / (self.axis[0][-1] - self.axis[0][0]) * (self.axis[0].shape[0] - 1) + 0.5)
                y1_pixel=int((self.line_artist_list[pos].get_data()[1][1] - self.axis[1][0]) / (self.axis[1][-1] - self.axis[1][0]) * (self.axis[1].shape[0] - 1) + 0.5)
                x2_pixel=int((self.line_artist_list[pos].get_data()[0][0] - self.axis[0][0]) / (self.axis[0][-1] - self.axis[0][0]) * (self.axis[0].shape[0] - 1) + 0.5)
                y2_pixel=int((self.line_artist_list[pos].get_data()[1][0] - self.axis[1][0]) / (self.axis[1][-1] - self.axis[1][0]) * (self.axis[1].shape[0] - 1) + 0.5)
                
                self.pixels_along_path[pos] = LinePixelGetter.get_pixels_along_line(x1_pixel, y1_pixel, x2_pixel, y2_pixel, self.linewidth)
                # print(x1_pixel,y1_pixel)
                # self.pixels_along_path[pos]=LinePixelGetter.get_pixels_along_line(self.line_artist_list[pos].get_data()[0][1], self.line_artist_list[pos].get_data()[1][1], self.line_artist_list[pos].get_data()[0][0], self.line_artist_list[pos].get_data()[1][0], self.linewidth)
                # for i in self.pixels_along_path:
                for i in range (0,self.number):
                    if self.pixels_along_path[i] is not None:
                        self.pixels+=self.pixels_along_path[i]
                        
        def drawdots(event):
            # if self.add_pressed:
                
                
            if self.cb_line.get_status()[0] and len(self.dots_list) < self.number and (self.new or not self.is_drawn):
                x =  event.xdata  # Round the x-coordinate to the nearest integer
                y =  event.ydata  # Round the y-coordinate to the nearest integer
                print('you hereeee')
                print(self.number)
                # print('line list=', len(self.line_artist_list))
                if self.dots_count==0:
                    self.dot= Circle((x, y), radius=0.1, color='yellow', picker=20)
                    self.ax.add_patch(self.dot)
                    # self.dot_coords[self.dots_count] = (x, y)
                    self.dots_list.append(self.dot)
                    self.dots_count += 1
                    self.fig.canvas.draw()
                else:
                    self.dot= Circle((x, y), radius=0.1, color='yellow', picker=20)
                    self.ax.add_patch(self.dot)
                    # self.dot_coords[self.dots_count] = (x, y)
                    self.dots_count += 1
                    self.dots_list.append(self.dot)
                    print('dots list=',len(self.dots_list))
                    drawline(self.dots_list[len(self.dots_list)-1],self.dots_list[len(self.dots_list)-2],len(self.dots_list)-2)
                    self.dots_count -= 1
                    update_plot_cut.update_plot_cut(self.data,self.ax2,self.pixels,self.slider_dcut.val)
                    
                    self.fig.canvas.draw()
                    if len(self.dots_list)== self.number:
                        self.is_drawn=True
                        # print(self.is_drawn)
        def on_checkbox_change(label):
                if self.cb_line.get_status()[0]:
                    if self.is_loaded:
                        for i in range(len(self.dots_list)):
                            self.ax.add_patch(self.dots_list[i])
                            plt.draw()
                        for i in range(len(self.line_artist_list)):
                            if self.line_artist_list[i] is not None:
                                self.ax.add_line(self.line_artist_list[i])
                                plt.draw()
                    elif self.is_drawn:
                        for i in range(len(self.dots_list)):
                            self.ax.add_patch(self.dots_list[i])
                            plt.draw()
                        for i in range(len(self.line_artist_list)):
                            if self.line_artist_list[i] is not None:
                                self.ax.add_line(self.line_artist_list[i])
                                plt.draw()
                    
                    else:
                        self.cid_press = self.fig.canvas.mpl_connect('button_press_event', drawdots)
                    
                else:
                    # Disconnect the click event
                    self.is_loaded= False
                    self.fig.canvas.mpl_disconnect(self.cid_press)
                    for i in range(len(self.dots_list)):
                        self.dots_list[i].remove()
                        plt.draw()
                    for i in range(len(self.line_artist_list)):
                        if self.line_artist_list[i] is not None:
                            self.line_artist_list[i].remove()
                            plt.draw()
        def new(event):
            
            for i in range(len(self.dots_list)):
                print(i)
                self.dots_list[i].remove()
                plt.draw()
            for i in range(len(self.line_artist_list)):
                print(i)
                if self.line_artist_list[i] is not None:
                    self.line_artist_list[i].remove()
                    plt.draw()
            self.new=True
            self.is_drawn= False
            self.is_loaded= False
            self.dots_list=[]
            self.line_artist_list=[None]*self.number
            self.pixels_along_path=[None]*self.number
            self.dots_count=0
            self.cid_press = self.fig.canvas.mpl_connect('button_press_event', drawdots)
        def on_pick(event):
            for i in range(len(self.dots_list)):
                if event.artist == self.dots_list[i]:
                    self.active_cursor = self.dots_list[i]
        def on_motion(event):
            # global dot1,dot2
            if self.active_cursor is not None and event.inaxes == self.ax:
                # Initialize a list of dictionaries to store dot information
                dot_info_list = [{"dot": dot, "center": dot.center} for dot in self.dots_list]
                self.dots_count=2
            
                # Iterate through the list to find the selected dot
                selected_dot_index = None
                for i, dot_info in enumerate(dot_info_list):
                    dot = dot_info["dot"]
                    contains, _ = dot.contains(event)
                    if contains:
                        selected_dot_index = i
                        break  # Exit the loop when a matching dot is found
                
                if selected_dot_index is not None:
                    selected_dot_info = dot_info_list[selected_dot_index]
                    selected_dot = selected_dot_info["dot"]
                    # print(f"Selected dot index: {selected_dot_index}")
                    # print(f"Selected dot center: {selected_dot_info['center']}")
                    selected_dot.center = (event.xdata, event.ydata)
                    plt.draw()
                    i=selected_dot_index
                    if i==len(self.dots_list)-1:
                        # self.line_artist_list[i-1].remove()
                        drawline(self.dots_list[i],self.dots_list[i-1],i-1)
                        update_plot_cut.update_plot_cut(self.data,self.ax2,self.pixels,self.slider_dcut.val)
                    elif i==0:
                        drawline(self.dots_list[i+1],self.dots_list[i],i)
                        update_plot_cut.update_plot_cut(self.data,self.ax2,self.pixels,self.slider_dcut.val)
                    else:
                        # self.line_artist_list[i-1].remove()
                        # self.line_artist_list[i].remove()
                        drawline(self.dots_list[i+1],self.dots_list[i],i)
                        update_plot_cut.update_plot_cut(self.data,self.ax2,self.pixels,self.slider_dcut.val)
                        drawline(self.dots_list[i],self.dots_list[i-1],i-1)
                        update_plot_cut.update_plot_cut(self.data,self.ax2,self.pixels,self.slider_dcut.val)
                    plt.draw()
                    
                
        def on_release(event):
            self.active_cursor = None
        def get_status():
            return self.cb_line.get_status()[0]
        def dots_coord():
            return [self.dot1.center, self.dot2.center]
        
        def update_dcut(val):
            self.linewidth=self.slider_dcut.val
            self.pixels=[]
            for position, line in enumerate(self.line_artist_list):
                if line is not None:
                    line.set_linewidth(self.linewidth+1)
                    x1_pixel=int((line.get_data()[0][1] - self.axis[0][0]) / (self.axis[0][-1] - self.axis[0][0]) * (self.axis[0].shape[0] - 1) + 0.5)
                    y1_pixel=int((line.get_data()[1][1] - self.axis[1][0]) / (self.axis[1][-1] - self.axis[1][0]) * (self.axis[1].shape[0] - 1) + 0.5)
                    x2_pixel=int((line.get_data()[0][0] - self.axis[0][0]) / (self.axis[0][-1] - self.axis[0][0]) * (self.axis[0].shape[0] - 1) + 0.5)
                    y2_pixel=int((line.get_data()[1][0] - self.axis[1][0]) / (self.axis[1][-1] - self.axis[1][0]) * (self.axis[1].shape[0] - 1) + 0.5)
                    # print(x1_pixel,y1_pixel,x2_pixel,y2_pixel)
                    self.pixels_along_path[position] = LinePixelGetter.get_pixels_along_line(x1_pixel, y1_pixel, x2_pixel, y2_pixel, self.linewidth)
                    self.pixels+=self.pixels_along_path[position]
                    
            print('before before line')
            # for pos in range(0,self.number):
            #     print('before line')
            #     if self.line_artist_list[pos] is not None:
            #         x1_pixel=int((self.line_artist_list[pos].get_data()[0][1] - self.axis[0][0]) / (self.axis[0][-1] - self.axis[0][0]) * (self.axis[0].shape[0] - 1) + 0.5)
            #         y1_pixel=int((self.line_artist_list[pos].get_data()[1][1] - self.axis[1][0]) / (self.axis[1][-1] - self.axis[1][0]) * (self.axis[1].shape[0] - 1) + 0.5)
            #         x2_pixel=int((self.line_artist_list[pos].get_data()[0][0] - self.axis[0][0]) / (self.axis[0][-1] - self.axis[0][0]) * (self.axis[0].shape[0] - 1) + 0.5)
            #         y2_pixel=int((self.line_artist_list[pos].get_data()[1][0] - self.axis[1][0]) / (self.axis[1][-1] - self.axis[1][0]) * (self.axis[1].shape[0] - 1) + 0.5)
            #         print(x1_pixel,y1_pixel,x2_pixel,y2_pixel)
            #         self.pixels_along_path[pos] = LinePixelGetter.get_pixels_along_line(x1_pixel, y1_pixel, x2_pixel, y2_pixel, self.linewidth)
            #         self.pixels+=self.pixels_along_path[pos]
            
            # self.pixels_along_line = LinePixelGetter.get_pixels_along_line(self.dot1_x_pixel, self.dot1_y_pixel, self.dot2_x_pixel, self.dot2_y_pixel, self.linewidth)
            # update_plot_cut.update_plot_cut(self.data,self.ax2,self.pixels_along_line,self.slider_dcut.val)
            update_plot_cut.update_plot_cut(self.data,self.ax2,self.pixels,self.slider_dcut.val)
        def draw_load():
            if self.is_loaded:
                for i in range(len(self.dots_list)):
                    self.ax.add_patch(self.dots_list[i])
                    plt.draw()
                for i in range(len(self.line_artist_list)):
                    if self.line_artist_list[i] is not None:
                        self.ax.add_line(self.line_artist_list[i])
                        plt.draw()
        def save_path(event):
            def c_to_string(circle):
                return f"{circle.center[0]}, {circle.center[1]}, {circle.radius}"
            def l_to_string(line):
                x_data, y_data = line.get_data()
                linewidth = line.get_linewidth()
                return f"{x_data[0]}, {y_data[0]}, {x_data[1]},{y_data[1]},{linewidth}"
            # self.positions= np.array([[0]*4]*len(self.line_artist_list))
            # for position, line in enumerate(self.line_artist_list):
            #     if line is not None:
            #         line.set_linewidth(self.linewidth+1)
            #         x1_pixel=int((line.get_data()[0][1] - self.axis[0][0]) / (self.axis[0][-1] - self.axis[0][0]) * (self.axis[0].shape[0] - 1) + 0.5)
            #         y1_pixel=int((line.get_data()[1][1] - self.axis[1][0]) / (self.axis[1][-1] - self.axis[1][0]) * (self.axis[1].shape[0] - 1) + 0.5)
            #         x2_pixel=int((line.get_data()[0][0] - self.axis[0][0]) / (self.axis[0][-1] - self.axis[0][0]) * (self.axis[0].shape[0] - 1) + 0.5)
            #         y2_pixel=int((line.get_data()[1][0] - self.axis[1][0]) / (self.axis[1][-1] - self.axis[1][0]) * (self.axis[1].shape[0] - 1) + 0.5)
            #         self.positions[position][0]
            output_directory = "C:/Users/admin-nisel131/Documents/CVS_TR_flatband_fig/"
            current_time = datetime.now()
            current_time_str = current_time.strftime("%Y-%m-%d_%H%M%S")
            file_name = "k_path"
            output_path = f"{output_directory}/{file_name}_{current_time_str}.txt"
            with open(output_path, "w",newline="") as file:
                file.write(f"{self.number}" + "\n")
                for circle in self.dots_list:
                    file.write(c_to_string(circle) + "\n")
                for line in self.line_artist_list:
                    if line is not None:
                        file.write(l_to_string(line) + "\n")
        def load_path(event):
            self.fig.canvas.mpl_disconnect(self.cid_press)
            circle_list=[]
            line_list=[]
            file_path1="C:/Users/admin-nisel131/Documents/CVS_TR_flatband_fig/"
            # file="k_path_2023-10-06_153243.txt"
            # file= "k_path_2023-10-10_221437.txt"
            # file= "k_path_2024-04-03_125248.txt"
            file= "k_path_2024-04-03_140548.txt"
            
            
            file_path=file_path1+file
            with open(file_path, "r") as file:
                lines=file.readlines()
                # print(lines)
                # for line_number, line in enumerate(file, start=1):
                for line_number, line in enumerate(lines, start =1):
                    # if line_number==2:
                    #     a,b,c= map(float, line.strip().split(', '))
                    #     print(a,b,c)
                    # print(map(float, line.strip().split(', ')))
                    # print('linenumber=',line_number)
                    # Split the line into individual values
                    # if line_number==1:
                    # print('firstline',line_number)
                    # number=7
                    # first_line = file.readline().strip()  # Read and strip whitespace
                    # print(line)
                    # first_line = file.readline()
                    
                    # number= int(first_line)
                    # print(number)
                    # print(first_line)
                    # print()
                    if line_number==1:
                        number= int(line)
                        # print(number)
                    elif line_number>=2 and line_number<=number+1:
                        x, y, radius = map(float, line.strip().split(', '))
                        # print(x,y,radius)
                        circle = Circle((x, y), radius=radius, color='yellow', picker=20)
                        circle_list.append(circle)
                        self.dots_list=circle_list
                    else:
                        x0,y0,x1,y1,lw=map(float, line.strip().split(','))
                        line1=Line2D([x0,x1], [y0, y1], linewidth=lw, color='red')
                        line_list.append(line1)
                        self.line_artist_list=line_list
                    self.is_loaded= True
                    self.dots_count=2
                    # draw_load()
                    # print(len(self.line_artist_list),len(self.dots_list))
                    
                        # print(x0,y0,x1,y1,lw)
                    # on_checkbox_change('K path')
                    
                
        self.slider_dcut.on_changed(update_dcut)
        self.fig.canvas.mpl_connect('pick_event', on_pick)
        self.fig.canvas.mpl_connect('motion_notify_event', on_motion)
        self.fig.canvas.mpl_connect('button_release_event', on_release)
    
        rax_line = self.fig.add_axes([0.45, 0.02, 0.06, 0.03])  # [left, bottom, width, height]
        self.cb_line = CheckButtons(rax_line, ['K path'], [False])
        self.cb_line.on_clicked(on_checkbox_change)
        
        rax_button = self.fig.add_axes([0.52, 0.02, 0.06, 0.03])
        self.button_update = Button(rax_button, 'new k')
        self.button_update.on_clicked(new)
        
        savepath_button = self.fig.add_axes([0.52, 0.06, 0.06, 0.03])
        self.button_save = Button(savepath_button, 'save k-path')
        self.button_save.on_clicked(save_path)
        
        loadpath_button = self.fig.add_axes([0.45, 0.06, 0.06, 0.03])
        self.button_load = Button(loadpath_button, 'load k-path')
        self.button_load.on_clicked(load_path)
        
        addpath_button = self.fig.add_axes([0.37, 0.06, 0.06, 0.03])
        self.button_add = Button(addpath_button, 'add k-path')
        self.button_add.on_clicked(add_path)
        
        plt.show()
        self.fig.canvas.draw()
        