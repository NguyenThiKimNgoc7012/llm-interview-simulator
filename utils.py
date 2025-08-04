import pandas as pd
from PyPDF2 import PdfReader
import random
import json
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def extract_text_from_cv(file_path):
    """
    Trích xuất text từ file CV (PDF hoặc DOCX).
    :param file_path: đường dẫn tới file CV
    :return: nội dung văn bản trích xuất
    """
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])

    else:
        raise ValueError("Định dạng CV không được hỗ trợ. Chỉ hỗ trợ PDF và DOCX.")
def extract_job_title_from_cv(cv_path):
    reader = PdfReader(cv_path)
    text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    keywords = ["Fullstack", "Data", "AI", "DevOps", "Backend", "Frontend"]
    for keyword in keywords:
        if keyword.lower() in text.lower():
            return keyword
    return "Unknown"

def load_questions_from_json(path="data/phongvan_by_nganh.json", job_title="Fullstack"):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    questions = data.get(job_title, [])
    return questions

def auto_select_model():
    models = [
        "llama2-70b-4096",
        "mixtral-8x7b-32768"
    ]
    return random.choice(models)

def select_cv_file():
    Tk().withdraw()  
    file_path = askopenfilename(
        title="Chọn file CV (.pdf)",
        filetypes=[("PDF files", "*.pdf")]
    )
    return file_path
def save_interview_results(qa_pairs, filename="ketqua_phongvan.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.extend(qa_pairs)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
def print_available_job_titles():
    import json

    with open("data/phongvan_by_nganh.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    for job in data.keys():
        print(f" - {job}")
def validate_job_consistency(job_title, job_description, cv_text):
    keyword = job_title.lower()
    combined_text = (job_description or "") + " " + (cv_text or "")
    return keyword in combined_text.lower()
