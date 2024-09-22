import os
import scipy.io
import numpy as np
import csv  # For creating CSV files
from statistics import mode

# Define constants
folder_path = "./PIR_DATASET/training_data"  # Path to the folder containing .mat files
output_csv = 'data_v3.csv'  # Output CSV file name
step = 10  # Step size for slicing
m = 5  # Number of sensors
offset = 2.05  # Voltage when no motion is detected

# Check if the folder exists
if not os.path.exists(folder_path):
    print("Folder not found!")
    exit()

# Create and open CSV file for writing
with open(output_csv, mode='w', newline='') as file:
    # Define the column names for the sensors and label
    fieldnames = ['x1', 'x2', 'x3', 'x4', 'x5', 'y']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()  # Write the header row

    # Loop through all .mat files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".mat"):  # Ensure we're processing only .mat files
            # Get the full file path and load the data from the .mat file
            mat_file_name = os.path.splitext(filename)[0]
            data = scipy.io.loadmat(os.path.join(folder_path, filename))

            # Loop through the sequences in 'profile_data'
            for s in range(len(data['profile_data'])):
                x = data['profile_data'][s, 0]  # Sensor data
                y = data['profile_data'][s, 1]  # Labels

                # Iterate over the samples in each sequence
                for sample in range(len(x[0, 0])):
                    start = 0
                    end = start + step

                    # Slice through the sequence in steps
                    while start < len(x[0, :, 0]):
                        x_str = []
                        # Handle sensor data and pad if necessary
                        for sensor in range(m):
                            current_segment = x[sensor, start:end, sample]
                            x_str_len = len(current_segment)
                            if x_str_len < step:
                                # Pad the sequence with offset values if it's shorter than the step
                                padded_segment = np.pad(current_segment, (0, step - x_str_len), 'constant', constant_values=offset)
                                x_str.append("[" + ",".join(map(lambda val: "{:.2f}".format(val - offset), padded_segment)) + "]")
                            else:
                                x_str.append("[" + ",".join(map(lambda val: "{:.2f}".format(val - offset), current_segment)) + "]")

                        # Handle label data and pad if necessary
                        y_segment = y[0, start:end, sample]
                        y_str_len = len(y_segment)
                        if y_str_len < step:
                            # Pad the labels with zeros if the length is shorter than the step
                            last_label_value = y[0, end - 1, sample] if end - 1 < len(y[0, :, sample]) else y[0, -1, sample]
                            # last_label_value=0
                            y_str = "[" + ",".join(map(str, np.pad(y_segment, (0, step - y_str_len), 'constant', constant_values=last_label_value))) + "]"
                        else:
                            y_str = "[" + ",".join(map(str, y_segment)) + "]"

                        # Write the data row into the CSV file
                        writer.writerow({'x1': x_str[0], 'x2': x_str[1], 'x3': x_str[2], 'x4': x_str[3], 'x5': x_str[4], 'y': y_str})

                        # Move to the next step
                        start += step
                        end += step

print(f"File CSV '{output_csv}' has been saved successfully.")
