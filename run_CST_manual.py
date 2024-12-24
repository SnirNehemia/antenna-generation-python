import os
import sys
# sys.path.append(r"C:\Program Files\Dassault Systemes\B426CSTEmagConnector\CSTStudio\AMD64\python_cst_libraries")
sys.path.append(r"C:\Program Files (x86)\CST Studio Suite 2024\AMD64\python_cst_libraries")

import cst
print('can now communicate with ' + cst.__file__) # should print '<PATH_TO_CST_AMD64>\python_cst_libraries\cst\__init__.py'
# documentation is at "https://space.mit.edu/RADIO/CST_online/Python/main.html"
# https://github.com/temf/CST_Python_Interface/blob/main/Documentation/CST_with_Python_Documentation.pdf provides examples

import cst.interface
import cst.results
import numpy as np

from distutils.dir_util import copy_tree
import shutil
import pickle
import time
import parametric_ant_utils_randish_ant as parametric_ant_utils
# import parametric_ant_utils
from matplotlib import pyplot as plt
from datetime import datetime

""" define run parameters """
# --- define local path and project name
# project_name = r'Model3Again'
simulation_name = 'CST_Model_better_parametric_moshe'
project_name = r'cst_project'
# local_path = "C:\\Users\\shg\\Documents\\CST_projects\\"
# local_path = 'C:\\Users\\Public\\'
# local_path = 'C:\\Users\\Snir\\OneDrive - Tel-Aviv University\\Documents\\local_model_3_path\\'
local_path = 'C:\\Users\\Public\\'


# ant_parameters_names = parametric_ant_utils.get_parameters_names()


""" create all tree folder paths """
# --- from here on I define the paths based on the manually defined project and local path ---
final_dir = local_path + project_name
project_path = final_dir + "\\" + simulation_name + ".cst"
results_path = final_dir+"\\output_moshe\\results"
# dxf_directory = "C:\\Users\\shg\\OneDrive - Tel-Aviv University\\Documents\\CST_projects\\"+project_name_DXF
models_path =  final_dir+"\\output_moshe\\models"
pattern_source_path = (final_dir+"\\" + simulation_name +
                  r'\Export\Farfield')
save_S11_pic_dir = final_dir+"\\output_moshe\\S11_pictures"
STEP_source_path = (final_dir+"\\" + simulation_name +
                  r'\Model\3D')
# --- for export STLs
file_names = ['Antenna_PEC', 'Antenna_Feed', 'Antenna_Feed_PEC',
              'Env_PEC', 'Env_FR4', 'Env_Polycarbonate', 'Env_Vacuum']

# file_names = ['Antenna_PEC', 'Antenna_Feed', 'Antenna_Feed_PEC',
#               'Env_FR4', 'Env_Vacuum']


""" open the CST project that we already created """

cst_instance = cst.interface.DesignEnvironment()
project = cst.interface.DesignEnvironment.open_project(cst_instance, project_path)

results = cst.results.ProjectFile(project_path, allow_interactive=True)

""" run the simulations """

# run the function that is currently called 'main' to generate the cst file

cst_time = time.time()
data_path = r"C:\Users\Public\cst_project\output_moshe\generated_top_1"
all_files = os.listdir(data_path)
antennas_names = np.unique([file[4:10] for file in all_files])
# TODO: if you want, you may write a for loop here.
bad_ant_list = ['130689','131197','131529','133205','133238','141781']
ant_name = '119348'
# for ant_name in antennas_names:
#     # if ant_name in bad_ant_list:
#     #     continue
model_path = r"C:\Users\shg\Desktop\model_parameters.pickle"
# for grade in ['grade_0']:
ant_ID = f'{ant_name}_test'
ant_path = r"C:\Users\shg\Desktop\ant_parameters.pickle"
print(f'Working on antenna in path: {ant_path} ')
# TODO:
""" LOAD HERE:
 model_parameters and antenna_parameters
 do it as you got them - as a dictionary!
 add a parameter ant_ID to save it to a different file (so your results won't overwrite each other)"""


file = open(model_path, 'rb')
model_parameters = pickle.load(file)
file.close()

file = open(ant_path, 'rb')
ant_parameters = pickle.load(file)
file.close()
assert parametric_ant_utils.check_ant_validity(ant_parameters=ant_parameters, model_parameters=model_parameters) == 1
print('MODEL VALID!')
# Delete files in the CST folder to prevent errors
target_SPI_folder =final_dir + "\\" + simulation_name +"\\Result"
for filename in os.listdir(target_SPI_folder):
    if filename.endswith('.spi'):
        os.remove(target_SPI_folder +"\\" + filename)
target_delete_folder = final_dir + "\\" + simulation_name +"\\Model\\3D"
for filename in os.listdir(target_delete_folder):
    if filename.endswith('.stp') or filename.endswith('.stl') or filename.endswith('.hlg'):
        os.remove(target_delete_folder +"\\" + filename)
target_delete_folder = final_dir + "\\" + simulation_name +"\\Export\\Farfield"
if os.path.isdir(target_delete_folder):
    for filename in os.listdir(target_delete_folder):
        if filename.endswith('.txt'):
            os.remove(target_delete_folder +"\\" + filename)
print('deleted SPI, models and results... ', end='')
# Determine env parameter by adjusting model_parameters values

# update model
for key, value in model_parameters.items():
    if type(value) != str and key != 'type':
        # print('U-'+key)
        VBA_code = r'''Sub Main
                StoreParameter("'''+key+'''", '''+str(model_parameters[key])+''')
                End Sub'''
        project.schematic.execute_vba_code(VBA_code)


for key, value in ant_parameters.items():
    VBA_code = r'''Sub Main
            StoreParameter("'''+key+'''", '''+str(value)+''')
            End Sub'''
    project.schematic.execute_vba_code(VBA_code)
# save picture of the antenna
parametric_ant_utils.save_figure(model_parameters, ant_parameters, local_path + project_name, ant_ID)


""" -------------------------- Rebuild the model and run it ------------------------------------ """
project.model3d.full_history_rebuild()  # I just replaced modeler with model3d
print(' run solver... ',end='')
try:
    project.model3d.run_solver()
    print(' finished simulation... ', end='')
    succeed = 1
except Exception as error:
    # handle the exception
    print("An exception occurred:", error)  # An exception occurred
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print('\n\n', exc_type, fname, exc_tb.tb_lineno, '\n\n')
    print('there was an error with the run!')

""" access results """
S_results = results.get_3d().get_result_item(r"1D Results\S-Parameters\S1,1")
S11 = np.array(S_results.get_ydata())
freq = np.array(S_results.get_xdata())
print(' got S11, ', end='')
radiation_efficiency_results = results.get_3d().get_result_item(r"1D Results\Efficiencies\Rad. Efficiency [1]")
radiation_efficiency = np.array(radiation_efficiency_results.get_ydata())
freq_efficiency = np.array(radiation_efficiency_results.get_xdata())
total_efficiency_results = results.get_3d().get_result_item(r"1D Results\Efficiencies\Tot. Efficiency [1]")
total_efficiency = np.array(total_efficiency_results.get_ydata())
print(' got efficiencies, ', end='')
# the farfield will be exported using post-proccessing methods and it should be moved to a designated location and renamed
print(' got results... ',end='')

# save the farfield
copy_tree(pattern_source_path, results_path + '\\' + str(ant_ID))

# TODO: save the DXFs too in 3 seperate files. try to also save the picture of the ant!
#  maybe after we save it we can load it with ezdxf and then print it in the same way.
# save and copy the STEP model:
# save:
for file_name in file_names:
    VBA_code = r'''Sub Main
    SelectTreeItem("Components'''+'\\'+file_name+r'''")
        Dim path As String
        Path = "./'''+file_name+'''_STEP.stp"
        With STEP
            .Reset
            .FileName(path)
            .WriteSelectedSolids
        End With
    End Sub'''
    project.schematic.execute_vba_code(VBA_code)
    VBA_code = r'''Sub Main
            SelectTreeItem("Components''' + '\\' + file_name + r'''")
                Dim path As String
                Path = "./''' + file_name + '''_STL.stl"
                With STEP
                    .Reset
                    .FileName(path)
                    .WriteSelectedSolids
                End With
            End Sub'''
    project.schematic.execute_vba_code(VBA_code)
VBA_code = r'''Sub Main
    Dim path As String
    Path = "./Whole_Model_STEP.stp"
    With STEP
        .Reset
        .FileName(path)
        .WriteAll
    End With
End Sub'''
project.schematic.execute_vba_code(VBA_code)
VBA_code = r'''Sub Main
        Dim path As String
        Path = "./Whole_Model_STL.stl"
        With STEP
            .Reset
            .FileName(path)
            .WriteAll
        End With
    End Sub'''
project.schematic.execute_vba_code(VBA_code)
# now copy:
target_STEP_folder = models_path + '\\' + str(ant_ID)
if not os.path.exists(target_STEP_folder):
    os.makedirs(target_STEP_folder)
for filename in os.listdir(STEP_source_path):
    if filename.endswith('.stp'):
        shutil.copy(STEP_source_path + '\\' + filename, target_STEP_folder)
    if filename.endswith('.stl'):
        shutil.copy(STEP_source_path + '\\' + filename, target_STEP_folder)
    if filename.endswith('.hlg'):
        shutil.copy(STEP_source_path + '\\' + filename, target_STEP_folder)
# save picture of the S11
plt.ioff()
f, ax1 = plt.subplots()
ax1.plot(freq, 20 * np.log10(np.abs(S11)))  # TODO: I fixed it here!
ax1.set_ylim(ymin=-20, ymax=0)
ax1.set_ylabel('|S11|', color='C0')
ax1.tick_params(axis='y', color='C0', labelcolor='C0')
ax2 = ax1.twinx()
ax2.plot(freq, np.angle(S11), 'C1')
ax2.set_ylim(ymin=-np.pi, ymax=np.pi)
ax2.set_ylabel('phase [rad]', color='C1')
ax2.tick_params(axis='y', color='C1', labelcolor='C1')
plt.title('S parameters')
plt.show(block=False)
f.savefig(save_S11_pic_dir + r'\S_parameters_' + str(ant_ID) + '.png')
plt.close(f)

# save the S parameters data
file_name = results_path + '\\' + str(ant_ID) + '\\S_parameters.pickle'
file = open(file_name, 'wb')
pickle.dump([S11, freq], file)
file.close()
# save the efficiencies data
file_name = results_path + '\\' + str(ant_ID) + '\\Efficiency.pickle'
file = open(file_name, 'wb')
pickle.dump([total_efficiency, radiation_efficiency, freq_efficiency], file)
file.close()

print('saved results. ')
        # print(f'\t RUNTIME for #{ant_ID:.0f}:\n\t\t ant #{ant_ID:.0f} time: {(time.time()-cst_time)/60:.1f} min \n\t\t overall time: {(time.time()-overall_sim_time)/60/60:.2f} hours')
        # print(f'\t\t average time: {(time.time() - overall_sim_time) / ants_count/60: .1f} min')



print(' --------------------------------- \n \t\t\t FINISHED THE RUN \n ---------------------------------')