

def rel2abs(ant_parameters, model_parameters):
    ant_parameters_abs = ant_parameters.copy()
    Sz = (model_parameters['length'] * model_parameters['adz'] * model_parameters['arz'] / 2 - ant_parameters['w'] / 2
          - model_parameters['feed_length'] / 2)
    Sy = model_parameters['height'] * model_parameters['ady'] * model_parameters['ary'] - ant_parameters['w']
    for key, value in ant_parameters.items():
        if len(key) == 4:
            if key[2] == 'z':
                ant_parameters_abs[key] = value * Sz
            if key[2] == 'y' or key == 'fx':
                ant_parameters_abs[key] = value * Sy
    return ant_parameters_abs
