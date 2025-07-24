<img width="1970" height="1058" alt="image" src="https://github.com/user-attachments/assets/4557c8af-b60f-4060-b50a-749abffa8eba" />


# Talking to Plants

## Overview

This project is a multi-component system for collecting, processing, and analyzing plant fluorescence data. It includes firmware for ESP32-based sensor nodes and gateways, offline Python scripts for image and data processing, and PHP scripts for database interaction and web-based data management. The system is designed to facilitate high-throughput plant phenotyping and data-driven plant research.

<img width="1100" height="614" alt="image" src="https://github.com/user-attachments/assets/71c2f832-f93e-461f-9cfc-e38c3a07a174" />

## Key Features

<img width="778" height="496" alt="image" src="https://github.com/user-attachments/assets/77cc3276-8c3d-4296-9f53-e641bf7b9f21" />

- **ESP32 Node & Gateway Firmware**: Code for sensor nodes and gateways (Arduino IDE, ESP32) to collect and transmit plant data.
- **Offline Image Processing**: Python scripts to process fluorescence images, generate false-color stacks, and analyze fluorescence response.
- **Data Management**: PHP scripts for inserting and retrieving node data from a MySQL database.
- **Automated Data Splitting & Cultivar Assessment**: Tools to split and organize data runs, decode and save images, and structure results for further analysis.
- **Visualization**: Automated plotting and saving of fluorescence response and difference plots.

## Build & Run

### ESP32 Firmware

- Use [Arduino IDE](https://www.arduino.cc/en/software) with the "DOIT ESP32 DEVKIT V1" board.
- Required libraries (install via Arduino Library Manager):
  - PainlessMesh
  - ArduinoJson
  - TaskScheduler
  - AsyncTCP

### Python Scripts

1. Install dependencies (see below).
2. Place your image and CSV data in the expected directories (update paths in scripts as needed).
3. Run scripts from the command line:
   ```bash
   python Create_cultivars.py
   python Fluorescence_intensity_across_leaf.py
   python Fluorescence_response_plot_api.py
   python Subtraction.py
   ```

### PHP Scripts

- Deploy `insertData.php` and `EntriesPerNode.php` on a web server with PHP and MySQL.
- Configure database credentials as needed.

## Dependencies

### Python

- numpy
- pandas
- matplotlib
- pillow (PIL)

Install with:
```bash
pip install numpy pandas matplotlib pillow
```

### PHP

- PHP 7.x or newer
- MySQL database

## Usage / Parameters to be Tuned

### Python Scripts

- **Create_cultivars.py**
  - Expects a CSV file with columns: 'Node Number', 'Time Period (s)', 'Date', 'Image Number', 'Image' (base64).
  - Adjust `csvfile` path to your data.
  - Output: Organizes images into folders by run, decodes and saves images.

- **Fluorescence_intensity_across_leaf.py**
  - Set `image_folder` to the directory containing your JPEG images.
  - Outputs row intensity profiles for a selected row in the image.

- **Fluorescence_response_plot_api.py**
  - Set `image_folder` to your image stack directory.
  - Adjust region of interest in the script as needed.
  - Outputs false-colored images, fluorescence response plots, and saves data as CSV.

- **Subtraction.py**
  - Set `image_folder` and `reference_path` to your response and reference data directories.
  - Outputs difference plots and saves results.

### PHP Scripts

- **insertData.php**
  - Receives POST requests with image data and metadata.
  - Requires a valid API key (see script for value).
  - Segments and stores image data in the database.

- **EntriesPerNode.php**
  - Connects to the database and displays the latest run per node in a table.

## Notes

- Update all hardcoded paths in scripts to match your environment.

## Additional Images

### Website
<img width="1102" height="506" alt="image" src="https://github.com/user-attachments/assets/73a65bbc-b52b-4256-911f-8029dd8f0444" />

<img width="543" height="468" alt="image" src="https://github.com/user-attachments/assets/4ac0f7f3-fc4d-4a98-a12e-9865f321bb5c" />

### False Colouring of Leaf - Colour Key (right) Indicates Highest to Lowest Light Intensity (top to bottom)

<img width="476" height="363" alt="image" src="https://github.com/user-attachments/assets/c279998c-05c8-47d0-b3a5-0ba9ac3c092f" />

