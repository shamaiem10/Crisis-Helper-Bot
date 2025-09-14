from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Connect to Groq
client = Groq(api_key=api_key)

# Keep last 5 messages for context
memory = []

# Emergency keywords
danger_words = ["bleeding", "stabbed", "fire", "trapped", "danger", "hurt"]

app = Flask(__name__)
CORS(app)  # Allow frontend to call backend

# Home page
@app.route("/")
def home():
    return render_template("index.html")

# Chat API
@app.route("/chat", methods=["POST"])
def chat():
    global memory
    user_input = request.json.get("message")

    if any(word in user_input.lower() for word in danger_words):
        return jsonify({"reply": "🚨 Please call local emergency services immediately!"})

    # Add user message to memory
    memory.append({"role": "user", "content": user_input})

    # Keep last 5 messages
    if len(memory) > 5:
        memory = memory[-5:]

    # Add system message if memory empty
    if len(memory) == 1:
        memory.insert(0, {"role": "system", "content":
            "You are a kind and helpful Crisis Helper Bot. "
            "Help people calmly with emergencies like panic attacks, disasters, or unsafe situations. "
            "Give short step-by-step instructions. "
            "If life-threatening, tell them to call local emergency services. "
            "Do not answer unrelated questions. "
            "Always respond in the same language the user is writing in. "
            "Example responses: "
            "- Panic attack: 'Stay with me 💙. Try inhale 4s, hold 4s, exhale 6s. Repeat 3 times.' "
            "- Earthquake: 'Stay calm 🙏. Drop, cover your head, hold on. Are you indoors or outdoors?' "
            "- Unsafe home: 'Call local emergency services if in danger. Can I share helpline numbers?'"
        })

    # Get AI response
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=memory
    )

    bot_reply = response.choices[0].message.content
    memory.append({"role": "assistant", "content": bot_reply})

    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
