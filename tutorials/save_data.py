import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import  Button
from datetime import datetime
class save_data():
    def __init__(self,axis,data,name,plc,fig): 
        # print('saveinit')
        self.size=[0.028,0.025]
        self.fig=fig
        self.save_button = self.fig.add_axes( [plc[0]+self.size[0],plc[1]]+self.size)
        # self.save_button =plt.axes([0.78, 0.02, 0.1, 0.06])
        
        # self.save_button=self.fig.add_axes([0.78, 0.02, 0.1, 0.06])
        self.button_save = Button(self.save_button, 'save')
        self.button_save.on_clicked(lambda event: self.save_data2(event))
        # self.button_save.on_clicked(lambda event: self.test_button(event))
        # plt.show()
        self.data=data
        self.axis=axis
        self.name=name
    def save_data2(self,event):
        # print('save')
        current_time = datetime.now()
        
        # Format the datetime object as a string
        current_time_str = current_time.strftime("%Y-%m-%d_%H%M%S")
        file_path = "C:/Users/admin-nisel131/Documents/CVS_TR_flatband_fig/"+ self.name + current_time_str +".txt"
        # file_path = name+".txt"
        self.data_saved = np.column_stack((self.axis, self.data))
        np.savetxt(file_path, self.data_saved, fmt='%.5f', delimiter='\t')  
    def test_button(self,event):
        print('test for save')