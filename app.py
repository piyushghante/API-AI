from flask import Flask, request, jsonify
import google.generativeai as genai
import requests
import random

# ==========================
# 1. Configure Gemini API Keys
# ==========================
GEMINI_API_KEYS = [
    "AIzaSyBDPhRKMHAalaL1EQCho9jADjon9tqHa9s",
    "AIzaSyCxP5EUH3-Unve35MufRUJNWyMx5_0Nry4",
    "AIzaSyDjgx3i_6e714ZE-O2wpJNOK2Gry_XYOac",
   
]

# ==========================
# 2. Get Model with Shuffled API Key
# ==========================
def get_model_with_key_rotation():
    random.shuffle(GEMINI_API_KEYS)
    for key in GEMINI_API_KEYS:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            return model
        except Exception as e:
            print(f"Key failed: {key} | Error: {e}")
    raise Exception("All API keys failed or quota exhausted.")

# ==========================
# 3. Flask App Setup
# ==========================
app = Flask(__name__)
sessions = {}  # session_id -> conversation history + form

# ==========================
# 4. Gemini Chat Function
# ==========================
def call_gemini(messages):
    model = get_model_with_key_rotation()
    chat = model.start_chat()
    for msg in messages:
        if msg["role"] == "user":
            chat.send_message(msg["content"])
    return chat.last.text

# ==========================
# 5. Chat Endpoint
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

    # Add user message to history
    history.append({"role": "user", "content": user_message})

    # Prompt
    system_prompt = (
        "You are a helpful assistant for booking appointments. "
        "Your job is to gather the user's name, appointment date/time, and purpose. "
        "Ask step by step if any info is missing. Once all is collected, say you're booking."
    )
    messages = [{"role": "system", "content": system_prompt}] + history[-5:]

    # Call Gemini
    try:
        assistant_reply = call_gemini(messages)
    except Exception as e:
        return jsonify({"reply": f"❌ Error: {str(e)}", "done": True})

    history.append({"role": "assistant", "content": assistant_reply})

    # Basic field detection
    if not form["name"] and "name" in user_message.lower():
        form["name"] = user_message.strip().split()[-1]
    if not form["datetime"] and any(c in user_message for c in [":", "-", "/"]):
        form["datetime"] = user_message.strip()
    if not form["purpose"] and "purpose" in user_message.lower():
        form["purpose"] = user_message.strip().split()[-1]

    # If form is complete
    if all(form.values()):
        try:
            payload = {
                "name": form["name"],
                "datetime": form["datetime"],
                "purpose": form["purpose"],
            }
            # Fake booking API
            response = requests.post("https://jsonplaceholder.typicode.com/posts", json=payload)
            return jsonify({
                "reply": f"✅ Appointment booked successfully for {form['name']} on {form['datetime']} for {form['purpose']}.",
                "done": True
            })
        except Exception as e:
            return jsonify({"reply": f"❌ Booking failed: {str(e)}", "done": True})

    # Otherwise continue conversation
    return jsonify({"reply": assistant_reply, "done": False})

# ==========================
# 6. Run the Server
# ==========================
# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
