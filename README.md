# ML_for_PIR_array

## To install venv and required lib on windows

Mở vscode thực thi lệnh sau:

```
python -m venv .venv
.\.venv\Scripts\Activate
pip install --upgrade pip
pip install -r requirements.txt
```

## To fix the error of not being able to activate venv

Lỗi này xuất hiện vì chính sách thực thi PowerShell trên hệ thống của bạn không cho phép chạy các script PowerShell. Để giải quyết vấn đề này, bạn cần thay đổi chính sách thực thi PowerShell sang một cấp độ cho phép chạy các script.

Dưới đây là cách thực hiện:

1. Mở PowerShell với quyền quản trị (Run as administrator).

2. Chạy lệnh sau để kiểm tra chính sách thực thi hiện tại:

   ```
   Get-ExecutionPolicy
   ```

3. Nếu kết quả là `Restricted`, tức là PowerShell không cho phép chạy script. Bạn cần thay đổi chính sách thực thi. Chạy lệnh sau để thay đổi chính sách thực thi sang `RemoteSigned` (hoặc một cấp độ thích hợp khác nếu bạn cần):

   ```
   Set-ExecutionPolicy RemoteSigned
   ```

4. Bạn sẽ được hỏi xác nhận, nhập `Y` và nhấn Enter để xác nhận.

5. Sau khi thay đổi chính sách thực thi, bạn có thể thử kích hoạt môi trường ảo bằng lệnh:
   ```
   .\.venv\Scripts\Activate
   ```

Lưu ý: Thay đổi chính sách thực thi PowerShell có thể ảnh hưởng đến bảo mật của hệ thống của bạn. Hãy đảm bảo bạn hiểu rõ rủi ro trước khi thực hiện thay đổi này.
