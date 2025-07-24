#Import libraries
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Define subfolder path for RESPONSE
image_folder = r'D:\Uni Work\Internship\Code\GitHub Repo\Talking-to-Plants-Summer-Work\Code\Offline Processing\Cultivar_assessment_SMFI\SMFI_stack__node_2_period_10_20230811_1433'
response_path = os.path.join(image_folder, 'false_coloured_stack')

# Define subfolder path for REFERENCE
reference_path = r'D:\plantdata\Data\Images\Downloaded from Website\1 - Reference'

# Get data from fluorescence response plot
data_plot_path = os.path.join(response_path, f"fluorescence_response_data.csv")
response = np.genfromtxt(data_plot_path, delimiter='\n')

# Get reference data
data_plot_path = os.path.join(reference_path, f"fluorescence_response_data.csv")
reference = np.genfromtxt(data_plot_path, delimiter='\n')
reference = np.flip(reference)

# Normalise data to reference
# response = response[:-1]
reference = np.flip(reference) # I'm not sure why the array needs to be flipped again but it just does
reference = reference - np.average(reference)
response = response - np.average(response)
scaling_factor = np.amax(reference) / np.amax(response)
response = response * scaling_factor

# Find difference
output = reference - response

size = output.size
x = np.arange(len(output))

plt.figure()    
graph = pd.DataFrame()
graph['samples'] = x
graph['difference'] = response
ax = plt.gca();
graph.plot(ax=ax,x='samples',y='difference',color='blue',kind='line',label='Response',legend=True);
ax.set_title('')
ax.set_xlabel("Sample number"); ax.set_ylabel("Difference")
ax.grid('on');

plt.figure()    
graph = pd.DataFrame()
graph['samples'] = x
graph['difference'] = reference
ax = plt.gca();
graph.plot(ax=ax,x='samples',y='difference',color='blue',kind='line',label='Reference',legend=True);
ax.set_title('')
ax.set_xlabel("Sample number"); ax.set_ylabel("Difference")
ax.grid('on');

# Plot graph
plt.figure()    
graph = pd.DataFrame()
graph['samples'] = x
graph['difference'] = output
ax = plt.gca();
graph.plot(ax=ax,x='samples',y='difference',color='blue',kind='line',label='Difference of Normalised data',legend=True);
ax.set_title('')
ax.set_xlabel("Sample number"); ax.set_ylabel("Difference")
ax.grid('on');
f_plot_name=f"difference_of_normalised_data.jpg"

# Save data and plot in downloads
np.savetxt("difference_data.csv",output,fmt='%f',delimiter='/n')
plt.savefig(f_plot_name);
