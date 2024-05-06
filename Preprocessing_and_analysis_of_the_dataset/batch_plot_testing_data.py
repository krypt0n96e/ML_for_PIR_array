import os
import scipy.io #thư viện để đọc file .mat
import matplotlib.pyplot as plt #thư viên để vẽ đồ thị



# Đường dẫn của thư mục chứa các file
folder_path = "./PIR_DATASET/testing_data"

# Lặp qua các file trong thư mục
for filename in os.listdir(folder_path):
    # Kiểm tra xem file có phải là file hay không
    if os.path.isfile(os.path.join(folder_path, filename)):
        # Lấy tên file mà không có phần mở rộng
        mat_file_name = os.path.basename(os.path.splitext(filename)[0])
    dc=f'./plot/testing_data/{mat_file_name}'
    # Đọc dữ liệu từ file .mat
    data = scipy.io.loadmat(f'./PIR_DATASET/testing_data/{mat_file_name}.mat')

    if not os.path.exists(dc):
        os.makedirs(dc)
        print("Thư mục mới đã được tạo thành công.")
    else:
        print("Thư mục đã tồn tại.")
    # Trích xuất dữ liệu từ file .mat
    v = data['testing_data'][0][0]
    n = len(v[0]) #number of timestep

    m = 5 #number of sensor
    t = [i for i in range(n)]
    j=0 #starting timestep
    m=350 #number of value per plot
    # Vẽ đồ thị
    while j<n:
        if j+m>n:
            m=n-j
        for i in range(5):
            v_plot= v[i][j:j+m].copy()
            x = [k for k in range(j,j+m)]
            plt.plot(x,v_plot,label=f'sensor{i+1}')
        plt.xlabel('timestep')
        plt.ylabel('voltage')
        plt.title('PIR analog signal captured by a PIR node')
        plt.grid(True)
        plt.axis([j, j+350, 0, 4])
        plt.legend()
        plt.savefig(f'./plot/testing_data/{mat_file_name}/{mat_file_name}_{j}_{j+m}')
        plt.clf()
        j=j+m
        # plt.show()
