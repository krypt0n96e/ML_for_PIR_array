import os
import scipy.io
import matplotlib.pyplot as plt

# mat_file_name='training_data_LR'

# Đường dẫn của thư mục chứa các file
folder_path = "./PIR_DATASET/training_data"

# Lặp qua các file trong thư mục
for filename in os.listdir(folder_path):
    # Kiểm tra xem file có phải là file hay không
    if os.path.isfile(os.path.join(folder_path, filename)):
        # Lấy tên file mà không có phần mở rộng
        mat_file_name = os.path.basename(os.path.splitext(filename)[0])

    # Đọc dữ liệu từ file .mat
    data = scipy.io.loadmat(f'./PIR_DATASET/training_data/{mat_file_name}.mat')
    # print(len(data['profile_data']))
    for s in range(len(data['profile_data'])):
        # Trích xuất dữ liệu từ file .mat
        v = data['profile_data'][s][0]

        # Số cảm biến
        m = 5

        # Số lượng giá trị trên mỗi đồ thị
        training_data_value = 360

        # Bước thời gian bắt đầu
        start_time_step = 0

        # Số lượng bước thời gian trong mỗi vòng lặp
        num_time_steps = 360

        # Số lượng tập dữ liệu
        num_datasets = len(v[0][0])


        n = len(v[0])  # Số bước thời gian

        # Tạo thư mục lưu trữ đồ thị
        directory = f'./plot/training_data/{mat_file_name}/{mat_file_name}_{s}'
        if not os.path.exists(directory):
            os.makedirs(directory)
            print("Thư mục mới đã được tạo thành công.")
        else:
            print("Thư mục đã tồn tại.")

        # Vẽ đồ thị
        for e in range(num_datasets):
            j = start_time_step
            while j < n:
                if j + training_data_value > n:
                    training_data_value = n - j

                # Tạo đồ thị
                for i in range(m):
                    v_plot=[]
                    for p in range(training_data_value):
                        v_plot.append(v[i][p][e])
                    x = [k for k in range(j, j + training_data_value)]
                    plt.plot(x, v_plot, label=f'sensor{i + 1}')
                
                # Cài đặt các thông số của đồ thị
                plt.xlabel('timestep')
                plt.ylabel('voltage')
                plt.title('PIR analog signal captured by a PIR node')
                plt.grid(True)
                plt.axis([j, j + num_time_steps, 0, 4])
                plt.legend()

                # Lưu đồ thị vào thư mục
                plt.savefig(f'{directory}/{mat_file_name}_{s}_{e}_{j}_{j + training_data_value}')
                plt.clf()
                
                j += training_data_value
