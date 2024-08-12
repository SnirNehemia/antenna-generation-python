import pickle
import numpy as np

local_path = 'D:\\model_3_data\\output\\'
count = 0
good_ants_ID = []
count_passed = 0
for i_ID in range(75000, 80200):
    count_passed += 1
    s_file = local_path + 'results\\' + str(i_ID) + '\\S_parameters.pickle'
    file = open(s_file, 'rb')
    data = pickle.load(file)
    file.close()
    if np.min(10*np.log10(np.abs(data[0]))) <= -6:
        count += 1
        good_ants_ID.append(i_ID)
        print(f'{i_ID} - current count = {count} | density [%]: {count/count_passed*100:.0f}%')

file = open(local_path + 'good_ants_simplified_ID-6.pickle', 'wb')
pickle.dump(good_ants_ID, file)
file.close()

print(f'total number of ants = {count:.0f}')
