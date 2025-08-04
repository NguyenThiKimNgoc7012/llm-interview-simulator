from flask import Flask, render_template, request, redirect, session, jsonify, url_for
import json
import os
import uuid
from flask import session
from db import collection
from bson.objectid import ObjectId
from flask import jsonify
from db import collection
from werkzeug.utils import secure_filename
from tasks import analyze_cv_and_generate_questions
from datetime import datetime
from tasks import ask_question, follow_up
from tasks import evaluate_candidate_responses, get_feedback_on_answer
from tasks import should_terminate_early
from pymongo import MongoClient
from flask import Flask, session
from flask_session import Session
from tts import speak
from tasks import evaluate_candidate_responses_voice
import time
from tasks import ask_question_cv
from utils import extract_text_from_cv, validate_job_consistency 
from db import save_evaluation_data, save_applicant_info, save_interview_audio_data, save_interview_script,save_interview_history_cv
from tts import speak
from fpdf import FPDF
from flask import send_file, session
import io
import os
import dash
import dash
import numpy as np
import dash.dcc as dcc
import dash.html as html
import plotly.graph_objects as go
from textblob import TextBlob
from flask import Flask, render_template
from flask_pymongo import PyMongo
from flask import send_from_directory, abort
from tasks import perform_rag_task
from experience import perform_rag_task_experience
from db import get_audio_file
from tasks import get_suggested_answer  
from datetime import datetime
from bson import ObjectId
from tasks import (
    load_data,
    preprocess_data,
    create_faiss_index,
    search_relevant_chunks,
    generate_response_experience
)
from tasks import perform_rag_experience_task


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/interview_db"
mongo = PyMongo(app)
app.secret_key = "monahr"  
app.config['SESSION_TYPE'] = 'mongodb'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_MONGODB'] = MongoClient('mongodb://localhost:27017/').interview_db  


# Khởi tạo Flask-Session
Session(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

interview_history = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS
def load_job_list():
    with open("data/phongvan_by_nganh.json", encoding="utf-8") as f:
        data = json.load(f)
    return list(data.keys())
def load_questions(job_title):
    with open("data/phongvan_by_nganh.json", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(job_title, [])

def get_all_histories():
    cursor = collection.find({}, {"name": 1, "job_title": 1})
    return {str(doc["_id"]): {"name": doc.get("name", ""), "job": doc.get("job_title", "") } for doc in cursor}

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/form")
def form():
    job_list = load_job_list()
    return render_template("form.html", job_list=job_list)

# === app.py (phần sửa route upload_cv & interview_cv) ===
  
def calculate_technical_score(answers):
      score = 0
      for answer in answers:
          if answer['answer'] != 'Không có câu trả lời.':
              score += 1
      total_questions = 10
      return (score / total_questions) * 100
  
def calculate_communication_score(messages):
    """
    Tính điểm giao tiếp dựa trên các tin nhắn từ ứng viên, với cải tiến kiểm tra độ rõ ràng, chính xác ngữ pháp.
    """
    score = 0
    total_answers = len(messages)

    for message in messages:
        if message.get("role") == "user" and message.get("text"):
            answer = message["text"]
            blob = TextBlob(answer)
            sentiment = blob.sentiment.polarity 
            score += len(answer.split()) 
            if sentiment > 0.1:
                score += 5  
            elif sentiment < -0.1:
                score -= 5  
    max_score = total_answers * 20  
    if max_score == 0:
        return 0 

    return min((score / max_score) * 100, 100)
  
def calculate_fit_score(answers, job_title):
      fit_score = 0
      total_weight = 0  
  
      for answer in answers:
          question = answer["question"]
          response = answer["answer"]
  
          if "kỹ năng" in question or "kiến thức" in question:
              fit_score += 20  
              total_weight += 20
          
          elif "văn hóa" in question or "công ty" in question:
              fit_score += 15  
              total_weight += 15
          
          elif "kinh nghiệm" in question:
              fit_score += 10  
              total_weight += 10
  
      if total_weight == 0:
          return 0  
  
      return (fit_score / total_weight) * 100
  
@app.route('/upload_cv', methods=['GET', 'POST'])
def upload_cv():
    if request.method == 'POST':
        name = request.form.get('name')
        language = request.form.get('language')
        job_title = request.form.get('job_title')
        job_description = request.form.get('job_description')
        cv_file = request.files.get('cv')

        if not cv_file or not allowed_file(cv_file.filename):
            return "Vui lòng chọn file CV hợp lệ (pdf, doc, docx)", 400

        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{cv_file.filename}")
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        cv_file.save(save_path)
        cv_text = extract_text_from_cv(save_path)
        if not validate_job_consistency(job_title, job_description, extract_text_from_cv(save_path)):
            with open("data/phongvan_by_nganh.json", "r", encoding="utf-8") as f:
                job_list = json.load(f)
            error_message = f"Nội dung CV và mô tả công việc không khớp với ngành '{job_title}'. Vui lòng kiểm tra lại."
            return render_template("upload_cv.html", job_list=job_list, error=error_message)
        session.clear()
        session['name'] = name
        session['language'] = language
        session['job_title'] = job_title
        session['job_description'] = job_description
        session['cv_path'] = save_path
        session['idx'] = 0
        session['answers'] = []
        if "session_id" not in session:
            session["session_id"] = str(uuid.uuid4())
        save_interview_history_cv(
            session["session_id"], 
            session["name"],  
            session["job_title"], 
            datetime.utcnow(),  
            [], 
            [],  
            "Chưa đánh giá",  
            {"technical_score": None, "communication_score": None, "fit_score": None}  
        )


        return redirect(url_for('interview_cv'))

    with open("data/phongvan_by_nganh.json", "r", encoding="utf-8") as f:
        job_list = json.load(f)

    return render_template('upload_cv.html', job_list=job_list)

@app.route("/interview_cv", methods=["GET", "POST"])
def interview_cv():
    
    if "language" not in session:
        session["language"] = "vi"  
    if "cv_path" not in session:
        return redirect("/upload_cv")

    session_id = session.get("session_id", str(uuid.uuid4()))
    session["session_id"] = session_id
    idx = session.get("idx", 0)
    if request.method == "GET" and "questions" not in session:
        questions = analyze_cv_and_generate_questions(
            session["cv_path"],
            session["job_title"],
            session.get("job_description", ""),
            language=session.get("language", "vi") 
        )
        
        session["questions"] = questions
        session["messages"] = []
        save_applicant_info(
            session["session_id"],
            session["name"],
            session["job_title"],
            session.get("job_description", ""),
            session["cv_path"]
        )
        print(f"Question 1: {questions[0]}")  

        question_audio = f"question_{session_id}_0.mp3"
        speak(questions[0], filename=question_audio, language=session.get("language", "vi"))

        return render_template("interview_cv.html", messages=[], audio_file=question_audio, popup_start=True, idx=idx)
    if request.method == "POST":
        answer = request.form.get("answer")
        end_interview = request.form.get("end_interview")
        idx = session["idx"]
        questions = session.get("questions", [])
        if idx < len(questions):
            session["answers"].append({"question": questions[idx], "answer": answer})
        else:
            session["answers"].append({"question": "Không có câu hỏi.", "answer": answer})
        session["messages"].append({"role": "user", "text": answer})
        idx += 1
        session["idx"] = idx
        print(f"Answer {idx}: {answer}")

        # Nếu có param end_interview thì thực hiện logic kết thúc phỏng vấn
        if end_interview:
            print("Kết thúc phỏng vấn")
            feedback_text = evaluate_candidate_responses_voice(
                session["job_title"], session["answers"], language=session.get("language", "vi")
            )
            qa_pairs = [{"question": answer["question"], "answer": answer["answer"]} for answer in session["answers"]]
            transcription = feedback_text.get("text", "")
            emotions = feedback_text.get("emotions", "neutral")
            confidence_score = feedback_text.get("confidence_score", 0.8)
            session["messages"].append({"role": "bot", "text": f"\U0001f4dd Đánh giá tổng quan:\n{feedback_text}"})
            summary_audio = f"summary_{session_id}.mp3"
            speak(feedback_text["audio"], filename=summary_audio, language=session.get("language", "vi"))
            feedback = feedback_text.get("text", "") 
            logs = session.get("messages", [])  
            summary = feedback_text.get("summary", "")  
            session["feedback"] = feedback 

            save_interview_audio_data(
                session["session_id"],
                session["name"],
                session.get("job_title", ""),
                session.get("job_description", ""),
                audio_file_path=os.path.join("static", "audio", summary_audio),  
                transcription=transcription,
                emotions=emotions,
                confidence_score=confidence_score,
                feedback=feedback,  
                logs=logs,  
                summary=summary  
            )

            save_interview_script(session["session_id"], session["messages"])

            save_evaluation_data(
                session["session_id"], 
                session["name"], 
                emotions,  
                confidence_score,  
                feedback,  
                session.get("messages", []),  
                feedback_text.get("summary", "")  
            )

            technical_score = calculate_technical_score(session["answers"])
            communication_score = calculate_communication_score(session["answers"])
            fit_score = calculate_fit_score(session["answers"], session["job_title"])
           
            save_interview_history_cv(
                session["session_id"],  
                session["name"],  
                session["job_title"],  
                datetime.utcnow(),  
                session["questions"],  
                session["answers"],  
                session["feedback"], 
                {"technical_score": technical_score,  
                "communication_score": communication_score,  
                "fit_score": fit_score}  
            )

            return render_template("interview_cv.html", messages=session["messages"], audio_file=summary_audio, finished=True, popup_start=False, idx=idx)

        # Nếu không có end_interview thì giữ logic cũ
        if idx >= 5:
            feedback_text = evaluate_candidate_responses_voice(
                session["job_title"], session["answers"], language=session.get("language", "vi")
            )
            qa_pairs = [{"question": answer["question"], "answer": answer["answer"]} for answer in session["answers"]]
            transcription = feedback_text.get("text", "")
            emotions = feedback_text.get("emotions", "neutral")
            confidence_score = feedback_text.get("confidence_score", 0.8)
            session["messages"].append({"role": "bot", "text": f"\U0001f4dd Đánh giá tổng quan:\n{feedback_text}"})
            summary_audio = f"summary_{session_id}.mp3"
            speak(feedback_text["audio"], filename=summary_audio, language=session.get("language", "vi"))
            feedback = feedback_text.get("text", "") 
            logs = session.get("messages", [])  
            summary = feedback_text.get("summary", "")  
            session["feedback"] = feedback 

            save_interview_audio_data(
                session["session_id"],
                session["name"],
                session.get("job_title", ""),
                session.get("job_description", ""),
                audio_file_path=os.path.join("static", "audio", summary_audio),  
                transcription=transcription,
                emotions=emotions,
                confidence_score=confidence_score,
                feedback=feedback,  
                logs=logs,  
                summary=summary  
            )

            save_interview_script(session["session_id"], session["messages"])

            save_evaluation_data(
                session["session_id"], 
                session["name"], 
                emotions,  
                confidence_score,  
                feedback,  
                session.get("messages", []),  
                feedback_text.get("summary", "")  
            )

            technical_score = calculate_technical_score(session["answers"])
            communication_score = calculate_communication_score(session["answers"])
            fit_score = calculate_fit_score(session["answers"], session["job_title"])
           
            save_interview_history_cv(
                session["session_id"],  
                session["name"],  
                session["job_title"],  
                datetime.utcnow(),  
                session["questions"],  
                session["answers"],  
                session["feedback"], 
                {"technical_score": technical_score,  
                "communication_score": communication_score,  
                "fit_score": fit_score}  
            )

            return render_template("interview_cv.html", messages=session["messages"], audio_file=summary_audio, finished=True, popup_start=False, idx=idx)

        next_question = session["questions"][idx]
        print(f"Question {idx + 1}: {next_question}")  
        session["messages"].append({"role": "bot", "text": f"\u2753 Câu hỏi {idx+1}: {next_question}"})
        question_audio = f"question_{session_id}_{idx}.mp3"
        speak(next_question, filename=question_audio)
        return render_template("interview_cv.html", messages=session["messages"], audio_file=question_audio, finished=False, popup_start=False, idx=idx)

    questions = session.get("questions", [])
    if questions:
        question_audio = f"question_{session_id}_{idx}.mp3"
        return render_template("interview_cv.html", messages=session["messages"], audio_file=question_audio, popup_start=False,  finished=False, idx=idx)

    return redirect("/upload_cv")

@app.route("/api/end_interview", methods=["POST"])
def api_end_interview():
    session["finished"] = True
    session_id = session.get("session_id")
    name = session.get("name")
    job_title = session.get("job_title")
    job_description = session.get("job_description", "")
    language = session.get("language", "vi")
    answers = session.get("answers", [])
    questions = session.get("questions", [])
    messages = session.get("messages", [])

    # Luôn thực hiện đánh giá và lưu dữ liệu khi gọi API này
    feedback_text = evaluate_candidate_responses_voice(
        job_title, answers, language=language
    )
    qa_pairs = [{"question": ans["question"], "answer": ans["answer"]} for ans in answers]
    transcription = feedback_text.get("text", "")
    emotions = feedback_text.get("emotions", "neutral")
    confidence_score = feedback_text.get("confidence_score", 0.8)
    summary_audio = f"summary_{session_id}.mp3"
    speak(feedback_text["audio"], filename=summary_audio, language=language)
    feedback = feedback_text.get("text", "")
    logs = messages
    summary = feedback_text.get("summary", "")
    session["feedback"] = feedback

    save_interview_audio_data(
        session_id,
        name,
        job_title,
        job_description,
        audio_file_path=os.path.join("static", "audio", summary_audio),
        transcription=transcription,
        emotions=emotions,
        confidence_score=confidence_score,
        feedback=feedback,
        logs=logs,
        summary=summary
    )
    save_interview_script(session_id, messages)
    save_evaluation_data(
        session_id,
        name,
        emotions,
        confidence_score,
        feedback,
        logs,
        summary
    )
    technical_score = calculate_technical_score(answers)
    communication_score = calculate_communication_score(answers)
    fit_score = calculate_fit_score(answers, job_title)
    save_interview_history_cv(
        session_id,
        name,
        job_title,
        datetime.utcnow(),
        questions,
        answers,
        feedback,
        {
            "technical_score": technical_score,
            "communication_score": communication_score,
            "fit_score": fit_score
        }
    )
    result = collection.insert_one({
        "session_id": session_id,
        "name": name,
        "job_title": job_title,
        "job_description": job_description,
        "language": language,
        "qa_pairs": qa_pairs,
        "feedback": feedback,
        "emotions": emotions,
        "confidence_score": confidence_score,
        "summary": summary,
        "timestamp": datetime.utcnow()
    })
    return jsonify({
        "status": "success",
        "message": "Phỏng vấn đã kết thúc!",
        "session_id": session_id,
        "interview_id": str(result.inserted_id)
    })

@app.route("/results")
def results():
    session_id = session.get("session_id") 
    
   
    questions = session.get("questions", [])
    answers = session.get("answers", [])
    qa_pairs = list(zip(questions, answers))
    feedback = session.get("feedback", "")
    audio_file = get_audio_file(session_id)
    print("Questions in session: ", questions)
    print("Answers in session: ", answers)
    print("Feedback in session: ", feedback)

    if not questions or not feedback:
        return redirect("/")  
    
    return render_template("results.html", questions=questions, answers=answers, qa_pairs=qa_pairs, feedback=feedback, audio_file=audio_file)




@app.route('/static/audio/<filename>')
def serve_audio(filename):
    try:
        audio_file_path = os.path.join(app.root_path, 'static', 'audio', filename)
        if os.path.exists(audio_file_path):
            return send_from_directory(os.path.join(app.root_path, 'static', 'audio'), filename)
        else:
            abort(404) 
    except Exception as e:
        print(f"Lỗi khi phục vụ tệp âm thanh: {e}")
        abort(404)


@app.route("/download_report")
def download_report():
    font_path = os.path.join(os.path.dirname(__file__), 'static', 'fonts', 'dejavu-sans.book.ttf')
    print("Font path: ", font_path)
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', font_path, uni=True)
    pdf.set_font('DejaVu', '', 12)
    pdf.cell(200, 10, txt="Báo cáo Kết quả Phỏng vấn", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Tên ứng viên: {session.get('name')}", ln=True)
    pdf.cell(200, 10, txt=f"Vị trí ứng tuyển: {session.get('job_title')}", ln=True)
    pdf.cell(200, 10, txt="Câu hỏi và câu trả lời:", ln=True)
    for i in range(len(session["questions"])):
        question = session["questions"][i]
        answer = session["answers"][i]["answer"] if i < len(session["answers"]) else "Không có câu trả lời."
        pdf.multi_cell(0, 10, txt=f"Q{i+1}: {question}\nA{i+1}: {answer}\n")

    pdf.cell(200, 10, txt="Đánh giá tổng quan:", ln=True)
    pdf.multi_cell(0, 10, txt=session.get("feedback", "Không có đánh giá."))
    file_path = os.path.join('static', 'interview_report.pdf')
    pdf.output(file_path)
    return send_file(file_path, as_attachment=True, download_name="interview_report.pdf", mimetype="application/pdf")


@app.route("/dashboard")
def dashboard():
    name = session.get("name", "Ứng viên ABC")
    job_title = session.get("job_title", "Product Designer")
    interview_date = session.get("interview_date", "10 Aug 2025")
    feedback = session.get("feedback", "Phản hồi chưa có.")
    name = session.get("name", "Ứng viên ABC")
    job_title = session.get("job_title", "Product Designer")
    interview_date = session.get("interview_date", "10 Aug 2025")
    total_questions = len(session.get("questions", []))  
    answered_questions = len(session.get("answers", []))  
    score = (answered_questions / total_questions) * 100 if total_questions > 0 else 0  
    technical_score_data = {
        'data': [{
            'type': 'indicator',
            'mode': 'gauge+number+delta',
            'value': score,
            'title': {'text': f""},
            'gauge': {
                'axis': {'range': [None, 100]},
                'steps': [
                    {'range': [0, 50], 'color': 'red'},
                    {'range': [50, 80], 'color': 'orange'},
                    {'range': [80, 100], 'color': 'green'}
                ],
                'bar': {'color': 'green'}
            },
            'number': {'suffix': '%'}
        }],
        'layout': {
            'annotations': [{
                'x': 0.5,  
                'y': -0.1,  
                'xref': 'paper',
                'yref': 'paper',
                'text': f" {answered_questions} câu trả lời",  
                'showarrow': False,
                'font': {'size': 20, 'color': 'black'}
            }]
        }
    }
    communication_skills_data = {
        'data': [{
            'type': 'scatterpolar',
            'r': [4, 3, 4, 2, 3],
            'theta': ['Fluency', 'Minimal Filler Words', 'Engagement', 'Confidence', 'Pace'],
            'fill': 'toself'
        }]
    }
    return render_template(
        'dashboard.html',  
        name=name,
        job_title=job_title,
        interview_date=interview_date,
        feedback=feedback,
        technical_score_data=technical_score_data,
        communication_skills_data=communication_skills_data,
        total_questions=total_questions,
        answered_questions=answered_questions,
        score=score,
        download_report_url=url_for('download_report')  
    )
  

  

collection_history_cv = mongo.db.collection_history_cv
@app.route("/history")
def history():
    interviews = list(mongo.db.interview_history_cv.find())  
    for interview in interviews:
        interview['qa_pairs'] = list(zip(interview['questions'], interview['answers']))

    return render_template("history_cv.html", interviews=interviews)

@app.route("/view_report/<session_id>")
def view_report(session_id):
    interview = mongo.db.interview_history_cv.find_one({"session_id": session_id})
  
    if not interview:
        return "Phiên phỏng vấn không tồn tại", 404 
  
    return render_template("view_report.html", interview=interview)


@app.route("/start_interview", methods=["POST"])
def start_interview():
    session.clear()
    name = request.form['name']
    job_title = request.form['job_title']
    level = request.form.get('level', 'Fresher')
    language = request.form.get('language', 'vi')
    job_description = request.form.get('job_description', '')

    session_id = str(uuid.uuid4())
    session["session_id"] = session_id
    session["name"] = name
    session["job_title"] = job_title
    session["level"] = level
    session["language"] = language
    session["job_description"] = job_description
    session["messages"] = []
    session["finished"] = False
    session["invalid_count"] = 0

    greeting = f"Xin chào, tôi là MONA HR. Rất vui được phỏng vấn bạn <strong>{name}</strong> cho vị trí <strong>{job_title}</strong>!" if language == "vi" else f"👋 Hello {name}, I'm your AI recruiter. Excited to interview you for the <strong>{job_title}</strong> position!"
    instructions = " Tôi sẽ lần lượt đưa ra 7 câu hỏi liên quan đến vị trí và mô tả công việc của bạn. Bạn trả lời tự tin nhé!" if language == "vi" else "💬 I will ask questions one by one. Please answer naturally."
    session["messages"].append({"role": "bot", "text": greeting})
    session["messages"].append({"role": "bot", "text": instructions})

    user_info = {
        "name": name,
        "job_title": job_title,
        "level": level,
        "language": language,
        "job_description": job_description
    }
    first_question = ask_question(user_info, session["messages"])
    session["messages"].append({"role": "bot", "text": first_question})

    interview_history[session_id] = {"name": name, "job": job_title}

    return redirect(url_for("interview"))
@app.route("/interview", methods=["GET", "POST"])
def interview():
   
    if "messages" not in session:
        return redirect("/form")
    messages = session.get("messages", [])
    name = session.get("name")
    job_title = session.get("job_title")
    level = session.get("level")
    language = session.get("language", "vi")
    finished = session.get("finished", False)
    job_description = session.get("job_description", "")
    invalid_count = session.get("invalid_count", 0)

    user_info = {
        "name": name,
        "job_title": job_title,
        "level": level,
        "language": language,
        "job_description": job_description
    }

    if request.method == "POST" and not finished:
        answer = request.form.get("answer", "").strip()
        if answer:
            messages.append({"role": "user", "text": answer})
            session["messages"] = messages
                        
            if any(
                msg["role"] == "user" and any(keyword in msg["text"].lower() for keyword in ["thoát", "không muốn tiếp tục", "exit"])
                for msg in messages[-2:]
            ):
                messages.append({
                    "role": "bot",
                    "text": f"<div class='alert alert-info'><strong>✅ Chào {name}, cuộc phỏng vấn đã kết thúc theo yêu cầu của bạn.</strong><br>Hẹn gặp lại bạn trong những buổi phỏng vấn khác. Chúc bạn thật nhiều may mắn trên hành trình sự nghiệp!</div>"
                })
                session["finished"] = True
                session["messages"] = messages
                return render_template("interview.html", messages=messages, finished=True, history=get_all_histories())

            last_question = next((m["text"] for m in reversed(messages) if m["role"] == "bot" and not m["text"].startswith("👋")), None)
            if last_question:
                feedback = get_feedback_on_answer(last_question, answer, language)
                followup = follow_up(answer, {
                    "last_question": last_question,
                    "job_title": job_title,
                    "language": language,
                    "job_description": job_description,
                    "name": name
                })

                if followup:
                 messages.append({"role": "bot", "text": followup})
                is_invalid = any(kw in feedback.lower() for kw in (
                    ["mơ hồ", "không rõ", "không hiểu", "vague", "unclear", "not specific"]
                    if language == "vi" else
                    ["vague", "unclear", "not specific", "unsuitable"]
                ))

                if is_invalid:
                    invalid_count += 1
                else:
                    invalid_count = 0
                
                session["invalid_count"] = invalid_count
                if invalid_count >= 10:
                    qa_pairs = []
                    q = None
                    for msg in messages:
                        if msg["role"] == "bot" and not msg["text"].startswith("👋"):
                            q = msg["text"]
                        elif msg["role"] == "user" and q:
                            qa_pairs.append({"question": q, "answer": msg["text"]})
                            q = None

                    evaluation = evaluate_candidate_responses(job_title, messages, language)
                    messages.append({
                        "role": "bot",
                        "text": f"<div class='card'><div class='card-body'><h5>{' Đánh giá tổng quan:' if language == 'vi' else '📝 Final Evaluation:'}</h5><p>{evaluation}</p></div></div>"
                    })
                    session["finished"] = True

                    collection.insert_one({
                        "session_id": session.get("session_id"),
                        "name": name,
                        "job_title": job_title,
                        "level": level,
                        "language": language,
                        "job_description": job_description,
                        "qa_pairs": qa_pairs,
                        "evaluation": evaluation,
                        "timestamp": datetime.utcnow()
                    })

                    session["messages"] = messages
                    return render_template("interview.html", messages=messages, finished=True, history=get_all_histories())
                if not followup:
                    question_difficulty = len([m for m in messages if m["role"] == "bot" and not m["text"].startswith("👋")])
                    next_q = ask_question(user_info, messages, difficulty=question_difficulty)
                    messages.append({"role": "bot", "text": next_q})
            print(f"Invalid count: {invalid_count}")
            print(f"Messages: {messages}")

        session["messages"] = messages
        if should_terminate_early(messages, user_info):
            qa_pairs = []
            q = None
            for msg in messages:
                if msg["role"] == "bot" and not msg["text"].startswith("👋"):
                    q = msg["text"]
                elif msg["role"] == "user" and q:
                    qa_pairs.append({"question": q, "answer": msg["text"]})
                    q = None

            evaluation = evaluate_candidate_responses(job_title, messages, language)
            messages.append({
                "role": "bot",
                "text": f"<div class='card'><div class='card-body'><h5>{' Đánh giá tổng quan:' if language == 'vi' else '📝 Final Evaluation:'}</h5><p>{evaluation}</p></div></div>"
            })
            session["finished"] = True

            collection.insert_one({
                "session_id": session.get("session_id"),
                "name": name,
                "job_title": job_title,
                "level": level,
                "language": language,
                "job_description": job_description,
                "qa_pairs": qa_pairs,
                "evaluation": evaluation,
                "timestamp": datetime.utcnow()
            })

            session["messages"] = messages
            return render_template("interview.html", messages=messages, finished=True, history=get_all_histories())
    return render_template("interview.html", messages=messages, finished=session.get("finished", False), history=get_all_histories())

from bson import ObjectId
from flask import render_template

@app.route("/end_interview/<session_id>", methods=["POST"])
def end_interview(session_id):
    session["finished"] = True
    messages = session.get("messages", [])
    user_info = {
        "name": session.get("name"),
        "job_title": session.get("job_title"),
        "level": session.get("level"),
        "language": session.get("language", "vi"),
        "job_description": session.get("job_description", ""),
    }

    evaluation = evaluate_candidate_responses(user_info["job_title"], messages, user_info["language"])
    qa_pairs = []
    q = None
    for msg in messages:
        if msg["role"] == "bot" and not msg["text"].startswith("👋"):
            q = msg["text"]
        elif msg["role"] == "user" and q:
            qa_pairs.append({"question": q, "answer": msg["text"]})
            q = None

    result = collection.insert_one({
        "session_id": session.get("session_id"),
        "name": user_info["name"],
        "job_title": user_info["job_title"],
        "level": user_info["level"],
        "language": user_info["language"],
        "job_description": user_info["job_description"],
        "qa_pairs": qa_pairs,
        "evaluation": evaluation,
        "timestamp": datetime.utcnow()
    })
    return jsonify({
        "status": "success",
        "message": "Phỏng vấn đã kết thúc!",
        "session_id": session.get("session_id"),
        "interview_id": str(result.inserted_id)
    })

@app.route("/result/<id>")
def show_result(id):
    interview = collection.find_one({"_id": ObjectId(id)})
    if not interview:
        return "Không tìm thấy phỏng vấn"

    qa_pairs = interview.get("qa_pairs", [])
    job_title = interview.get("job_title", "")
    language = interview.get("language", "vi")
    name = interview.get("name", "")
    job_description = interview.get("job_description", "")
    email = interview.get("email", "N/A")
    interview_datetime = interview.get("interview_datetime", "")
    messages = []
    for qa in qa_pairs:
        messages.append({"role": "bot", "text": qa["question"]})
        messages.append({"role": "user", "text": qa["answer"]})

    feedback = evaluate_candidate_responses(job_title, messages, language)

    suggested_answers = []
    for qa in qa_pairs:
        # Lấy thông tin user_info và đảm bảo không thiếu trường quan trọng
        job_title_val = job_title if job_title else interview.get("job_title", "")
        level_val = interview.get("level", None)
        if not level_val or not isinstance(level_val, str) or not level_val.strip():
            level_val = "Junior"
        job_description_val = job_description if job_description else interview.get("job_description", "")
        if not job_title_val or not job_description_val:
            # Nếu vẫn thiếu thì bỏ qua suggest answer cho câu này
            suggested_answers.append("Không đủ thông tin để gợi ý trả lời.")
            continue
        user_info = {
            "job_title": job_title_val,
            "level": level_val,
            "job_description": job_description_val
        }
        suggested_answer = get_suggested_answer(qa["question"], qa["answer"], language, user_info)
        suggested_answers.append(suggested_answer)

    return render_template("result.html", 
                           feedback=feedback,
                           qa_pairs=qa_pairs,
                           suggested_answers=suggested_answers,
                           name=name,
                           job_title=job_title,
                           job_description=job_description,
                           email=email,
                           language=language,
                           interview_datetime=interview_datetime)

print("Received ID:", id)
print("Interview Data:", interview)

@app.route('/process_cv', methods=['POST'])
def process_cv():
    try:
        cv_file = request.files['cv']
        questions = analyze_cv_and_generate_questions(cv_file)
        return jsonify({"questions": questions}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/resume_form')
def resume_form():
    cv_id = request.args.get('cv_id')
    cv_data = None
    
    if cv_id:
        try:
            from db import db
            from bson import ObjectId
            cv_collection = db["cv_data"]
            cv_data = cv_collection.find_one({"_id": ObjectId(cv_id)})
        except Exception as e:
            print(f"Lỗi khi lấy dữ liệu CV: {str(e)}")
            cv_data = None
    
    return render_template('resume_form.html', cv_data=cv_data) 

@app.route('/generate_objective', methods=['POST'])
def generate_objective():
    try:
        
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Không có dữ liệu mục tiêu nghề nghiệp.'}), 400
        
        query = data['query'] 
        objective_json_file = 'data/Object_data.json' 
        response = perform_rag_task(objective_json_file, query)
        if not response:
            return jsonify({'error': 'Không thể tạo mục tiêu nghề nghiệp, vui lòng thử lại sau.'}), 500
        return jsonify({'response': response})

    except Exception as e:
        print(f"Lỗi xảy ra: {str(e)}")
        return jsonify({'error': 'Đã xảy ra lỗi, vui lòng thử lại.'}), 500





@app.route('/generate_experience', methods=['POST'])
def generate_experience():
    try:
        data = request.get_json()

        # Kiểm tra dữ liệu đầu vào
        if not data or 'job_desc' not in data:
            return jsonify({'error': 'Không có mô tả công việc.'}), 400

        query = data['job_desc']  # Lấy nội dung mô tả công việc
        experience_json_file = 'data/experience_data.json'  # File JSON chứa dữ liệu mẫu kinh nghiệm

        # Gọi hàm xử lý RAG dành riêng cho kinh nghiệm làm việc
        response = perform_rag_experience_task(experience_json_file, query)

        if not response:
            return jsonify({'error': 'Không thể tạo nội dung kinh nghiệm làm việc, vui lòng thử lại sau.'}), 500

        return jsonify({'response': response})

    except Exception as e:
        print(f"Lỗi xảy ra: {str(e)}")
        return jsonify({'error': 'Đã xảy ra lỗi, vui lòng thử lại.'}), 500
@app.route('/static/<filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/save_cv', methods=['POST'])
def save_cv():
    try:
        data = request.get_json()
        
        # Kiểm tra dữ liệu đầu vào
        if not data:
            return jsonify({'error': 'Không có dữ liệu CV.'}), 400
        
        # Tạo CV data với timestamp
        cv_data = {
            'personal_info': {
                'name': data.get('name', ''),
                'position': data.get('position', ''),
                'phone': data.get('phone', ''),
                'email': data.get('email', ''),
                'website': data.get('website', ''),
                'objective': data.get('objective', '')
            },
            'work_experience': {
                'company': data.get('company', ''),
                'job_date': data.get('job_date', ''),
                'job_title': data.get('job_title', ''),
                'job_description': data.get('job_description', ''),
                'generated_experience': data.get('generated_experience', '')
            },
            'education': {
                'school': data.get('school', ''),
                'edu_date': data.get('edu_date', ''),
                'major': data.get('major', ''),
                'gpa': data.get('gpa', '')
            },
            'project': {
                'project_name': data.get('project_name', ''),
                'project_date': data.get('project_date', ''),
                'project_desc': data.get('project_desc', '')
            },
            'skills': data.get('skills', ''),
            'featured_skills': {
                'skill1': data.get('featured_skill1', ''),
                'skill2': data.get('featured_skill2', '')
            },
            'created_at': datetime.now(),
            'user_session': session.get('session_id', str(uuid.uuid4()))
        }
        
        # Lưu vào database
        from db import db
        cv_collection = db["cv_data"]
        result = cv_collection.insert_one(cv_data)
        
        return jsonify({
            'success': True,
            'message': 'CV đã được lưu thành công!',
            'cv_id': str(result.inserted_id)
        })
        
    except Exception as e:
        print(f"Lỗi khi lưu CV: {str(e)}")
        return jsonify({'error': 'Đã xảy ra lỗi khi lưu CV.'}), 500

@app.route('/download_cv', methods=['POST'])
def download_cv():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Không có dữ liệu CV để tải xuống.'}), 400
            
        # Tạo PDF từ dữ liệu CV
        font_path = os.path.join(os.path.dirname(__file__), 'static', 'fonts', 'dejavu-sans.book.ttf')
        
        pdf = FPDF()
        pdf.add_page()
        
        # Thêm font hỗ trợ tiếng Việt
        if os.path.exists(font_path):
            pdf.add_font('DejaVu', '', font_path, uni=True)
            pdf.set_font('DejaVu', '', 14)
        else:
            pdf.set_font('Arial', 'B', 14)
        
        # Header - Thông tin cá nhân
        name = data.get('name', 'Họ và tên')
        pdf.cell(0, 10, name.upper(), ln=True, align='C')
        pdf.set_font('DejaVu', '', 12) if os.path.exists(font_path) else pdf.set_font('Arial', '', 12)
        
        position = data.get('position', '')
        phone = data.get('phone', '')
        email = data.get('email', '')
        website = data.get('website', '')
        
        # Thông tin liên hệ
        contact_line = f"{position} | {phone} | {email}"
        if website:
            contact_line += f" | {website}"
        pdf.cell(0, 8, contact_line, ln=True, align='C')
        pdf.ln(5)
        
        # Objective
        objective = data.get('objective', '')
        if objective:
            pdf.set_font('DejaVu', 'B', 12) if os.path.exists(font_path) else pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'OBJECTIVE', ln=True)
            pdf.set_font('DejaVu', '', 11) if os.path.exists(font_path) else pdf.set_font('Arial', '', 11)
            pdf.multi_cell(0, 6, objective)
            pdf.ln(3)
        
        # Work Experience
        company = data.get('company', '')
        job_title = data.get('job_title', '')
        job_date = data.get('job_date', '')
        generated_experience = data.get('generated_experience', '')
        
        if company or job_title:
            pdf.set_font('DejaVu', 'B', 12) if os.path.exists(font_path) else pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'WORK EXPERIENCE', ln=True)
            pdf.set_font('DejaVu', '', 11) if os.path.exists(font_path) else pdf.set_font('Arial', '', 11)
            
            if company:
                pdf.cell(0, 6, f"Company: {company}", ln=True)
            if job_title:
                pdf.cell(0, 6, f"Position: {job_title}", ln=True)
            if job_date:
                pdf.cell(0, 6, f"Duration: {job_date}", ln=True)
            if generated_experience:
                pdf.multi_cell(0, 6, f"Description: {generated_experience}")
            pdf.ln(3)
        
        # Education
        school = data.get('school', '')
        major = data.get('major', '')
        edu_date = data.get('edu_date', '')
        gpa = data.get('gpa', '')
        
        if school or major:
            pdf.set_font('DejaVu', 'B', 12) if os.path.exists(font_path) else pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'EDUCATION', ln=True)
            pdf.set_font('DejaVu', '', 11) if os.path.exists(font_path) else pdf.set_font('Arial', '', 11)
            
            if school:
                pdf.cell(0, 6, f"School: {school}", ln=True)
            if major:
                pdf.cell(0, 6, f"Major: {major}", ln=True)
            if edu_date:
                pdf.cell(0, 6, f"Graduation: {edu_date}", ln=True)
            if gpa:
                pdf.cell(0, 6, f"GPA: {gpa}", ln=True)
            pdf.ln(3)
        
        # Projects
        project_name = data.get('project_name', '')
        project_date = data.get('project_date', '')
        project_desc = data.get('project_desc', '')
        
        if project_name:
            pdf.set_font('DejaVu', 'B', 12) if os.path.exists(font_path) else pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'PROJECTS', ln=True)
            pdf.set_font('DejaVu', '', 11) if os.path.exists(font_path) else pdf.set_font('Arial', '', 11)
            
            pdf.cell(0, 6, f"Project: {project_name}", ln=True)
            if project_date:
                pdf.cell(0, 6, f"Duration: {project_date}", ln=True)
            if project_desc:
                pdf.multi_cell(0, 6, f"Description: {project_desc}")
            pdf.ln(3)
        
        # Skills
        skills = data.get('skills', '')
        featured_skill1 = data.get('featured_skill1', '')
        featured_skill2 = data.get('featured_skill2', '')
        
        if skills or featured_skill1 or featured_skill2:
            pdf.set_font('DejaVu', 'B', 12) if os.path.exists(font_path) else pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'SKILLS', ln=True)
            pdf.set_font('DejaVu', '', 11) if os.path.exists(font_path) else pdf.set_font('Arial', '', 11)
            
            if skills:
                pdf.multi_cell(0, 6, skills)
            if featured_skill1:
                pdf.cell(0, 6, f"Featured Skill 1: {featured_skill1}", ln=True)
            if featured_skill2:
                pdf.cell(0, 6, f"Featured Skill 2: {featured_skill2}", ln=True)
        
        # Tạo tên file với timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"CV_{name.replace(' ', '_')}_{timestamp}.pdf"
        file_path = os.path.join('static', 'pdf', filename)
        
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Lưu file PDF
        pdf.output(file_path)
        
        return send_file(file_path, as_attachment=True, download_name=filename, mimetype="application/pdf")
        
    except Exception as e:
        print(f"Lỗi khi tạo PDF: {str(e)}")
        return jsonify({'error': 'Đã xảy ra lỗi khi tạo file PDF.'}), 500




@app.route('/cv_history')
def cv_history():
    """Lấy danh sách CV đã lưu"""
    try:
        from db import db
        cv_collection = db["cv_data"]
        cvs = list(cv_collection.find().sort("created_at", -1))
        
        # Chuyển đổi ObjectId thành string
        for cv in cvs:
            cv['_id'] = str(cv['_id'])
            
        return render_template('cv_history.html', cvs=cvs)
    except Exception as e:
        print(f"Lỗi khi lấy danh sách CV: {str(e)}")
        return render_template('cv_history.html', cvs=[])

@app.route('/cv_detail/<cv_id>')
def cv_detail(cv_id):
    """Hiển thị chi tiết CV đã lưu"""
    try:
        from db import db
        from bson import ObjectId
        cv_collection = db["cv_data"]
        cv = cv_collection.find_one({"_id": ObjectId(cv_id)})
        
        if not cv:
            return "CV không tồn tại", 404
            
        return render_template('cv_detail.html', cv=cv)
    except Exception as e:
        print(f"Lỗi khi lấy chi tiết CV: {str(e)}")
        return "Có lỗi xảy ra", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)