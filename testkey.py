from groq import Groq
import os

# Lấy API key từ biến môi trường
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Gửi yêu cầu sử dụng mô hình LLaMA 3-8B-8192
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Xin chào, Groq! Tôi muốn thử mô hình LLaMA."}],  # Gửi câu hỏi tới API
    model="llama3-8b-8192",  # Sử dụng mô hình LLaMA 3-8B-8192
    max_tokens=50
)

# Kiểm tra nội dung trả về
print(response)  # In ra toàn bộ response để kiểm tra cấu trúc

# Kiểm tra nếu response có thuộc tính json() hoặc tương tự
if hasattr(response, 'json'):
    print("API Key hoạt động bình thường.")
    print(response.json())  # In kết quả trả về từ API
else:
    print("Lỗi: Không tìm thấy dữ liệu trả về hoặc không có thuộc tính json.")
