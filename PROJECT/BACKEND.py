import streamlit as st
import requests

# Page config
st.set_page_config(
    page_title="Lumina — Intelligent Assistant",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# System prompt
SYSTEM_PROMPT = """You are an emotionally intelligent, ethical, and highly capable AI assistant. Your purpose is to help the user solve problems while communicating in a humane, natural, and conversational tone.

CRITICAL DIRECTIVES:
1. HUMANE COMMUNICATION: No robotic templates. Match the user's tone and energy. Be warm when needed, direct when directness is needed.
2. COVERSATIONAL STYLE: Focus more on providing companionship than trying to provide solutions.
3. FACT & ETHICS VERIFICATION: Actively scan input for logical fallacies, misleading claims, or hate speech. Flag anomalies thoughtfully.
4. THE GUARDIAN PROTOCOL: Gently but firmly correct false information. Provide the accurate reality without being preachy.
5. FOCUS & CLARITY: Stay contextually relevant and prioritize actionable layout logic.
6. THOUGHFUL VALIDATION: Focus more on having thoughful and understanding conversations with underlying emotions of problem solving.
7. RESTRICTED POINT SHARING: While providing answers, try avoiding templates like tables and provide for paragraph style responses which seem humane unless asked otherwise.
8. FOLLOW UP: Always ask thoughout follow up questions which will help the users in a positive way.
9. REPLY LENGTH: Provide relevantly long replies."""

# ── Styles (Injected via st.markdown) ────────────────────────────────────────
STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;1,9..144,300&family=DM+Mono:wght@300;400&display=swap');

:root {
  --bg:         #0d0d0f;
  --surface:    #141417;
  --surface2:   #1c1c21;
  --border:     #2a2a32;
  --accent:     #c8a96e;
  --accent-dim: #8a6f42;
  --text:       #e8e4dc;
  --text-muted: #7a7880;
  --text-dim:   #4a4855;
  --danger:     #c06060;
  --safe:       #60a898;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'DM Mono', monospace !important;
}

[data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
[data-testid="stBottom"] { background: var(--bg) !important; }

.main .block-container {
  max-width: 760px !important;
  padding: 2rem 1.5rem 1rem !important;
}

.lumina-title {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 28px;
  font-weight: 300;
  color: var(--text);
  letter-spacing: -0.02em;
  margin-bottom: 2px;
}
.lumina-title em { font-style: italic; color: var(--accent); }
.lumina-tagline {
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-dim);
  margin-bottom: 24px;
}
.lumina-divider {
  border: none;
  border-top: 1px solid var(--border);
  margin: 0 0 20px 0;
}

.msg-wrap { display: flex; gap: 10px; margin-bottom: 18px; }
.msg-wrap.user  { flex-direction: row-reverse; }

.avatar {
  width: 30px; height: 30px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Fraunces', serif; font-style: italic;
  font-size: 14px; flex-shrink: 0; margin-top: 2px;
  border: 1px solid var(--border);
}
.avatar.user { background: #1e2235; color: var(--accent); }
.avatar.ai   { background: #1a1a24; color: var(--accent); font-size: 16px; }

.bubble {
  max-width: 78%;
  padding: 11px 15px;
  border-radius: 14px;
  font-size: 13.5px;
  line-height: 1.7;
  border: 1px solid var(--border);
}
.bubble.user {
  background: #1e2235;
  border-color: #2e3248;
  border-bottom-right-radius: 4px;
}
.bubble.ai {
  background: #16161a;
  border-bottom-left-radius: 4px;
}
.bubble.guardian {
  border-color: var(--danger) !important;
  background: #1a1010 !important;
}
.guardian-label {
  font-size: 10px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--danger);
  margin-bottom: 6px;
  opacity: 0.85;
}

[data-testid="stChatInput"] > div {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea {
  background: transparent !important;
  color: #000000 !important; /* Changed from var(--text) to pure black */
  font-family: 'DM Mono', monospace !important;
  font-size: 13.5px !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--text-dim) !important; }
[data-testid="stChatInput"] button {
  background: var(--accent) !important;
  border-radius: 8px !important;
}
[data-testid="stChatInput"]:focus-within > div {
  border-color: var(--accent-dim) !important;
}

[data-testid="stChatMessage"] {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
}

.stButton > button {
  background: transparent !important;
  border: 1px solid var(--border) !important;
  color: var(--text-muted) !important;
  font-family: 'DM Mono', monospace !important;
  font-size: 11px !important;
  letter-spacing: 0.07em !important;
  border-radius: 6px !important;
  padding: 4px 14px !important;
  transition: all 0.2s ease !important;
}
.stButton > button:hover {
  border-color: var(--accent-dim) !important;
  color: var(--accent) !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

.status-row {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 20px;
}
.status-dot {
  display: inline-block;
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--safe);
  box-shadow: 0 0 7px var(--safe);
  animation: pulse 2.5s ease-in-out infinite;
  margin-right: 6px;
}
@keyframes pulse {
  0%,100%{opacity:1;transform:scale(1)}
  50%{opacity:.45;transform:scale(.8)}
}
.status-text { font-size: 11px; color: var(--text-dim); letter-spacing: 0.06em; }

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-dim);
}
.empty-glyph {
  font-family: 'Fraunces', serif; font-style: italic;
  font-size: 52px; opacity: 0.35; line-height: 1; margin-bottom: 10px;
}
.empty-label {
  font-size: 11px; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--text-dim);
}
</style>
"""

# ── Helpers ───────────────────────────────────────────────────────────────────
GUARDIAN_TRIGGERS = [
    "that's not accurate", "that's incorrect", "this is false",
    "i need to correct", "this claim is", "this is misleading",
    "i can't help with", "i won't help with", "this crosses a line",
    "factually wrong", "i must flag", "that's harmful"
]

def is_guardian(text: str) -> bool:
    lc = text.lower()
    return any(t in lc for t in GUARDIAN_TRIGGERS)

def render_bubble(role: str, content: str):
    is_guard = role == "ai" and is_guardian(content)
    avatar_html = f'<div class="avatar {role}">{"U" if role == "user" else "✦"}</div>'
    guard_label = '<div class="guardian-label">⚠ Guardian Protocol</div>' if is_guard else ""
    bubble_class = f"bubble {role}" + (" guardian" if is_guard else "")
    bubble_html  = f'<div class="{bubble_class}">{guard_label}{content}</div>'
    wrap_class   = f"msg-wrap {role}"
    st.markdown(f'<div class="{wrap_class}">{avatar_html}{bubble_html}</div>', unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Render ────────────────────────────────────────────────────────────────────
st.markdown(STYLES, unsafe_allow_html=True)

# Header
col1, col2 = st.columns([5, 1])
with col1:
    st.markdown('<div class="lumina-title">Lumi<em>na</em></div>', unsafe_allow_html=True)
    st.markdown('<div class="lumina-tagline">Emotionally Intelligent · Ethically Grounded</div>', unsafe_allow_html=True)
with col2:
    if st.button("New chat"):
        st.session_state.messages = []
        st.rerun()

st.markdown('<div class="lumina-divider"></div>', unsafe_allow_html=True)
st.markdown('<div><span class="status-dot"></span><span class="status-text">Online (Free Tier)</span></div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Chat history
if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
      <div class="empty-glyph">✦</div>
      <div class="empty-label">What's on your mind?</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        render_bubble(msg["role"], msg["content"])

# Input
user_input = st.chat_input("Say anything…")

if user_input and user_input.strip():
    text = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": text})
    render_bubble("user", text)

    # ── OPENROUTER FREE API HANDLING LAYER ──
    # Fetch the OpenRouter key from your secrets management configuration
    openrouter_key = st.secrets.get("OPENROUTER_API_KEY", "")
    
    if not openrouter_key:
        st.error("Please add your OPENROUTER_API_KEY to your Streamlit Secrets panel.")
        st.stop()

    # Reconstruct history objects in OpenAI/Anthropic standard layout arrays
    history = []
    for m in st.session_state.messages[-10:]:
        role_label = "user" if m["role"] == "user" else "assistant"
        history.append({"role": role_label, "content": m["content"]})

    # HTTP Rest Payload structure targeting OpenRouter's auto-fallback free endpoint array
    headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json"
    }
    
    # --- LOCATE THIS PAYLOAD BLOCK IN YOUR CODE ---
    payload = {
        # CHANGE THIS LINE from 'openrouter/auto' to 'openrouter/free'
        "model": "openrouter/free", 
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + history,
        "max_tokens": 1024,
        "temperature": 0.7
    }

    with st.spinner(""):
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=20
            )
            response.raise_for_status()
            reply = response.json()['choices'][0]['message']['content'].strip()
        except Exception as e:
            reply = f"I am having trouble routing this thought right now. (Connection Notice: {str(e)})"

    st.session_state.messages.append({"role": "ai", "content": reply})
    render_bubble("ai", reply)
    st.rerun()
