import os
import sys
sys.path.append(r"C:\Program Files\Dassault Systemes\B426CSTEmagConnector\CSTStudio\AMD64\python_cst_libraries")
import cst
import shutil
import cst.interface
import cst.results
import time

project_file = r'C:\Users\shg\Documents\CST_projects\STEP_correction\CST_STEP_correction.cst'
project_path = r'C:\Users\shg\Documents\CST_projects\STEP_correction'
STEP_modified_path = r'C:\Users\shg\Documents\CST_projects\STEP_correction\CST_STEP_correction\Model\3D'
STEP_origin_path = r'C:\Users\shg\Documents\CST_projects\Model3Again\output\models'
STEP_origin_name = 'Antenna_STEP'
backup_path = r'C:\Users\shg\Documents\CST_projects\Model3Again\backup'
file_names = ['Antenna_PEC', 'Antenna_Feed', 'Antenna_Feed_PEC',
              'Env_PEC', 'Env_FR4', 'Env_Polycarbonate', 'Env_Vacuum']

cst_instance = cst.interface.DesignEnvironment()
project = cst.interface.DesignEnvironment.open_project(cst_instance, project_file)

# run_ID = 3234
for run_ID in range(555,3234):
    print('starting ' + str(run_ID) + '...',end='')
    # step 1: copy the step file
    target_STEP_folder = STEP_origin_path + '\\' + str(run_ID)
    shutil.copy(target_STEP_folder + '\\' + STEP_origin_name + '.stp', project_path)
    shutil.copy(target_STEP_folder + '\\' + STEP_origin_name + '.hlg', project_path)

    shutil.copy(target_STEP_folder + '\\' + STEP_origin_name + '.stp', backup_path + '\\' + str(run_ID) + '_STEP.stp')
    shutil.copy(target_STEP_folder + '\\' + STEP_origin_name + '.hlg', backup_path + '\\' + str(run_ID) + '_STEP.hlg')
    # step 2: load the new model
    project.model3d.full_history_rebuild()

    # step 3: export the correct STEP files
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
        try:
            project.schematic.execute_vba_code(VBA_code)
        except:
            time.sleep(5)
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
    # step 4: copy the new step file to the right folder and delete the previous model
    # delete previous models
    for filename in os.listdir(target_STEP_folder):
        if filename.endswith('.stp'):
            os.remove(target_STEP_folder + '\\' + filename)
        if filename.endswith('.hlg'):
            os.remove(target_STEP_folder + '\\' + filename)
    # copy modified models
    for file_name in file_names:
        shutil.copy(STEP_modified_path + '\\' + file_name + '_STEP.stp', target_STEP_folder)
        shutil.copy(STEP_modified_path + '\\' + file_name + '_STEP.hlg', target_STEP_folder)
    file_name = 'Whole_Model'
    shutil.copy(STEP_modified_path + '\\' + file_name + '_STEP.stp', target_STEP_folder)
    shutil.copy(STEP_modified_path + '\\' + file_name + '_STEP.hlg', target_STEP_folder)
    print('finished ' + str(run_ID))

