import os
import sys
import pickle
import time

# [0,10000] (not including last one)
model_parameters = {
    'type': 3,
    # parameters that change both the antenna and the environment
    'length': 50,  # coordinate along the y (green) axis
    'width': 100,  # coordinate along the x (red) axis
    'adx': 0.9,
    'arx': 0.9,
    'adz': 0.85,
    'arz': 0.85,
    'a': 0.6,
    # parameters that change only the environment
    'thickness': 1,
    'height': 15,
    'ady': 0.85,
    'ary': 0.7,
    'b': 0.4,
    'c': 0.2,
    'bdx': 0.8,
    'brx': 0.75,
    'bdy': 0.8,
    'bry': 0.75,
    'bdz': 0.8,
    'brz': 0.75,
    'cdx': 0.8,
    'crx': 0.75,
    'cdy': 0.8,
    'cry': 0.75,
    'cdz': 0.8,
    'crz': 0.75,
    'ddx': 0.8,
    'drx': 0.75,
    'ddy': 0.8,
    'dry': 0.75,
    'ddz': 0.8,
    'drz': 0.75
}
save_path = r'D:\model_3_data\output\models'
t_0 = time.time()
for run_ID in range(0, 10000):
    # save the S parameters data
    file_name = save_path + '\\' + str(run_ID) + '\\model_parameters.pickle'
    file = open(file_name, 'wb')
    pickle.dump(model_parameters, file)
    file.close()
    if run_ID % 500 == 0:
        print(f'now at {run_ID}, time is: {time.time()-t_0:.1f} sec')
