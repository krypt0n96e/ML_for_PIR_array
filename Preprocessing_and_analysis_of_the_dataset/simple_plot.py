import scipy.io #thư viện để đọc file .mat
import matplotlib.pyplot as plt #thư viên để vẽ đồ thị

# Đọc dữ liệu từ file .mat
data = scipy.io.loadmat('./PIR_DATASET/testing_data/sc1.mat')

# Trích xuất dữ liệu từ file .mat
v = data['testing_data'][0][0]
n = len(v[0]) #number of timestep
m = 5 #number of sensor
t = [i for i in range(n)]

# Vẽ đồ thị
for i in range(5):
    plt.plot(t,v[i],label=f'sensor{i+1}')
plt.xlabel('timestep')
plt.ylabel('voltage')
plt.title('PIR analog signal captured by a PIR node')
plt.grid(True)
plt.axis([0, 350, 0, 4])
plt.legend()
plt.show()
