from flask import Flask, request, jsonify
import google.generativeai as genai
import requests
import os

# ==========================
# 1. Configure Gemini
# ==========================
genai.configure(api_key="AIzaSyC0KJrJhZ5V0Ug2-rqejMjnVdnQ13ozfjs")  # Replace with your Gemini API key
model = genai.GenerativeModel("gemini-1.5-flash")

# ==========================
# 2. Flask app setup
# ==========================
app = Flask(__name__)
sessions = {}  # session_id -> conversation and user data

# ==========================
# 3. Gemini Call Handler
# ==========================
def call_gemini(messages):
    chat = model.start_chat()
    for msg in messages:
        if msg["role"] == "user":
            chat.send_message(msg["content"])
        elif msg["role"] == "system":
            pass  # You can prepend this to context if needed
    return chat.last.text

# ==========================
# 4. Chat Endpoint
# ==========================
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    session_id = data.get("session_id", "default")
    user_message = data.get("message", "")

    # Create session state if not exists
    if session_id not in sessions:
        sessions[session_id] = {
            "history": [],
            "form": {"name": None, "datetime": None, "purpose": None},
        }

    state = sessions[session_id]
    history = state["history"]
    form = state["form"]

    # Append new user message
    history.append({"role": "user", "content": user_message})

    # Prompt for Gemini
    system_prompt = (
        "You are a helpful assistant for booking appointments. "
        "Your job is to gather the user's name, appointment date/time, and purpose. "
        "Ask step by step if any info is missing. Once all is collected, say you're booking."
    )
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history[-5:])  # Limit context for speed

    # Call Gemini
    assistant_reply = call_gemini(messages)
    history.append({"role": "assistant", "content": assistant_reply})

    # Very basic logic to extract fields (for demo only)
    if not form["name"] and "name" in user_message.lower():
        form["name"] = user_message.strip().split()[-1]
    if not form["datetime"] and any(c in user_message for c in [":", "-", "/"]):
        form["datetime"] = user_message.strip()
    if not form["purpose"] and "purpose" in user_message.lower():
        form["purpose"] = user_message.strip().split()[-1]

    # If all data collected, call mock API
    if all(form.values()):
        try:
            payload = {
                "name": form["name"],
                "datetime": form["datetime"],
                "purpose": form["purpose"],
            }
            # Fake booking API (mock)
            api_response = requests.post("https://jsonplaceholder.typicode.com/posts", json=payload)
            return jsonify({
                "reply": f"✅ Appointment booked successfully for {form['name']} on {form['datetime']} for {form['purpose']}.",
                "done": True
            })
        except Exception as e:
            return jsonify({"reply": f"❌ Error while booking: {str(e)}", "done": True})

    # Return next assistant reply
    return jsonify({"reply": assistant_reply, "done": False})

# ==========================
# 5. Run Server
# ==========================
# if __name__ == '__main__':
#     app.run(debug=True)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
