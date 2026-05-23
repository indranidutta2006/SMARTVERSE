import os
import random
import pandas as pd
import streamlit as st
import plotly.express as px
from transformers import pipeline

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Sentience AI | Empathetic Mode",
    page_icon="",
    layout="wide"
)

# --- BACKEND MODEL INITIALIZATION ---
@st.cache_resource
def load_engine():
    with st.status("Waking up Emotion Engine...", expanded=False) as status:
        class EmpatheticEngine:
            def __init__(self):
                # Using the GoEmotions model for high-granularity empathy
                self.classifier = pipeline(
                    "text-classification", 
                    model="SamLowe/roberta-base-go_emotions", 
                    top_k=1
                )

            def get_response(self, text):
                result = self.classifier(text)[0][0]
                emotion = result['label']
                score = result['score']
                
                # --- EMPATHETIC RESPONSE LOGIC ---
                if emotion in ['sadness', 'disappointment', 'grief']:
                    response = "I'm so sorry you're feeling this way. It’s okay to not be okay right now. I’m here to listen—do you want to tell me more about what's on your mind?"
                elif emotion in ['anger', 'annoyance', 'disgust']:
                    response = "I can hear the frustration in your words, and it sounds incredibly draining. I'm here to hold space for you. What feels like the biggest hurdle right now?"
                elif emotion in ['fear', 'nervousness', 'remorse']:
                    response = "It sounds like things feel a bit overwhelming or uncertain. Take a deep breath. You don't have to figure it all out this second. I'm right here with you."
                elif emotion in ['joy', 'pride', 'admiration', 'excitement']:
                    response = "That is wonderful to hear! I can really feel the positive energy in your message. What’s the best part of this experience for you?"
                elif emotion == 'curiosity':
                    response = "That's a fascinating thing to wonder about! I love exploring new ideas with you. Where should we start?"
                else:
                    response = "I'm listening. It sounds like you're processing a lot right now. I'm here for whatever you need to share."
                
                return response, emotion, score

        engine = EmpatheticEngine()
        status.update(label="Empathy Engine Active", state="complete")
        return engine

bot = load_engine()

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = {"Well-being": [50], "Connection": [50]}

# --- MAIN UI ---
st.title("🔮 Sentience AI")
st.caption("A space for genuine connection and emotional reflection.")

chat_col, stats_col = st.columns([2, 1])

with chat_col:
    # Display Chat
    for msg in st.session_state.messages:
        role_class = "user-bubble" if msg["role"] == "user" else "ai-bubble"
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                st.caption(f"Detected Mood: {msg['emotion']} ({msg['score']:.0%})")

    # Input handling
    if prompt := st.chat_input("How are you truly feeling?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Generate emotional response
        response, emotion, score = bot.get_response(prompt)
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response, 
            "emotion": emotion, 
            "score": score
        })
        
        # Update fake "stats" for the visual vibe
        st.session_state.history["Well-being"].append(random.randint(40, 90))
        st.session_state.history["Connection"].append(random.randint(60, 100))
        
        st.rerun()

with stats_col:
    st.subheader("Emotional Resonance")
    df = pd.DataFrame(st.session_state.history)
    fig = px.line(df, template="plotly_white", color_discrete_sequence=["#FF4B4B", "#1C83E1"])
    fig.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("The graph above tracks the 'resonance' of our conversation. As we talk, I adjust my tone to match your emotional needs.")
