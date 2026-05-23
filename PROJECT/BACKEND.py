import streamlit as st
import pandas as pd
from datetime import datetime
from transformers import pipeline

# --- ENGINE ---
@st.cache_resource
def load_engine():
    class SmartBot:
        def __init__(self):
            # Using the stable classification model
            self.classifier = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions", top_k=1)
        
        def generate_title(self, text):
            """Extracts a short title from the first message"""
            words = [w for w in text.split() if len(w) > 3]
            # Take the first 3 meaningful words
            title = " ".join(words[:3]).title()
            return title if title else "New Conversation"

        def get_reply(self, text, history):
            # Detect emotion
            emo = self.classifier(text)[0][0]
            # Simple keyword extraction for context
            topic = " ".join([w for w in text.split() if len(w) > 3][-2:])
            reply = f"I hear you talking about {topic}. It sounds like you're feeling {emo['label']}."
            return reply, emo['label'], emo['score']

    return SmartBot()

bot = load_engine()

# --- STATE MANAGEMENT ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {} # { "Chat Name": [messages] }
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# --- SIDEBAR: NAVIGATION ---
with st.sidebar:
    st.title("🔮 Sentience AI")
    
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        # Temporary ID until renamed
        temp_id = f"New Chat {datetime.now().strftime('%H:%M:%S')}"
        st.session_state.all_chats[temp_id] = []
        st.session_state.current_chat_id = temp_id
        st.rerun()

    st.markdown("---")
    st.subheader("History")
    
    # List all chat names
    for chat_id in list(st.session_state.all_chats.keys()):
        if st.button(f"💬 {chat_id}", key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

# --- MAIN INTERFACE ---
if st.session_state.current_chat_id is None:
    st.info("Click 'New Chat' to start a conversation.")
else:
    st.title(st.session_state.current_chat_id)
    chat_history = st.session_state.all_chats[st.session_state.current_chat_id]

    # Display History
    for msg in chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Say something..."):
        # 1. Store User Input
        chat_history.append({"role": "user", "content": prompt})

        # 2. DYNAMIC RENAMING (Only if it's the first message)
        if len(chat_history) == 1:
            new_title = bot.generate_title(prompt)
            # Transfer history to new key and delete old one
            st.session_state.all_chats[new_title] = st.session_state.all_chats.pop(st.session_state.current_chat_id)
            st.session_state.current_chat_id = new_title

        # 3. Generate AI Response
        with st.spinner("Reflecting..."):
            answer, emo, conf = bot.get_reply(prompt, chat_history)
        
        chat_history.append({
            "role": "assistant", 
            "content": answer, 
            "emotion": emo, 
            "score": conf
        })
        st.rerun()
