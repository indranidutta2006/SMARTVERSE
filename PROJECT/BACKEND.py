import streamlit as st
import pandas as pd
import random
from datetime import datetime
from transformers import pipeline

# --- PAGE CONFIG ---
st.set_page_config(page_title="Sentience AI", layout="wide")

# --- ENGINE INITIALIZATION ---
@st.cache_resource
def load_sentience_engine():
    class ContextualBot:
        def __init__(self):
            self.classifier = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions", top_k=1)
        
        def extract_topic(self, history):
            if len(history) < 2: return "our conversation"
            last_user_msg = history[-1]["content"] if history[-1]["role"] == "user" else ""
            words = [w for w in last_user_msg.lower().split() if len(w) > 3]
            return f"'{ ' '.join(words[-2:]) }'" if words else "what you shared"

        def generate_contextual_reply(self, current_input, history):
            emotion_data = self.classifier(current_input)[0][0]
            emotion = emotion_data['label']
            topic = self.extract_topic(history)
            
            replies = {
                'sadness': f"I'm truly sorry about {topic}. It's understandable to feel {emotion}.",
                'joy': f"That sounds wonderful! {topic.capitalize()} clearly brings you {emotion}.",
                'anger': f"I can hear the frustration regarding {topic}. It's valid to feel {emotion}."
            }
            reply = replies.get(emotion, f"I'm following what you're saying about {topic}.")
            return reply, emotion, emotion_data['score']

    return ContextualBot()

bot = load_sentience_engine()

# --- MULTI-CHAT SESSION MANAGEMENT ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {} # Dictionary to store { "Chat Name": [messages] }
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "Default Chat"
if st.session_state.current_chat_id not in st.session_state.all_chats:
    st.session_state.all_chats[st.session_state.current_chat_id] = []

# --- SIDEBAR: HISTORY & NEW CHAT ---
with st.sidebar:
    st.title("🔮 Sentience AI")
    
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        # Create a unique ID for the new chat
        new_id = f"Chat {datetime.now().strftime('%H:%M:%S')}"
        st.session_state.all_chats[new_id] = []
        st.session_state.current_chat_id = new_id
        st.rerun()

    st.markdown("---")
    st.subheader("Previous Chats")
    
    # Selection box to switch between chats
    chat_options = list(st.session_state.all_chats.keys())
    selected_chat = st.selectbox("Select History", chat_options, index=chat_options.index(st.session_state.current_chat_id))
    
    if selected_chat != st.session_state.current_chat_id:
        st.session_state.current_chat_id = selected_chat
        st.rerun()

    if st.button("🗑️ Clear All History"):
        st.session_state.all_chats = {"Default Chat": []}
        st.session_state.current_chat_id = "Default Chat"
        st.rerun()

# --- MAIN CHAT INTERFACE ---
st.title(f"Intelligence Stream: {st.session_state.current_chat_id}")
current_messages = st.session_state.all_chats[st.session_state.current_chat_id]

# Display current chat history
for msg in current_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat Input
if prompt := st.chat_input("Type your message..."):
    # Append User Message
    current_messages.append({"role": "user", "content": prompt})
    
    # Generate and Append AI Message
    with st.spinner("Synthesizing..."):
        answer, emo, conf = bot.generate_contextual_reply(prompt, current_messages)
    
    current_messages.append({
        "role": "assistant", 
        "content": answer, 
        "emotion": emo, 
        "score": conf
    })
    
    st.rerun()
