import streamlit as st
from transformers import pipeline
from datetime import datetime

# --- ENGINE CONFIG ---
@st.cache_resource
def load_context_engine():
    class AdvancedSentience:
        def __init__(self):
            # Stability: using text-classification for sentiment/intent
            self.classifier = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions", top_k=1)
            
        def generate_title(self, text):
            """Creates a meaningful sidebar label from the first message"""
            words = [w for w in text.split() if len(w) > 3]
            return " ".join(words[:3]).title() if words else "New Chat"

        def get_human_reply(self, current_text, history):
            # 1. Detect emotion
            emo_result = self.classifier(current_text)[0][0]
            emotion = emo_result['label']
            
            # 2. Contextual Inference (Sliding Window)
            # We look at the last user topic to acknowledge continuity
            context_snippet = ""
            if len(history) >= 2:
                prev_text = history[-2]['content']
                context_snippet = " ".join(prev_text.split()[-3:])

            # 3. Build Response with 'Human' continuity
            prefix = f"Regarding what we discussed about {context_snippet}... " if context_snippet else ""
            
            responses = {
                'sadness': f"{prefix}I'm so sorry you're feeling this way. It sounds like a lot to handle.",
                'joy': f"{prefix}That's amazing! I can really feel the excitement in your words.",
                'anger': f"{prefix}I hear the frustration. It's completely valid to feel that way.",
                'curiosity': f"{prefix}That's a great question. Let's explore that more deeply."
            }
            
            main_reply = responses.get(emotion, f"{prefix}I'm following you. Tell me more about how you're feeling.")
            return main_reply, emotion, emo_result['score']

    return AdvancedSentience()

bot = load_context_engine()

# --- MULTI-CHAT SESSION STATE ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {} 
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# --- SIDEBAR: NEW CHAT & HISTORY ---
with st.sidebar:
    st.title("🔮 Sentience AI")
    
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        temp_id = f"New Chat {datetime.now().strftime('%H:%M:%S')}"
        st.session_state.all_chats[temp_id] = []
        st.session_state.current_chat_id = temp_id
        st.rerun()

    st.markdown("---")
    st.subheader("History")
    
    for chat_id in list(st.session_state.all_chats.keys()):
        if st.button(f"💬 {chat_id}", key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

# --- MAIN CHAT INTERFACE ---
if st.session_state.current_chat_id is None:
    st.info("Start a new conversation to begin.")
else:
    st.title(st.session_state.current_chat_id)
    active_history = st.session_state.all_chats[st.session_state.current_chat_id]

    # Display History
    for msg in active_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant":
                st.caption(f"Mood: {msg.get('emotion', 'neutral')} | {msg.get('score', 0):.0%}")

    # Chat Input
    if prompt := st.chat_input("How are you truly feeling?"):
        # 1. Rename chat if it's the first message
        if not active_history:
            new_title = bot.generate_title(prompt)
            # Transfer and update key
            st.session_state.all_chats[new_title] = st.session_state.all_chats.pop(st.session_state.current_chat_id)
            st.session_state.current_chat_id = new_title
            active_history = st.session_state.all_chats[new_title]

        # 2. Process message
        active_history.append({"role": "user", "content": prompt})
        
        with st.spinner("Connecting..."):
            reply, emo, conf = bot.get_human_reply(prompt, active_history)
        
        active_history.append({
            "role": "assistant", 
            "content": reply, 
            "emotion": emo, 
            "score": conf
        })
        st.rerun()
