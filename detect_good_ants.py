import pickle
import numpy as np

local_path = 'D:\\model_3_data\\output\\'
count = 0
good_ants_ID = []
for i_ID in range(10000):
    s_file = local_path + 'results\\' + str(i_ID) + '\\S_parameters.pickle'
    file = open(s_file, 'rb')
    data = pickle.load(file)
    file.close()
    if np.min(10*np.log10(np.abs(data[0]))) <= -6:
        count += 1
        good_ants_ID.append(i_ID)
        print(f'{i_ID} - current count = {count} | density [%]: {count/i_ID*100:.0f}%')

file = open(local_path + 'good_ants_ID-6.pickle', 'wb')
pickle.dump(good_ants_ID, file)
file.close()

print(f'total number of ants = {count:.0f}')