import os
from utils import extract_job_title_from_cv, load_questions_from_json, auto_select_model
from interview_simulation import InterviewSimulation
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from utils import print_available_job_titles


def run_with_cv():
    print(" Đang mở cửa sổ để chọn file CV...")
    Tk().withdraw()  
    path = askopenfilename(
        title="Chọn file CV (.pdf)",
        filetypes=[("PDF files", "*.pdf")]
    )
    
    if not path:
        print(" Bạn chưa chọn file nào. Thoát chương trình.")
        return

    job_title = extract_job_title_from_cv(path)
    print(f"Ngành/phòng ban trích xuất từ CV: {job_title}")
    run_interview(job_title)

def run_manual():
    job_title = input("Nhập ngành/phòng ban: ")
    run_interview(job_title)

def run_interview(job_title):
    questions = load_questions_from_json(job_title=job_title)
    
    if not questions:
        print(f"\nKhông tìm thấy câu hỏi nào cho ngành '{job_title}'.")
        print("Hãy kiểm tra lại ngành bạn nhập hoặc đảm bảo CV ghi rõ ngành có trong hệ thống.")
        print("Gợi ý: Các ngành có trong cơ sở dữ liệu bao gồm:")
        print_available_job_titles()  
        return

    selected_model = auto_select_model()
    print(f"\n➡️ Bắt đầu phiên phỏng vấn: {job_title} với model `{selected_model}`")

    sim = InterviewSimulation(job_title, questions, model_name=selected_model)
    sim.conduct_manual_interview()


def main():
    print("\n🔍 Bạn muốn khởi động theo cách nào?")
    print("1. Tải lên CV (.pdf) để tự động trích xuất ngành nghề")
    print("2. Nhập ngành/phòng ban thủ công")
    choice = input("Chọn (1 hoặc 2): ")

    if choice == "1":
        run_with_cv()
    else:
        run_manual()
if __name__ == "__main__":
    main()
