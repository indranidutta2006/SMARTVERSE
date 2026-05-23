from transformers import pipeline
import os
import streamlit as st

# Find the absolute path to FRONTEND.css next to BACKEND.py
current_dir = os.path.dirname(__file__)
css_path = os.path.join(current_dir, "FRONTEND.css")

if os.path.exists(css_path):
    try:
        # Added explicit utf-8 encoding to fix server environment decode errors
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
            if css_content.strip():  # Verify file is not empty
                #st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading styles: {e}")
else:
    st.error("FRONTEND.css file not found!")

class EmpatheticBot:
    def __init__(self):
        # Using a model trained on the 'GoEmotions' dataset (28 emotion categories)
        print("Initializing Emotion Engine...")
        self.emotion_classifier = pipeline(
            "text-classification", 
            model="SamLowe/roberta-base-go_emotions", 
            top_k=3
        )

    def analyze_input(self, user_text):
        # Detect top 3 emotions
        results = self.emotion_classifier(user_text)[0]
        
        # Primary emotion and confidence score
        top_emotion = results[0]['label']
        confidence = results[0]['score']
        
        return top_emotion, confidence

    def generate_safe_response(self, user_text):
        emotion, score = self.analyze_input(user_text)
        
        # High-arousal/Negative emotion de-escalation logic
        if emotion in ['anger', 'annoyance', 'disappointment', 'fear']:
            prefix = f"[System: De-escalation Mode Active | Detected: {emotion.upper()}]"
            response = f"I can tell you're feeling {emotion}. It's understandable to feel that way. Let's look at the facts together."
        
        # Positive/Inquisitive logic
        elif emotion in ['curiosity', 'admiration', 'joy']:
            prefix = f"[System: Engagement Mode | Detected: {emotion.upper()}]"
            response = "That's a great point! I'm glad we're exploring this topic together."
            
        else:
            prefix = "[System: Standard Mode]"
            response = "I hear you. Here is the information I found on that topic."

        return f"{prefix}\nAI: {response}"

# Example Usage
bot = EmpatheticBot()
user_input = "I am so frustrated because this news article feels like a total lie!"
print(bot.generate_safe_response(user_input))
