#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chương trình tìm file video và CSV trong một thư mục gốc (bao gồm cả các thư mục con)
dựa trên timestamp nhập vào, sau đó hiển thị khung hình video (frame gần nhất)
và đồ thị tín hiệu (các kênh x1 đến x5) đồng bộ trong cùng một cửa sổ.

Các điểm chính:
  - File video và CSV có tên dạng: {start}-{end}.webm (hoặc .wepm, .mp4, .avi) và {start}-{end}.csv.
  - Nếu file video là webm, chuyển sang MP4 bằng ffmpeg.
  - Khi đọc video, lấy FPS thực tế từ file để tính chỉ số frame và điều chỉnh tốc độ.
  - Nút Play cho phép video và tín hiệu chạy liên tục từ vị trí đã chọn.
  - Nút "Chọn thư mục" cho phép chọn thư mục gốc, sau đó tìm kiếm đệ quy trong tất cả các thư mục con.
  
Video mặc định 30fps (nếu không lấy được FPS thực tế), tín hiệu 100Hz, cửa sổ tín hiệu ±1100ms, trục y từ 500 đến 3000.
"""

import sys
import os
import re
import cv2
import subprocess
import tempfile
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, QtCore, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# --- Các hằng số mặc định ---
DEFAULT_FPS = 30             # Nếu không lấy được FPS thực tế, dùng 30fps
FS_SIGNAL = 100              # Tín hiệu 100Hz (mỗi 10ms 1 mẫu)
TIME_WINDOW = 2200           # Cửa sổ ±1100ms quanh timestamp
Y_MIN, Y_MAX = 500, 3000     # Trục y cố định

# --- Hàm xử lý nhãn ---
def parse_label(label_str):
    """
    Nếu label có dạng 'id{k}', trả về k; nếu không, trả về 0.
    """
    m = re.match(r'id(\d+)', label_str)
    if m:
        return int(m.group(1))
    else:
        return 0

# --- Hàm chuyển đổi video webm sang mp4 sử dụng ffmpeg ---
def convert_webm_to_mp4(webm_path):
    """
    Chuyển đổi file video webm sang mp4 bằng ffmpeg.
    Trả về đường dẫn đến file mp4 tạm thời nếu thành công, hoặc None nếu có lỗi.
    """
    try:
        tmp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        tmp_file.close()
        mp4_path = tmp_file.name

        cmd = ['ffmpeg', '-y', '-i', webm_path, '-c:v', 'libx264', '-c:a', 'aac', mp4_path]
        print("Chuyển đổi video với lệnh:", " ".join(cmd))
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print("Lỗi chuyển đổi ffmpeg:", result.stderr)
            return None
        print("Chuyển đổi thành công. File mp4:", mp4_path)
        return mp4_path
    except Exception as e:
        print("Exception khi chuyển đổi video:", e)
        return None

# --- Lớp vẽ đồ thị tín hiệu ---
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=3, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        self.fig.tight_layout()

# --- Lớp giao diện chính ---
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, folder_path=None):
        """
        folder_path: thư mục chứa file video và CSV.
        Nếu không có, mặc định sử dụng thư mục hiện hành.
        """
        super().__init__()
        self.setWindowTitle("Hiển thị Video, Tín hiệu và Nhãn")
        self.folder_path = folder_path if folder_path else os.getcwd()

        # Các biến liên quan đến file
        self.video_path = None           # Đường dẫn file gốc được chọn
        self.converted_video_path = None # Nếu chuyển đổi, đường dẫn file mp4
        self.csv_path = None
        self.video_start = None
        self.video_end = None
        self.cap = None
        self.df = None

        # Tạo nút "Chọn thư mục"
        self.folderButton = QtWidgets.QPushButton("Chọn thư mục")
        self.folderButton.clicked.connect(self.choose_folder)

        # Slider: giá trị relative (0 đến video_end - video_start)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setEnabled(False)
        self.slider.valueChanged.connect(self.on_slider_change)

        # Các widget nhập liệu và nút
        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setPlaceholderText("Nhập timestamp (ms)")
        self.jumpButton = QtWidgets.QPushButton("Jump")
        self.jumpButton.clicked.connect(self.on_jump)
        self.playButton = QtWidgets.QPushButton("Play")
        self.playButton.clicked.connect(self.on_play)

        # Widget hiển thị video
        self.videoLabel = QtWidgets.QLabel()
        self.videoLabel.setFixedSize(640, 480)
        self.videoLabel.setStyleSheet("background-color: black;")

        # Canvas hiển thị đồ thị tín hiệu
        self.canvas = MplCanvas(self, width=8, height=3, dpi=100)

        # Sắp xếp layout
        topLayout = QtWidgets.QHBoxLayout()
        topLayout.addWidget(self.videoLabel)
        topLayout.addWidget(self.canvas)

        controlLayout = QtWidgets.QHBoxLayout()
        controlLayout.addWidget(self.folderButton)  # Nút chọn thư mục
        controlLayout.addWidget(QtWidgets.QLabel("Timestamp:"))
        controlLayout.addWidget(self.lineEdit)
        controlLayout.addWidget(self.jumpButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addStretch()
        controlLayout.addWidget(self.slider)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(controlLayout)

        widget = QtWidgets.QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)

        # Timer để chạy video (Play)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(int(1000 / DEFAULT_FPS))
        self.timer.timeout.connect(self.next_frame)
        self.isPlaying = False

        self.current_relative_ts = None  # relative = timestamp - video_start

    def choose_folder(self):
        """Hiển thị hộp thoại chọn thư mục và cập nhật self.folder_path."""
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Chọn thư mục chứa video và CSV", self.folder_path)
        if folder:
            self.folder_path = folder
            QtWidgets.QMessageBox.information(self, "Thông báo", f"Đã chọn thư mục: {folder}")
            print(f"Đã chọn thư mục: {folder}")

    def select_files(self, timestamp):
        """
        Duyệt self.folder_path (bao gồm cả thư mục con) để tìm file video và CSV phù hợp với timestamp.
        File video: {start}-{end}.webm (hoặc .wepm, .mp4, .avi), CSV: {start}-{end}.csv.
        Nếu timestamp nằm giữa start và end, trả về (video_path, csv_path, start, end).
        Nếu không tìm thấy, trả về (None, None, None, None).
        Lưu ý: file video có end == 0 được coi là không hợp lệ.
        """
        video_candidates = []
        csv_dict = {}
        # Duyệt đệ quy trong self.folder_path
        for root, dirs, files in os.walk(self.folder_path):
            for f in files:
                full_path = os.path.join(root, f)
                if f.lower().endswith(('.webm', '.wepm', '.mp4', '.avi')):
                    m = re.match(r'(\d+)-(\d+)\.(webm|wepm|mp4|avi)$', f.lower())
                    if m:
                        start = int(m.group(1))
                        end = int(m.group(2))
                        if end == 0:
                            continue
                        if timestamp >= start and timestamp <= end:
                            video_candidates.append((start, end, full_path))
                elif f.lower().endswith('.csv'):
                    m = re.match(r'(\d+)-(\d+)\.csv$', f.lower())
                    if m:
                        start = int(m.group(1))
                        end = int(m.group(2))
                        csv_dict[(start, end)] = full_path

        if not video_candidates:
            return None, None, None, None

        video_candidates.sort(key=lambda x: x[0])
        chosen = video_candidates[0]
        start, end, video_path = chosen
        csv_path = csv_dict.get((start, end), None)
        return video_path, csv_path, start, end

    def on_jump(self):
        """Khi người dùng nhập timestamp và nhấn Jump, tìm file video/CSV và cập nhật giao diện."""
        try:
            t = int(self.lineEdit.text())
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Timestamp nhập vào không hợp lệ!")
            return

        video_path, csv_path, start, end = self.select_files(t)
        if video_path is None:
            QtWidgets.QMessageBox.information(self, "Thông báo", "Không có video tương ứng!")
            return

        self.video_path = video_path
        self.csv_path = csv_path
        self.video_start = start
        self.video_end = end

        relative_ts = t - start
        self.current_relative_ts = relative_ts

        info = (f"Đã tìm được video:\n  Path: {video_path}\n  Video_start: {start}\n"
                f"  Video_end: {end}\n  Relative timestamp: {relative_ts} ms")
        print(info)
        QtWidgets.QMessageBox.information(self, "Thông tin video", info)

        # Nếu video định dạng webm/wepm, chuyển đổi sang mp4
        if video_path.lower().endswith(('.webm', '.wepm')):
            converted = convert_webm_to_mp4(video_path)
            if converted is None:
                QtWidgets.QMessageBox.warning(self, "Lỗi chuyển đổi", "Không chuyển được video từ webm sang mp4.")
                return
            else:
                self.converted_video_path = converted
                used_video_path = converted
                print("Sử dụng file video chuyển đổi:", used_video_path)
        else:
            used_video_path = video_path

        # Đọc file CSV nếu có
        if self.csv_path:
            try:
                self.df = pd.read_csv(self.csv_path, header=None,
                                      names=['timestep','x1','x2','x3','x4','x5','y'])
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Lỗi", f"Lỗi đọc CSV: {e}")
                self.df = None
        else:
            self.df = None

        # Mở video
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(used_video_path)
        if not self.cap.isOpened():
            QtWidgets.QMessageBox.critical(self, "Lỗi", "Không mở được video!")
            return

        # Lấy FPS thực tế từ video
        actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
        if actual_fps <= 0:
            actual_fps = DEFAULT_FPS
        print(f"FPS thực tế của video: {actual_fps}")
        self.timer.setInterval(int(1000 / actual_fps))

        # Cập nhật slider: từ 0 đến (video_end - video_start)
        self.slider.setEnabled(True)
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.video_end - self.video_start)
        self.slider.setValue(relative_ts)

        # Cập nhật hiển thị video và tín hiệu tại timestamp đã chọn
        self.on_slider_change(relative_ts)

    def on_play(self):
        """Bật hoặc tạm dừng chế độ Play: video và tín hiệu chạy liên tục."""
        if self.cap is None:
            QtWidgets.QMessageBox.information(self, "Thông báo", "Chưa chọn video (nhập timestamp và nhấn Jump)!")
            return
        if not self.isPlaying:
            self.isPlaying = True
            self.timer.start()
        else:
            self.timer.stop()
            self.isPlaying = False

    def on_slider_change(self, relative_value):
        """Khi slider thay đổi, cập nhật hiển thị video và đồ thị tín hiệu.
           relative_value = timestamp hiện tại - video_start."""
        if self.video_start is None:
            return
        timestamp = relative_value + self.video_start
        self.current_relative_ts = relative_value
        self.update_video_frame(timestamp)
        self.update_signal_plot(timestamp)

    def next_frame(self):
        """Hàm được gọi bởi timer khi Play bật: tăng thời gian hiện tại và cập nhật hiển thị."""
        actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
        if actual_fps <= 0:
            actual_fps = DEFAULT_FPS
        new_relative = self.current_relative_ts + (1000 / actual_fps)
        if new_relative > (self.video_end - self.video_start):
            self.timer.stop()
            self.isPlaying = False
            return
        self.slider.setValue(int(new_relative))
        # on_slider_change sẽ được gọi tự động khi slider thay đổi

    def update_video_frame(self, timestamp):
        """
        Hiển thị khung hình video gần nhất với timestamp.
        Tính frame_index theo: round((timestamp - video_start) * actual_fps / 1000).
        Nếu CAP_PROP_FRAME_COUNT trả về số <= 0, bỏ qua kiểm tra giới hạn frame.
        Nếu không đọc được frame, hiển thị thông báo lỗi và in ra thông tin debug.
        """
        if self.cap is None:
            return

        rel_time = timestamp - self.video_start  # thời gian tương đối (ms)
        actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
        if actual_fps <= 0:
            actual_fps = DEFAULT_FPS

        frame_index = int(round(rel_time * actual_fps / 1000))
        total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        debug_info = (f"timestamp: {timestamp} ms, video_start: {self.video_start} ms, "
                      f"rel_time: {rel_time} ms\nComputed frame_index: {frame_index}, "
                      f"Total frames: {total_frames}\n")

        if total_frames > 0 and frame_index >= total_frames:
            debug_info += "Frame index vượt quá tổng số frame."
            print(debug_info)
            QtWidgets.QMessageBox.warning(self, "Lỗi video", debug_info)
            error_img = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(error_img, "Khong co video tai timestamp nay", (50,240),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
            self.show_frame(error_img)
            return

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = self.cap.read()
        if not ret or frame is None:
            debug_info += "Không đọc được frame từ CAP_PROP_POS_FRAMES."
            print(debug_info)
            QtWidgets.QMessageBox.warning(self, "Lỗi video", debug_info)
            error_img = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(error_img, "Khong co video tai timestamp nay", (50,240),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
            self.show_frame(error_img)
        else:
            print("Đã đọc được frame thành công:")
            print(debug_info)
            self.show_frame(frame)

    def show_frame(self, frame):
        """Chuyển frame OpenCV sang QPixmap và hiển thị trên videoLabel."""
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, _ = frame.shape
        bytesPerLine = 3 * width
        qImg = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(qImg)
        self.videoLabel.setPixmap(pix.scaled(self.videoLabel.size(), QtCore.Qt.KeepAspectRatio))

    def update_signal_plot(self, timestamp):
        """
        Vẽ đồ thị tín hiệu trong khoảng ±1100ms quanh timestamp.
        Vẽ đồng thời 5 kênh x1 đến x5, đánh dấu điểm dữ liệu gần nhất và hiển thị nhãn (nếu hiệu số ≤ 10ms).
        """
        ax = self.canvas.ax
        ax.clear()

        half_window = TIME_WINDOW // 2  # ±1100ms
        t_start = timestamp - half_window
        t_end = timestamp + half_window

        colors = ['blue', 'green', 'orange', 'purple', 'brown']

        if self.df is not None:
            df_window = self.df[(self.df['timestep'] >= t_start) & (self.df['timestep'] <= t_end)]
            if df_window.empty:
                ax.text(0.5, 0.5, "Khong co tin hieu trong khoang nay",
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax.transAxes, fontsize=12, color='red')
            else:
                for i, col in enumerate(['x1', 'x2', 'x3', 'x4', 'x5']):
                    ax.plot(df_window['timestep'].values, df_window[col].values,
                            label=col, color=colors[i])
                ax.set_ylim(Y_MIN, Y_MAX)
                ax.set_xlim(t_start, t_end)
                ax.legend()

                diff = np.abs(df_window['timestep'] - timestamp)
                min_idx = diff.idxmin()
                marker_timestamp = self.df.loc[min_idx, 'timestep']
                for i, col in enumerate(['x1', 'x2', 'x3', 'x4', 'x5']):
                    marker_signal = self.df.loc[min_idx, col]
                    ax.plot(marker_timestamp, marker_signal, marker="o", markersize=8, color=colors[i])
        else:
            ax.text(0.5, 0.5, "Khong co tin hieu (CSV khong ton tai)",
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=12, color='red')

        ax.axvline(timestamp, color='k', linestyle='--', linewidth=2)

        label_found = None
        if self.df is not None:
            diff_all = np.abs(self.df['timestep'] - timestamp)
            min_diff = diff_all.min()
            min_idx_all = diff_all.idxmin()
            if min_diff <= 10:
                label_found = self.df.loc[min_idx_all, 'y']

        if label_found is not None:
            label_id = parse_label(str(label_found))
            text_label = f"Nhan hien tai: {label_found} (id={label_id})"
        else:
            text_label = "Khong co nhan"
        ax.text(0.02, 0.95, text_label, transform=ax.transAxes, fontsize=12,
                verticalalignment='top', bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
        self.canvas.draw()

def main():
    folder_path = None  # Nếu None, sẽ sử dụng thư mục hiện hành
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow(folder_path)
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
