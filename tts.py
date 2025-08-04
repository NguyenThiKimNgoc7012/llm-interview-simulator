import edge_tts
import os
import asyncio
from gtts import gTTS
import sys
import io

AUDIO_DIR = "static/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'doc', 'docx'}

def speak(text: str, filename="output.mp3", language="vi"):
    """
    Tạo giọng nói từ văn bản với edge-tts.
    Tự động chọn giọng Việt hoặc Anh.
    """
    print(f"Language: {language}")  # Debug log để kiểm tra giá trị language
    filepath = os.path.join(AUDIO_DIR, filename)

    # Kiểm tra và chọn giọng cho phù hợp với ngôn ngữ
    # Nếu ngôn ngữ là tiếng Việt thì chọn giọng tiếng Việt
    voice = "vi-VN-HoaiMyNeural" if language == "vi" else "en-US-GuyNeural"

    # Debug log cho giọng nói được chọn
    print(f"Selected voice: {voice}")

    # Hàm tạo âm thanh sử dụng edge-tts
    async def generate():
        await generate_audio(text, filepath, voice)

    # Gọi hàm bất đồng bộ để tạo âm thanh
    asyncio.run(generate())
    return f"audio/{filename}"

async def generate_audio(text, filepath, voice):
    """
    Sử dụng edge-tts để tạo và lưu âm thanh.
    """
    # Khởi tạo Communicate từ edge-tts
    communicate = edge_tts.Communicate(text, voice=voice)
    
    # Tạo và lưu file âm thanh
    await communicate.save(filepath)

    print(f"Audio saved at {filepath}")  # Kiểm tra nếu audio được tạo thành công
    
    
    
    

