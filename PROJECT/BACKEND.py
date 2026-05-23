import streamlit as st
import requests
import time
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Sentience AI", page_icon="🔮", layout="wide")

# --- DYNAMIC ENGINE ---
@st.cache_resource
def load_dynamic_engine():
    class DynamicSentience:
        def __init__(self):
            # Safe Secrets Access Layer
            hf_token = st.secrets.get("HF_TOKEN", "")
            self.headers = {"Authorization": f"Bearer {hf_token}"} 
            
            # API Endpoints
            self.EMOTION_URL = "https://api-inference.huggingface.co/models/SamLowe/roberta-base-go_emotions"
            self.GENERATION_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

        def _query_api_with_retry(self, url, payload, max_retries=5, initial_delay=3):
            """Safely waits and retries if the Hugging Face model is waking up (Cold Start)"""
            delay = initial_delay
            for i in range(max_retries):
                try:
                    response = requests.post(url, headers=self.headers, json=payload, timeout=15)
                    res_json = response.json()
                    
                    # Check if Hugging Face tells us the model is loading
                    if isinstance(res_json, dict) and "estimated_time" in res_json:
                        time.sleep(delay)
                        delay += 2  # Gradually increase wait time
                        continue
                        
                    response.raise_for_status()
                    return res_json
                except Exception:
                    if i == max_retries - 1:
                        raise
                    time.sleep(delay)
            return None

        def generate_title(self, text):
            words = [w for w in text.split() if len(w) > 3]
            return " ".join(words[:3]).title() if words else "Conversation Thread"

        def get_dynamic_reply(self, prompt, history):
            # 1. Cloud-based Emotion Detection with retry framework
            try:
                emo_data = self._query_api_with_retry(self.EMOTION_URL, {"inputs": prompt})
                emotion = emo_data[0][0]['label']
            except Exception:
                emotion = "neutral" 
            
            # 2. Build Continuous Conversation Memory Context
            conversation_context = ""
            for msg in history[:-1]:
                role_label = "User" if msg["role"] == "user" else "Assistant"
                conversation_context += f"{role_label}: {msg['content']}\n"
            
            # Construct human wrapper instructions
            system_prompt = (
                f"You are an organic, highly empathetic, and human-like conversational AI. "
                f"The user is feeling subtle hints of {emotion}. Maintain continuity by remembering everything "
                f"said prior, and respond warmly and naturally. Do not sound robotic or mention that you are an AI.\n"
                f"Past log context:\n{conversation_context}"
            )
            
            # Format payload for Mistral Instruct syntax
            full_prompt = f"<s>[INST] {system_prompt}\nUser: {prompt} [/INST]"
            payload = {
                "inputs": full_prompt, 
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.7, 
                    "top_p": 0.9
                }
            }
            
            # 3. Dynamic Text Generation with retry framework
            try:
                gen_data = self._query_api_with_retry(self.GENERATION_URL, payload)
                gen_text = gen_data[0]['generated_text']
                reply = gen_text.split("[/INST]")[-1].strip()
            except Exception:
                reply = "I'm reflecting deeply on what you just shared. Could you talk a bit more about that thought?"

            return reply

    return DynamicSentience()

bot = load_dynamic_engine()

# --- SIDEBAR & CHAT SESSION HISTORY MANAGEMENT ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# INSTANT SESSION INITIALIZATION: Open default chat session automatically on first load
if not st.session_state.all_chats:
    default_session_name = "New Chat Session"
    st.session_state.all_chats[default_session_name] = [
        {"role": "assistant", "content": "Hi, how can I help you today?"}
    ]
    st.session_state.current_chat_id = default_session_name

with st.sidebar:
    st.title("🔮 Sentience AI")
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        tid = f"New Chat ({datetime.now().strftime('%H:%M')})"
        st.session_state.all_chats[tid] = [
            {"role": "assistant", "content": "Hi, how can I help you today?"}
        ]
        st.session_state.current_chat_id = tid
        st.rerun()
        
    st.markdown("---")
    st.subheader("Saved Histories")
    for cid in list(st.session_state.all_chats.keys()):
        if st.button(f"💬 {cid}", key=cid, use_container_width=True):
            st.session_state.current_chat_id = cid
            st.rerun()

# --- MAIN CHAT INTERFACE ---
if st.session_state.current_chat_id:
    active_history = st.session_state.all_chats[st.session_state.current_chat_id]
    st.title(st.session_state.current_chat_id)

    for msg in active_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Share what's on your mind..."):
        is_fresh_session = (len(active_history) == 1 and active_history[0]["role"] == "assistant")
        active_history.append({"role": "user", "content": prompt})
        
        if is_fresh_session:
            new_title = bot.generate_title(prompt)
            if new_title not in st.session_state.all_chats:
                st.session_state.all_chats[new_title] = st.session_state.all_chats.pop(st.session_state.current_chat_id)
                st.session_state.current_chat_id = new_title
                active_history = st.session_state.all_chats[new_title]

        with st.spinner("Reflecting..."):
            reply = bot.get_dynamic_reply(prompt, active_history)
        
        active_history.append({"role": "assistant", "content": reply})
        st.rerun()
