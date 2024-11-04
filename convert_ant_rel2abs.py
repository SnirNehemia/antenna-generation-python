
import numpy as np

def rel2abs(ant_parameters, model_parameters):
    ant_parameters_abs = ant_parameters.copy()
    Sz = (model_parameters['length'] * model_parameters['adz'] * model_parameters['arz'] / 2 - ant_parameters['w'] / 2
          - model_parameters['feed_length'] / 2)
    Sy = model_parameters['height'] * model_parameters['ady'] * model_parameters['ary'] - ant_parameters['w']
    for key, value in ant_parameters.items():
        if len(key) == 4:
            if key[2] == 'z':
                ant_parameters_abs[key] = np.round(value * Sz, decimals=2)
            if key[2] == 'y':
                ant_parameters_abs[key] = np.round(value * Sy, decimals=2)
        if key == 'fx':
            ant_parameters_abs[key] = np.round(value * Sy, decimals=2)
    return ant_parameters_abs

def abs2rel(ant_parameters_abs, model_parameters):
    ant_parameters_rel = ant_parameters_abs.copy()
    Sz = (model_parameters['length'] * model_parameters['adz'] * model_parameters['arz'] / 2 - ant_parameters['w'] / 2
          - model_parameters['feed_length'] / 2)
    Sy = model_parameters['height'] * model_parameters['ady'] * model_parameters['ary'] - ant_parameters['w']
    for key, value in ant_parameters_abs.items():
        if len(key) == 4:
            if key[2] == 'z':
                ant_parameters_rel[key] = np.round(value / Sz, decimals=2)
            if key[2] == 'y':
                ant_parameters_rel[key] = np.round(value / Sy, decimals=2)
        if key == 'fx':
            ant_parameters_rel[key] = np.round(value / Sy, decimals=2)
    return ant_parameters_rel

def model_rel2abs(model_parameters):
    model_parameters_abs = model_parameters.copy()
    axes = ['x','y','z']
    dimensions = ['width','height','length']

    elements = ['a','b','c','d']
    for e in elements:
        for [axis,i_axis] in enumerate(axes):
            model_parameters_abs[e+'d' + axis] = model_parameters[e+'d' + axis] * model_parameters[dimensions[i_axis]]
            model_parameters_abs[e+'r' + axis] = model_parameters[e+'r' + axis] * model_parameters[e+'d' + axis] * model_parameters[dimensions[i_axis]]
    model_parameters_abs['a'] = model_parameters['a'] *model_parameters['width']
    model_parameters_abs['b'] = model_parameters['b'] * model_parameters['height']
    model_parameters_abs['c'] = model_parameters['c'] * model_parameters['height']
    # model_parameters_abs['d'] = model_parameters['d'] * model_parameters['height']
    return model_parameters_abs

# def model_abs2rel(ant_parameters_abs, model_parameters):
#     ant_parameters_rel = ant_parameters_abs.copy()
#     Sz = (model_parameters['length'] * model_parameters['adz'] * model_parameters['arz'] / 2 - ant_parameters['w'] / 2
#           - model_parameters['feed_length'] / 2)
#     Sy = model_parameters['height'] * model_parameters['ady'] * model_parameters['ary'] - ant_parameters['w']
#     for key, value in ant_parameters_abs.items():
#         if len(key) == 4:
#             if key[2] == 'z':
#                 ant_parameters_rel[key] = np.round(value / Sz, decimals=2)
#             if key[2] == 'y':
#                 ant_parameters_rel[key] = np.round(value / Sy, decimals=2)
#         if key == 'fx':
#             ant_parameters_rel[key] = np.round(value / Sy, decimals=2)
#     return ant_parameters_rel
