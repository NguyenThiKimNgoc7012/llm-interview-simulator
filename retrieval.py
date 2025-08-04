import faiss
import numpy as np
from groq import GroqClient  

groq_client = GroqClient() 
groq_model = groq_client.load_model('llama3-8b-8192')  

def generate_query_embedding_with_groq(query):
    embedding = groq_model.encode(query)  
    return np.array(embedding).reshape(1, -1).astype('float32')

def load_faiss_index(index_path="vectorstore.index"):
    return faiss.read_index(index_path)

def search_in_vector_store(query, index, k=3):
    query_embedding = generate_query_embedding_with_groq(query)  
    distances, indices = index.search(query_embedding, k)  
    return distances, indices


index = load_faiss_index()  
query = "Bạn có kinh nghiệm làm việc với AI không?"  
distances, indices = search_in_vector_store(query, index)  


print("Kết quả tìm kiếm:")
for idx in indices[0]:
    print(f"Thông tin phù hợp: {texts[idx]}")
