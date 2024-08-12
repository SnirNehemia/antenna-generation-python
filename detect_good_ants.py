import pickle
import numpy as np

local_path = 'E:\\model_3_data\\output\\'
count = 0
good_ants_ID = []
count_all = 0
for i_ID in range(75000, 80200):
    count_all += 1
    s_file = local_path + 'results\\' + str(i_ID) + '\\S_parameters.pickle'
    file = open(s_file, 'rb')
    data = pickle.load(file)
    file.close()
    if np.min(10*np.log10(np.abs(data[0]))) <= -9:
        count += 1
        good_ants_ID.append(i_ID)
        print(f'{i_ID} - current count = {count} | density [%]: {count/count_all*100:.0f}%')

file = open(local_path + 'good_ants_simplified_ID-9.pickle', 'wb')
pickle.dump(good_ants_ID, file)
file.close()

print(f'total number of ants = {count:.0f}')
