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
# 10000 - 12499
model_parameters = {
    'type': 3,
    'plane': 'xz',
    # parameters that change both the antenna and the enviroment
    'length': 50,  # coordinate along the v (green) axis
    'width': 100,  # coordinate along the x (red) axis
    'adx': 0.9,
    'arx': 0.9,
    'adz': 0.85,
    'arz': 0.85,
    'a': 0.6,
    # parameters that change only the enviroment in a plane=xz configuration
    'thickness': 1,
    'height': 15,
    'ady': 0.9,
    'ary': 0.1,
    'b': 0.8,
    'c': 0.8,
    'bdx': 0.2,
    'brx': 1,
    'bdy': 0.8,
    'bry': 0.75,
    'bdz': 0.8,
    'brz': 0.75,
    'cdx': 1,
    'crx': 0.3,
    'cdy': 0.8,
    'cry': 0.75,
    'cdz': 0.8,
    'crz': 0.75,
    'ddx': 1,
    'drx': 1,
    'ddy': 0.8,
    'dry': 0.75,
    'ddz': 1,
    'drz': 1
}

# 12500-15000
model_parameters = {
    'type': 3,
    'plane': 'xz', # change to yz-flipped
    # parameters that change both the antenna and the enviroment
    'length': 50,  # coordinate along the v (green) axis
    'width': 100,  # coordinate along the x (red) axis
    'adx': 0.9,
    'arx': 0.9,
    'adz': 0.85,
    'arz': 0.85,
    'a': 0.6,
    # parameters that change only the enviroment in a plane=xz configuration
    'thickness': 1,
    'height': 50,
    'ady': 1,
    'ary': 0.1,
    'b': 0.8,
    'c': 0.8,
    'bdx': 0.2,
    'brx': 1,
    'bdy': 0.8,
    'bry': 0.75,
    'bdz': 0.8,
    'brz': 0.75,
    'cdx': 1,
    'crx': 0.3,
    'cdy': 0.8,
    'cry': 0.75,
    'cdz': 0.8,
    'crz': 0.75,
    'ddx': 1,
    'drx': 1,
    'ddy': 0.8,
    'dry': 0.75,
    'ddz': 1,
    'drz': 1
}
# 15000-17500 - ATTENTION! the antenna is rotated
model_parameters = {
    'type': 3,
    'plane': 'yz-flipped', # change to yz-flipped
    # parameters that change both the antenna and the enviroment
    'length': 60,  # coordinate along the v (green) axis
    'width': 40,  # coordinate along the x (red) axis
    'adx': 0.9,
    'arx': 0.9,
    'adz': 0.9,
    'arz': 0.9,
    'a': 0.6,
    # parameters that change only the enviroment in a plane=xz configuration
    'thickness': 1,
    'height': 50,
    'ady': 0.85,
    'ary': 0.85,
    'b': 0.8,
    'c': 0.8,
    'bdx': 0.2,
    'brx': 1,
    'bdy': 0.8,
    'bry': 0.75,
    'bdz': 0.8,
    'brz': 0.75,
    'cdx': 1,
    'crx': 0.3,
    'cdy': 0.8,
    'cry': 0.75,
    'cdz': 0.8,
    'crz': 0.75,
    'ddx': 1,
    'drx': 1,
    'ddy': 0.8,
    'dry': 0.75,
    'ddz': 1,
    'drz': 1
}
# 17500-20000 - ATTENTION! the antenna is rotated
model_parameters = {
    'type': 3,
    'plane': 'yz-flipped', # change to yz-flipped
    # parameters that change both the antenna and the enviroment
    'length': 60,  # coordinate along the v (green) axis
    'width': 40,  # coordinate along the x (red) axis
    'adx': 0.9,
    'arx': 0.9,
    'adz': 0.9,
    'arz': 0.9,
    'a': 0.6,
    # parameters that change only the enviroment in a plane=xz configuration
    'thickness': 1,
    'height': 50,
    'ady': 0.85,
    'ary': 0.85,
    'b': 0.8,
    'c': 0.8,
    'bdx': 1,
    'brx': 0.2,
    'bdy': 0.8,
    'bry': 0.75,
    'bdz': 0.8,
    'brz': 0.75,
    'cdx': 1,
    'crx': 0.3,
    'cdy': 0.8,
    'cry': 0.75,
    'cdz': 0.8,
    'crz': 0.75,
    'ddx': 1,
    'drx': 1,
    'ddy': 0.8,
    'dry': 0.75,
    'ddz': 1,
    'drz': 1
}
# 20000-22500 - ATTENTION! there is no env!
model_parameters = {
    'type': 3,
    'plane': 'xz',
    # parameters that change both the antenna and the enviroment
    'length': 50,  # coordinate along the v (green) axis
    'width': 100,  # coordinate along the x (red) axis
    'adx': 0.9,
    'arx': 0.9,
    'adz': 0.85,
    'arz': 0.85,
    'a': 0.6,
    # parameters that change only the enviroment in a plane=xz configuration
    'thickness': 0,
    'height': 15,
    'ady': 0.85,
    'ary': 0.7,
    'b': 0,
    'c': 0,
    'bdx': 0,
    'brx': 0,
    'bdy': 0,
    'bry': 0,
    'bdz': 0,
    'brz': 0,
    'cdx': 0,
    'crx': 0,
    'cdy': 0,
    'cry': 0,
    'cdz': 0,
    'crz': 0,
    'ddx': 0,
    'drx': 0,
    'ddy': 0,
    'dry': 0,
    'ddz': 0,
    'drz': 0
}

# 30000-40000 - ATTENTION! there is no env! It's Shahar-style
model_parameters = {
    'type': 4,
    'plane': 'xz',
    # parameters that change both the antenna and the enviroment
    'length': 50,  # coordinate along the v (green) axis
    'width': 100,  # coordinate along the x (red) axis
    'adx': 0.9,
    'arx': 0.9,
    'adz': 0.85,
    'arz': 0.85,
    'a': 0.6,
    # parameters that change only the enviroment in a plane=xz configuration
    'thickness': 0,
    'height': 15,
    'ady': 0.85,
    'ary': 0.01,
    'b': 0,
    'c': 0,
    'bdx': 0,
    'brx': 0,
    'bdy': 0,
    'bry': 0,
    'bdz': 0,
    'brz': 0,
    'cdx': 0,
    'crx': 0,
    'cdy': 0,
    'cry': 0,
    'cdz': 0,
    'crz': 0,
    'ddx': 0,
    'drx': 0,
    'ddy': 0,
    'dry': 0,
    'ddz': 0,
    'drz': 0
}

return
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
