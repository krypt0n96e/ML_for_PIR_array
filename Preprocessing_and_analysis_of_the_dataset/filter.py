import os
import scipy.io
import numpy as np
import matplotlib.pyplot as plt
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

        # Lọc nhiễu tín hiệu
        filtered_signals = []
        for sensor in range(m):
            filtered_signals.append(lowpass_filter(x[sensor, :]))

        # Vẽ đồ thị tín hiệu gốc và đã lọc trên hai subplot
        plt.figure(figsize=(12, 6))

        # Subplot cho tín hiệu gốc
        plt.subplot(2, 1, 1)
        for j in range(m):
            plt.plot(x[j, :], label=f'Sensor {j+1} Original', linestyle='--')
        plt.title(f'Original signals for file {filename}')
        plt.ylim(1.8, 2.4)
        plt.ylabel('Voltage (V)')
        plt.legend()
        plt.grid()

        # Subplot cho tín hiệu đã lọc
        plt.subplot(2, 1, 2)
        for j in range(m):
            plt.plot(filtered_signals[j], label=f'Sensor {j+1} Filtered')
        plt.title(f'Filtered signals for file {filename}')
        plt.ylim(1.8, 2.4)
        plt.ylabel('Voltage (V)')
        plt.xlabel('Timestep')
        plt.legend()
        plt.grid()

        plt.tight_layout()
        plt.show()
