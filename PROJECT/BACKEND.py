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
if "all_chats" not in st.session_state: st.session_state.all_chats = {}import streamlit as st
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
