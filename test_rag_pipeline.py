from rag_pipeline import retrieve_relevant_chunks, generate_answer_with_groq

# Test ngữ cảnh và câu hỏi
query = "Bạn có kinh nghiệm làm việc với AI không?"
retrieved_texts = ["Câu hỏi về AI", "Câu hỏi về Data Science"]  # Ví dụ về ngữ cảnh đã truy xuất

# Truy vấn ngữ cảnh
context_chunks = retrieve_relevant_chunks(query, k=3)
print(f"Context Chunks: {context_chunks}")

# Tạo câu trả lời từ mô hình Groq
answer = generate_answer_with_groq(query, retrieved_texts)
print(f"Generated Answer: {answer}")
