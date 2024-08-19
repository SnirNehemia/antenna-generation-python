import os
import pickle
import pandas as pd
import numpy as np
import torch
from torchvision.transforms import v2
import matplotlib

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

def farfeild_txt_to_np(txt_file_path:str):
    """
    Methode: parses farfeild text file
    text file header:
        theta [deg.]  Phi   [deg.]  Abs(Grlz)[]   Abs(Theta)[ ]  Phase(Theta)[deg.]  Abs(Phi  )[]  Phase(Phi )[deg.]  Ax.Ratio[]
    """
    assert txt_file_path.endswith('.txt'), "Input file should have a .txt extension."
    df = pd.read_csv(txt_file_path, delim_whitespace=True)
    # f = open(r"C:\Users\shg\Documents\CST_projects\Model3Again\output\results\13092\Efficiency.pickle", 'rb')
    # [a,b,c] = pickle.load(f)
    # f.close()
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
    d_theta = np.max(np.diff(theta_phi, axis=0), axis=0)[0]
    d_phi = np.max(np.diff(theta_phi, axis=0), axis=0)[1]
    farfeild = np.zeros((int(180/d_theta)+1, int(360/d_phi), 6))  # 73 rows for Theta (0 to 180 with 2.5 increments), 144 columns for Phi (0 to 357.5 with 2.5 increments), 6 channels

    # Iterate over each image index and set tensor values
    for i, (theta, phi) in enumerate(theta_phi):
        # Map theta and phi to indices in the tensor
        theta_index = int(theta / d_theta)  # Scale theta to match tensor indices
        phi_index = int(phi / d_phi)  # Scale phi to match tensor indices
        # Set tensor values at corresponding index
        farfeild[theta_index, phi_index, :] = values[i]
    # extract and orginize the abs and phase of E and B andd disgarding Abs(Grlz) and Ax.Ratio

    # get directivity
    theta_abs = farfeild[:,:,1]
    theta_phase = farfeild[:,:,2]
    phi_abs = farfeild[:,:,3]
    phi_phase = farfeild[:,:,4]
    farfeild =  np.stack((theta_abs, phi_abs, theta_phase, phi_phase), axis=-1)

    # print('plot_old')
    # plt.subplot(1, 1, 1)
    # plt.imshow(theta_abs)  # , cmap='gray')
    # plt.title('Absolute Theta')
    # plt.colorbar()
    # plt.show()
    # print('hi')
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

# -----------------------------------------------------------------------------------



def save_ff_images_from_raw_directory(input_folder, output_folder):
    '''
    input_folder: root directory of the numberd ff folderes containing the ff in text format
    output_folder: folder to save the processed ff images
    example:

    root_directory = '/home/avi/Desktop/uni/git/data_sets/model3_all_data/raw/CST_results/'
    ff_image_directory = '/home/avi/Desktop/uni/git/data_sets/farfeild_images_model3_all_data'
    save_ff_images_from_raw_directory(root_directory, ff_image_directory)

    '''

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)


    farfeild = get_farfeild(input_folder)
    farfeild = resize_farfeild(farfeild, (64, 64))
    farfeild = normalize_gain(farfeild[:, :, 0], farfeild[:, :, 1])
    output_path = os.path.join(output_folder, f"{2400}.png")
    # print('saving ff image number: ', output_file_path)

    # Display the image using matplotlib
    tensor_np = farfeild.numpy()
    print('plotting')
    plt.figure(figsize=(8, 4))
    plt.imshow(10*np.log10(tensor_np),extent=[0,360,0,180],cmap='jet',vmin=-15,vmax=5)
    plt.colorbar()  # To show the color scale
    plt.savefig(output_path)
    plt.close()

    # for folder_name in os.listdir(input_folder):
    #     folder_path = os.path.join(input_folder, folder_name)
    #     if os.path.isdir(folder_path) and folder_name.isdigit():
    #         farfeild = get_farfeild(folder_path)
    #         farfeild = resize_farfeild(farfeild, (64, 64))
    #         farfeild = normalize_gain(farfeild[:, :, 0], farfeild[:, :, 1])
    #         output_path = os.path.join(output_folder, f"{folder_name}.png")
    #         # print('saving ff image number: ', output_file_path)
    #
    #         # Display the image using matplotlib
    #         tensor_np = farfeild.numpy()
    #         plt.figure(figsize=(8, 8))
    #         plt.imshow(tensor_np, aspect='auto')
    #         plt.colorbar()  # To show the color scale
    #         plt.savefig(output_path)
    #         plt.close()


def get_farfeild(result_path: str, frequency=2400):
    farfeild_path = result_path + '/farfield (f=' + str(frequency) + ') [1].txt'
    farfield = torch.tensor(farfeild_txt_to_np(farfeild_path))
    return farfield


def resize_farfeild(farfeild, new_shape=(91, 181)):
    # permute to fit v2.Resize format
    permuted_farfeild = farfeild.permute(2, 0, 1)
    resized_farfeild = v2.Resize(new_shape)(permuted_farfeild)
    resized_farfeild = resized_farfeild.permute(1, 2, 0)
    return resized_farfeild


def normalize_gain(abs_theta, abs_phi, gain_pol=None):
    gain = abs_theta + abs_phi
    theta_rad = (torch.linspace(0, 180, 64, dtype=torch.float32) * torch.pi / 180)  # 91
    phi_rad = (torch.linspace(0, 360, 64, dtype=torch.float32) * torch.pi / 180)  # 181
    d_theta = torch.max(torch.diff(theta_rad))
    d_phi = torch.max(torch.diff(phi_rad))
    efficiency = torch.sum(torch.multiply(gain, torch.sin(theta_rad).unsqueeze(1))) * d_theta * d_phi / (4 * torch.pi)
    directivity = gain / efficiency
    if gain_pol == None:
        return directivity
    else:
        directivity_pol = gain_pol / efficiency
        return directivity_pol

# -----------------------------------------------------------------------------------




# farfeild_txt_to_np(r'C:\Users\shg\Documents\CST_projects\Model3Again\output\results\10421\farfield (f=2850) [1].txt')
print('start')
save_ff_images_from_raw_directory(r"C:\Users\snirn\Desktop",r"C:\Users\snirn\Desktop\test")
print('stop')
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
