import streamlit as st
import pandas as pd
from transformers import pipeline
import random

# --- ENGINE INITIALIZATION ---
@st.cache_resource
def load_sentience_engine():
    class ContextualBot:
        def __init__(self):
            # Engine 1: Detects the Vibe
            self.classifier = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions", top_k=1)
            # Engine 2: Understands the Context (Summarization)
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

        def generate_contextual_reply(self, current_input, history):
            # 1. Get Emotion
            emotion_data = self.classifier(current_input)[0][0]
            emotion = emotion_data['label']
            
            # 2. Extract Context (What have we been talking about?)
            if len(history) > 2:
                # Combine last 3 exchanges to find the core "topic"
                past_text = " ".join([m["content"] for m in history[-3:]])
                # Create a tiny summary (max 10 words) to use as context
                try:
                    context_summary = self.summarizer(past_text, max_length=15, min_length=5, do_sample=False)[0]['summary_text']
                except:
                    context_summary = "our conversation"
            else:
                context_summary = "what you just shared"

            # 3. Construct Contextually Correct Response
            if emotion in ['sadness', 'disappointment', 'remorse']:
                reply = f"I can feel the weight in your words regarding {context_summary}. It's understandable to feel {emotion} when dealing with that. How are you holding up right now?"
            elif emotion in ['joy', 'excitement', 'approval']:
                reply = f"It’s great to hear some positivity about {context_summary}! That shift to {emotion} makes a lot of sense. What’s the highlight of this for you?"
            elif emotion in ['anger', 'annoyance', 'frustration']:
                reply = f"I hear your frustration. Dealing with {context_summary} is clearly draining. It’s valid to feel {emotion}—do you want to vent more about it?"
            else:
                reply = f"I'm following what you're saying about {context_summary}. It seems like a lot to process. What's the next step in your mind?"

            return reply, emotion, emotion_data['score']

    return ContextualBot()

# --- APP SETUP ---
st.set_page_config(page_title="Sentience AI", layout="wide")
bot = load_sentience_engine()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello. I am here to listen and analyze. How are you today?", "emotion": "neutral", "score": 1.0}]

# --- UI DISPLAY ---
st.title("🔮 Sentience Contextual Intelligence")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant" and "emotion" in msg:
            st.caption(f"Contextual Tone: {msg['emotion']} | Accuracy: {msg['score']:.0%}")

# --- LOGIC ---
if prompt := st.chat_input("Type here..."):
    # Save User Input
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate Reply using History for Context
    with st.spinner("Synthesizing context..."):
        answer, emo, conf = bot.generate_contextual_reply(prompt, st.session_state.messages)
    
    # Save AI Reply
    st.session_state.messages.append({
        "role": "assistant", 
        "content": answer, 
        "emotion": emo, 
        "score": conf
    })
    
    st.rerun()
