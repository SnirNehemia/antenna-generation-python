import os
import sys
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
import dxf_management
from matplotlib import pyplot as plt


""" define run parameters """
# --- define local path and project name
simulation_name = r'CST_Model_100X100'
project_name = 'cst_project'
# local_path = "C:\\Users\\shg\\Documents\\CST_projects\\"
local_path = 'C:\\Users\\Public\\'
# --- the following lines is relevant when we have a path to pre-defined geometries (in DXF format)
create_new_models = 0 # 1 for creating new models, 0 to use existing ones
original_models_path = r'C:\Users\shg\OneDrive - Tel-Aviv University\AI RF design\model_3_data\output'  # path to existing models output folder
# --- choose whether to use fix or changed environment
change_env = 1

# model_parameters = {
#     'type': 1,
#     'height': 160, # coordinate along the y (green) axis
#     'width': 300, # coordinate along the x (red) axis
#     'adx': 0.8,
#     'arx': 0.75,
#     'ady': 0.8,
#     'ary': 0.8
# }

model_parameters = {
    'type': 3,
    'plane': 'yz-flipped',
    # parameters that change both the antenna and the enviroment
    'length': 50,  # coordinate along the v (green) axis
    'width': 100,  # coordinate along the x (red) axis
    'adx': 0.9,
    'arx': 0.9,
    'adz': 0.85,
    'arz': 0.85,
    'a': 0.6,
    # parameters that change only the enviroment in a plane=xz configuration
    'thickness': 0,
    'height': 15,
    'ady': 0.85,
    'ary': 0.7,
    'b': 0,
    'c': 0,
    'bdx': 0,
    'brx': 0,
    'bdy': 0,
    'bry': 0,
    'bdz': 0,
    'brz': 0,
    'cdx': 0,
    'crx': 0,
    'cdy': 0,
    'cry': 0,
    'cdz': 0,
    'crz': 0,
    'ddx': 0,
    'drx': 0,
    'ddy': 0,
    'dry': 0,
    'ddz': 0,
    'drz': 0
}

## --- define the parameters limits for randomization:
model_parameters_limits = model_parameters.copy()
for key, value in model_parameters_limits.items():
    if type(value) == int:
        if model_parameters_limits[key]<=1:
            model_parameters_limits[key] = [0, 1]
# EXAMPLE for a costum parameter
# model_parameters_limits['adx'] = [0.2,0.8]
model_parameters_limits['length'] = [30,100]
model_parameters_limits['width'] = [30,100]
model_parameters_limits['height'] = [30, 100]
model_parameters_limits['thickness'] = 1

""" create all tree folder paths """
# --- from here on I define the paths based on the manually defined project and local path ---
# project_path = local_path +project_name + "\\CST_Model.cst"
# results_path = local_path+project_name+"\\output\\results"
# # dxf_directory = "C:\\Users\\shg\\OneDrive - Tel-Aviv University\\Documents\\CST_projects\\"+project_name_DXF
# models_path =  local_path +project_name+"\\output\\models"
# pattern_source_path = (local_path+project_name+"\\CST_Model" +
#                   r'\Export\Farfield')
# save_S11_pic_dir = local_path+project_name+"\\output\\S11_pictures"
# STEP_source_path = (local_path+project_name+"\\CST_Model" +
#                   r'\Model\3D')

final_dir = local_path + project_name
project_path = final_dir + "\\" + simulation_name + ".cst"
results_path = final_dir+"\\output\\results"
# dxf_directory = "C:\\Users\\shg\\OneDrive - Tel-Aviv University\\Documents\\CST_projects\\"+project_name_DXF
models_path =  final_dir+"\\output\\models"
pattern_source_path = (final_dir+"\\" + simulation_name +
                  r'\Export\Farfield')
save_S11_pic_dir = final_dir+"\\output\\S11_pictures"
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
overall_sim_time = time.time()
ants_count = 0
starting_index = 50500
threshold_ID = 10000


good_ants_file = original_models_path + '\\good_ants_ID-9.pickle'
file = open(good_ants_file, 'rb')
good_ants_file_list = pickle.load(file)
file.close()


for ID_num in range(0, 99):
    for repeat_num in range(0, 99):
        ID_good = good_ants_file_list[ID_num]
        run_ID = starting_index + ID_num*100 + repeat_num
        succeed = 0
        repeat_count = 0
        if os.path.isfile(save_S11_pic_dir + r'\S_parameters_' + str(run_ID) + '.png'): #os.path.isdir(models_path + '\\' + str(run_ID)):
            print(str(run_ID) + 'ran already')
            continue
        while not succeed:
            try:
                cst_time = time.time()
                # create\choose model
                if not os.path.isdir(models_path + '\\' + str(run_ID)):
                    os.mkdir(models_path + '\\' + str(run_ID))
                # find a good antenna to run in different environment:
                if create_new_models:  # for new models
                    dxf_management.CreateDXF(plot=False, run_ID=str(run_ID), project_name=project_name, local_path=local_path, model=model_parameters)
                else:  # for existing models
                    original_model_path = original_models_path + '\\models\\' + str(ID_good)
                    curr_model_path = models_path
                    # copy each dxf file for reconstraction
                    for filename in os.listdir(original_model_path):
                        if filename.endswith('.dxf'):
                            shutil.copy(original_model_path + '\\' + filename, models_path + '\\' + str(run_ID) + '\\' + filename)
                            shutil.copy(original_model_path + '\\' + filename, local_path + project_name + '\\DXF_Model\\'+filename)
                    shutil.copy(original_models_path + '\\model_pictures\\image_' + str(ID_good) + '.png',
                                local_path + project_name + '\\output\\model_pictures\\image_' + str(run_ID) +'.png')
                    # TODO: it's a plaster because of outdated format in the drive (as oppose to the hard-drive)
                    # model_file = original_models_path + '\\models\\' + str(ID_good) + '\\model_parameters.pickle'
                    model_file = r"C:\Users\shg\OneDrive - Tel-Aviv University\AI RF design\model_3_data\output\model_parameters.pickle"
                    file = open(model_file, 'rb')
                    original_model_params = pickle.load(file)
                    file.close()
                    # store original ant id
                    file = open(models_path + '\\' + str(run_ID) + '\\' + 'original_ant_ID.pickle', 'wb')
                    pickle.dump(ID_good, file)
                    file.close()
                print('created DXFs... ',end='')
                # # Delete files in the CST folder to prevent errors
                # target_SPI_folder = local_path +project_name + "\\CST_Model\\Result"
                # for filename in os.listdir(target_SPI_folder):
                #     if filename.endswith('.spi'):
                #         os.remove(local_path +project_name + "\\CST_Model\\Result\\" + filename)

                # Delete files in the CST folder to prevent errors
                target_SPI_folder = final_dir + "\\" + simulation_name + "\\Result"
                for filename in os.listdir(target_SPI_folder):
                    if filename.endswith('.spi'):
                        os.remove(target_SPI_folder + "\\" + filename)
                target_delete_folder = final_dir + "\\" + simulation_name + "\\Model\\3D"
                for filename in os.listdir(target_delete_folder):
                    if filename.endswith('.stp') or filename.endswith('.stl') or filename.endswith('.hlg'):
                        os.remove(target_delete_folder + "\\" + filename)
                target_delete_folder = final_dir + "\\" + simulation_name + "\\Export\\Farfield"
                for filename in os.listdir(target_delete_folder):
                    if filename.endswith('.txt'):
                        os.remove(target_delete_folder + "\\" + filename)
                print('deleted SPI and model files... ', end='')
                # Determine env parameter by adjusting model_parameters values
                if change_env:
                    env_condition_failed = 1
                    while env_condition_failed:
                        for key, value in original_model_params.items():
                            # if key in ['ary','arx','arz','ady','adx','adz','length','width','height']:  #
                            #     if type(model_parameters_limits[key]) == list:
                            #         model_parameters[key] = np.round(np.random.uniform(
                            #             max(model_parameters_limits[key][0],original_model_params[key])
                            #             , model_parameters_limits[key][1]), 1)
                            #         # update the changed variables in environment and save the current run as previous
                            #         continue
                            if type(model_parameters_limits[key]) == list:
                                model_parameters[key] = np.round(np.random.uniform(
                                    model_parameters_limits[key][0]  # original_model_params[key]
                                    , model_parameters_limits[key][1]), 1)
                                model_parameters[key] = np.max([model_parameters[key], 0.1])  # prevent 0 value parameters
                                # update the changed variables in environment and save the current run as previous
                                # print('U-'+key)
                        # to shift from xz model to yz-flipped
                        if (model_parameters['length'] * model_parameters['adz'] * model_parameters['arz'] >=
                                original_model_params['width']*original_model_params['a']*original_model_params['adx']*original_model_params['arx']
                                and
                                model_parameters['height'] * model_parameters['ady'] * model_parameters['ary'] >=
                                original_model_params['length'] * original_model_params['adz'] * original_model_params['arz']):
                            env_condition_failed = 0
                    for key, value in original_model_params.items():
                        if type(model_parameters_limits[key]) == list:
                            VBA_code = r'''Sub Main
                                    StoreParameter("'''+key+'''", '''+str(model_parameters[key])+''')
                                    End Sub'''
                            project.schematic.execute_vba_code(VBA_code)
                """ Rebuild the model and run it """
                project.model3d.full_history_rebuild()  # I just replaced modeler with model3d
                print(' run solver... ',end='')
                project.model3d.run_solver()
                print(' finished simulation... ', end='')
                succeed = 1
            except Exception as error:
                # handle the exception
                print("An exception occurred:", error) # An exception occurred: division by zero
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print('\n\n', exc_type, fname, exc_tb.tb_lineno, '\n\n')
                repeat_count += 1

                print(f"\n\n ------------- FAILED IN #{run_ID:.0f} ------------\n")
                input('Wait')
                time.sleep(300)  # wait for 2 minutes, for the case of temporary license error
                if repeat_count > 3:
                    dxf_management.CreateDXF(plot=False, run_ID=str(run_ID), project_name=project_name,
                                             local_path=local_path, model=3)
                    project.model3d.full_history_rebuild()  # I just replaced modeler with model3d
                    time.sleep(600)  # wait for 20 minutes, for the case of temporary license error
                if repeat_count == 6:
                    input('PRESS ENTER TO CONTINUE ----> ERROR ALERT')
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
        copy_tree(pattern_source_path, results_path + '\\' + str(run_ID))

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
            Dim path As String
            Path = "./Whole_Model_STEP.stp"
            With STEP
                .Reset
                .FileName(path)
                .WriteAll
            End With
        End Sub'''
        project.schematic.execute_vba_code(VBA_code)
        # now copy:
        target_STEP_folder = models_path + '\\' + str(run_ID)
        for filename in os.listdir(STEP_source_path):
            if filename.endswith('.stp'):
                shutil.copy(STEP_source_path + '\\' + filename, target_STEP_folder)
            if filename.endswith('.hlg'):
                shutil.copy(STEP_source_path + '\\' + filename, target_STEP_folder)
        # save parameters of model and environment
        file_name = models_path + '\\' + str(run_ID) + '\\model_parameters.pickle'
        file = open(file_name, 'wb')
        pickle.dump(model_parameters, file)
        file.close()
        # save picture of the S11
        plt.ioff()
        f, ax1 = plt.subplots()
        ax1.plot(freq, 10 * np.log10(np.abs(S11)))
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
        f.savefig(save_S11_pic_dir + r'\S_parameters_' + str(run_ID) + '.png')
        plt.close(f)

        # save the S parameters data
        file_name = results_path + '\\' + str(run_ID) + '\\S_parameters.pickle'
        file = open(file_name, 'wb')
        pickle.dump([S11, freq], file)
        file.close()
        # save the efficiencies data
        file_name = results_path + '\\' + str(run_ID) + '\\Efficiency.pickle'
        file = open(file_name, 'wb')
        pickle.dump([total_efficiency, radiation_efficiency, freq_efficiency], file)
        file.close()

        ants_count += 1
        print('saved results. ')
        print(f'\t RUNTIME for #{run_ID:.0f}:\n\t\t ant #{run_ID:.0f} time: {(time.time()-cst_time)/60:.1f} min \n\t\t overall time: {(time.time()-overall_sim_time)/60/60:.2f} hours')
        print(f'\t\t average time: {(time.time() - overall_sim_time) / ants_count/60: .1f} min')


print(' --------------------------------- \n \t\t\t FINISHED THE RUN \n ---------------------------------')