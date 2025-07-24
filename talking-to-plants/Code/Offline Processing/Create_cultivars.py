# Import Libraries
import os
import time
import pandas as pd
import base64
from PIL import Image
from io import BytesIO


def create_directory_with_timestamp():
    try:
        # Get current timestamp
        #timestamp = time.strftime("%Y%m%d_%H%M%S")

        # Create directory name with timestamp
        directory_name = f"Cultivar_assessment_SMFI"

        # Create the directory
        os.mkdir(directory_name)
        
        print(f"Directory '{directory_name}' created successfully.")
    except OSError as e:
        print(f"An error occurred while creating the directory: {e}")
        
    directory_path = os.path.abspath(directory_name)
    return (directory_path)


def create_directory_for_each_stack(dir_path, name):
    subfolder_path = os.path.join(dir_path, name)
    os.makedirs(subfolder_path, exist_ok=True)
    return (subfolder_path)


def split_dataframe(df, column_name):
    # List to store the split dataframes
    global no_splits
    no_splits = 0
    splits = []
    # Variable to keep track of the current value being processed
    current_value = None
    # Variable to keep track of the start index of each split
    start_index = 0
    # Iterate over each row in the dataframe
    for index, row in df.iterrows():
        # Get the value from the specified column for the current row
        print("Current Value: ")
        print(current_value)
        print("Value: ")
        value = row[column_name]
        print(value)
        print(" ")
        # If current_value is None, assign it the value of the first row
        if current_value is None:
            current_value = value
        # If the value is greater than or equal to the current value
        if value > current_value:
            print(" ")
            print("Split")
            print(" ")
            # Create a new dataframe slice from start_index to current index
            split_df = df[start_index:index]
            # Append the split dataframe to the list of splits
            splits.append(split_df)
            # Update the start index to the current index
            start_index = index
            # Update the current value to the new value
            current_value = value
            no_splits = no_splits + 1
            
        
            
        current_value = value

    # Create a dataframe slice from the last start_index to the end of the dataframe
    split_df = df[start_index:]
    # Add the last split
    splits.append(split_df)
    return splits

def formatdate(datetime_str):
    print(datetime_str)
    date, time = datetime_str.split(" ")
    print(date)
    print(time)
    day, month, year = date.split("-")
    hour, minute, seconds = time.split(":")
    transformed_datetime = f"{day}{month}{year}_{hour}{minute}"
    return transformed_datetime


# Call the function to create the directory
dir_path= create_directory_with_timestamp()

# Read .csv file into Pandas dataframe
csvfile = pd.read_csv('D:\plantdata\csv.csv')

column_name = 'Image Number'

# Split the dataframe that contains the website data into the constituent data runs
split_dataframes = split_dataframe(csvfile, column_name)

# Iterate through the split dataframes containing the individual runs
for i, split_df in enumerate(split_dataframes):
    ind=0
    # Get the starting index of the split dataframe
    var=split_df.index.start
    print("var: " + str(var))
    # Skip the first iteration as it contains an empty dataframe
    if i==0:
        var = 1
    # Get the 'Node Number' value of this run
    node_number=split_df['Node Number'][var]
    # Get the 'Time Period (s)' value of this run
    period=split_df['Time Period (s)'][var]
    # Get the 'Date' value of this run
    date=split_df['Date'][var]
    # Change date format from "dd/mm/yy hh:mm" to "ddmmyy_hhmm"
    date=formatdate(date)
    
    # Create a folder in the current directory for each SMFI run
    dir_name=f"SMFI_stack__node_{node_number}_period_{period}_{date}"
    dir_path_for_stack= create_directory_for_each_stack(dir_path, dir_name)
    
    print("No: " + str(no_splits))
    
    # Iterate over the indices in the split dataframe
    for ind in split_df.index:
        # Get the 'Image' data at the current index
        data=split_df['Image'][ind]
        # Decode base64 image to jpg
        im = Image.open(BytesIO(base64.b64decode(data)))
        #Index the images and save as jpeg
        indexing=ind-var+1
        st_name=f"Leaf-{period}s_fluorescence-frameno"
        file_name= st_name + str(indexing) + ".jpg"
        output_file_path = os.path.join(dir_path_for_stack, file_name)
        im.save(output_file_path, 'JPEG')
