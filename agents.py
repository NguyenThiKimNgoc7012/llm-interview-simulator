from crewai import Agent

def create_interviewer(job_title: str, model_name: str) -> Agent:
    return Agent(
        role="HR Interviewer",
        goal=f"Interview candidates for the {job_title} role",
        backstory="Bạn là chuyên viên tuyển dụng chuyên đặt câu hỏi phỏng vấn phù hợp và đánh giá ứng viên.",
        verbose=True,
        allow_delegation=False,
        llm=model_name
    )
