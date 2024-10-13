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
import parametric_ant_utils
from matplotlib import pyplot as plt
from datetime import datetime

""" define run parameters """
# --- define local path and project name
# project_name = r'Model3Again'
simulation_name = 'CST_Model_better_parametric'
project_name = r'simplified'
# local_path = "C:\\Users\\shg\\Documents\\CST_projects\\"
# local_path = 'C:\\Users\\Public\\'
# local_path = 'C:\\Users\\Snir\\OneDrive - Tel-Aviv University\\Documents\\local_model_3_path\\'
local_path = 'G:\\local_model_3_path\\'
# --- the following lines is relevant when we have a path to pre-defined geometries (in DXF format)
create_new_models = 1  # 1 for creating new models, 0 to use existing ones
original_models_path = r'D:\model_3_data\output'  # path to existing models output folder
# --- choose whether to use fix or changed environment
change_env = 1

model_parameters = {
    'type':3,
    'plane':'yz-flipped',#changetoyz-flipped
    #parametersthatchangeboththeantennaandtheenviroment
    'width':10,#coordinatealongthex(red)axis
    'height': 50,
    'length':60,#coordinatealongthev(green)axis
    'thickness':1,
    'adx':0.9,
    'arx':0.9,
    'ady': 0.9,
    'ary': 0.85,
    'adz':0.9,
    'arz':0.9,
    'a':0.6,
    'b':0.8,
    'c':0.8,
    'bdx':1,
    'brx':0.2,
    'bdy':0.8,
    'bry':0.75,
    'bdz':0.8,
    'brz':0.75,
    'cdx':1,
    'crx':0.3,
    'cdy':0.8,
    'cry':0.75,
    'cdz':0.8,
    'crz':0.75,
    'ddx':1,
    'drx':1,
    'ddy':0.8,
    'dry':0.75,
    'ddz':1,
    'drz':1,
    'feed_length':2
}

## --- define the model parameters limits for randomization:
model_parameters_limits = model_parameters.copy()
for key, value in model_parameters_limits.items():
    if type(value) != str and key != 'type':
        if model_parameters_limits[key]<=1:
            model_parameters_limits[key] = [0, 1]
# EXAMPLE for a costum parameter
# model_parameters_limits['adx'] = [0.2,0.8]
model_parameters_limits['length'] = [50,200]
model_parameters_limits['width'] = [10,100]
model_parameters_limits['height'] = [50, 200]
# model_parameters_limits['ady'] = [0.4, 1]
# model_parameters_limits['ary'] = [0.4, 1]
# model_parameters_limits['adz'] = [0.4, 1]
# model_parameters_limits['arz'] = [0.4, 1]
model_parameters_limits['thickness'] = 1

ant_parameters_names = parametric_ant_utils.get_parameters_names()


""" create all tree folder paths """
# --- from here on I define the paths based on the manually defined project and local path ---
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
starting_index = 110000
for run_ID_local in range(0, 10000):  #15001-starting_index-1 % 15067 is problematic!
    run_ID = starting_index + run_ID_local
    if os.path.isfile(save_S11_pic_dir + r'\S_parameters_' + str(
            run_ID) + '.png'):  # os.path.isdir(models_path + '\\' + str(run_ID)):
        print(str(run_ID) + ' ran already')
        continue
    print(str(run_ID) + ' running')
    succeed = 0
    repeat_count = 0
    print('time is: %s' % datetime.now())
    while not succeed:
        cst_time = time.time()
        # create\choose model
        if not os.path.isdir(models_path + '\\' + str(run_ID)):
            os.mkdir(models_path + '\\' + str(run_ID))
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
        if change_env:
            np.random.seed(run_ID)
            # randomize environment
            valid_env = 0
            while not valid_env:
                for key, value in model_parameters_limits.items():
                    if type(value) == list:
                        model_parameters[key] = np.round(np.random.uniform(value[0],value[1]),1)
                        # update the changed variables in environment and save the current run as previous
                        model_parameters[key] = np.max([model_parameters[key], 0.1])
                if (model_parameters['length'] * model_parameters['adz'] * model_parameters['arz'] / 2 > 50 and
                    model_parameters['height'] * model_parameters['ady'] * model_parameters['ary'] >50):
                    valid_env = 1
            # update model
            for key, value in model_parameters_limits.items():
                if type(value) != str and key != 'type':
                    # print('U-'+key)
                    VBA_code = r'''Sub Main
                            StoreParameter("'''+key+'''", '''+str(model_parameters[key])+''')
                            End Sub'''
                    project.schematic.execute_vba_code(VBA_code)
        if create_new_models: # for new models
            ant_parameters = parametric_ant_utils.randomize_ant(ant_parameters_names,model_parameters,seed=run_ID)
            for key, value in ant_parameters.items():
                VBA_code = r'''Sub Main
                        StoreParameter("'''+key+'''", '''+str(value)+''')
                        End Sub'''
                project.schematic.execute_vba_code(VBA_code)
            # save picture of the antenna
            parametric_ant_utils.save_figure(model_parameters, ant_parameters, local_path + project_name, run_ID)
            # plt.ioff()
            # f, ax1 = plt.subplots()
            # wings = ['w1', 'w2', 'q1', 'q2']
            # Sz = (model_parameters['length'] * model_parameters['adz']* model_parameters['arz']/2-ant_parameters['w']/2
            #       - model_parameters['feed_length']/2)
            # Sy = model_parameters['height'] * model_parameters['ady']* model_parameters['ary']-ant_parameters['w']
            # data_linewidth_plot([0,0], [model_parameters['feed_length']/2,-model_parameters['feed_length']/2],
            #                         linewidth=ant_parameters['w'], alpha=0.4, color='r')
            # for wing in wings:
            #     z = [model_parameters['feed_length']/2]
            #     y = [0,0]
            #     for i1 in range(3):
            #         z.append(Sz * ant_parameters[f'{wing}z{i1 + 1:d}'])
            #         z.append(Sz * ant_parameters[f'{wing}z{i1 + 1:d}'])
            #         y.append(Sy * ant_parameters[f'{wing}y{i1 + 1:d}'])
            #         y.append(Sy * ant_parameters[f'{wing}y{i1 + 1:d}'])
            #     y.pop()
            #     data_linewidth_plot(y, z,
            #                             linewidth=ant_parameters['w'], alpha=0.4, color='b')
            # wings = ['w3', 'q3']
            # for wing in wings:
            #     z = [model_parameters['feed_length'] / 2]
            #     y = [0, 0]
            #     z.append(Sz * ant_parameters[f'{wing}z{1:d}'])
            #     z.append(Sz * ant_parameters[f'{wing}z{1:d}'])
            #     y.append(Sy * ant_parameters[f'{wing}y{1:d}'])
            #     data_linewidth_plot(y, z,
            #                         linewidth=ant_parameters['w'], alpha=0.4, color='b')
            #     plt.title('dimensions in mm')
            #     plt.show(block=False)
            #     f.savefig(local_path + project_name + '\\output\\model_pictures\\image_' + str(run_ID)+'.png')
            #     plt.close(f)
        else: # for existing models
            print('not supported yet')
            # original_model_path = original_models_path + '\\models\\' + str(run_ID_local)
            # curr_model_path = models_path
            # for filename in os.listdir(original_model_path):
            #     if filename.endswith('.dxf'):
            #         shutil.copy(original_model_path + '\\' + filename, models_path + '\\' + str(run_ID))
            #         shutil.copy(original_model_path + '\\' + filename, local_path + project_name + '\\DXF_Model')
            # shutil.copy(original_models_path + '\\model_pictures\\image_' + str(run_ID_local)+'.png',
            #             local_path + project_name + '\\output\\model_pictures\\image_' + str(run_ID)+'.png')
        print('created antenna... ',end='')
        """ Rebuild the model and run it """
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
            repeat_count += 1
            time.sleep(2)  # wait for 1 minutes, for the case of temporary license error
            os.system('taskkill /im "CST DESIGN ENVIRONMENT_AMD64.exe" /F')
            time.sleep(30)  # wait for 0.5 minutes, for the case of temporary license error
            print(f"\n\n ------------- FAILED IN #{run_ID:.0f} ------------\n")
            cst_instance = cst.interface.DesignEnvironment()
            project = cst.interface.DesignEnvironment.open_project(cst_instance, project_path)

            results = cst.results.ProjectFile(project_path, allow_interactive=True)

            if repeat_count > 2:
                ant_parameters = parametric_ant_utils.randomize_ant(ant_parameters_names,model_parameters)
                for key, value in ant_parameters.items():
                    VBA_code = r'''Sub Main
                                        StoreParameter("''' + key + '''", ''' + str(value) + ''')
                                        End Sub'''
                    project.schematic.execute_vba_code(VBA_code)
                # save picture of the antenna
                parametric_ant_utils.save_figure(model_parameters, ant_parameters, local_path + project_name, run_ID)
                project.model3d.full_history_rebuild()  # I just replaced modeler with model3d
                time.sleep(30)  # wait for 20 minutes, for the case of temporary license error
            if repeat_count == 6:
                input('PRESS ENTER TO CONTINUE ----> ERROR ALERT')
        print('counts repeated : ',repeat_count)

    """ access results """
    if not succeed:
        print('Did not succeed, continue to next iteration.')
        continue # will immediately start next id
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
    target_STEP_folder = models_path + '\\' + str(run_ID)
    for filename in os.listdir(STEP_source_path):
        if filename.endswith('.stp'):
            shutil.copy(STEP_source_path + '\\' + filename, target_STEP_folder)
        if filename.endswith('.stl'):
            shutil.copy(STEP_source_path + '\\' + filename, target_STEP_folder)
        if filename.endswith('.hlg'):
            shutil.copy(STEP_source_path + '\\' + filename, target_STEP_folder)
    # save parameters of model and environment
    file_name = models_path + '\\' + str(run_ID) + '\\model_parameters.pickle'
    file = open(file_name, 'wb')
    pickle.dump(model_parameters, file)
    file.close()
    file_name = models_path + '\\' + str(run_ID) + '\\ant_parameters.pickle'
    file = open(file_name, 'wb')
    pickle.dump(ant_parameters, file)
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