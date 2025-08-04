from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime
from bson import Binary


# Kết nối đến MongoDB
try:
    client = MongoClient("mongodb://localhost:27017/")  
    # Kiểm tra kết nối
    client.admin.command('ping')
    print("Đã kết nối đến MongoDB.")
except ConnectionFailure as e:
    print(f"Lỗi kết nối đến MongoDB: {e}")

# Chọn database và collection
db = client["interview_db"]  
collection = db["interview_sessions"]# phỏng vấn qua text 
collection_cv = db["applicants"] 
collection_audio = db["interview_audio_sessions"]
collection_script = db["interview_scripts"]
collection_evaluation = db["interview_evaluation"]
collection_history_cv = db["interview_history_cv"] 
 
def save_interview_data(session_id, messages, name, job_title, level, language, job_description):
    qa_pairs = []
    q = None
    for msg in messages:
        if msg["role"] == "bot" and not msg["text"].startswith("👋"):
            q = msg["text"]
        elif msg["role"] == "user" and q:
            qa_pairs.append({"question": q, "answer": msg["text"]})
            q = None

    # Lưu trữ vào MongoDB
    collection.insert_one({
        "session_id": session_id,
        "name": name,
        "job_title": job_title,
        "level": level,
        "language": language,
        "job_description": job_description,
        "qa_pairs": qa_pairs,
        "interview_datetime": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), 
        "timestamp": datetime.utcnow()
    })
# Lưu phỏng vấn CV


def save_applicant_info(session_id, name, job_title, job_description, cv_file_path):
    """
    Lưu trữ thông tin ứng viên và CV vào MongoDB
    """
    with open(cv_file_path, "rb") as file:
        cv_data = file.read()  

    applicant_data = {
        "session_id": session_id,
        "name": name,
        "job_title": job_title,
        "job_description": job_description,
        "cv_file": Binary(cv_data), 
        "timestamp": datetime.utcnow() 
    }

    # Lưu vào MongoDB
    collection_cv.insert_one(applicant_data)
    print(f"Thông tin ứng viên {name} đã được lưu vào MongoDB.")

def save_interview_audio_data(session_id, name, job_title, job_description, audio_file_path, transcription, emotions, confidence_score, feedback, logs, summary):
    """
    Lưu trữ cuộc hội thoại giọng nói vào MongoDB (bao gồm STT, cảm xúc, điểm tự tin, phản hồi, nhật ký và tóm tắt)
    """
    try:
       
        with open(audio_file_path, "rb") as file:
            audio_data = file.read()

        
        audio_data_doc = {
            "session_id": session_id,
            "name": name,
            "job_title": job_title,
            "job_description": job_description,
            "audio_file": Binary(audio_data), 
            "transcription": transcription,  
            "emotions": emotions, 
            "confidence_score": confidence_score,  
            "feedback": feedback, 
            "logs": logs,  
            "summary": summary, 
            "timestamp": datetime.utcnow()  
        }

        # Lưu vào MongoDB
        collection_audio.insert_one(audio_data_doc)
        print(f"Phỏng vấn qua giọng nói của ứng viên {name} đã được lưu vào MongoDB.")
        save_evaluation_data(session_id, name, emotions, confidence_score, feedback, logs, summary)
    
    except Exception as e:
        print(f"Lỗi khi lưu dữ liệu âm thanh vào MongoDB: {e}")

def save_interview_script(session_id, messages):
    """
    Lưu trữ script phỏng vấn (câu hỏi và câu trả lời) vào MongoDB
    """
    script_data = []
    q = None
    for msg in messages:
        if msg["role"] == "bot" and not msg["text"].startswith("👋"):
            q = msg["text"]
        elif msg["role"] == "user" and q:
            script_data.append({"question": q, "answer": msg["text"]})
            q = None

    script_data_doc = {
        "session_id": session_id,
        "script": script_data,
        "timestamp": datetime.utcnow()  
    }

    # Lưu vào MongoDB
    collection_script.insert_one(script_data_doc)
    print(f"Script phỏng vấn của ứng viên đã được lưu vào MongoDB.")

def save_evaluation_data(session_id, name, emotions, confidence_score, feedback, logs, summary):
    """
    Lưu trữ kết quả đánh giá cảm xúc, mức độ tự tin, phản hồi, nhật ký và tóm tắt cuộc phỏng vấn vào MongoDB
    """
    evaluation_data = {
        "session_id": session_id,
        "name": name,
        "emotions": emotions, 
        "confidence_score": confidence_score,  
        "feedback": feedback,  
        "logs": logs, 
        "summary": summary,  
        "timestamp": datetime.utcnow()  
    }

    collection_evaluation.insert_one(evaluation_data)
    print(f"Đánh giá cảm xúc và mức độ tự tin của ứng viên {name} đã được lưu vào MongoDB.")

def save_interview_history_cv(session_id, name, job_title, interview_date, questions, answers, feedback, dashboard_data):
    """
    Lưu lịch sử phỏng vấn vào MongoDB khi phỏng vấn bắt đầu.
    Chưa có điểm số vì phỏng vấn chưa kết thúc.
    """
    interview_data = {
        "session_id": session_id,
        "name": name,
        "job_title": job_title,
        "interview_date": interview_date,
        "questions": questions,
        "answers": answers,
        "feedback": feedback,
        "dashboard_data": dashboard_data,
        "score": None,  
        "communication_score": None,  
        "fit_score": None 
    }
    collection_history_cv.insert_one(interview_data)  
    print(f"Lịch sử phiên phỏng vấn cho {name} đã được lưu (chưa có điểm số).")


def get_audio_file(session_id):
    try:
        audio_data_doc = collection_audio.find_one({"session_id": session_id})

        if audio_data_doc:
            audio_data = audio_data_doc["audio_file"]
            audio_file_path = f"static/audio/{session_id}_audio.mp3"
            with open(audio_file_path, "wb") as file:
                file.write(audio_data)

            print(f"Tệp âm thanh {audio_file_path} đã được lưu thành công.")
            return f"{session_id}_audio.mp3"
        else:
            print(f"Không tìm thấy tệp âm thanh cho session_id: {session_id}.")
            return None

    except Exception as e:
        print(f"Lỗi khi tải tệp âm thanh từ MongoDB: {e}")
        return None

