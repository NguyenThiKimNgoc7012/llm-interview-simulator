from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")  
db = client["chatbot_db"]
feedback_collection = db["feedbacks"]

def save_feedback(feedback_data):
    feedback_data["timestamp"] = datetime.now()  
    feedback_collection.insert_one(feedback_data)
    print("Feedback đã được lưu vào MongoDB.")

def read_feedback():
    feedbacks = feedback_collection.find()
    for feedback in feedbacks:
        print(feedback)
        
        
