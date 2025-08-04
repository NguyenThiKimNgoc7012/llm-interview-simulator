from llm import ask_llama

# Ví dụ câu hỏi muốn gửi tới mô hình
prompt = "Bạn có thể giải thích cách thức hoạt động của một hệ thống RAG không?"

# Gọi hàm ask_llama để lấy câu trả lời
response = ask_llama(prompt)

# In ra câu trả lời từ mô hình
print("Câu trả lời từ mô hình Llama3-8b-8192:")
print(response)
