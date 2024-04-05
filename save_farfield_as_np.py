import os
import pickle
import pandas as pd
import numpy as np

def farfeild_txt_to_np(txt_file_path:str):
    """
    Methode: parses farfeild text file
    text file header:
        theta [deg.]  Phi   [deg.]  Abs(Grlz)[]   Abs(Theta)[ ]  Phase(Theta)[deg.]  Abs(Phi  )[]  Phase(Phi )[deg.]  Ax.Ratio[]
    """
    assert txt_file_path.endswith('.txt'), "Input file should have a .txt extension."
    df = pd.read_csv(txt_file_path, delim_whitespace=True)
    f = open(r"C:\Users\shg\Documents\CST_projects\Model3Again\output\results\13092\Efficiency.pickle", 'rb')
    [a,b,c] = pickle.load(f)
    f.close()
    # parse the .txt file
    with open(txt_file_path, 'r') as file:
        # Read all lines in the file
        lines = file.readlines()
        data = []
        # Initialize a flag to skip the header
        skip_header = True
        # Iterate over each line
        for line in lines:
            if skip_header or '--' in line:
                skip_header = False
                continue
            # Split the line by whitespace
            columns = line.split()
            # Convert each column value to float and append to the data list
            data.append([float(column) for column in columns])

    # Convert the data list to a NumPy array
    data_array = np.array(data)
    # Extract phi and theta columns
    theta_phi = data_array[:,:2]
    values = data_array[:, 2:]
    # Initialize a tensor with zeros
    farfeild = np.zeros((73, 144, 6))  # 73 rows for Theta (0 to 180 with 2.5 increments), 144 columns for Phi (0 to 357.5 with 2.5 increments), 6 channels

    # Iterate over each image index and set tensor values
    for i, (theta, phi) in enumerate(theta_phi):
        # Map theta and phi to indices in the tensor
        theta_index = int(theta / 2.5)  # Scale theta to match tensor indices
        phi_index = int(phi / 2.5)  # Scale phi to match tensor indices
        # Set tensor values at corresponding index
        farfeild[theta_index, phi_index, :] = values[i]
    # extract and orginize the abs and phase of E and B andd disgarding Abs(Grlz) and Ax.Ratio

    # get directivity
    theta_abs = farfeild[:,:,1]
    theta_phase = farfeild[:,:,2]
    phi_abs = farfeild[:,:,3]
    phi_phase = farfeild[:,:,4]
    farfeild =  np.stack((theta_abs, phi_abs, theta_phase, phi_phase), axis=-1)
    import matplotlib
    matplotlib.use('Qt5Agg')
    import matplotlib.pyplot as plt
    plt.subplot(1, 1, 1)
    plt.imshow(theta_abs)  # , cmap='gray')
    plt.title('Absolute Theta')
    plt.colorbar()
    plt.show()
    print('hi')
    return farfeild

def display_farfeild(farfeild, path_to_save_image):
    """
    the farfeild has shape [1,91,181,4]
    where the first 4 chanels of axes 3 are the abs_theta, abs_phi, phase_theta, phase_phi
    """

    # Extracting channels
    abs_theta = farfeild[0, :, :, 0]
    abs_phi = farfeild[0, :, :, 1]
    phase_theta = farfeild[0, :, :, 2]
    phase_phi = farfeild[0, :, :, 3]

    # Plotting and saving figures
    plt.figure(figsize=(10, 10))

    plt.subplot(2, 2, 1)
    plt.imshow(abs_theta)#, cmap='gray')
    plt.title('Absolute Theta')
    plt.colorbar()

    plt.subplot(2, 2, 2)
    plt.imshow(abs_phi)#, cmap='gray')
    plt.title('Absolute Phi')
    plt.colorbar()

    plt.subplot(2, 2, 3)
    plt.imshow(phase_theta)#, cmap='gray')
    plt.title('Phase Theta')
    plt.colorbar()

    plt.subplot(2, 2, 4)
    plt.imshow(phase_phi)#, cmap='gray')
    plt.title('Phase Phi')
    plt.colorbar()

    # Adjust layout
    plt.tight_layout()

    # Save the figure
    plt.savefig(path_to_save_image)

    # Show the figures
    plt.show()

# farfeild_txt_to_np(r'C:\Users\shg\Documents\CST_projects\Model3Again\output\results\10421\farfield (f=2850) [1].txt')
farfeild_txt_to_np(r'C:\Users\shg\Documents\CST_projects\Model3Again\output\results\13092\farfield (f=2850) [1].txt')
# import pickle
# import matplotlib; matplotlib.use('Qt5Agg')
# import matplotlib.pyplot as plt
# import numpy as np
# # plt.show(block=True)
# f = open(r"C:\Users\shg\Documents\CST_projects\Model3Again\output\results\10006\Efficiency.pickle",'rb')
# [a,b,c] = pickle.load(f)
# f.close()
# plt.plot(c,np.abs(a))
# plt.show()
# plt.ylim([0,1])
