# Import libraries
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import numpy.ma as ma

plt.rc('figure', max_open_warning = 0)

# Function to sort the recorded frames for a particular frequency from a folder on PC
def sortByFrameNumber(imageName):
    #print(imageName)
    #components = imageName.split("-")
    #frameName = components[2]
    #print(frameName)
    #frameName = frameName[7:]
    #frameNumber = int((frameName.split(".")[0]))
    #print(frameNumber)
    components = imageName.split(".")
    frameNumber = int(components[0])
    print(frameNumber)
    return frameNumber

# Define image folder
image_folder = r'D:\plantdata\Data\Images\Downloaded from Camera\6 - 15 dB 300 us'

# Get all .jpg files from that folder
filenames = [f for f in os.listdir(image_folder) if f.endswith('.jpg')]

# Sort files by frame number - i.e. in the order they've been taken
filenames.sort(key = sortByFrameNumber)

print(filenames)

# Total number of images recorded for a particular frequency
total_images = len(filenames)

# Define some empty data structures to be used for image stack values

# This holds fluorescence values
pixel_value = np.arange(1, total_images+1)
pixel_value = pixel_value.astype(float)

# This holds the samples indices
samples = np.arange(1, total_images+1)

our_images_series = np.zeros((20, 20, total_images))

# Make a folder in the current directory for the respective false coloured images
subfolder_path = os.path.join(image_folder, 'false_coloured_stack')
os.makedirs(subfolder_path, exist_ok=True)


for n in range(total_images):
    # Load images from folder one-by-one in the empty data structure
    f = os.path.join(image_folder, filenames[n])
    our_images = np.array(Image.open(f))
    # Normalise
    our_images = our_images.astype(float) / 255

    # Display false coloured image and the legend
    plt.figure()
    plt.imshow(our_images)
    plt.colorbar()
    # Save false coloured image in the previously defined folder and index it accordingly
    f_name=f"false_colour_{n+1}.jpg"
    output_false_colour_path = os.path.join(subfolder_path, f_name)
    plt.savefig(output_false_colour_path)
    
    # Define a cluster of pixels as your "sub-image" - region of interest
    sub_image = our_images[60:80, 60:80]
    
    # Add it to your stack of "sub-images"
    our_images_series[:, :, n] = sub_image
    
    # Take the mean value of those pixels
    mean_intensity = ma.mean(our_images_series[:, :, n])
    imageMean = ma.mean(our_images[: ,: ])
    
    print("Sub Image Mean: " + str(mean_intensity) + ", Image Mean: " + str(imageMean) + ", Img No: " + str(n))
    
    # Store them in an array to be used for the fluorescence respnse plot
    pixel_value[n] = mean_intensity
    #print(pixel_value)
    
plt.figure()    
# Define a Pandas dataframe to more easily view the fluorescence response
graph = pd.DataFrame()
# Sample number on x-axis
graph['samples'] = samples
# Averaged value of those pixels on the y-axis - the fluorescence response of that region 
PlotData = pixel_value#[::-1]
graph['fluorescence'] = PlotData
ax = plt.gca();
graph.plot(ax=ax,x='samples',y='fluorescence',color='green',kind='line',label='SMFI',legend=True);
ax.set_title('')
ax.set_xlabel("Sample number"); ax.set_ylabel("Light Intensity (0-1)")
ax.grid('on');
f_plot_name=f"fluorescence_response_plot.jpg"

# Save a copy of fluorescence response data to a .csv file, so it can be used for subtraction
data_plot_path = os.path.join(subfolder_path, f"fluorescence_response_data.csv")
np.savetxt(data_plot_path,PlotData,fmt='%f',delimiter='/n')

# Save fluorescence plot in the same folder as the false coloured images
output_plot_path = os.path.join(subfolder_path, f_plot_name)
plt.savefig(output_plot_path);

