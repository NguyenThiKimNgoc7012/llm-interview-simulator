import logging
import os
from rag_pipeline import retrieve_relevant_chunks, generate_answer_with_groq
logging.basicConfig(level=logging.DEBUG)

def analyze_cv_and_generate_questions(file_path):
    logging.info(f"Đang phân tích CV từ file: {file_path}")
    if not os.path.exists(file_path):
        logging.error(f"Không tìm thấy file CV tại {file_path}")
        return f"❌ Không tìm thấy file CV tại {file_path}"

    try:
        logging.info("Đang truy vấn vector store để lấy ngữ cảnh liên quan...")
        context_chunks = retrieve_relevant_chunks(file_path)
        logging.debug(f"Ngữ cảnh truy vấn được: {context_chunks}")
    except Exception as e:
        logging.error(f"Lỗi khi truy vấn vector store: {e}")
        return f"❌ Lỗi khi truy vấn vector store: {e}"

    if not context_chunks:
        logging.warning("Không có ngữ cảnh liên quan được tìm thấy.")
        return "❌ Không tìm thấy ngữ cảnh liên quan từ CV."
    try:
        logging.info("Đang sinh câu trả lời từ mô hình Groq...")
        question = generate_answer_with_groq("Bạn có kinh nghiệm làm việc với AI không?", context_chunks)
        logging.debug(f"Câu trả lời từ mô hình: {question}")
    except Exception as e:
        logging.error(f"Lỗi khi gọi Groq API: {e}")
        return f"❌ Lỗi khi gọi Groq API: {e}"

    return question

def get_cv_file_path():
    file_path = input("Nhập đường dẫn file CV: ")
    return file_path.strip()

if __name__ == "__main__":
   
    file_path = get_cv_file_path()
    result = analyze_cv_and_generate_questions(file_path)
    print(result)
