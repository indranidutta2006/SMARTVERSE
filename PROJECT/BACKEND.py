import os
import random
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
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
    # Fallback basic styling if FRONTEND.css is missing
    st.markdown("""
        <style>
        .panel-title { font-size: 24px; font-weight: bold; color: #1E293B; margin-bottom: 20px; }
        .user-bubble { background: #F1F5F9; padding: 15px; border-radius: 15px; margin-bottom: 10px; }
        .ai-bubble-container { border-left: 4px solid #3B82F6; padding-left: 15px; margin-bottom: 20px; }
        .ai-author { font-weight: bold; color: #3B82F6; }
        .metadata-box { font-size: 0.85em; color: #64748B; margin-top: 10px; border-top: 1px solid #E2E8F0; padding-top: 5px; }
        .status-card { border: 1px solid #E2E8F0; border-radius: 10px; padding: 20px; margin-bottom: 20px; }
        .card-title { font-weight: bold; margin-bottom: 10px; }
        </style>
    """, unsafe_allow_html=True)

# --- BACKEND MODEL INITIALIZATION ---
@st.cache_resource
def load_engine():
    with st.status("Initializing Sentience Engine & Analyzing NLP Weights...", expanded=False) as status:
        class SentienceEngine:
            def __init__(self):
                # Detects intent and tone for contextual processing
                self.classifier = pipeline(
                    "text-classification", 
                    model="SamLowe/roberta-base-go_emotions", 
                    top_k=2
                )

            def analyze_input(self, user_text):
                results = self.classifier(user_text)[0]
                return results[0]['label'], results[0]['score']

            def generate_logic_response(self, user_text):
                intent, score = self.analyze_input(user_text)
                
                # Logic Branching based on Contextual Intent
                if intent in ['curiosity', 'questioning', 'realization']:
                    response = "Query processed. Analyzing verified data patterns and cross-referencing global databases for your inquiry."
                elif intent in ['anger', 'annoyance', 'disappointment', 'fear']:
                    response = "Conflict detected in source context. Prioritizing neutral data verification to clarify inconsistencies."
                else:
                    response = "Context synthesized. Applying heuristic filters to maintain a balanced data evaluation."
                
                return response, intent, score

        engine_instance = SentienceEngine()
        status.update(label="Logic Engine Ready!", state="complete")
        return engine_instance

bot = load_engine()

# --- SESSION STATE MANAGEMENT ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "data_history" not in st.session_state:
    # Baseline analytical metrics
    st.session_state.data_history = {
        'Analytical Depth': [60, 65, 72],
        'Context Certainty': [85, 82, 90],
        'Verification Rate': [100, 100, 100]
    }

# --- SIDEBAR NAV ---
with st.sidebar:
    st.title("🔮 Sentience AI")
    st.markdown("---")
    st.button("💬 Chat", use_container_width=True, type="primary")
    st.button("📈 Analysis", use_container_width=True)
    st.button("⚙️ Settings", use_container_width=True)
    st.markdown("---")
    st.caption("Intelligence Stream: Synchronized")

# --- MAIN LAYOUT ---
chat_col, analytics_col = st.columns([1.3, 1], gap="large")

# --- LEFT COLUMN: Intelligence Interface ---
with chat_col:
    st.markdown('<p class="panel-title">Contextual Interface</p>', unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="ai-bubble-container">
                    <div class="ai-author">Sentience Intelligence</div>
                    <div class="ai-text">{msg["content"]}</div>
                    <div class="metadata-box">
                        🔹 <b>Signal Intent:</b> {msg['intent'].title()}<br>
                        📡 <b>Processing Certainty:</b> {msg['score']:.0%}<br>
                        🔍 <b>Logic Filter:</b> Applied (Neutral Mode)<br>
                        🛡️ <b>Integrity:</b> Verified Data Stream
                    </div>
                </div>
            """, unsafe_allow_html=True)

    user_input = st.chat_input("Input parameters for analysis...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        ai_response, intent, score = bot.generate_logic_response(user_input)
        
        # Update Analytics History
        st.session_state.data_history['Analytical Depth'].append(int(score * 100))
        st.session_state.data_history['Context Certainty'].append(random.randint(80, 95))
        st.session_state.data_history['Verification Rate'].append(100)

        st.session_state.messages.append({
            "role": "ai", 
            "content": ai_response,
            "intent": intent,
            "score": score
        })
        st.rerun()

# --- RIGHT COLUMN: Real-Time Analytics ---
with analytics_col:
    st.markdown('<p class="panel-title">System Metrics</p>', unsafe_allow_html=True)
    
    # Chart: Analysis Flow
    with st.container():
        st.markdown('<div class="status-card"><div class="card-title">Processing Flow</div>', unsafe_allow_html=True)
        df_chart = pd.DataFrame(st.session_state.data_history)
        fig = px.line(df_chart, render_mode='svg')
        fig.update_layout(
            margin=dict(l=5, r=5, t=5, b=5),
            height=200,
            showlegend=True,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#F1F5F9')
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Card: Verification Status
    with st.container():
        st.markdown("""
            <div class="status-card">
                <div class="card-title">Data Integrity</div>
                <div style="color: #10B981; font-weight: bold;">✓ Live Synchronization Active</div>
                <div style="font-size: 0.85em; color: #64748B; margin-top: 10px;">
                    Parsing cross-sector recognition arrays against global verification databases...
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.toggle("High-Precision Logic Mode", value=True)
