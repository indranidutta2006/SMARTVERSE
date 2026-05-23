import streamlit as st
from transformers import pipeline

# --- CONTEXTUAL ENGINE ---
@st.cache_resource
def load_context_engine():
    class HumanLikeBot:
        def __init__(self):
            # Stability: using text-classification for emotion/intent detection
            self.classifier = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions", top_k=1)
            
        def generate_human_reply(self, current_text, history):
            # 1. ANALYZE CURRENT STATE
            current_emo = self.classifier(current_text)[0][0]
            
            # 2. ANALYZE HISTORY (Looking for the 'it' factor)
            context_snippet = ""
            if len(history) >= 2:
                # Reference the last user topic to maintain continuity
                prev_user_text = history[-2]['content']
                context_snippet = " ".join(prev_user_text.split()[-2:])

            # 3. BUILD DYNAMIC RESPONSE
            if context_snippet and len(history) > 2:
                reply = f"Building on what you said about {context_snippet}... "
            else:
                reply = ""

            # Branching based on emotion
            if current_emo['label'] in ['sadness', 'disappointment']:
                reply += "I'm really sorry to hear that. I'm here for you—want to share more?"
            elif current_emo['label'] in ['joy', 'excitement']:
                reply += "That's fantastic! I love hearing positive updates like this."
            else:
                reply += "I see. I'm following your point—what's next on your mind?"

            return reply, current_emo['label'], current_emo['score']

    return HumanLikeBot()

bot = load_context_engine()

# --- STREAMLIT CHAT APP ---
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🔮 Contextual Sentience")

# Display historical messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User Input
if prompt := st.chat_input("Tell me what's happening..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Process with history awareness
    answer, emo, conf = bot.generate_human_reply(prompt, st.session_state.messages)
    
    st.session_state.messages.append({
        "role": "assistant", 
        "content": answer,
        "emotion": emo,
        "score": conf
    })
    st.rerun()
