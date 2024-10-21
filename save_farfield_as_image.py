import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
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

from numpy import matlib

def save_ff_images_from_raw_directory(input_folder, output_folder, ID=0, freq=2400, mode='both'):
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

    image_3d_name = f"3D_{ID:d}_{freq:d}_ff.png"
    image_2d_name = f"{ID:d}_{freq:d}_ff.png"

    farfeild = get_farfeild(input_folder,frequency=freq)
    farfeild = resize_farfeild(farfeild, (64, 64))
    farfeild = normalize_gain(farfeild[:, :, 0], farfeild[:, :, 1])
    output_path = os.path.join(output_folder, image_2d_name)
    # print('saving ff image number: ', output_file_path)

    # Display the image using matplotlib
    tensor_np = farfeild.numpy()
    if mode == '2d' or mode == 'both':
        plt.figure(figsize=(8, 4))
        plt.imshow(10*np.log10(tensor_np),extent=[0,360,0,180],cmap='jet',vmin=-15,vmax=5)
        plt.colorbar()  # To show the color scale
        plt.savefig(output_path)
        plt.close()

    if mode == '3d' or mode == 'both':
        phi = np.linspace(0,360,64)
        phi = matlib.repmat(phi,64,1)
        theta = np.linspace(0, 180, 64)
        theta = matlib.repmat(theta, 64, 1)
        theta = theta.transpose()

        plot_3d(10*np.log10(tensor_np),phi,theta,output_folder,image_3d_name)

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

import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as Axes3D
from numpy import sin,cos,pi, exp,log
from tqdm import tqdm
# import mpl_toolkits.mplot3d.axes3d as Axes3D
from matplotlib import cm, colors

def plot_3d(power,phi,theta,output_folder,image_name):
    null = 15
    phi = phi*np.pi/180
    theta = theta * np.pi / 180
    power = power+null
    X = power*sin(phi)*sin(theta)
    Y = power*cos(phi)*sin(theta)
    Z = power*cos(theta)

    # X = X.reshape([72,37])
    # Y = Y.reshape([72,37])
    # Z = Z.reshape([72,37])

    def interp_array(N1):  # add interpolated rows and columns to array
        N2 = np.empty([int(N1.shape[0]), int(2*N1.shape[1] - 1)])  # insert interpolated columns
        N2[:, 0] = N1[:, 0]  # original column
        for k in range(N1.shape[1] - 1):  # loop through columns
            N2[:, 2*k+1] = np.mean(N1[:, [k, k + 1]], axis=1)  # interpolated column
            N2[:, 2*k+2] = N1[:, k+1]  # original column
        N3 = np.empty([int(2*N2.shape[0]-1), int(N2.shape[1])])  # insert interpolated columns
        N3[0] = N2[0]  # original row
        for k in range(N2.shape[0] - 1):  # loop through rows
            N3[2*k+1] = np.mean(N2[[k, k + 1]], axis=0)  # interpolated row
            N3[2*k+2] = N2[k+1]  # original row
        return N3

    interp_factor=1

    for counter in range(interp_factor):  # Interpolate between points to increase number of faces
        X = interp_array(X)
        Y = interp_array(Y)
        Z = interp_array(Z)

    N = np.sqrt(X**2 + Y**2 + Z**2)
    Rmax = np.max(N)
    N = N/Rmax

    fig = plt.figure(figsize=(10,8))

    ax = fig.add_subplot(1,1,1, projection='3d')
    axes_length = 0.65
    ax.plot([0, axes_length*Rmax], [0, 0], [0, 0], linewidth=2, color='red')
    ax.plot([0, 0], [0, axes_length*Rmax], [0, 0], linewidth=2, color='green')
    ax.plot([0, 0], [0, 0], [0, axes_length*Rmax], linewidth=2, color='blue')

    # Find middle points between values for face colours
    N = interp_array(N)[1::2,1::2]

    mycol = cm.jet(N)

    surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, facecolors=mycol, linewidth=0.5, antialiased=True, shade=False,vmin=-15,vmax=5)  # , alpha=0.5, zorder = 0.5)

    ax.set_xlim([-axes_length*Rmax, axes_length*Rmax])
    ax.set_ylim([-axes_length*Rmax, axes_length*Rmax])
    ax.set_zlim([-axes_length*Rmax, axes_length*Rmax])

    m = cm.ScalarMappable(cmap=cm.jet)
    m.set_array(power-null)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    fig.colorbar(m,ax=plt.gca())#m, shrink=0.8)
    ax.view_init(azim=300, elev=30)
    plt.savefig(os.path.join(output_folder, image_name))
    plt.close()
    # plt.show()

def plot_3d_test(filepath,output_folder):

    vals_theta = []
    vals_phi = []
    vals_r = []
    with open(filepath) as f:
        for s in f.readlines()[2:]:
            vals_theta.append(float(s.strip().split()[0]))
            vals_phi.append(float(s.strip().split()[1]))
            vals_r.append(float(s.strip().split()[2]))

    theta1d = vals_theta
    theta = np.array(theta1d) / 180 * pi;

    phi1d = vals_phi
    phi = np.array(phi1d) / 180 * pi;

    power1d = vals_r
    power = 10*np.log10(np.array(power1d))
    X = power*sin(phi)*sin(theta)
    Y = power*cos(phi)*sin(theta)
    Z = power*cos(theta)

    X = X.reshape([72,37])
    Y = Y.reshape([72,37])
    Z = Z.reshape([72,37])

    def interp_array(N1):  # add interpolated rows and columns to array
        N2 = np.empty([int(N1.shape[0]), int(2*N1.shape[1] - 1)])  # insert interpolated columns
        N2[:, 0] = N1[:, 0]  # original column
        for k in range(N1.shape[1] - 1):  # loop through columns
            N2[:, 2*k+1] = np.mean(N1[:, [k, k + 1]], axis=1)  # interpolated column
            N2[:, 2*k+2] = N1[:, k+1]  # original column
        N3 = np.empty([int(2*N2.shape[0]-1), int(N2.shape[1])])  # insert interpolated columns
        N3[0] = N2[0]  # original row
        for k in range(N2.shape[0] - 1):  # loop through rows
            N3[2*k+1] = np.mean(N2[[k, k + 1]], axis=0)  # interpolated row
            N3[2*k+2] = N2[k+1]  # original row
        return N3

    interp_factor=1

    for counter in range(interp_factor):  # Interpolate between points to increase number of faces
        X = interp_array(X)
        Y = interp_array(Y)
        Z = interp_array(Z)

    N = np.sqrt(X**2 + Y**2 + Z**2)
    Rmax = np.max(N)
    N = N/Rmax

    fig = plt.figure(figsize=(10,8))

    ax = fig.add_subplot(1,1,1, projection='3d')
    axes_length = 0.65
    ax.plot([0, axes_length*Rmax], [0, 0], [0, 0], linewidth=2, color='red')
    ax.plot([0, 0], [0, axes_length*Rmax], [0, 0], linewidth=2, color='green')
    ax.plot([0, 0], [0, 0], [0, axes_length*Rmax], linewidth=2, color='blue')

    # Find middle points between values for face colours
    N = interp_array(N)[1::2,1::2]

    mycol = cm.jet(N)

    surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, facecolors=mycol, linewidth=0.5, antialiased=True, shade=False)  # , alpha=0.5, zorder = 0.5)

    ax.set_xlim([-axes_length*Rmax, axes_length*Rmax])
    ax.set_ylim([-axes_length*Rmax, axes_length*Rmax])
    ax.set_zlim([-axes_length*Rmax, axes_length*Rmax])

    m = cm.ScalarMappable(cmap=cm.jet)
    m.set_array(power)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    fig.colorbar(m, shrink=0.8)
    ax.view_init(azim=300, elev=30)
    plt.savefig(os.path.join(output_folder, f"{2400}3d.png"))
    plt.close()
    # plt.show()

import time
start_time = time.time()


# text_path = r"C:\Users\shg\Desktop\farfield (f=2400) [1].txt"
# for i in range(100000):
mode = '2d'
freq=2400
start = int(70e3)
stop = int(100e3)
for ID in range(start,stop):
    raw_results_folder = r'E:\model_3_data\output\results'
    destination_folder = r'E:\model_3_data\output\radiation_pattern_2400'
    ID_folder = os.path.join(raw_results_folder,str(ID))
    if mode =='3d' or mode=='both': image_name = f"3D_{ID:d}_{freq:d}_ff.png"
    if mode =='2d': image_name = f"{ID:d}_{freq:d}_ff.png"

    if os.path.isdir(ID_folder) and not(os.path.isfile(os.path.join(destination_folder,image_name))):
        save_ff_images_from_raw_directory(ID_folder,destination_folder,ID=ID,freq=freq,mode=mode)
    print(f'done with {ID:d}')
    # save_ff_images_from_raw_directory(r"C:\Users\shg\Desktop",r"C:\Users\shg\Desktop\farfield_test") # for testing!!!!
    if ID % 10 == 0:
        print(f"--- {(time.time() - start_time):.1f} seconds | avg time = {(time.time() - start_time)/(ID-start+1):2f} ---")
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
