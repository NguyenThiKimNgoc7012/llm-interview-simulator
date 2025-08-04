from tasks import evaluate_candidate_responses

class InterviewSimulation:
    def __init__(self, job_title, questions, model_name="default-model"):
        self.job_title = job_title
        self.questions = questions
        self.model_name = model_name
        self.qa_pairs = []

    def conduct_manual_interview(self, return_feedback_only=False):
        """
        Nếu return_feedback_only=True: dùng cho Flask – chỉ trả về string đánh giá.
        Nếu False: dùng cho terminal – hỏi từng câu và in ra đánh giá.
        """
        print("\n--- PHỎNG VẤN BẮT ĐẦU ---")
        self.qa_pairs = []

        for i, question in enumerate(self.questions[:10], start=1): 
            print(f"\nCâu hỏi #{i}: {question}")
            answer = input(" Bạn trả lời: ")
            self.qa_pairs.append({"question": question, "answer": answer})

        print("\n Đang đánh giá tổng quan câu trả lời của bạn...\n")
        evaluation = evaluate_candidate_responses(self.job_title, self.qa_pairs)

        if return_feedback_only:
            return evaluation  
        else:
            print("📋 Đánh giá tổng kết:\n")
            print(evaluation)
