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
            # 1. The 'Heart' (Emotion Detection for custom framing)
            self.classifier = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions", top_k=1)
            
            # 2. Generative Model API (Using HuggingFace free inference layer)
            self.API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
            
            # --- FIXED SECRETS RETRIEVAL LAYER ---
            # This references the variable flag inside your local .streamlit/secrets.toml file or cloud dashboard
            hf_token = st.secrets.get("HF_TOKEN", "")
            self.headers = {"Authorization": f"Bearer {hf_token}"} 

        def generate_title(self, text):
            words = [w for w in text.split() if len(w) > 3]
            return " ".join(words[:3]).title() if words else "Conversation Thread"

        def get_dynamic_reply(self, prompt, history):
            # Detect emotional tone to instruct the generator model contextually
            emo_result = self.classifier(prompt)[0][0]
            emotion = emo_result['label']
            
            # REPLICATE CHATGPT/GEMINI CONTINUOUS CONVERSATION MEMORY:
            # Format the entire existing history thread so the AI model understands the full scope contextually
            conversation_context = ""
            for msg in history[:-1]: # Include previous messages up to the current prompt
                role_label = "User" if msg["role"] == "user" else "Assistant"
                conversation_context += f"{role_label}: {msg['content']}\n"
            
            # Construct a human instructions wrapper
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
                    "temperature": 0.7, # Adds variations to avoid repetitive patterns
                    "top_p": 0.9
                }
            }
            
            try:
                response = requests.post(self.API_URL, headers=self.headers, json=payload, timeout=8)
                response.raise_for_status()
                gen_text = response.json()[0]['generated_text']
                # Isolate the newly generated assistant response
                reply = gen_text.split("[/INST]")[-1].strip()
            except Exception:
                # Humane fallback if the API or key configuration fails
                reply = "I'm processing what you just said, and I want to understand it completely. Could you expand on that thought for me?"

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
        # Create a temporary unique chat key containing a clean placeholder string
        tid = f"New Chat ({datetime.now().strftime('%H:%M')})"
        # Seed the new history with the required default greeting statement instantly
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

    # Render clean human dialogue rows
    for msg in active_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Share what's on your mind..."):
        # Check if the session is still named by default placeholders and has no user speech yet
        is_fresh_session = (len(active_history) == 1 and active_history[0]["role"] == "assistant")
        
        # Append the new user text message object to our active history chain array
        active_history.append({"role": "user", "content": prompt})
        
        # Dynamic Renaming execution based on user's very first intent input statement
        if is_fresh_session:
            new_title = bot.generate_title(prompt)
            # Safeguard overlapping key collisions
            if new_title not in st.session_state.all_chats:
                st.session_state.all_chats[new_title] = st.session_state.all_chats.pop(st.session_state.current_chat_id)
                st.session_state.current_chat_id = new_title
                active_history = st.session_state.all_chats[new_title]

        with st.spinner("Reflecting..."):
            # Fetch dynamic continuous reply passing our complete chronological list object
            reply = bot.get_dynamic_reply(prompt, active_history)
        
        # Persist assistant result statement block to memory chain array
        active_history.append({"role": "assistant", "content": reply})
        st.rerun()
