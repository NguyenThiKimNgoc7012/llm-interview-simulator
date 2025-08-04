import numpy as np
import faiss
import os
from dotenv import load_dotenv


load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
def generate_embeddings(text):
    """
    Giả sử đây là phương thức tạo embeddings từ Groq (bạn cần thay thế bằng API thực tế của Groq)
    """
    embedding = np.random.rand(8192)  
    return embedding

def generate_embeddings_with_groq(texts):
    embeddings = []  
    for text in texts:
        try:
           
            embedding = generate_embeddings(text)  
            embeddings.append(np.array(embedding, dtype=np.float32)) 
        except Exception as e:
            print(f"Error: {e}")
    return np.array(embeddings).astype('float32')

def create_faiss_index(dim=8192): 
    return faiss.IndexFlatL2(dim)  

def add_embeddings_to_faiss(index, texts):
    embeddings = generate_embeddings_with_groq(texts)  
    print(f"Embeddings shape: {embeddings.shape}") 
    index.add(embeddings)  
    return index

texts = ["Câu hỏi 1 về AI", "Câu hỏi 2 về Data Science", "Câu hỏi về Fullstack"]
index = create_faiss_index()  
index = add_embeddings_to_faiss(index, texts)  

faiss.write_index(index, "vectorstore.index") 
