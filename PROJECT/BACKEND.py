import streamlit as st
import requests
from datetime import datetime
from transformers import pipeline

# --- PAGE CONFIG ---
st.set_page_config(page_title="Sentience AI", page_icon="🔮", layout="wide")

# --- DYNAMIC ENGINE ---
@st.cache_resource
def load_dynamic_engine():
    class DynamicSentience:
        def __init__(self):
            # 1. The 'Heart' (Emotion Detection)
            self.classifier = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions", top_k=1)
            
            # 2. Generative Model API (Using HuggingFace free inference)
            self.API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
            # It will look for your token inside .streamlit/secrets.toml
            self.headers = {"Authorization": f"Bearer {st.secrets.get('HF_TOKEN', '')}"} 

        def generate_title(self, text):
            words = [w for w in text.split() if len(w) > 3]
            return " ".join(words[:3]).title() if words else "New Chat"

        def get_dynamic_reply(self, prompt, history):
            emo_result = self.classifier(prompt)[0][0]
            emotion = emo_result['label']
            
            chat_context = "\n".join([f"{m['role']}: {m['content']}" for m in history[-3:]])
            
            system_prompt = f"You are a highly empathetic AI. The user is currently feeling {emotion}. " \
                            f"Respond naturally to their last message based on this chat history:\n{chat_context}\n"
            
            payload = {"inputs": f"<s>[INST] {system_prompt} \nUser: {prompt} [/INST]", "parameters": {"max_new_tokens": 150}}
            
            try:
                response = requests.post(self.API_URL, headers=self.headers, json=payload, timeout=5)
                gen_text = response.json()[0]['generated_text']
                reply = gen_text.split("[/INST]")[-1].strip()
            except Exception:
                reply = f"I hear you. It sounds like '{prompt}' is really on your mind right now. Tell me more."

            return reply

    return DynamicSentience()

bot = load_dynamic_engine()

# --- SIDEBAR & HISTORY LOGIC ---
if "all_chats" not in st.session_state: st.session_state.all_chats = {}
if "current_chat_id" not in st.session_state: st.session_state.current_chat_id = None

with st.sidebar:
    st.title("🔮 Sentience AI")
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        tid = f"New Chat {datetime.now().strftime('%H:%M:%S')}"
        st.session_state.all_chats[tid] = []
        st.session_state.current_chat_id = tid
        st.rerun()
    st.markdown("---")
    for cid in list(st.session_state.all_chats.keys()):
        if st.button(f"💬 {cid}", key=cid, use_container_width=True):
            st.session_state.current_chat_id = cid
            st.rerun()

# --- MAIN INTERFACE ---
if st.session_state.current_chat_id:
    active_history = st.session_state.all_chats[st.session_state.current_chat_id]
    st.title(st.session_state.current_chat_id)

    # Display clean history without the metadata scales
    for msg in active_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            # The line tracking 'st.caption(Tone/Confidence)' has been removed from here 

    if prompt := st.chat_input("What's on your mind?"):
        if not active_history:
            new_t = bot.generate_title(prompt)
            st.session_state.all_chats[new_t] = st.session_state.all_chats.pop(st.session_state.current_chat_id)
            st.session_state.current_chat_id = new_t
            active_history = st.session_state.all_chats[new_t]

        active_history.append({"role": "user", "content": prompt})
        with st.spinner("Thinking..."):
            reply = bot.get_dynamic_reply(prompt, active_history)
        
        # Storing clean messages 
        active_history.append({"role": "assistant", "content": reply})
        st.rerun()
