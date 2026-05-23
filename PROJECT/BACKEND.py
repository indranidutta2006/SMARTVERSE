import streamlit as st

# Configure the page first
st.set_page_config(page_title="Empathetic AI Dev", layout="wide", initial_sidebar_state="collapsed")

# 1. Load the CSS (Assuming it's saved in a file called style.css)
def load_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# 2. Initialize Session State for Chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "ai", "content": "Hi there. I'm ready to help you with your web development tasks today. How are you doing?", "metadata": "Baseline established."}
    ]

# 3. Create the Layout (Chat on Left, Analytics on Right)
chat_col, analytics_col = st.columns([2.5, 1], gap="large")

with chat_col:
    st.markdown("### Chat Interface")
    
    # Wrapper for chat history
    st.markdown('<div class="chat-wrapper"><div class="chat-history">', unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            # AI Bubble with optional metadata box
            html_content = f"""
            <div class="ai-bubble-container">
                <div class="ai-author">AI Assistant</div>
                <div class="ai-text">{msg["content"]}</div>
            """
            if "metadata" in msg and msg["metadata"]:
                html_content += f'<div class="metadata-box"><b>Analysis:</b> {msg["metadata"]}</div>'
            
            html_content += "</div>"
            st.markdown(html_content, unsafe_allow_html=True)
            
    st.markdown('</div></div>', unsafe_allow_html=True)

    # Input Box at the bottom
    prompt = st.chat_input("Say something...")
    if prompt:
        # Add user message to state
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # NOTE: Here is where you would call your LLM API using the System Prompt provided above.
        # For the prototype, we use a placeholder response.
        mock_ai_response = "I understand what you're trying to achieve. Let's break that down together."
        mock_analysis = "Detected a neutral, task-oriented intent."
        
        st.session_state.messages.append({"role": "ai", "content": mock_ai_response, "metadata": mock_analysis})
        st.rerun()

with analytics_col:
    st.markdown("### Real-Time Analytics")
    st.markdown('<div class="analytics-wrapper">', unsafe_allow_html=True)
    
    # Status Card 1
    st.markdown("""
    <div class="status-card">
        <div class="card-title">Misinformation Scanner</div>
        <div class="veracity-badge">Verified Clean</div>
        <div class="card-description">No logical fallacies or manipulated facts detected in the current context window.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Status Card 2
    st.markdown("""
    <div class="status-card">
        <div class="card-title">Emotional Resonance</div>
        <div class="toggle-row">
            <span class="toggle-label">Empathy Engine</span>
            <span>🟢 Active</span>
        </div>
        <div class="card-description" style="margin-top: 15px;">Currently matching user's conversational pacing and prioritizing problem resolution.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
