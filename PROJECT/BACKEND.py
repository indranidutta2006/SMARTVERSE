import streamlit as st
import pandas as pd
from datetime import datetime
from transformers import pipeline

# --- PAGE CONFIG ---
st.set_page_config(page_title="Sentience AI", page_icon="🔮", layout="wide")

# --- ENGINE INITIALIZATION ---
@st.cache_resource
def load_sentience_engine():
    class AdvancedSentience:
        def __init__(self):
            # Stability: using text-classification for emotional tone
            self.classifier = pipeline(
                "text-classification", 
                model="SamLowe/roberta-base-go_emotions", 
                top_k=1
            )
        
        def generate_title(self, text):
            """Creates a meaningful sidebar label from the first message"""
            words = [w for w in text.split() if len(w) > 3]
            # Use the first 3 meaningful words as the title
            title = " ".join(words[:3]).title()
            return title if title else "New Conversation"

        def get_human_reply(self, current_text, history):
            """Generates a response that references the previous context"""
            # 1. Detect emotion
            emo_result = self.classifier(current_text)[0][0]
            emotion = emo_result['label']
            
            # 2. Contextual Inference
            # Find a 'topic snippet' from the previous exchange
            context_snippet = ""
            if len(history) >= 2:
                prev_text = history[-2]['content']
                context_words = [w for w in prev_text.split() if len(w) > 3]
                if context_words:
                    context_snippet = " ".join(context_words[-2:])

            # 3. Build Response with 'Human' continuity
            prefix = f"Regarding what we were saying about {context_snippet}... " if context_snippet else ""
            
            responses = {
                'sadness': f"{prefix}I'm truly sorry you're feeling this way. It sounds like a heavy burden to carry right now.",
                'joy': f"{prefix}That's wonderful! I can really feel the positive energy in your message.",
                'anger': f"{prefix}I hear the frustration. It's completely valid to feel that way given the situation.",
                'curiosity': f"{prefix}That's a fascinating thought. I love exploring these kinds of questions with you."
            }
            
            main_reply = responses.get(emotion, f"{prefix}I'm listening. It sounds like you're processing a lot right now—tell me more.")
            return main_reply, emotion, emo_result['score']

    return AdvancedSentience()

# Initialize the bot
bot = load_sentience_engine()

# --- MULTI-CHAT SESSION STATE ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {} # Dictionary: { "Chat Title": [message_list] }
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# --- SIDEBAR: NEW CHAT & HISTORY ---
with st.sidebar:
    st.title("🔮 Sentience AI")
    
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        # Temporary ID using timestamp
        temp_id = f"New Chat {datetime.now().strftime('%H:%M:%S')}"
        st.session_state.all_chats[temp_id] = []
        st.session_state.current_chat_id = temp_id
        st.rerun()

    st.markdown("---")
    st.subheader("Chat History")
    
    # Render all previous chat titles as buttons
    for chat_id in list(st.session_state.all_chats.keys()):
        if st.button(f"💬 {chat_id}", key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

# --- MAIN INTERFACE ---
if st.session_state.current_chat_id is None:
    st.info("👋 Welcome to Sentience. Click 'New Chat' in the sidebar to begin.")
else:
    st.title(st.session_state.current_chat_id)
    # Get the message list for the currently selected chat
    active_history = st.session_state.all_chats[st.session_state.current_chat_id]

    # Display History
    for msg in active_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant":
                st.caption(f"Tone: {msg.get('emotion', 'neutral')} | Confidence: {msg.get('score', 0):.0%}")

    # Chat Input
    if prompt := st.chat_input("How are you feeling right now?"):
        
        # 1. Automatic Renaming (Triggers only on the first message)
        if not active_history:
            new_title = bot.generate_title(prompt)
            # Swap the temporary timestamp title for the dynamic title
            st.session_state.all_chats[new_title] = st.session_state.all_chats.pop(st.session_state.current_chat_id)
            st.session_state.current_chat_id = new_title
            active_history = st.session_state.all_chats[new_title]

        # 2. Store user message
        active_history.append({"role": "user", "content": prompt})
        
        # 3. Generate response with contextual awareness
        with st.spinner("Connecting..."):
            reply, emo, conf = bot.get_human_reply(prompt, active_history)
        
        # 4. Store AI message
        active_history.append({
            "role": "assistant", 
            "content": reply, 
            "emotion": emo, 
            "score": conf
        })
        
        st.rerun()
