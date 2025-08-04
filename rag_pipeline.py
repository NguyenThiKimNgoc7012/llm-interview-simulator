# rag_pipeline.py
from utils import load_questions_from_json, extract_job_title_from_cv, auto_select_model
from vectorstore import load_vectorstore
from llm import client 
from langchain.docstore.document import Document
from langchain_ollama import OllamaEmbeddings
from generation import generate_answer_with_groq


def retrieve_relevant_chunks(query, k=3):
    """
    Truy vấn vectorstore để lấy các đoạn văn bản liên quan.
    """
    vectordb = load_vectorstore()
    if vectordb is None:
        return []

    results = vectordb.similarity_search(query, k=k)
    print(f"Kết quả truy vấn cho '{query}':", results)
    return [doc.page_content for doc in results]
print(retrieve_relevant_chunks("Làm thế nào để tạo một chatbot phỏng vấn?"))

def retrieve_relevant_chunks_from_cv(cv_text):
    """
    Trích xuất các chunk dữ liệu từ CV sử dụng Llama3-8b-8192 embedding.
    """
    response = client.chat.completions.create(
        model="llama3-8b-8192", 
        messages=[
            {"role": "user", "content": cv_text}
        ],
        temperature=0.3
    )
    embeddings = response.choices[0].message.content.strip()  
    chunks = embeddings.split("\n") 

    return chunks




def generate_question_with_rag(cv_path):
    job_title = extract_job_title_from_cv(cv_path)
    question_list = load_questions_from_json(job_title=job_title)

    if not question_list:
        return f" Không tìm thấy câu hỏi mẫu cho ngành: {job_title}"
    context_chunks = retrieve_relevant_chunks(job_title, k=3)
    context = "\n".join(context_chunks)
    prompt = f"""
Bạn là AI phỏng vấn chuyên nghiệp cho ngành: {job_title}.
Dưới đây là thông tin liên quan được trích xuất từ CV:

--- NGỮ CẢNH ---
{context}

--- DANH SÁCH CÂU HỎI ---
{question_list}

--- YÊU CẦU ---
Dựa vào thông tin trên, hãy chọn và viết lại 1 câu hỏi phù hợp nhất từ danh sách.
Nếu cần, bạn có thể tinh chỉnh câu hỏi để phù hợp hơn với ngữ cảnh.
Viết bằng tiếng Việt.
"""

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "Bạn là chuyên gia tuyển dụng, hãy đưa ra 1 câu hỏi phù hợp nhất dựa trên ngữ cảnh."},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0.5
    )

    question = response.choices[0].message.content.strip()
    return question
