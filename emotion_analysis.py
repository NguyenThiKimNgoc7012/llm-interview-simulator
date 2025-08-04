from textblob import TextBlob

def analyze_emotion(text):
    """
    Phân tích cảm xúc từ văn bản (text) dựa trên TextBlob (hoặc có thể sử dụng mô hình mạnh mẽ hơn).
    Cảm xúc sẽ được đánh giá từ -1 (tiêu cực) đến 1 (tích cực).
    """
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity 
    confidence_score = 0.8 if sentiment > 0 else 0.5 
    emotions = {
        "sentiment": sentiment,
        "confidence_score": confidence_score
    }
    return emotions

