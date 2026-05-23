import os
import random
import pandas as pd
import streamlit as st
import plotly.express as px
from transformers import pipeline

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Sentience AI", page_icon="🔮", layout="wide")

# --- BACKEND ENGINE ---
@st.cache_resource
def load_engine():
    class ContextualEmpathyEngine:
        def __init__(self):
            # Using the specialized GoEmotions model
            self.classifier = pipeline(
                "text-classification", 
                model="SamLowe/roberta-base-go_emotions", 
                top_k=1
            )

        def get_contextual_response(self, current_text, history):
            # 1. Analyze current emotion
            result = self.classifier(current_text)[0][0]
            current_emotion = result['label']
            score = result['score']

            # 2. Reference the previous message if it exists
            last_ai_msg = ""
            if len(history) >= 2:
                # Get the last AI response to see what we previously discussed
                last_ai_msg = history[-2]['content']

            # 3. Build a "Connected" Response
            if current_emotion in ['sadness', 'disappointment', 'grief']:
                response = f"I hear the sadness in that. It connects back to what we were discussing—{current_text}. I'm here to sit with you through this."
            elif current_emotion in ['joy', 'gratitude', 'admiration']:
                response = "That's a beautiful shift in energy! It's heartening to see this following our previous exchange."
            elif current_emotion in ['anger', 'annoyance']:
                response = "I can feel the tension rising. It's valid to feel this way, especially given the context of our chat."
            else:
                response = "I'm following your thoughts closely. Please, continue—I want to understand the full picture."

            return response, current_emotion, score

    return ContextualEmpathyEngine()

bot = load_engine()

# --- STATE MANAGEMENT ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "emotion_trend" not in st.session_state:
    st.session_state.emotion_trend = [50]

# --- UI LAYOUT ---
st.title("🔮 Sentience AI")
st.markdown("---")

# Use a container for the chat to ensure scrolling works well
chat_placeholder = st.container()

with chat_placeholder:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant":
                st.caption(f"Reflecting on: {msg['emotion']} | Confidence: {msg['score']:.0%}")

# --- INPUT & LOGIC ---
if prompt := st.chat_input("Tell me what's on your mind..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate response based on current prompt AND history
    response_text, emotion, conf = bot.get_contextual_response(prompt, st.session_state.messages)
    
    # Add AI response to history
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response_text,
        "emotion": emotion,
        "score": conf
    })
    
    # Update trend data for the sidebar/analytics
    st.session_state.emotion_trend.append(int(conf * 100))
    st.rerun()

# --- OPTIONAL SIDEBAR FOR ANALYTICS ---
with st.sidebar:
    st.subheader("Conversation Resonance")
    if len(st.session_state.emotion_trend) > 1:
        st.line_chart(st.session_state.emotion_trend)
    st.caption("Tracking emotional synchronization in real-time.")
