import streamlit as st
from transformers import pipeline
import requests # Used for the generative API call

# --- DYNAMIC GENERATOR SETUP ---
@st.cache_resource
def load_sentience_engine():
    class DynamicSentience:
        def __init__(self):
            # 1. The 'Ear': Detects how the user feels
            self.classifier = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions")
            
        def generate_dynamic_reply(self, prompt, history, api_key):
            # A. Get the Emotion
            emo = self.classifier(prompt)[0][0]
            emotion_label = emo['label']
            
            # B. Build the 'Memory' context
            past_context = "\n".join([f"{m['role']}: {m['content']}" for m in history[-3:]])
            
            # C. Call a Generative Model (Example using a free Inference API)
            # You can replace this with OpenAI, Anthropic, or a local Llama model
            API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            system_instruction = f"You are a helpful AI. The user is feeling {emotion_label}. " \
                                 f"Respond naturally, acknowledging the history: {past_context}"
            
            payload = {"inputs": f"{system_instruction}\nUser: {prompt}\nAI:"}
            response = requests.post(API_URL, headers=headers, json=payload)
            
            try:
                # Extracting just the generated text
                full_text = response.json()[0]['generated_text']
                reply = full_text.split("AI:")[-1].strip()
            except:
                reply = "I'm having trouble generating a thought right now, but I hear you."
                
            return reply, emotion_label, emo['score']

    return DynamicSentience()

bot = load_sentience_engine()

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
