import streamlit as st
import os

# Configure the page for a clean, centered layout
st.set_page_config(page_title="Aware AI", page_icon="🌐", layout="centered", initial_sidebar_state="collapsed")

# Load CSS dynamically
def load_css(file_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(current_dir, file_name)
    try:
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Styling file {file_name} not found. Running with default styles.")

load_css("FRONTEND.css")

# App Header
st.markdown("<h2 style='text-align: center; margin-bottom: 2rem;'>Contextual & Aware AI</h2>", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello. I'm here to help you work through your topics today. What's on your mind?", "flagged": False}
    ]

# Display Chat History
for msg in st.session_state.messages:
    # We use Streamlit's native chat UI for a cleaner look
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # If the AI flagged misinformation in its response, display a warning badge
        if msg.get("flagged"):
            st.markdown('<div class="guardrail-badge">⚠️ Misinformation / Policy Violation Detected</div>', unsafe_allow_html=True)

# The Input Box (Anchored to the bottom natively by Streamlit)
if prompt := st.chat_input("Message the assistant..."):
    # 1. Add user prompt to UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate AI Response (Placeholder for your actual LLM API call)
    # You would pass the System Prompt here, evaluate the input, and return the response.
    
    # Mock logic: Simulating the AI detecting something harmful/fake
    is_harmful_or_fake = "fake" in prompt.lower() or "hate" in prompt.lower()
    
    if is_harmful_or_fake:
        mock_response = "I need to clarify that the premise of that statement is factually incorrect. Let's look at the verified data..."
    else:
        mock_response = "That makes sense. Let's break down the best way to handle that."

    # 3. Add AI response to UI
    st.session_state.messages.append({"role": "assistant", "content": mock_response, "flagged": is_harmful_or_fake})
    with st.chat_message("assistant"):
        st.markdown(mock_response)
        if is_harmful_or_fake:
            st.markdown('<div class="guardrail-badge">⚠️ Misinformation / Policy Violation Detected</div>', unsafe_allow_html=True)
