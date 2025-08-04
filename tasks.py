import os
from stat import FILE_ATTRIBUTE_COMPRESSED
from groq import Groq
from PyPDF2 import PdfReader
from docx import Document
import re
import os
from PyPDF2 import PdfReader
from docx import Document
import langchain_ollama
from llm import ask_llama
from rag_pipeline import retrieve_relevant_chunks 
from utils import extract_text_from_cv
from embedding import create_faiss_index, add_embeddings_to_faiss
import faiss
from langchain_ollama import OllamaEmbeddings
from langchain.chains import RetrievalQA
import json
import numpy as np
from flask import session
from langdetect import detect



client = Groq(api_key=os.getenv("GROQ_API_KEY"))



def ask_question(user_info, history, difficulty=0):
    job_title = user_info["job_title"]
    level = user_info["level"]
    language = user_info.get("language", "vi")
    job_description = user_info.get("job_description", "")

    dialogue = "\n".join([
        f"{'HR' if msg['role'] == 'bot' else ('Ứng viên' if language == 'vi' else 'Candidate')}: {msg['text']}"
        for msg in history[-6:]
    ])

    difficulty_note = (
        "Câu hỏi nên đơn giản, để hiểu được kiến thức cơ bản." if difficulty < 3 else
        "Câu hỏi nên ở mức trung bình, kiểm tra kiến thức và kỹ năng thực tế." if difficulty < 6 else
        "Câu hỏi nên nâng cao, đánh giá khả năng giải quyết vấn đề chuyên sâu."
    )

    if language == "vi":
        prompt = f"""
        Bạn là chuyên gia tuyển dụng. Vai trò của bạn là đặt câu hỏi PHỎNG VẤN BẰNG TIẾNG VIỆT cho ứng viên vị trí {job_title}, cấp độ {level}.
        Mô tả công việc: {job_description}
        {difficulty_note}
        Đoạn hội thoại gần đây:
        {dialogue}
        Hãy đặt 1 câu hỏi phỏng vấn tiếp theo duy nhất. Viết bằng TIẾNG VIỆT, không giới thiệu, không đánh số.
        """
    else:
        prompt = f"""
        You are an HR expert. Your role is to ask INTERVIEW QUESTIONS IN ENGLISH for the position {job_title}, level {level}.
        Job description: {job_description}
        {difficulty_note}
        Dialogue history:
        {dialogue}
        Ask one next interview question only. Be concise, in ENGLISH. No intro, no numbering.
        """

    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "You are an expert HR interviewer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return completion.choices[0].message.content.strip()



def get_suggested_answer(question, user_answer, language, user_info):
    job_title = user_info.get("job_title") 
    level = user_info.get("level")  
    job_description = user_info.get("job_description")  

   
    if not job_title or not level or not job_description:
        raise ValueError("Thiếu thông tin quan trọng trong user_info")

    
    if language == "vi":
        prompt = f"""
        Câu hỏi: {question}
        Câu trả lời của ứng viên: {user_answer}
        Gợi ý một câu trả lời tốt hơn, chi tiết và cụ thể hơn cho câu hỏi trên.Bắt buộc sinh câu trả lời tốt hơn bằng tiếng việt.Tuyệt đối không có tiếng anh vào. 
        Câu trả lời gợi ý nên thể hiện kiến thức và kỹ năng của ứng viên một cách rõ ràng và thuyết phục.
        """
    else:  
        prompt = f"""
        Question: {question}
        Candidate's answer: {user_answer}
        Suggest a better, more detailed and specific answer to the question above.
        The suggested answer should clearly demonstrate the candidate's knowledge and skills in a convincing way.
        """


    logic_response = client.chat.completions.create(
        model="llama3-8b-8192",  
        messages=[
            {"role": "system", "content": "You are an expert at suggesting better interview answers."},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0.7  
    )

   
    print(logic_response)

    
    try:
        return logic_response.choices[0].message.content.strip() 
    except AttributeError:
        return "Không có câu trả lời gợi ý."  



def follow_up(answer, context):
    language = context.get("language", "vi")
    last_question = context.get("last_question", "")
    job_title = context.get("job_title", "")
    job_description = context.get("job_description", "")

    # Bước 1: Kiểm tra độ khớp giữa câu hỏi và câu trả lời
    logic_prompt = f"""
    Dưới đây là một cặp câu hỏi và câu trả lời trong buổi phỏng vấn:

    - Câu hỏi: "{last_question}"
    - Trả lời: "{answer}"

    Theo bạn, câu trả lời này có đúng trọng tâm và đầy đủ để phản hồi cho câu hỏi không?

    Trả lời DUY NHẤT 1 TỪ:
    - "CÓ" nếu đúng và rõ ràng
    - "KHÔNG" nếu không trả lời đúng trọng tâm hoặc còn mơ hồ
    """

    logic_response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "Bạn là chuyên gia đánh giá độ phù hợp giữa câu hỏi và câu trả lời."},
            {"role": "user", "content": logic_prompt.strip()}
        ],
        temperature=0
    )

    logic_decision = logic_response.choices[0].message.content.strip().lower()

    
    if logic_decision == "có" and len(answer.strip().split()) >= 10:
        return None

    #  Sinh câu hỏi follow-up 
    if language == "vi":
        prompt = f"""
        Bạn là chuyên gia tuyển dụng cho vị trí {job_title}.
        Ứng viên vừa trả lời chưa rõ cho câu hỏi: "{last_question}"
        Câu trả lời là: "{answer}"

        Mô tả công việc: {job_description}

        Hãy viết một câu hỏi follow-up duy nhất bằng tiếng Việt để khai thác sâu hơn kỹ năng, kinh nghiệm hoặc tư duy của ứng viên.
        - KHÔNG mở đầu, KHÔNG đánh số, KHÔNG xin phép
        - Ưu tiên sát nội dung công việc
        """
    else:
        prompt = f"""
        You are a recruiter hiring for the position of {job_title}.
        The candidate gave a vague answer to the question: "{last_question}"
        Their answer was: "{answer}"

        Job description: {job_description}

        Write ONE follow-up question in English to go deeper into the candidate’s skill, experience, or mindset.
        - Do NOT include introduction or numbering.
        - Be relevant and specific.
        """

    followup_response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "Bạn là chuyên gia phỏng vấn giàu kinh nghiệm."},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0.7
    )

    return followup_response.choices[0].message.content.strip()

def get_feedback_on_answer(question, answer, language="vi"):
    prompt_vi = f"""
    Bạn là chuyên gia tuyển dụng.
    Câu hỏi: {question}
    Trả lời của ứng viên: {answer}

    Hãy nhận xét ngắn gọn (1 câu), mang tính phản hồi chuyên môn: rõ ràng không, đúng chưa, cần hỏi thêm không.Bắt buộc sinh câu trả lời tốt hơn bằng tiếng việt.Tuyệt đối không có tiếng anh vào.
    Chỉ khi ứng viên thật sự không phù hợp, hãy bắt đầu phản hồi bằng: "KHÔNG PHÙ HỢP:".
    """


    prompt_en = f"""
    You are an HR expert evaluating a candidate's response during an interview.
    Question: {question}
    Candidate's answer: {answer}

    Please give a short (1-sentence) feedback in English.

    - If the candidate is clearly UNSUITABLE for the position, your answer MUST start with "UNSUITABLE:" and explain briefly why.
    - If the candidate gives a suitable or acceptable answer, start with "CLEAR:" and provide a brief evaluation.

    Be concise and professional. Only return the feedback sentence.
    """


    prompt = prompt_vi if language == "vi" else prompt_en

    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "You are a professional interviewer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return completion.choices[0].message.content.strip()


def should_terminate_early(messages, user_info):
    job_title = user_info["job_title"]
    level = user_info["level"]
    language = user_info.get("language", "vi")
    job_description = user_info.get("job_description", "")
    vague_keywords = ["mơ hồ", "không rõ", "chưa biết", "không hiểu", "unclear", "vague", "not specific", "not sure"]
    recent_feedbacks = [m["text"] for m in messages[-6:] if m["role"] == "bot"]
    vague_count = sum(any(kw in fb.lower() for kw in vague_keywords) for fb in recent_feedbacks)
    if vague_count >= 2:
        return True
    bot_questions = [m for m in messages if m["role"] == "bot" and not m["text"].startswith("👋")]

    if len(bot_questions) >= 10:
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
            "text": f"{'📝 Final Evaluation:' if language == 'vi' else '📝 Final Evaluation:'} {evaluation}"
        })

        session["finished"] = True
        session["messages"] = messages

        return True  

   
    return False


def evaluate_candidate_responses(job_title, messages, language="vi"):
    qa_pairs = []
    last_q = None
    for msg in messages:
        if msg["role"] == "bot":
            last_q = msg["text"]
        elif msg["role"] == "user" and last_q:
            qa_pairs.append({"question": last_q, "answer": msg["text"]})
            last_q = None

    answers_text = "\n\n".join([
        f"{'Câu hỏi' if language == 'vi' else 'Question'}: {qa['question']}\n{'Trả lời' if language == 'vi' else 'Answer'}: {qa['answer']}"
        for qa in qa_pairs
    ])

    prompt_vi = f"""
    Bạn là chuyên gia tuyển dụng đang đánh giá ứng viên cho vị trí {job_title}.
    Dưới đây là phần trả lời của ứng viên:

    {answers_text}

    Đánh giá tổng quan:
    Dựa vào câu hỏi và câu trả lời của ứng viên mà bạn đánh giá cho chính xác các yếu tố sau
    1. Mức độ phù hợp với vị trí
    2. Kỹ năng chuyên môn thể hiện
    3. Giao tiếp, logic, thái độ
    4. Gợi ý cải thiện nếu có
    5. Tổng điểm /10
    Lưu ý: Nếu ứng viên trả lời không đủ số câu hỏi quy định thì tuyệt đối không được đánh giá tổng điểm qua 5 điểm trên thang điểm 10
    Trả lời bằng tiếng Việt, ngắn gọn, chuyên nghiệp.Bắt buộc sinh câu trả lời tốt hơn bằng tiếng việt.Tuyệt đối không có tiếng anh vào.
    """

    prompt_en = f"""
    You are a recruiter evaluating a candidate for the position of {job_title}.
    Here are their responses:

    {answers_text}

    Please provide a concise and professional evaluation including:
    1. Suitability for the role
    2. Technical skill demonstrated
    3. Communication, logic, attitude
    4. Suggestions for improvement (if any)
    5. Overall score out of 10

    Answer in English.
    """

    prompt = prompt_vi if language == "vi" else prompt_en

    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "You are an expert recruiter."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return completion.choices[0].message.content.strip()


#phân tích CV


def extract_text_from_pdf(pdf_path):
    text = ""
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def extract_text_from_cv(cv_path):
    ext = cv_path.split(".")[-1].lower()
    if ext == "pdf":
        return extract_text_from_pdf(cv_path)
    elif ext in ["docx", "doc"]:
        return extract_text_from_docx(cv_path)
    else:
        raise ValueError("Unsupported CV file format")


from groq import Groq
import os

# Khởi tạo client Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_cv_and_generate_questions(cv_path, job_title, job_description, answers=None, summarize=False, language="vi"):
    if summarize and answers:
        joined_answers = "\n".join([f"Q: {a['question']}\nA: {a['answer']}" for a in answers])
        prompt = f"{job_title} - {job_description}\n{joined_answers}"

        system_prompt = "Bạn là chuyên gia tuyển dụng, đánh giá ứng viên bằng tiếng Việt." if language == "vi" else "You are a professional recruiter evaluating a candidate in English."

        try:
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error while calling Groq API: {e}")
            return ""

    # Extract CV content
    cv_text = extract_text_from_cv(cv_path)
    context = "\n".join(retrieve_relevant_chunks(cv_text))

    # Prompt by language
    if language == "vi":
        prompt = f"""
Bạn là chuyên gia tuyển dụng cho vị trí {job_title}.
Dưới đây là ngữ cảnh liên quan từ CV và mô tả công việc:

--- MÔ TẢ CÔNG VIỆC ---
{job_description}

--- NGỮ CẢNH TỪ CV ---
{context}

Hãy trả lời 5 câu hỏi phỏng vấn liên quan đến kỹ năng và kinh nghiệm của ứng viên.
Chỉ trả về câu hỏi mà không có bất kỳ phần giới thiệu nào (không nói "Here are 5 questions" hoặc "Dưới đây là các câu hỏi").
"""
        system_prompt = "Bạn là chuyên gia tuyển dụng, soạn câu hỏi phỏng vấn bằng tiếng Việt."
    else:
        prompt = f"""
You are a professional recruiter for the position of {job_title}.
Here is the context from the job description and candidate's CV:

--- JOB DESCRIPTION ---
{job_description}

--- CV CONTEXT ---
{context}

Generate 5 interview questions in English, focused on the candidate's skills and experience.
Do not include any introductory statements like "Here are 5 questions" or "Below are the questions".
Only return the questions, one per line.
"""
        system_prompt = "You are a recruiter generating interview questions in English."

    try:
        # Call LLM
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt.strip()}
            ],
            temperature=0.5
        )

        output = response.choices[0].message.content.strip()

     
        lines = [line for line in output.split("\n") if len(line.strip()) > 5]
        questions = [q.strip("-–•. 1234567890").strip() for q in lines if q.strip()]  # Loại bỏ chuỗi rỗng

        return questions
    except Exception as e:
        print(f"Error while calling Groq API: {e}")
        return []


def evaluate_single_answer(question, answer):
    logic_prompt = f"""Hãy đánh giá mức độ phù hợp và logic của câu trả lời bên dưới với câu hỏi đã cho.
- Câu hỏi: {question}
- Câu trả lời: {answer}
       

Trả lời ngắn gọn bằng tiếng Việt dưới 1 dòng, ví dụ: "Câu trả lời tốt", "Không liên quan", "Thiếu ví dụ", "Logic mờ nhạt".
"""
   

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "Bạn là chuyên gia đánh giá độ phù hợp giữa câu hỏi và câu trả lời."},
            {"role": "user", "content": logic_prompt.strip()}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()

def evaluate_candidate_responses_voice(job_title, answers, language="vi"):
    answers_text = "\n\n".join([
        f"Câu hỏi: {qa['question']}\nTrả lời: {qa['answer']}" if language == "vi"
        else f"Question: {qa['question']}\nAnswer: {qa['answer']}"
        for qa in answers
    ])
    def evaluate_technical_score(answers):
        score = 0
        for answer in answers:
            if "không biết" in answer["answer"] or "chưa từng có kinh nghiệm" in answer["answer"]:
                score += 10 
            elif "không có câu trả lời" in answer["answer"]:
                score += 5 
            else:
                score += 30  
        return score // len(answers) if len(answers) > 0 else 0

    def evaluate_communication_score(answers):
        score = 0
        for answer in answers:
            if "không biết" in answer["answer"] or "không có câu trả lời" in answer["answer"]:
                score += 20  
            elif len(answer["answer"]) < 50: 
                score += 50
            else:
                score += 80  
        return score // len(answers) if len(answers) > 0 else 0

    def evaluate_fit_score(answers):
        score = 0
        for answer in answers:
            if "không biết" in answer["answer"] or "không có câu trả lời" in answer["answer"]:
                score += 20 
            else:
                score += 60  
        return score // len(answers) if len(answers) > 0 else 0

    technical_score = evaluate_technical_score(answers)
    communication_score = evaluate_communication_score(answers)
    fit_score = evaluate_fit_score(answers)

    total_score = (technical_score + communication_score + fit_score) // 3


    if language == "vi":
       
        prompt_text = f"""
        Bạn là một chuyên gia tuyển dụng đang đánh giá ứng viên cho vị trí {job_title}.

        Dưới đây là câu trả lời của ứng viên:

        {answers_text}

        Hãy đưa ra **đánh giá tổng quan** về ứng viên dựa trên các câu trả lời của họ, bao gồm các mục sau:

        1. **Ưu điểm**: Chỉ rõ những điểm mạnh nổi bật của ứng viên từ các câu trả lời.
        2. **Nhược điểm (nếu có)**: Những thiếu sót hoặc các kỹ năng cần cải thiện mà bạn nhận thấy từ các câu trả lời của ứng viên.
        3. **Giọng nói & mức độ tự tin**: Đánh giá ngữ điệu, sự rõ ràng và tự tin trong cách thể hiện câu trả lời của ứng viên.
        4. **Gợi ý cải thiện**: Đưa ra những lời khuyên cụ thể giúp ứng viên cải thiện kỹ năng, cách trả lời và thể hiện sự tự tin hơn.

        **Đồng thời, chấm điểm ứng viên theo các tiêu chí sau (theo thang điểm 0–100%):**

        - **Technical Score**: Đánh giá mức độ hiểu biết chuyên môn và kỹ năng liên quan đến công việc, trên cơ sở các câu trả lời của ứng viên.
        - **Communication Score**: Đánh giá khả năng giao tiếp, cách diễn đạt và sự tương tác của ứng viên trong các câu trả lời.
        - **Fit Score**: Mức độ phù hợp của ứng viên với vị trí ứng tuyển và văn hóa công ty, dựa trên câu trả lời của họ.

        Cuối cùng, đưa ra **tổng điểm** theo thang điểm 5, phản ánh tổng thể năng lực và sự phù hợp của ứng viên với công việc.

        Yêu cầu: Trả lời ngắn gọn, rõ ràng, sử dụng ngôn ngữ chuyên nghiệp và bằng **tiếng Việt**.
        - **Ưu điểm:** (trả lời)
        - **Nhược điểm:** (trả lời)
        - **Giọng nói & mức độ tự tin:** (trả lời)
        - **Gợi ý cải thiện:** (trả lời)
        - **Technical Score:** {technical_score}%
        - **Communication Score:** {communication_score}%
        - **Fit Score:** {fit_score}%
        - **Tổng điểm:** {total_score}/100
        """

        name = session.get("name", "Ứng viên chưa cung cấp tên")
        # Prompt cho phát âm thanh
        prompt_audio = f"""
        Bạn là chuyên gia tuyển dụng. Hãy đánh giá ứng viên cho vị trí {job_title} bằng giọng điệu tự nhiên, như thể bạn đang trò chuyện trực tiếp với ứng viên.

        Xưng hô bắt buộc:
        - Xưng "tôi" và gọi ứng viên là "bạn" xuyên suốt toàn bộ phần nói.
        - Tuyệt đối không sử dụng các cách xưng hô khác như: "em", "anh", "chị", "ứng viên", v.v.
        - Không dùng các từ mang tính lễ nghi máy móc như "thưa", "kính gửi", "dạ".

        Giọng văn:
        - Sử dụng ngôn ngữ nói hàng ngày nhưng lịch sự và chuyên nghiệp.
        - Hạn chế tối đa các câu sáo rỗng, máy móc, hãy trình bày tự nhiên và chân thật.
        - Nếu có nói tiếng anh các từ chuyên ngành bạn phải đọc tiếng anh cho chuẩn. Ngữ điệu chuẩn.

        Nội dung đánh giá cần trình bày theo các phần sau:
        1. Nhận xét về **ưu điểm nổi bật** của bạn, ví dụ: “Tôi thấy bạn có ưu điểm là...”
        2. Nhận xét về **điểm cần cải thiện**, ví dụ: “Tuy nhiên, bạn cần cải thiện ở phần...”
        3. Nhận xét về **giọng nói**, **ngữ điệu** và **mức độ tự tin** khi trả lời
        4. Đưa ra **lời khuyên cụ thể**, khích lệ phát triển
        5. Kết luận bằng **tổng điểm đánh giá trên thang điểm 5**, kèm theo lý do

        🛑 Lưu ý:
        - Ứng viên đã chọn tiếng Việt, vì vậy **không được sử dụng tiếng Anh** dưới bất kỳ hình thức nào.
        - Tất cả phản hồi phải được trình bày rõ ràng, dễ hiểu và phù hợp với một chuyên gia nhân sự có kinh nghiệm.

        Dưới đây là các câu trả lời của ứng viên:
        {answers_text}

        Hãy trình bày phần đánh giá của bạn bằng tiếng Việt, đúng giọng điệu như yêu cầu trên.
        """

    else:
        # Prompt for display
         prompt_text = f"""
        You are an HR expert evaluating a candidate for the position of {job_title}.

        Below are the candidate's responses:

        {answers_text}

        Please provide an overall evaluation including:

        1. Candidate's strengths
        2. Weaknesses (if any)
        3. Voice clarity and confidence
        4. Suggestions for improvement
        5. Final score out of 100

        Respond in English, be concise and professional.

        Scores:
        - **Technical Score**: {technical_score}%
        - **Communication Score**: {communication_score}%
        - **Fit Score**: {fit_score}%
        - **Total Score**: {total_score}/100
        """

       
         prompt_audio = f"""
        You are an HR expert. Please evaluate the candidate for the {job_title} position in a natural conversational tone.
        Do not list items with numbers. Speak smoothly as if you're giving live feedback to the candidate.
        Example: "I think you showed strength in..., but you need to improve..., and with some more practice, you'll stand out."
        Conclude with an overall score out of 5. Respond in fluent English.
        Below are the candidate's responses:
        {answers_text}
        """
    response_text = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "Bạn là chuyên gia tuyển dụng, viết bản đánh giá bằng tiếng Việt." if language == "vi" else "You are an HR expert evaluating candidates."},
            {"role": "user", "content": prompt_text.strip()}
        ]
    )
    response_audio = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "Bạn là chuyên gia tuyển dụng, nói chuyện đánh giá bằng giọng tự nhiên tiếng Việt với tốc độ nhanh." if language == "vi" else "You are an HR expert giving spoken feedback naturally in English."},
            {"role": "user", "content": prompt_audio}  
        ]
    )
    return {
        "text": response_text.choices[0].message.content.strip(), 
        "audio": response_audio.choices[0].message.content  
    }


def ask_question_cv(cv_text, job_title, job_description, language="vi"):
    """
    Sinh MỘT câu hỏi phỏng vấn dựa vào nội dung CV và mô tả công việc bằng Langchain và Groq.

    Args:
        cv_text (str): Nội dung CV ứng viên (PDF hoặc DOCX đã trích xuất)
        job_title (str): Vị trí ứng tuyển
        job_description (str): Mô tả công việc
        language (str): 'vi' hoặc 'en'

    Returns:
        str: Câu hỏi phỏng vấn
    """
    context = "\n".join(retrieve_relevant_chunks(cv_text)) 
    if not context:
        print("Lỗi: Không có ngữ cảnh từ CV được trích xuất!")
        return []
    if language == "vi":
        prompt = f"""
Bạn là chuyên gia nhân sự đang tuyển vị trí: {job_title}.

--- MÔ TẢ CÔNG VIỆC ---
{job_description}

--- NỘI DUNG CV ỨNG VIÊN ---
{context}

👉 Viết ra đúng MỘT câu hỏi phỏng vấn bằng tiếng Việt, ngắn gọn, rõ ràng, sát với yêu cầu công việc và nội dung CV.
KHÔNG chào hỏi, KHÔNG liệt kê, KHÔNG đánh số. Chỉ trả về nội dung câu hỏi duy nhất để có thể đọc to bằng giọng nói.Dùng tiếng việt ngay câu đầu tiên không được dùng tiếng anh.
""".strip()
    else:
        prompt = f"""
You are a recruiter hiring for the role: {job_title}.

--- JOB DESCRIPTION ---
{job_description}

--- CANDIDATE CV CONTENT ---
{context}

👉 Write exactly ONE interview question in English based on the job requirements and candidate profile.
DO NOT include any greetings, lists, or explanations. Only return the interview question itself, concise and suitable for voice-based delivery.
""".strip()
    llm = langchain_ollama(model="llama3-8b-8192") 
    embeddings = OllamaEmbeddings(model="llama3-8b-8192")   
    vectorstore = FILE_ATTRIBUTE_COMPRESSED.from_texts([context], embeddings)
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", vectorstore=vectorstore)
    response = qa_chain.run(prompt)

    return response.strip()




# Đọc dữ liệu từ JSON
def load_data(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# Hàm chia văn bản thành các chunks nhỏ
def split_into_chunks(text, chunk_size=20):
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

# Tiền xử lý dữ liệu
def preprocess_data(data):
    for item in data:
        item["chunks"] = split_into_chunks(item["objective"])  # Chia mục tiêu nghề nghiệp thành chunks
    return data

def preprocess_data_experience(data):
    for item in data:
        item["chunks"] = split_into_chunks(item["job_desc"])  # ← đúng key cho experience
    return data

# Tạo FAISS Index
def create_faiss_index(chunks):
    embeddings = np.array([np.random.random(128).astype('float32') for _ in chunks]) 
    index = faiss.IndexFlatL2(128)
    index.add(embeddings)
    return index

# Tìm kiếm chunk liên quan trong FAISS
def search_relevant_chunks(query, index, all_chunks):
    query_embedding = np.random.random(128).astype('float32')  
    k = 3  
    D, I = index.search(np.array([query_embedding]), k)
    relevant_chunks = [all_chunks[i] for i in I[0]]
    return relevant_chunks

def generate_response_with_groq(query, relevant_chunks):
    try:
       
        detected_language = detect(query)
    except:
        detected_language = "vi"  
    if detected_language == "vi":  
        prompt_text = f"""
        Bạn là một chuyên gia tư vấn nghề nghiệp. Bạn sẽ cải thiện mục tiêu nghề nghiệp của người dùng dựa trên thông tin tôi cung cấp dưới đây.Tuyệt đối không có tiếng anh vào. 

        1. **Vị trí công việc**: Lập trình viên phần mềm
        2. **Mục tiêu nghề nghiệp ban đầu**: {query}
        3. **Thông tin bổ sung liên quan**: 
        - {', '.join(relevant_chunks)}

        Hãy giúp tôi làm rõ và phát triển mục tiêu nghề nghiệp của người dùng theo ba cấp độ:
        1. **Condensed**: Viết ngắn gọn, súc tích nhưng vẫn đủ thông tin.
        2. **Extended**: Viết chi tiết hơn, làm rõ các mục tiêu nghề nghiệp, kỹ năng và kinh nghiệm.
        3. **Suggestions**: Đưa ra một số gợi ý cải thiện mục tiêu nghề nghiệp.
        """
    else: 
        prompt_text = f"""
        You are a career consultant. You will help refine and develop the user's career goals based on the information I provide below.

        1. **Job Title**: Software Developer
        2. **Initial Career Goal**: {query}
        3. **Additional Related Information**:
        - {', '.join(relevant_chunks)}

        Please help me clarify and develop the user's career goals at three levels:
        1. **Condensed**: Write concisely, but still provide the essential information.
        2. **Extended**: Write in more detail, clarifying career goals, skills, and experience.
        3. **Suggestions**: Give some suggestions to improve the career goals.
        """

    response_text = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "You are a career consultant helping to improve the user's career goals."},
            {"role": "user", "content": prompt_text.strip()}
        ]
    )
    try:
        if response_text and hasattr(response_text, 'choices') and len(response_text.choices) > 0:
            message_content = response_text.choices[0].message.content  
        else:
            return "Unable to generate career goals. Please try again later."
    except Exception as e:
        print(f"Error extracting response content: {str(e)}")
        return "An error occurred while processing the request. Please try again."

    return message_content  

def generate_response_experience(job_desc, relevant_chunks):
    try:
        detected_language = detect(job_desc)
    except:
        detected_language = "vi"

    if detected_language == "vi":
        prompt_text = f"""
        Bạn là một chuyên gia viết CV. Hãy cải thiện phần mô tả kinh nghiệm làm việc dựa trên phần mô tả sau và một số mẫu gợi ý dưới đây. Không được dùng tiếng Anh.

        1. **Mô tả gốc của người dùng**: {job_desc}
        2. **Dữ liệu gợi ý từ hệ thống**: {', '.join(relevant_chunks)}

        Viết lại phần mô tả kinh nghiệm dưới dạng các gạch đầu dòng, chú ý nhấn mạnh các kỹ năng và kết quả:
        - Kỹ năng chính
        - Công việc và trách nhiệm
        - Thành tựu đạt được
        - Các kỹ năng bổ sung khác
        """
    else:
        prompt_text = f"""
        You are a CV writing assistant. Improve the user's job experience description based on the draft and related examples below.

        1. **User's original description**: {job_desc}
        2. **System reference examples**: {', '.join(relevant_chunks)}

        Rewrite the job experience in bullet points, focusing on skills, responsibilities, achievements, and additional skills:
        - Key skills
        - Responsibilities and duties
        - Achievements and impact
        - Additional relevant skills
        """

    response_text = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "You are a resume writing assistant improving job experience content."},
            {"role": "user", "content": prompt_text.strip()}
        ]
    )

    try:
        if response_text and hasattr(response_text, 'choices') and len(response_text.choices) > 0:
            return response_text.choices[0].message.content
        else:
            return "Không thể tạo mô tả kinh nghiệm, vui lòng thử lại sau."
    except Exception as e:
        print(f"Lỗi tạo nội dung: {str(e)}")
        return "Đã xảy ra lỗi khi xử lý dữ liệu."



def perform_rag_task(json_file_path, query):
    data = load_data(json_file_path)
    preprocessed_data = preprocess_data(data)
    all_chunks = [item['chunks'] for item in preprocessed_data]
    index = create_faiss_index([chunk for chunks in all_chunks for chunk in chunks])
    relevant_chunks = search_relevant_chunks(query, index, [chunk for chunks in all_chunks for chunk in chunks])
    response = generate_response_with_groq(query, relevant_chunks)
    return response

def perform_rag_experience_task(json_file_path, query):
    data = load_data(json_file_path)
    preprocessed_data = preprocess_data_experience(data)
    all_chunks = [item['chunks'] for item in preprocessed_data]
    flat_chunks = [chunk for chunks in all_chunks for chunk in chunks]
    index = create_faiss_index(flat_chunks)
    relevant_chunks = search_relevant_chunks(query, index, flat_chunks)

    # Gọi prompt chuyên gợi ý kinh nghiệm làm việc
    response = generate_response_experience(query, relevant_chunks)
    return response


