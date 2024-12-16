import os
import shutil
import glob

data_path = r'D:\model_3_data\output'
output_path = r'D:\model_3_data\moshe_2500x4'
os.mkdir(output_path) if not os.path.exists(output_path) else None
models_path = os.path.join(data_path, 'models')
spectrums_path = os.path.join(data_path, 'results')
output_models_path = os.path.join(output_path, 'models')
output_spectrums_path = os.path.join(output_path, 'results')
os.mkdir(output_models_path) if not os.path.exists(output_models_path) else None
os.mkdir(output_spectrums_path) if not os.path.exists(output_spectrums_path) else None

def copy_spectrum(idx):
    src_folder = os.path.join(spectrums_path, str(idx))
    dst_folder = os.path.join(output_spectrums_path,str(idx))
    os.mkdir(dst_folder) if not os.path.exists(dst_folder) else None
    src_file_rad = glob.glob(os.path.join(src_folder , '*(f=2400)*'))[0]
    dst_file_rad= os.path.join(dst_folder,f'{idx}_farfield.txt')

    src_file_gamma = os.path.join(src_folder , 'S_parameters.pickle')
    dst_file_gamma = os.path.join(dst_folder,f'{idx}_S11.pickle')

    shutil.copy(src_file_rad, dst_file_rad)
    shutil.copy(src_file_gamma, dst_file_gamma)
    print(f'Successfully saved for antenna #{idx} ')
# if __name__ == "__main__":
#     idx_start, idx_end = 10000, 20000
#     for idx in range(idx_start, idx_end):

        # copy_spectrum(idx)

