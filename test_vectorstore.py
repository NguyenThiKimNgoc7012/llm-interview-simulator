import faiss
import numpy as np

# Mở FAISS index
index = faiss.read_index("vectorstore.index")

# Kiểm tra số lượng vectors (embeddings) trong index
print(f"Số lượng vectors trong FAISS index: {index.ntotal}")

# Tạo một vector truy vấn ngẫu nhiên (hoặc từ câu hỏi của bạn)
query_vector = np.random.random((1, 8192)).astype('float32')  # Dùng vector phù hợp với kích thước embeddings

# Truy vấn FAISS index
D, I = index.search(query_vector, k=3)  # Lấy 3 kết quả gần nhất

# In kết quả truy vấn
print("Distances:", D)
print("Indices:", I)
