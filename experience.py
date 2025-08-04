import json
import numpy as np
import faiss
from langdetect import detect
from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
def load_data(experience_json_file_path):
    with open(experience_json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def split_experience_into_chunks(text, chunk_size=20):
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks
def preprocess_experience_data(data):
    for item in data:
        item["experience_chunks"] = split_experience_into_chunks(item["experience"])  
    return data

def create_faiss_experience_index(chunks):
    embeddings = np.array([np.random.random(128).astype('float32') for _ in chunks])  
    index = faiss.IndexFlatL2(128)
    index.add(embeddings)
    return index

def search_relevant_experience_chunks(query, index, all_chunks):
    query_embedding = np.random.random(128).astype('float32') 
    k = 3 
    D, I = index.search(np.array([query_embedding]), k)
    relevant_chunks = [all_chunks[i] for i in I[0]]
    return relevant_chunks

def generate_response_with_experience(query, relevant_chunks):
    try:
        detected_language = detect(query)
    except:
        detected_language = "vi" 

    if detected_language == "vi":
        prompt_text = f"""
        Bạn là một chuyên gia tư vấn nghề nghiệp. Bạn sẽ giúp cải thiện phần kinh nghiệm làm việc của người dùng dựa trên thông tin tôi cung cấp dưới đây.

        1. **Vị trí công việc**: {query}
        2. **Thông tin bổ sung liên quan**:
        - {', '.join(relevant_chunks)}

        Hãy giúp tôi làm rõ và phát triển kinh nghiệm làm việc của người dùng theo ba cấp độ:
        1. **Condensed**: Viết ngắn gọn, súc tích nhưng vẫn đủ thông tin.
        2. **Extended**: Viết chi tiết hơn, làm rõ các kinh nghiệm làm việc, kỹ năng và thành tựu.
        3. **Suggestions**: Đưa ra một số gợi ý cải thiện phần kinh nghiệm làm việc.
        """
    else:
        prompt_text = f"""
        You are a career consultant. You will help refine and develop the user's work experience based on the information I provide below.

        1. **Job Title**: {query}
        2. **Additional Related Information**:
        - {', '.join(relevant_chunks)}

        Please help me clarify and develop the user's work experience at three levels:
        1. **Condensed**: Write concisely, but still provide the essential information.
        2. **Extended**: Write in more detail, clarifying work experience, skills, and achievements.
        3. **Suggestions**: Give some suggestions to improve the work experience.
        """

    response_text = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "You are a career consultant helping to improve the user's work experience."},
            {"role": "user", "content": prompt_text.strip()}
        ]
    )

    try:
        if response_text and hasattr(response_text, 'choices') and len(response_text.choices) > 0:
            message_content = response_text.choices[0].message['content']
            return message_content
        else:
            return "Unable to generate work experience. Please try again later."
    except Exception as e:
        print(f"Error extracting response content: {str(e)}")
        return "An error occurred while processing the request. Please try again."

def perform_rag_task_experience(experience_json_file, query):
   
    data = load_data(experience_json_file)
    preprocess_experience_data = preprocess_experience_data(data)  
    all_chunks = [item['experience_chunks'] for item in preprocess_experience_data]  
    index = create_faiss_experience_index([chunk for chunks in all_chunks for chunk in chunks])
    relevant_chunks = search_relevant_experience_chunks(query, index, [chunk for chunks in all_chunks for chunk in chunks])
    response = generate_response_with_experience(query, relevant_chunks)
    
    return response
