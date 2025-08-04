# vectorstore.py
from PyPDF2 import PdfReader
from langchain_community.vectorstores import Chroma
# Sửa lại import embeddings
from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import CharacterTextSplitter
import os

CHROMA_DIR = "chroma_db"

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

def create_vectorstore_from_cv(file_path):
    text = extract_text_from_pdf(file_path)
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)
    
    # Dùng OllamaEmbeddings với model Llama3
    embedding = OllamaEmbeddings(model="llama3")  
    vectordb = Chroma.from_texts(chunks, embedding=embedding, persist_directory=CHROMA_DIR)
    vectordb.persist()
print(f"Vector store đã được lưu tại {CHROMA_DIR}")
def load_vectorstore():
    if not os.path.exists(CHROMA_DIR):
        return None
    embedding = OllamaEmbeddings(model="llama3")
    return Chroma(persist_directory=CHROMA_DIR, embedding_function=embedding)
def retrieve_relevant_chunks(query, k=3):
    """
    Truy vấn vectorstore để lấy các đoạn văn bản liên quan.
    """
    vectordb = load_vectorstore()  # Tải vector store
    if vectordb is None:
        return []

    # Truy vấn tương tự, tìm các đoạn văn bản liên quan
    results = vectordb.similarity_search(query, k=k)
    return [doc.page_content for doc in results]