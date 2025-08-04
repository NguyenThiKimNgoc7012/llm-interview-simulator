# tts_demo.py
from tts import speak

# Văn bản mẫu bạn muốn nghe
text = "Xin chào Kim Ngọc, tôi là avatar HR của bạn. Chúng ta cùng bắt đầu buổi phỏng vấn hôm nay nhé!"

# Tạo giọng nói
audio_path = speak(text)  # Mặc định sẽ tạo static/audio/question.mp3
print(f"✅ Đã tạo file âm thanh tại: static/{audio_path}")
