import numpy as np
from numpy import loadtxt
import matplotlib.pyplot as plt
from fit_beforeFFT import fit
from scipy.signal import savgol_filter
from matplotlib.ticker import FuncFormatter
# from decay_sinus_fit import fit
%matplotlib qt 

# data = loadtxt('C:/Users/admin-nisel131/Documents/data_CVS_new/11443/lor_FD_conv/peak_position2025-03-11_195236.txt')


# data = loadtxt('C:/Users/admin-nisel131/Documents/data_CVS_new/11626/lor_FD_conv/peak_position2025-03-13_174235.txt')




# data = loadtxt('C:/Users/admin-nisel131/Documents/data_CVS_new/11626/vhs3/position2025-03-13_173331.txt')


# data = loadtxt('C:/Users/admin-nisel131/Documents/data_CVS_new/11443/FB/position2025-03-13_191115.txt')



# data = loadtxt('C:/Users/admin-nisel131/Documents/data_CVS_new/11710/FB2/position2025-03-14_190703dt_0.txt')

# data = loadtxt('C:/Users/admin-nisel131/Documents/data_CVS_new/11558/lor_FD_conv/peak_position2025-03-11_201952.txt')


# data8 = loadtxt('C:/Users/admin-nisel131/Documents/data_CVS_new/11595/lor_FD_conv/peak_position2025-03-11_204534.txt')
# data_fft8= loadtxt('C:/Users/admin-nisel131/Documents//data_CVS_new/11595/lor_FD_conv/peak_position_fft2025-03-15_131409.txt')

# data = loadtxt('C:/Users/admin-nisel131/Documents/data_CVS_new/11595/lor_FD_conv2/peak_position2025-03-16_164933.txt')


# data = loadtxt('C:/Users/admin-nisel131/Documents/data_CVS_new/11595/vhs3/position2025-03-11_203439.txt')


data = loadtxt('C:/Users/admin-nisel131/Documents/data_CVS_new/11558/FB2/position2025-03-13_203530.txt')

# old 11595 vhs2
# data = loadtxt('C:/Users/admin-nisel131/Documents/data_CVS_new/11632/vhs3/linewidth2025-03-11_205009.txt')

# data = loadtxt('C:/Users/admin-nisel131/Documents/data_CVS_new/11763/vhs3/position2025-03-11_230346.txt')
# data = loadtxt('C:/Users/admin-nisel131/Documents/data_CVS_new/11763/vhs3/linewidth2025-03-11_230345.txt')
# data = loadtxt('C:/Users/admin-nisel131/Documents/data_CVS_new/11763/vhs3/intensity2025-03-11_230344.txt')

# data = loadtxt('C:/Users/admin-nisel131/Documents/data_CVS_new/11744/FB/position2025-03-11_224245.txt')
# data = loadtxt('C:/Users/admin-nisel131/Documents/data_CVS_new/11744/FB/linewidth2025-03-11_224246.txt')
# data = loadtxt('C:/Users/admin-nisel131/Documents/data_CVS_new/11744/FB/intensity2025-03-11_224246.txt')


# folder='C:/Users/admin-nisel131/Documents/data_CVS_new/11443/FB/'

# data = loadtxt(folder+'intensity2025-03-13_191117.txt')


# data = loadtxt(folder+'position2025-03-13_191115.txt')


# data = loadtxt(folder+'linewidth2025-03-13_191116.txt')



sign=1
# sign=-1
##################box###############



# name='intensity'
name='peak_position'
# name='linewidth'


#display content of text file
# print(data)
# x1=13
# x2=18
# # print(-200+ x*1700/50)
# y1=-200+ x1*1700/50
# y2=-200+ x2*1700/50
# s=0.97
# s=np.max(data)/np.max(data2)
#display data type of NumPy array
# print(data.shape)
# plt.figure(figsize=(12, 6))
# plt.subplot(3, 1, 3)
# plt.plot(data[0:data.shape[0]-1,0],data[0:data.shape[0]-1,1])
# Moving average function
M=1
# plt.figure()
# plt.plot(data[0:data.shape[0]-1-M,0],data[0:data.shape[0]-1-M,1])
# plt.xlim(0, 8)


def moving_average(data, window_size):
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')
y=data[:-M,1]
# Smooth the data with a window size of 5
window_size = 5
y_smoothed = moving_average(y, window_size)
y=data[:-M,1]
# y2=data2[:-M,1]
window_size_2 = 13  # Window size (must be odd)
poly_order = 2    # Polynomial order
y_smoothed_1 = savgol_filter(y, window_size_2, poly_order)
# y_smoothed_2 = savgol_filter(y2, window_size_2, poly_order)

fig, ax = plt.subplots(1, 1, figsize=(12, 8))

ax.plot(data[0:data.shape[0]-1-M,0],sign*data[0:data.shape[0]-1-M,1],color='blue',linewidth=4)
# ax.plot(data2[:-M,0],data2[:-M,1],color='red',linewidth=4)
# ax.plot(data[0:data.shape[0]-1,0],data[0:data.shape[0]-1,1],linewidth=4)
# ax.plot(data[window_size-1:,0],y_smoothed,linewidth=4)
# ax.plot(data[:-M,0],y_smoothed_1,color='lightskyblue',linewidth=6)
# ax.plot(data[:-M,0],y_smoothed_2,color='lightcoral',linewidth=6)
ax.set_xlabel('time (fs)',fontsize=28,labelpad=14)
# ax.set_ylabel('Peak position (eV)',fontsize=28,labelpad=14)
ax.set_ylabel('Intensity (a.u.)',fontsize=28,labelpad=14)
# ax.set_ylabel('Signal (a.u.)',fontsize=28,labelpad=14)
ax.tick_params(axis='both',labelsize=28)
ax.tick_params(axis='both', direction='in', length=10, width=3)
plt.gca().xaxis.set_tick_params(top=True, labeltop=False)  # Enable ticks on the top
plt.gca().yaxis.set_tick_params(right=True, labelright=False)  # Enable ticks on the right
# ax.set_ylabel('intensity (a.u.)')
print(data[:,0].shape)
# f=fit(data[0:data.shape[0]-1,0],data[0:data.shape[0]-1,1], [0.5,0.5], fig, ax)
print(np.argmax(data[:-2,1]),np.max(data[:-2,1]))
max_index=np.argmax(data[:-2,1])
min_index=np.argmin(data[max_index:-2,1])
print(np.argmin(data[max_index:-2,1]),np.min(data[max_index:-2,1]))
print(data[np.argmax(data[:-2,1]),0],data[np.argmin(data[max_index:-2,1]),0])
ax.spines['top'].set_linewidth(3)
ax.spines['right'].set_linewidth(3)
ax.spines['bottom'].set_linewidth(3)
ax.spines['left'].set_linewidth(3)
legend = plt.legend(['M point below Fermi','M point above Fermi'], frameon=True, edgecolor='black', facecolor='white',fontsize=14)
legend.get_frame().set_linewidth(2)  # Set the thickness of the legend box
fig.tight_layout()
def millions_formatter(x, pos):
    return f'{x*1e0:.3f}'

# Set the formatter for the y-axis
ax.yaxis.set_major_formatter(FuncFormatter(millions_formatter))
# ax.set_ylabel('intensity (a.u.)')
print(data[:,0].shape)
# f=fit(data[0:data.shape[0]-1,0],data[0:data.shape[0]-1,1], [0.5,0.5], fig, ax)
print(np.argmax(data[:-2,1]),np.max(data[:-2,1]))
max_index=np.argmax(data[:-2,1])
min_index=np.argmin(data[max_index:-2,1])
print(np.argmin(data[max_index:-2,1]),np.min(data[max_index:-2,1]))
print(data[np.argmax(data[:-2,1]),0],data[np.argmin(data[max_index:-2,1]),0])
new_data=np.zeros((data.shape[0]-M,2))
new_data[:,0]=data[:-M,0]
# new_data[:,1]=y_smoothed_1
new_data[:,1]=sign*data[:-M,1]
# f=fit(data, [0.5,0.95], fig, ax,name)
c=fit(new_data, [0.5,0.95], fig, ax, name)
# plt.plot(data2[:,0],s*data2[:,1], label='time= '+str(y2)+" fs" )
# plt.xlim(-0.7,-.1)
# plt.ylim(np.min(data2[10:80,1]),1.1*np.max(data2[10:80,1]))
# plt.xlabel('Energy (eV)', fontsize= 14)
# plt.ylabel('Intensity (a.u.)',fontsize= 14)
# plt.title('Convolution Result')
# plt.legend()

plt.show()