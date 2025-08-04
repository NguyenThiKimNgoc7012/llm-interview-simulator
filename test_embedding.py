import os
import faiss
import numpy as np
from embedding import create_faiss_index, add_embeddings_to_faiss, generate_embeddings_with_groq
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def test_generate_embeddings_with_groq():
    texts = ["Câu hỏi 1 về AI", "Câu hỏi 2 về Data Science", "Câu hỏi về Fullstack"]
    embeddings = generate_embeddings_with_groq(texts)

    print("Embeddings shape:", embeddings.shape)
    assert embeddings.shape == (len(texts), 8192), f"Expected (3, 8192), got {embeddings.shape}"

    print("generate_embeddings_with_groq passed!")

def test_faiss_index():
    texts = ["Câu hỏi 1 về AI", "Câu hỏi 2 về Data Science", "Câu hỏi về Fullstack"]
    index = create_faiss_index() 
    index = add_embeddings_to_faiss(index, texts)
    print("FAISS index size:", index.ntotal)
    assert index.ntotal == len(texts), f"Expected {len(texts)}, got {index.ntotal}"

    print("FAISS index test passed!")
def test_save_faiss_index():
    texts = ["Câu hỏi 1 về AI", "Câu hỏi 2 về Data Science", "Câu hỏi về Fullstack"]
    index = create_faiss_index()
    index = add_embeddings_to_faiss(index, texts)
    faiss.write_index(index, "vectorstore.index")
    loaded_index = faiss.read_index("vectorstore.index")
    print("Loaded FAISS index size:", loaded_index.ntotal)
    assert loaded_index.ntotal == len(texts), f"Expected {len(texts)}, got {loaded_index.ntotal}"

    print("Save and load FAISS index test passed!")

# Chạy các bài test
def run_tests():
    test_generate_embeddings_with_groq()
    test_faiss_index()
    test_save_faiss_index()

if __name__ == "__main__":
    run_tests()
