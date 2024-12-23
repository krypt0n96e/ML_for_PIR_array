import os
import scipy.io
import numpy as np
import matplotlib.pyplot as plt #ve do thi
import csv  #tao file csv 
import pandas as pd #thao tac voi du lieu bang
from statistics import mode


# mat_file_name='training_data_LR'

# Đường dẫn của thư mục chứa các file
folder_path = "./PIR_DATASET/training_data"

# Kiểm tra xem file CSV đã tồn tại hay không
csv_exists = os.path.exists('data_v2.csv')

# Khởi tạo và mở file CSV để ghi
with open('data_v2.csv', mode='w', newline='') as file:
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
        data = scipy.io.loadmat(f'./PIR_DATASET/training_data/{mat_file_name}.mat')

        for s in range(len(data['profile_data'])):
            # Trích xuất dữ liệu từ file .mat
            x = data['profile_data'][s,0]
            y = data['profile_data'][s,1]

            # Số cảm biến
            m = 5
            step=10
            offset=2.05#dien ap luc khong phat hien chuyen dong

            for sample in range(len(x[0,0])):
                #cat 10 timestep mot
                start=0
                end=start+step
            
                while start<len(x[0,:,0]):
                    x_str=[]
                    x_str_len=len(x[0,start:end,sample])
                    for sensor in range(m):
                        # Nếu độ dài ngắn hơn step, thêm các giá trị `offset` để mở rộng chuỗi
                        if x_str_len < step:
                            sensor_data = [val - offset for val in x[sensor, start:end, sample]] + [0] * (step - x_str_len)
                        else:
                            # Chuyển các giá trị thành chuỗi sau khi trừ offset
                            sensor_data = [val - offset for val in x[sensor, start:end, sample]]
                        
                        # Chuyển đổi thành chuỗi và làm tròn đến 2 chữ số thập phân
                        x_str.append("[" + ",".join("{:.2f}".format(val) for val in sensor_data) + "]")
                    

                    y_str="[" + ",".join(map(str, y[0,start:end,sample])) + "]" #chuyen thanh xau
                    y_str=mode(y[0,start:end,sample].tolist()) #lay nhan xuat hien nhieu nhat trong khoang
                    # if y_str_len<step:
                    #     y_str="[" + ",".join(map(str, y[0,start:end,sample])) + ",".join(map(str, np.zeros(step-len(y_str_len)))) + "]"
                    start+=10
                    end+=10

                    # Ghi dữ liệu vào file CSV
                    writer.writerow({'x1': x_str[0], 'x2': x_str[1], 'x3': x_str[2],'x4': x_str[3],'x5': x_str[4], 'y': y_str})

print("File CSV đã được lưu.")