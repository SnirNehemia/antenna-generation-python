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
import pickle
import time
import dxf_management
""" open the CST project that we already created"""


project_path = r"C:\Users\shg\OneDrive - Tel-Aviv University\Documents\CST_projects\phase_2\rect_dxf\rect_test.cst"
results_path = r'C:\Users\shg\OneDrive - Tel-Aviv University\Documents\CST_projects\phase_2\rect_dxf\output\results'
models_path = r'C:\Users\shg\OneDrive - Tel-Aviv University\Documents\CST_projects\phase_2\rect_dxf\output\models'
pattern_source_path = (r'C:\Users\shg\OneDrive - Tel-Aviv University\Documents\CST_projects\phase_2\rect_dxf\rect_test'
                  r'\Export\Farfield')

cst_instance = cst.interface.DesignEnvironment()
project =cst.interface.DesignEnvironment.open_project(cst_instance, project_path)

results = cst.results.ProjectFile(project_path, allow_interactive=True)


""" Generate the DXFs """

# run the function that is currently called 'main' to generate the cst file
overall_sim_time = time.time()
for run_ID in range(10):
    cst_time = time.time()
    # run_ID = 1
    if not os.path.isdir(models_path + '\\' + str(run_ID)):
        os.mkdir(models_path + '\\' + str(run_ID))
    dxf_management.CreateDXF(plot=False, run_ID=str(run_ID))
    print('created DXFs... ',end='')

    """ Rebuild the model and run it """

    project.model3d.full_history_rebuild()  # I just replaced modeler with model3d
    project.model3d.run_solver()

    """ access results """
    S_results = results.get_3d().get_result_item(r"1D Results\S-Parameters\S1,1")
    S11 = np.array(S_results.get_ydata())
    freq = np.array(S_results.get_xdata())

    # the farfield will be exported using post-proccessing methods and it should be moved to a designated location and renamed
    print('got results... ',end='')

    # file_name = 'Radiation_' + str(run_ID)
    copy_tree(pattern_source_path, results_path + '\\' + str(run_ID))
    # os.mkdir(save_path + '\\' + str(run_ID))

    file_name = results_path + '\\' + str(run_ID) + '\\S_parameters.pickle'   # TODO: determine how it should be saved
    file = open(file_name, 'wb')
    pickle.dump([S11, freq], file)
    file.close()
    print('saved results. ')
    print(f'\t RUNTIME is:\n\t\t {run_ID:.0} ant time: {time.time()-cst_time:.1} sec \n\t\t overall time: {(time.time()-overall_sim_time)/60:.1} min')

