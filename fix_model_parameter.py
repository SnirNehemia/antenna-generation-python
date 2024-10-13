import pickle
import os
computer = 'beast' # beast, server or office

if computer == 'beast':
    model_parameters_fix = {
        'ady': 0.7,
        'ary': 0.7,
        'adz':0.6,
        'arz':0.7,
    }
# else:
#     model_parameters = {
#         'adx': 0.9,
#         'arx': 0.9,
#         'ady': 0.9,
#         'ary': 0.85,
#         'adz': 0.9,
#         'arz': 0.9,
#         'a': 0.6,
#         'b': 0.8,
#         'c': 0.8,
#         'brx': 0.2,
#         'bdy': 0.8,
#         'bry': 0.75,
#         'bdz': 0.8,
#         'brz': 0.75,
#         'crx': 0.3,
#         'cdy': 0.8,
#         'cry': 0.75,
#         'cdz': 0.8,
#         'crz': 0.75,
#         'ddy': 0.8,
#         'dry': 0.75,
#     }

models_path = r'C:\Users\User\Documents\CST_project\output\models'
dir_list = os.listdir(models_path)
print('starting')
for run_ID in dir_list:
    # load
    file_name = models_path + '\\' + str(run_ID) + '\\model_parameters.pickle'
    file = open(file_name, 'rb')
    model_parameters = pickle.load(file)
    file.close()
    print(f'opened {run_ID:s} ',end='')
    # add
    for key, value in model_parameters_fix.items():
        model_parameters[key] = value
    # ant_parameters['fx'] = 0
    # wings = ['w1', 'w2', 'w3', 'q1', 'q2', 'q3']
    # for wing in wings:
    #     ant_parameters[f'{wing}z0'] = 0
    # resave
    file = open(file_name, 'wb')
    pickle.dump(model_parameters, file)
    file.close()
    print('closed')


