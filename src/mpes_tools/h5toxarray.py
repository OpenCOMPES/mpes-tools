import h5py
import numpy as np
import xarray as xr


class h5toxarray_loader():
    def __init__(self, df):

        if len(list(df['binned'].keys()))>1:
            first_key = sorted(df['binned'].keys(), key=lambda x: int(x[1:]))[0]
            data_shape = df['binned/' + first_key][:].shape  
            self.M = np.empty((data_shape[0], data_shape[1], data_shape[2], len(df['binned'])))
            axis=[]
            for idx, v in enumerate(sorted(df['binned'].keys(), key=lambda x: int(x[1:]))):
                self.M[:, :, :, idx] = df['binned/' + v][:]
        else: 
            self.M= df['binned/' + list(df['binned'].keys())[0]][:]
        
        
        # Define the desired order lists
        desired_orders = [
            ['ax0', 'ax1', 'ax2', 'ax3'],
            ['kx', 'ky', 'E', 'delay'],
            ['kx', 'ky', 'E', 'ADC']
        ]
        
        axes_list = []
      
        matched_order = None
        for i, order in enumerate(desired_orders):
            # Check if all keys in the current order exist in df['axes']
            if all(f'axes/{axis}' in df for axis in order):
                # If match is found, generate axes_list based on this order
                axes_list = [df[f'axes/{axis}'] for axis in order]
                matched_order = i + 1  # Store which list worked (1-based index)
                break  # Stop once the first matching list is found
        
        if matched_order:
            print(f"Matched desired list {matched_order}: {desired_orders[matched_order - 1]}")
        else:
            print("No matching desired list found.")
        
        # print("Axes list:", axes_list)
        # print(M[12,50,4,20])
        self.data_array = xr.DataArray(
            self.M,
            coords={"kx": axes_list[0], "ky": axes_list[1], "E": axes_list[2], "dt": axes_list[3]},
            dims=["kx", "ky", "E","dt"]
        )
    def get_data_array(self):
        return self.data_array
    def get_original_array(self):
        return self.M
# df =h5py.File(r'C:\Users\admin-nisel131\Documents\Scan130_scan130_Amine_100x100x300x50_spacecharge4_gamma850_amp_3p3.h5', 'r')
# test=h5toxarray_loader(df)
