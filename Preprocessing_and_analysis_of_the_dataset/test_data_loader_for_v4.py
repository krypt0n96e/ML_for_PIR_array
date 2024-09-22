import os
import scipy.io
import numpy as np
import csv
import pandas as pd
import matplotlib.pyplot as plt

# Đường dẫn của thư mục chứa các file
folder_path = "./PIR_DATASET/testing_data"

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

# Khởi tạo và mở file CSV để ghi
with open('data_test_data_v4.csv', mode='w', newline='') as file:
    fieldnames = ['x1', 'x2', 'x3', 'x4', 'x5', 'y1', 'y2']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    # Ghi tiêu đề
    writer.writeheader()

    # Lặp qua các file trong thư mục
    for filename in os.listdir(folder_path):
        # Kiểm tra xem file có phải là file .mat hay không
        if filename.endswith('.mat'):
            # Đọc dữ liệu từ file .mat
            data = scipy.io.loadmat(os.path.join(folder_path, filename))

            for s in range(len(data['testing_data'])):
                # Trích xuất dữ liệu từ file .mat
                x = data['testing_data'][s, 0]
                y_segment_padded = data['testing_data'][s, 1]

                # Số cảm biến
                m = 5
                x_str = []
                offset = 2.05

                # Làm tròn và lưu dữ liệu cảm biến
                for sensor in range(m):
                    segment_x = np.round(x[sensor, :] - offset, 2)  # Làm tròn giá trị tới 2 chữ số
                    x_str.append("[" + ",".join(map(lambda val: f"{val:.2f}", segment_x)) + "]")

                # Khởi tạo danh sách y1_list và y2_list, không lặp lại giá trị
                y1_list, y2_list = [], []

                # Chuyển nhãn trong y_segment_padded thành tọa độ (y1, y2)
                for label in y_segment_padded[0]:
                    # Lấy giá trị đầu tiên của mảng label nếu nó là một mảng, dùng .item() cho giá trị đơn
                    if isinstance(label, np.ndarray):
                        label_value = int(label.item())
                    else:
                        label_value = int(label)

                    # Convert the label to coordinates (y1, y2)
                    y1, y2 = label_to_coordinates(label_value)
                    y1_list.append(round(y1, 2))
                    y2_list.append(round(y2, 2))

                # Write the data row into the CSV file
                writer.writerow({
                    'x1': x_str[0], 'x2': x_str[1], 'x3': x_str[2],
                    'x4': x_str[3], 'x5': x_str[4],
                    'y1': "[" + ",".join(map(lambda val: f"{val:.2f}", y1_list)) + "]",
                    'y2': "[" + ",".join(map(lambda val: f"{val:.2f}", y2_list)) + "]"
                })
print("File CSV đã được lưu.")
