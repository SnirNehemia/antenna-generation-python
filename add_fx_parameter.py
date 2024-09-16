import pickle


models_path = r'G:\local_model_3_path\simplified\output\models'
for run_ID in range(100000,101110):
    # load
    file_name = models_path + '\\' + str(run_ID) + '\\ant_parameters.pickle'
    file = open(file_name, 'rb')
    ant_parameters = pickle.load(file)
    file.close()
    # add
    # ant_parameters['fx'] = 0
    # wings = ['w1', 'w2', 'w3', 'q1', 'q2', 'q3']
    # for wing in wings:
    #     ant_parameters[f'{wing}z0'] = 0
    # resave
    file = open(file_name, 'wb')
    pickle.dump(ant_parameters, file)
    file.close()
    print(run_ID)


