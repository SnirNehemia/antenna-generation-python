import os
import sys
sys.path.append(r"C:\Program Files\Dassault Systemes\B426CSTEmagConnector\CSTStudio\AMD64\python_cst_libraries")
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
""" open the CST project that we already created"""

# project_name = r'phase_2\ALL_Model_1_1_layer'
# project_name_DXF = r'phase_2\ALL_Model_1_1_layer\DXF_Model_1_1_layer'
# # local_path = "C:\\Users\\shg\\OneDrive - Tel-Aviv University\\Documents\\CST_projects\\"
# project_name = r'test_performance_local'
# local_path = "C:\\Users\\shg\\Documents\\CST_projects\\"

project_name = r'Model3Again'
local_path = "C:\\Users\\shg\\Documents\\CST_projects\\"

project_path = local_path +project_name + "\\CST_Model.cst"
results_path = local_path+project_name+"\\output\\results"
# dxf_directory = "C:\\Users\\shg\\OneDrive - Tel-Aviv University\\Documents\\CST_projects\\"+project_name_DXF
models_path =  local_path +project_name+"\\output\\models"
pattern_source_path = (local_path+project_name+"\\CST_Model" +
                  r'\Export\Farfield')
save_S11_pic_dir = local_path+project_name+"\\output\\S11_pictures"
STEP_source_path = (local_path+project_name+"\\CST_Model" +
                  r'\Model\3D')

file_names = ['Antenna_PEC', 'Antenna_Feed', 'Antenna_Feed_PEC',
              'Env_PEC', 'Env_FR4', 'Env_Polycarbonate', 'Env_Vacuum']

cst_instance = cst.interface.DesignEnvironment()
project = cst.interface.DesignEnvironment.open_project(cst_instance, project_path)

results = cst.results.ProjectFile(project_path, allow_interactive=True)


""" Generate the DXFs """

# run the function that is currently called 'main' to generate the cst file
overall_sim_time = time.time()
ants_count = 0
for run_ID in range(3987, 3989):
    succeed = 0
    repeat_count = 0
    while not succeed:
        try:
            cst_time = time.time()
            if not os.path.isdir(models_path + '\\' + str(run_ID)):
                os.mkdir(models_path + '\\' + str(run_ID))
            dxf_management.CreateDXF(plot=False, run_ID=str(run_ID), project_name=project_name, local_path=local_path, model=3)

            print('created DXFs... ',end='')

            target_SPI_folder = local_path +project_name + "\\CST_Model\\Result"
            for filename in os.listdir(target_SPI_folder):
                if filename.endswith('.spi'):
                    os.remove(local_path +project_name + "\\CST_Model\\Result\\" + filename)
            print('deleted SPI... ', end='')

            """ Rebuild the model and run it """
            project.model3d.full_history_rebuild()  # I just replaced modeler with model3d
            print(' run solver... ',end='')
            project.model3d.run_solver()
            print(' finished simulation... ', end='')
            succeed = 1
        except Exception as error:
            # handle the exception
            print("An exception occurred:", error) # An exception occurred: division by zero
            repeat_count += 1

            print(f"\n\n ------------- FAILED IN #{run_ID:.0f} ------------\n")
            input('Wait')
            time.sleep(120)  # wait for 2 minutes, for the case of temporary license error
            if repeat_count == 8:
                dxf_management.CreateDXF(plot=False, run_ID=str(run_ID), project_name=project_name,
                                         local_path=local_path, model=3)
                time.sleep(1200)  # wait for 20 minutes, for the case of temporary license error
            if repeat_count == 10:
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
    total_efficiency = np.array(radiation_efficiency_results.get_ydata())
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
    plt.show()
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