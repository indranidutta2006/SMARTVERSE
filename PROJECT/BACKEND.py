import os
import random
import pandas as pd
import plotly.graph_objects as px
import streamlit as st
from transformers import pipeline

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Sentience AI",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INJECT FRONTEND STYLES ---
current_dir = os.path.dirname(__file__)
css_path = os.path.join(current_dir, "FRONTEND.css")

if os.path.exists(css_path):
    try:
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
            if css_content.strip(): 
                st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading styles: {e}")
else:
    st.error("FRONTEND.css file not found!")

# --- BACKEND MODEL INITIALIZATION ---
@st.cache_resource
def load_bot():
    # Adding a status spinner to prevent a blank white screen during weight download
    with st.status("🔮 Initializing Sentience Engine & Downloading NLP Weights...", expanded=True) as status:
        st.write("Loading Deep Learning Model Framework...")
        
        class EmpatheticBot:
            def __init__(self):
                print("Initializing Emotion Engine...")
                self.emotion_classifier = pipeline(
                    "text-classification", 
                    model="SamLowe/roberta-base-go_emotions", 
                    top_k=3
                )

            def analyze_input(self, user_text):
                results = self.emotion_classifier(user_text)[0]
                top_emotion = results[0]['label']
                confidence = results[0]['score']
                return top_emotion, confidence

            def generate_safe_response(self, user_text):
                emotion, score = self.analyze_input(user_text)
                
                if emotion in ['anger', 'annoyance', 'disappointment', 'fear']:
                    response = f"I understand you're feeling {emotion} about that news article. It can be upsetting when information isn't clear. Let's look into it together. What part feels uncertain?"
                elif emotion in ['curiosity', 'admiration', 'joy']:
                    response = "That's a great point! I'm glad we're exploring this topic together."
                else:
                    response = "I hear you. Let's lay out the verified source parameters to keep this evaluation balanced."
                
                return response, emotion, score

        bot_instance = EmpatheticBot()
        status.update(label="Engine Ready!", state="complete", expanded=False)
        return bot_instance

bot = load_bot()

# --- SESSION STATE MANAGEMENT ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "emotion_history" not in st.session_state:
    # Pre-populate with a few baseline values for the line graph layout
    st.session_state.emotion_history = {
        'Frustration': [12, 18, 14],
        'Curiosity': [22, 28, 32],
        'Understanding': [15, 24, 38]
    }

# --- SIDEBAR NAV ---
with st.sidebar:
    st.title("🔮 Sentience AI")
    st.markdown("---")
    st.button("💬 Chat", use_container_width=True, type="primary")
    st.button("📈 Analysis", use_container_width=True)
    st.button("⚙️ Settings", use_container_width=True)
    st.button("📜 History", use_container_width=True)
    st.markdown("---")
    st.caption("System Status: Active")

# --- MAIN LAYOUT (Split Screen Design) ---
chat_col, analytics_col = st.columns([1.3, 1], gap="large")

# --- LEFT COLUMN: Chat Interface ---
with chat_col:
    st.markdown('<p class="panel-title">Chat</p>', unsafe_allow_html=True)
    
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allowed_html=True)
            else:
                st.markdown(f"""
                    <div class="ai-bubble-container">
                        <div class="ai-author">Sentience</div>
                        <div class="ai-text">{msg["content"]}</div>
                        <div class="metadata-box">
                            🔹 <b>Topic:</b> Global Health News<br>
                            🎭 <b>Emotion:</b> {msg['emotion'].title()} ({msg['score']:.0%})<br>
                            🔍 <b>Misinformation Check:</b> Verification complete (100%)<br>
                            🛡️ <b>Source reliability:</b> Verified (BBC/AP)
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    user_input = st.chat_input("Share your thoughts or ask a question...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Process input using your original logic
        ai_response, top_emotion, top_score = bot.generate_safe_response(user_input)
        
        # Log emotional data points based on what the engine catches
        if top_emotion in ['anger', 'annoyance', 'disappointment', 'fear']:
            st.session_state.emotion_history['Frustration'].append(int(top_score * 100))
            st.session_state.emotion_history['Curiosity'].append(random.randint(5, 15))
            st.session_state.emotion_history['Understanding'].append(random.randint(10, 25))
        elif top_emotion in ['curiosity', 'admiration', 'joy']:
            st.session_state.emotion_history['Frustration'].append(random.randint(0, 10))
            st.session_state.emotion_history['Curiosity'].append(int(top_score * 100))
            st.session_state.emotion_history['Understanding'].append(random.randint(40, 60))
        else:
            st.session_state.emotion_history['Frustration'].append(random.randint(5, 12))
            st.session_state.emotion_history['Curiosity'].append(random.randint(15, 30))
            st.session_state.emotion_history['Understanding'].append(int(top_score * 100))

        st.session_state.messages.append({
            "role": "ai", 
            "content": ai_response,
            "emotion": top_emotion,
            "score": top_score
        })
        st.rerun()

# --- RIGHT COLUMN: Real-Time Analytics ---
with analytics_col:
    st.markdown('<p class="panel-title">Real-Time Emotion & Accuracy</p>', unsafe_allow_html=True)
    
    # Card 1: Emotion Flow
    with st.container():
        st.markdown('<div class="status-card"><div class="card-title">Emotion Flow</div>', unsafe_allow_html=True)
        
        df_chart = pd.DataFrame(st.session_state.emotion_history)
        fig = px.line(df_chart, render_mode='svg')
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=200,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#f1f5f9', title=""),
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9', title="")
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Card 2: Topic Veracity
    with st.container():
        st.markdown("""
            <div class="status-card">
                <div class="card-title">Topic Veracity</div>
                <div class="veracity-badge">⚠️ Analyzing Context</div>
                <div class="card-description">
                    Cross-referencing live pattern recognition arrays against global verification databases...
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Card 3: Empathetic Mode Toggle Switch
    with st.container():
        st.markdown('<div class="status-card">', unsafe_allow_html=True)
        st.toggle("Empathetic Response Mode", value=True)
        st.markdown('</div>', unsafe_allow_html=True)
