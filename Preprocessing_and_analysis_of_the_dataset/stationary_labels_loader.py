import os
import scipy.io
import numpy as np
import csv
import pandas as pd
import matplotlib.pyplot as plt
from statistics import mode
from scipy.signal import butter, filtfilt

# Hàm tạo bộ lọc thông thấp
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

# Hàm áp dụng bộ lọc thông thấp
def lowpass_filter(data, cutoff=0.1, fs=1.0, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

# Đường dẫn của thư mục chứa các file
folder_path = "./PIR_DATASET/testing_data"

# Tạo thư mục để lưu đồ thị nếu chưa tồn tại
output_folder = "./plot_stationary_labels"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Khởi tạo và mở file CSV để ghi
with open('data_stationary_labels.csv', mode='w', newline='') as file:
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
            step = 10
            offset = 2.05  # điện áp lúc không phát hiện chuyển động

            # cắt 10 timestep một
            start = 0
            end = start + step

            # Lọc nhiễu tín hiệu
            filtered_signals = []
            for sensor in range(m):
                filtered_signals.append(lowpass_filter(x[sensor, :]))
            
            while start < len(x[0, :]):
                x_str = []
                x_str_len = len(x[0, start:end])
                if x_str_len < step:
                    for sensor in range(m):
                        # thêm vào cuối các giá trị = điện áp khi không có chuyển động để mở rộng xâu bị cắt
                        x_str.append("[" + ",".join(map(str, x[sensor, start:end])) + "," + ",".join(map(str, np.zeros(step - x_str_len) + offset)) + "]")
                else:
                    for sensor in range(m):
                        segment = x[sensor, start:end]
                        filter_segment = filtered_signals[sensor][start:end]
                        # Kiểm tra giá trị điện áp trong khoảng từ 1.9 V đến 2.3 V
                        if np.all((filter_segment >= 1.9) & (filter_segment <= 2.3)):
                            x_str.append("[" + ",".join(map(str, segment)) + "]")
                        else:
                            x_str = []
                            break

                if x_str:
                    # y_str = mode(y[0, start:end].tolist())  # lấy nhãn xuất hiện nhiều nhất trong khoảng
                    y_str = 0
                    writer.writerow({'x1': x_str[0], 'x2': x_str[1], 'x3': x_str[2], 'x4': x_str[3], 'x5': x_str[4], 'y': y_str})

                start += 10
                end += 10

print("File CSV đã được lưu.")


# Đọc dữ liệu từ file CSV và vẽ đồ thị
data_frame = pd.read_csv('data_test.csv')

# Vẽ đồ thị cho từng xâu đã qua kiểm tra ngưỡng
for i in range(len(data_frame)):
    fig, axs = plt.subplots(5, 1, figsize=(10, 10))
    fig.suptitle(f'Plot for row {i+1} with label {data_frame["y"][i]}')

    for j in range(5):
        sensor_data = eval(data_frame[f'x{j+1}'][i])  # Chuyển đổi chuỗi thành danh sách số
        axs[j].plot(sensor_data)
        axs[j].set_title(f'Sensor {j+1}')
        axs[j].set_ylim(1.8, 2.4)  # Đặt giới hạn trục y từ 1.8 V đến 2.4 V
        axs[j].set_ylabel('Voltage (V)')
        axs[j].set_xlabel('Timestep')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    # Lưu đồ thị vào thư mục
    fig.savefig(os.path.join(output_folder, f'plot_{i+1}.png'))
    plt.close(fig)
