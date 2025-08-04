import os
from dotenv import load_dotenv
from groq import Groq
from vectorstore import retrieve_relevant_chunks  

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_llama(prompt: str) -> str:
    """
    Gửi prompt đến mô hình llama3-8b-8192 qua Groq và trả về phản hồi dạng text.
    Quy trình RAG được tích hợp ở đây:
    1. Truy vấn vector store để lấy ngữ cảnh liên quan từ các văn bản đã lưu.
    2. Tạo câu hỏi với ngữ cảnh truy xuất được từ vector store và prompt của người dùng.
    """
    try:
        context_chunks = retrieve_relevant_chunks(prompt, k=3)  
        if not context_chunks:
            return "❌ Không tìm thấy thông tin liên quan trong cơ sở dữ liệu."
        context = "\n".join(context_chunks) 
        full_prompt = f"""
Bạn là chuyên gia tuyển dụng, phản hồi bằng tiếng Việt.
Dưới đây là thông tin liên quan trích xuất từ các tài liệu:

--- NGỮ CẢNH ---
{context}

--- YÊU CẦU ---
{prompt}
"""
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "Bạn là chuyên gia tuyển dụng, phản hồi bằng tiếng Việt."},
                {"role": "user", "content": full_prompt.strip()}
            ],
            temperature=0.5,
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"[Lỗi khi gọi LLaMA3]: {e}"
