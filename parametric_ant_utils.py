
import numpy as np

def get_parameters_names():
    parameters_names = []
    for iw in range(2):
        for i1 in range(3):
            if iw==1 and i1==2:
                continue
            parameters_names.append(f'w{iw+1:d}x{i1+1:d}')
            parameters_names.append(f'w{iw + 1:d}y{i1 + 1:d}'
    return parameters_names

def randomize_ant(parameters_names,seed=0):
    ant_parameters = {}
    if seed > 0:
        np.random.seed(seed)
    for key in parameters_names:
        ant_parameters[key] = np.round(np.random.uniform(),decimals=1)
    return ant_parameters