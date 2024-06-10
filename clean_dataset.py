import os
import glob
import shutil
writing_path = r'D:\model_3_data\spectrum_moshe'
reading_path = r'D:\model_3_data\output\results'
if __name__ == '__main__':
    dirs = os.listdir(reading_path)
    dirs = sorted(int(dir) for dir in dirs)
    for i,dir in enumerate(dirs):
        print(f'sample #{i}')
        spectrum_dir = os.path.join(reading_path,str(dir))
        assert os.path.exists(spectrum_dir)
        radiation_file =  glob.glob('*f=2400*.txt',root_dir=spectrum_dir)[0]
        s11_file = glob.glob('*S_parameters*',root_dir=spectrum_dir)[0]
        radiation_path = os.path.join(spectrum_dir,radiation_file)
        s11_path = os.path.join(spectrum_dir,s11_file)
        shutil.copy(radiation_path,os.path.join(writing_path,f'ant{i}_farfield.txt'))
        shutil.copy(s11_path,os.path.join(writing_path,f'ant{i}_S11.pickle'))
    pass