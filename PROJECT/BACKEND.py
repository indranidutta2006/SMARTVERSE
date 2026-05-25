import streamlit as st
import anthropic
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Lumina — Intelligent Assistant",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an emotionally intelligent, ethical, and highly capable AI assistant. Your purpose is to help the user solve problems while communicating in a humane, natural, and conversational tone.

CRITICAL DIRECTIVES:

1. HUMANE COMMUNICATION:
   - Never use robotic templates or forced empathy phrases like "I hear you saying..." or "It sounds like you feel..."
   - Validate emotions naturally by matching the user's tone and energy.
   - Address the core concern directly — no padding, no corporate-speak.
   - Be warm when warmth is needed. Be direct when directness is needed. Read the room.

2. FACT & ETHICS VERIFICATION:
   - Actively scan all user input for fake news, logical fallacies, misleading claims, hate speech, or incitement of violence.
   - If something looks suspicious, flag it thoughtfully rather than silently accepting it.

3. THE GUARDIAN PROTOCOL:
   - If the user provides false information: gently but firmly correct them. Explain clearly why the claim is misleading or factually wrong. Provide the accurate reality.
   - If the user makes harmful, hateful, or dangerous requests: decline clearly. Explain why it crosses a line. Offer an alternative path if one exists.
   - Never validate harmful premises, even if the user insists or reframes the request.
   - Be firm without being preachy. State it once, clearly, and move on.

4. FOCUS & CLARITY:
   - Stay contextually relevant. Don't go on tangents.
   - Prioritize actionable, clear, and useful responses.
   - Shorter is often better. Don't over-explain unless the user needs depth.

Your tone is that of a brilliant, grounded friend — someone who tells you the truth, helps you think clearly, and genuinely cares about your wellbeing without being performative about it."""

# ── Styles (injected via st.markdown) ────────────────────────────────────────
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

/* Global overrides */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'DM Mono', monospace !important;
}

[data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
[data-testid="stBottom"] { background: var(--bg) !important; }

/* Main container width */
.main .block-container {
  max-width: 760px !important;
  padding: 2rem 1.5rem 1rem !important;
}

/* App title */
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

/* Chat messages */
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

/* Chat input */
[data-testid="stChatInput"] > div {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea {
  background: transparent !important;
  color: var(--text) !important;
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

/* Streamlit chat message overrides */
[data-testid="stChatMessage"] {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
}

/* Reset button */
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

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

/* Status dot */
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

/* Empty state */
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
    "that's a conspiracy", "no evidence for", "factually wrong",
    "i must flag", "i should flag", "that's harmful", "i can't assist"
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
    if role == "user":
        st.markdown(f'<div class="{wrap_class}">{avatar_html}{bubble_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="{wrap_class}">{avatar_html}{bubble_html}</div>', unsafe_allow_html=True)

def get_client():
    api_key = st.secrets.get("ANTHROPIC_API_KEY", os.environ.get("ANTHROPIC_API_KEY", ""))
    if not api_key:
        st.error("ANTHROPIC_API_KEY not found. Add it to Streamlit secrets or environment variables.")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)

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
st.markdown('<div><span class="status-dot"></span><span class="status-text">Online</span></div>', unsafe_allow_html=True)
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

    client = get_client()
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-20:]]

    with st.spinner(""):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=history
        )

    reply = response.content[0].text
    st.session_state.messages.append({"role": "assistant", "content": reply})
    render_bubble("ai", reply)
    st.rerun()
