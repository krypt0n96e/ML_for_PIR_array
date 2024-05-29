import os
import scipy.io
import numpy as np
import csv
import pandas as pd
import matplotlib.pyplot as plt

# Đường dẫn của thư mục chứa các file
folder_path = "./PIR_DATASET/testing_data"

# Tạo thư mục để lưu đồ thị nếu chưa tồn tại
output_folder = "./plot_test_data"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Khởi tạo và mở file CSV để ghi
with open('data_test_data.csv', mode='w', newline='') as file:
    fieldnames = ['x1', 'x2', 'x3', 'x4', 'x5', 'y']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    # Ghi tiêu đề
    writer.writeheader()

    # Lặp qua các file trong thư mục
    for filename in os.listdir(folder_path):
        # Kiểm tra xem file có phải là file hay không
        if os.path.isfile(os.path.join(folder_path, filename)):
            # Lấy tên file mà không có phần mở rộng
            mat_file_name = os.path.basename(os.path.splitext(filename)[0])

            # Đọc dữ liệu từ file .mat
            data = scipy.io.loadmat(os.path.join(folder_path, f'{mat_file_name}.mat'))

            for s in range(len(data['testing_data'])):
                # Trích xuất dữ liệu từ file .mat
                x = data['testing_data'][s, 0]
                y = data['testing_data'][s, 1]

                # Số cảm biến
                m = 5
                x_str = []
                x_str_len = len(x[0, :])

                for sensor in range(m):
                    segment_x = x[sensor, :]
                    x_str.append("[" + ",".join(map(str, segment_x)) + "]")

                if x_str:
                    y_str = ",".join(map(str, y.tolist()))
                    writer.writerow({'x1': x_str[0], 'x2': x_str[1], 'x3': x_str[2], 'x4': x_str[3], 'x5': x_str[4], 'y': y_str})

print("File CSV đã được lưu.")


# Đọc dữ liệu từ file CSV và vẽ đồ thị
data_frame = pd.read_csv('data_test_data.csv')

# Vẽ đồ thị cho từng xâu đã qua kiểm tra ngưỡng
for i in range(len(data_frame)):
    plt.figure(figsize=(12, 6))

    for j in range(5):
        sensor_data = eval(data_frame[f'x{j+1}'][i])  # Chuyển đổi chuỗi thành danh sách số
        plt.plot(sensor_data)
    plt.title(f'Sensor {j+1}')
    plt.ylabel('Voltage (V)')
    plt.xlabel('Timestep')
    plt.grid()

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    # Lưu đồ thị vào thư mục
    plt.savefig(os.path.join(output_folder, f'plot_{i+1}.png'))
    plt.close()

