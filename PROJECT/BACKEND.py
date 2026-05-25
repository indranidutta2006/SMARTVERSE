from flask import Flask, request, jsonify, send_from_directory
import anthropic
import os

app = Flask(__name__, static_folder=".")

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

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

conversation_histories = {}

@app.route("/")
def index():
    return send_from_directory(".", "FRONTENDHTML.html")

@app.route("/FRONTENDCSS.css")
def styles():
    return send_from_directory(".", "FRONTENDCSS.css")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    session_id = data.get("session_id", "default")
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    if session_id not in conversation_histories:
        conversation_histories[session_id] = []

    conversation_histories[session_id].append({
        "role": "user",
        "content": user_message
    })

    # Keep last 20 messages to avoid token overflow
    history = conversation_histories[session_id][-20:]

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=history
    )

    assistant_message = response.content[0].text

    conversation_histories[session_id].append({
        "role": "assistant",
        "content": assistant_message
    })

    return jsonify({"reply": assistant_message})

@app.route("/reset", methods=["POST"])
def reset():
    data = request.get_json()
    session_id = data.get("session_id", "default")
    conversation_histories.pop(session_id, None)
    return jsonify({"status": "reset"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
