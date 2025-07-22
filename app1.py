
from flask import Flask, request, jsonify
import google.generativeai as genai
import uuid
import json

# Gemini setup
API_KEY = "AIzaSyC0KJrJhZ5V0Ug2-rqejMjnVdnQ13ozfjs"  # Replace with actual key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# MCP context store (in-memory)
sessions = {}

def create_session():
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "context": {
            "user": {"name": None},
            "appointment": {"datetime": None, "purpose": None},
            "task_state": "awaiting_name",
            "history": []
        }
    }
    return session_id

def get_session(session_id):
    return sessions.get(session_id)

def determine_next_action(ctx):
    if not ctx["user"]["name"]:
        return "ask_name"
    elif not ctx["appointment"]["datetime"]:
        return "ask_datetime"
    elif not ctx["appointment"]["purpose"]:
        return "ask_purpose"
    else:
        return "submit_api"

def prompt_ai(system_prompt, user_message):
    convo = model.start_chat(history=[
        {"role": "user", "parts": [system_prompt]},
        {"role": "user", "parts": [user_message]}
    ])
    reply = convo.send_message(user_message)
    return reply.text

def extract_slots(text):
    prompt = (
        f"Extract name, date/time, and purpose from this user input: '{text}'. "
        "Return JSON format: {\"name\":..., \"datetime\":..., \"purpose\":...}"
    )
    try:
        response = model.generate_content(prompt).text
        return json.loads(response)
    except:
        return {}

# Flask setup
app = Flask(__name__)

@app.route("/start", methods=["POST"])
def start():
    session_id = create_session()
    return jsonify({"session_id": session_id})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    session_id = data.get("session_id")
    message = data.get("message")
    sess = get_session(session_id)

    if not sess:
        return jsonify({"error": "Invalid session ID"}), 400

    ctx = sess["context"]
    ctx["history"].append({"role": "user", "message": message})

    action = determine_next_action(ctx)
    reply = ""

    if action == "ask_name":
        reply = "Sure, can I know your name?"
        slots = extract_slots(message)
        if "name" in slots and slots["name"]:
            ctx["user"]["name"] = slots["name"]
            reply = f"Thanks {slots['name']}! When would you like the appointment?"
            ctx["task_state"] = "awaiting_datetime"

    elif action == "ask_datetime":
        slots = extract_slots(message)
        if "datetime" in slots and slots["datetime"]:
            ctx["appointment"]["datetime"] = slots["datetime"]
            reply = f"Got it! What’s the purpose of your visit?"
            ctx["task_state"] = "awaiting_purpose"
        else:
            reply = "Can you please tell me the date and time for your appointment?"

    elif action == "ask_purpose":
        slots = extract_slots(message)
        if "purpose" in slots and slots["purpose"]:
            ctx["appointment"]["purpose"] = slots["purpose"]
            reply = f"Perfect! Confirming your {ctx['appointment']['purpose']} appointment on {ctx['appointment']['datetime']}. Submitting now..."
            ctx["task_state"] = "ready_to_submit"
        else:
            reply = "What’s the purpose of your appointment?"

    elif action == "submit_api":
        # Here we fake API call
        payload = {
            "name": ctx["user"]["name"],
            "datetime": ctx["appointment"]["datetime"],
            "purpose": ctx["appointment"]["purpose"]
        }
        # Simulated API logic
        reply = f"Appointment booked successfully with details: {payload}"
        ctx["task_state"] = "completed"

    ctx["history"].append({"role": "assistant", "message": reply})
    return jsonify({"reply": reply, "context": ctx})

@app.route("/debug/<session_id>", methods=["GET"])
def debug(session_id):
    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(session)

if __name__ == "__main__":
    app.run(debug=True)
