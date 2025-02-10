import os
import scipy.io
import numpy as np
import csv  # For creating CSV files

# Define constants
folder_path = "./PIR_DATASET/training_data"  # Path to the folder containing .mat files
output_csv = 'data_v4_2.csv'  # Output CSV file name
step = 60  # Step size for slicing
m = 5  # Number of sensors
offset = 2.05  # Voltage when no motion is detected

# Define the area matrix for label-to-coordinate mapping
area = [
    [11, 12, 21, 22, 31, 32],
    [13, 14, 23, 24, 33, 34],
    [41, 42, 51, 52, 61, 62],
    [43, 44, 53, 54, 63, 64],
    [71, 72, 81, 82, 91, 92],
    [73, 74, 83, 84, 93, 94]
]

# Function to map a label to (x, y) coordinates (midpoint in the cell)
def label_to_coordinates(label):
    for i, row in enumerate(area):
        if label in row:
            x = 0.25 + (row.index(label) * 0.5)  # Column index * 0.5 for spacing + 0.25 for offset
            y = 0.25 + ((len(area) - i - 1) * 0.5)  # Row index flipped, * 0.5 for spacing + 0.25 for offset
            return x, y
    raise ValueError(f"Label {label} not found in the area matrix")


# Check if the folder exists
if not os.path.exists(folder_path):
    print("Folder not found!")
    exit()

# Create and open CSV file for writing
with open(output_csv, mode='w', newline='') as file:
    # Define the column names for the sensors and label (y1 and y2 for coordinates)
    fieldnames = ['x1', 'x2', 'x3', 'x4', 'x5', 'y1', 'y2']
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
                            y_segment_padded = np.pad(y_segment, (0, step - y_str_len), 'constant', constant_values=last_label_value)
                        else:
                            y_segment_padded = y_segment

                        # For each label in y_segment, convert to coordinates (y1, y2)
                        y1_list, y2_list = [], []
                        for label in y_segment_padded:
                            y1, y2 = label_to_coordinates(int(label))  # Convert label to coordinates
                            y1_list.append(y1)
                            y2_list.append(y2)

                        # Write the data row into the CSV file
                        writer.writerow({
                            'x1': x_str[0], 'x2': x_str[1], 'x3': x_str[2],
                            'x4': x_str[3], 'x5': x_str[4],
                            'y1': "[" + ",".join(map(str, y1_list)) + "]",
                            'y2': "[" + ",".join(map(str, y2_list)) + "]"
                        })

                        # Move to the next step
                        start += step
                        end += step

print(f"File CSV '{output_csv}' has been saved successfully.")
