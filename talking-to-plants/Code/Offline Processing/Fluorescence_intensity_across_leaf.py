import os
import numpy as np
from PIL import Image

# Function to sort the recorded frames for a particular frequency from a folder on PC
def sortByFrameNumber(imageName):
    components = imageName.split("-")
    frameName = components[2]
    frameNumber = int((frameName.split(".")[0]).removeprefix('frameno'))
    return frameNumber

# Define image folder
image_folder = r'D:\OneDrive_1_2-9-2023\Image'

# Get all .png files from that folder
filenames = [f for f in os.listdir(image_folder) if f.endswith('.jpeg')]

# Total number of images recorded for a particular frequency
total_images = len(filenames)
print(total_images)
f = os.path.join(image_folder, filenames[0])
our_images = np.array(Image.open(f))
our_images = our_images.astype(float) / 255
rows, columns = our_images.shape
print(rows)
print(columns)
row1 = int(rows/2)
print(row1)
np.transpose(our_images[row1,:])
print(our_images[row1,:])
    
    
