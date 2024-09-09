
import shutil
import os
import time

origin_path = r'C:\Users\Public\cst_project\output'
destination_path = r'E:\model_3_data\output'

# start = int(70e3)
# stop = int(100e3)

result_list = os.listdir(os.path.join(origin_path,'results'))
result_list = [int(i) for i in result_list]
start = min(result_list)
stop = max(result_list)
print(f'------------------ copying {max(result_list)-min(result_list):d} images -------------')
start_time = time.time()
for ID in range(start, stop):

    s_image = f"S11_pictures\\S_parameters_{ID:d}.png"
    model_image = f"model_pictures\\image_{ID:d}.png"
    model_folder = os.path.join('models',str(ID))
    result_folder = os.path.join('results',str(ID))

    if (os.path.isfile(os.path.join(origin_path,s_image)) and
            not(os.path.isfile(os.path.join(destination_path,s_image)))):
        shutil.move(os.path.join(origin_path,model_folder), os.path.join(destination_path,model_folder))
        shutil.move(os.path.join(origin_path,model_image), os.path.join(destination_path,model_image))
        shutil.move(os.path.join(origin_path,result_folder), os.path.join(destination_path,result_folder))
        shutil.copy(os.path.join(origin_path,s_image), os.path.join(destination_path,s_image))
        print(f'done with {ID:d}')
        if ID % 10 == 0:
            print(f"--- {stop-ID:d} remains |  {(time.time() - start_time):.1f} seconds | avg time = "
                  f"{(time.time() - start_time)/(ID-start+1):2f} ---")

print('DONE WITH THE JOB')
