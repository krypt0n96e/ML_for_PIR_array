import pandas as pd

# Đọc dữ liệu từ file CSV
df = pd.read_csv('data.csv')

# Chọn cột cần kiểm tra giá trị khác nhau
column_to_check = 'y'

# Tìm tất cả các giá trị khác nhau trong cột
unique_values = df[column_to_check].unique()

# Tạo label map từ chuỗi nhãn sang số nguyên
label_map = {}
index = 0
for value in unique_values:
    label_map[value] = index
    index += 1
print(index)
# In label map để kiểm tra
print(label_map)