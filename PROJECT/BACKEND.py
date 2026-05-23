import streamlit as st
import pandas as pd
import random
import os
from transformers import pipeline

# --- PAGE CONFIG ---
st.set_page_config(page_title="Sentience AI", layout="wide")

# --- ENGINE INITIALIZATION ---
@st.cache_resource
def load_sentience_engine():
    class ContextualBot:
        def __init__(self):
            # Using only the emotion classifier to avoid the summarization KeyError
            # This model is very stable and handles 'text-classification'
            self.classifier = pipeline(
                "text-classification", 
                model="SamLowe/roberta-base-go_emotions", 
                top_k=1
            )

        def extract_topic(self, history):
            """Simple extraction logic to find the 'context' without a heavy model"""
            if len(history) < 2:
                return "our conversation"
            
            # Look at the last user message
            last_user_msg = history[-1]["content"] if history[-1]["role"] == "user" else ""
            
            # List of common filler words to ignore
            stop_words = ["i", "am", "feel", "the", "a", "is", "to", "it", "my", "was"]
            words = [w for w in last_user_msg.lower().split() if w not in stop_words]
            
            # Return the last 3 meaningful words as the 'topic'
            if words:
                return f"'{ ' '.join(words[-3:]) }'"
            return "what you shared"

        def generate_contextual_reply(self, current_input, history):
            # 1. Detect Emotion
            emotion_data = self.classifier(current_input)[0][0]
            emotion = emotion_data['label']
            
            # 2. Get Contextual Topic from History
            topic = self.extract_topic(history)

            # 3. Empathetic Branching
            if emotion in ['sadness', 'disappointment', 'grief', 'remorse']:
                reply = f"I'm truly sorry you're dealing with {topic}. It's understandable that this brings up feelings of {emotion}. I'm here to listen if you want to say more."
            elif emotion in ['joy', 'excitement', 'approval', 'pride']:
                reply = f"That sounds wonderful! Hearing about {topic} clearly brings you {emotion}. I'm happy for you—what's the best part about it?"
            elif emotion in ['anger', 'annoyance', 'frustration']:
                reply = f"I can hear how much {topic} is frustrating you. It's completely valid to feel {emotion} in this situation. What feels the most unfair right now?"
            elif emotion in ['fear', 'nervousness', 'anxiety']:
                reply = f"It sounds like {topic} is causing some anxiety. Take a deep breath. It's okay to feel {emotion} when things are uncertain."
            else:
                reply = f"I'm following what you're saying about {topic}. It sounds like a lot to process. How are you feeling about it all now?"

            return reply, emotion, emotion_data['score']

    return ContextualBot()

# --- APP LAYOUT ---
bot = load_sentience_engine()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello. I'm Sentience. I'm here to listen and understand your context. How are you?", "emotion": "neutral", "score": 1.0}
    ]

st.title("🔮 Sentience Intelligence")
st.caption("Contextually Aware Emotional Analysis")

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant" and "emotion" in msg:
            st.divider()
            st.caption(f"Context: {msg['emotion'].upper()} | Confidence: {msg['score']:.0%}")

# --- CHAT INPUT ---
if prompt := st.chat_input("Share your thoughts..."):
    # 1. Store User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. Generate Contextual AI Message
    with st.spinner("Processing context..."):
        answer, emo, conf = bot.generate_contextual_reply(prompt, st.session_state.messages)
    
    # 3. Store AI Message
    st.session_state.messages.append({
        "role": "assistant", 
        "content": answer, 
        "emotion": emo, 
        "score": conf
    })
    
    st.rerun()
