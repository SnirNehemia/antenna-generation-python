
import dxf_management

model_parameters = {
    'type':3,
    'plane':'yz-flipped',#changetoyz-flipped
    #parametersthatchangeboththeantennaandtheenviroment
    'length':60,#coordinatealongthev(green)axis
    'width':30,#coordinatealongthex(red)axis
    'adx':0.9,
    'arx':0.9,
    'adz':0.9,
    'arz':0.9,
    'a':0.6,
    #parametersthatchangeonlytheenviromentinaplane=xzconfiguration
    'thickness':1,
    'height':50,
    'ady':0.85,
    'ary':0.85,
    'b':0.8,
    'c':0.8,
    'bdx':1,
    'brx':0.2,
    'bdy':0.8,
    'bry':0.75,
    'bdz':0.8,
    'brz':0.75,
    'cdx':1,
    'crx':0.3,
    'cdy':0.8,
    'cry':0.75,
    'cdz':0.8,
    'crz':0.75,
    'ddx':1,
    'drx':1,
    'ddy':0.8,
    'dry':0.75,
    'ddz':1,
    'drz':1
}

MY_PATH = r'C:\Users\Snir\OneDrive - Tel-Aviv University\Documents\tests'
MY_PATH_sub_folder = '\\sub_folder'
import time
import numpy as np
start = time.time()
for i in range(10000):
    dxf_management.CreateDXF(plot=False, run_ID=str(i), project_name=MY_PATH_sub_folder, local_path=MY_PATH,
                             model=model_parameters)
    print(i)
    if i%100 == 0:
        print(f'{time.time()-start:.0f} sec passed')



