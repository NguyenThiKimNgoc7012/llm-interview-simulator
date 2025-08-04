import speech_recognition as sr
import pydub
from pydub import AudioSegment

def speech_to_text(audio_file_path):
    """
    Chuyển âm thanh (định dạng WAV hoặc MP3) thành văn bản bằng thư viện SpeechRecognition.
    """
    recognizer = sr.Recognizer()

    if audio_file_path.lower().endswith(".mp3"):
        audio = AudioSegment.from_mp3(audio_file_path)
        audio_file_path = "converted_audio.wav"
        audio.export(audio_file_path, format="wav")

    with sr.AudioFile(audio_file_path) as source:
        recognizer.adjust_for_ambient_noise(source)
        audio_data = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio_data, language="vi-VN")  # Sử dụng Google Web Speech API
            return text
        except sr.UnknownValueError:
            return "Không hiểu nội dung."
        except sr.RequestError as e:
            return f"Lỗi kết nối dịch vụ nhận dạng: {e}"
