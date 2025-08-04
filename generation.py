import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("API Key không hợp lệ hoặc chưa được cấu hình trong file .env. Vui lòng kiểm tra lại.")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions" 

def generate_answer_with_groq(query, retrieved_texts):
    context = " ".join(retrieved_texts)
    full_input = query + " " + context  
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192", 
        "messages": [
            {
                "role": "user",
                "content": full_input
            }
        ],
        "temperature": 0.7  
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"]
            return answer
        else:
            print(f"Error calling Groq API: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    return None

retrieved_texts = ["Câu hỏi về AI", "Câu hỏi về Data Science"] 
answer = generate_answer_with_groq("Bạn có kinh nghiệm làm việc với AI không?", retrieved_texts)  

print("Câu trả lời AI:", answer)  
def create_programming_question(skill):
    retrieved_texts = [
        f"Tạo câu hỏi về {skill} lập trình",
        f"Hỏi về {skill} với các ví dụ trong lập trình"
    ]
    
    question = generate_answer_with_groq(f"Tạo câu hỏi về lập trình {skill}", retrieved_texts)
    return question
def query_groq_model(prompt):
    data = {
        "input": prompt,
        "model": "llama3-8b-8192"
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(GROQ_API_URL, json=data, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

