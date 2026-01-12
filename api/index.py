from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

# --- SAFE IMPORT ---
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
HF_TOKEN = os.environ.get("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"

SYSTEM_CONTEXT = """
You are the AI Assistant for Medly (Tagline: Build It).
Your Goal: Answer customer questions about vacuum flasks.
RULES:
1. WARRANTY: 10 Years on heat retention.
2. SHIPPING: Free across India (2-4 business days).
3. RETURNS: 7-day easy return policy for manufacturing defects.
4. CONTACT: support@mymedly.in
5. TONE: Professional, concise (max 2 sentences).
6. PRICE: "Please check the product page for the latest price."
"""

# --- BACKUP LOGIC ---
def get_fallback_reply(user_message):
    msg = user_message.lower()
    if "warranty" in msg:
        return "Medly offers Lifetime Warranty on heat retention, backed by our 'Build It' promise."
    elif "shipping" in msg or "delivery" in msg:
        return "We offer Free Shipping across India! Deliveries typically take 2-4 business days."
    elif "return" in msg or "refund" in msg:
        return "We have a 7-day easy return policy for any manufacturing defects."
    elif "hello" in msg or "hi" in msg:
        return "Hello! Welcome to Medly. How can I help you today?"
    else:
        return "Please email support@mymedly.in for immediate help."

# --- ROUTES ---

@app.route('/', methods=['GET'])
def home():
    return "Medly Chatbot is ALIVE and Ready to Chat!"

@app.route('/api/index', methods=['GET'])
def home_direct():
    return "Medly Chatbot is ALIVE (Direct Path)"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    reply = ""

    # Try AI First
    try:
        full_prompt = f"<s>[INST] {SYSTEM_CONTEXT} \n\n User Question: {user_message} [/INST]"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {
            "inputs": full_prompt,
            "parameters": {"max_new_tokens": 100, "return_full_text": False, "temperature": 0.3}
        }

        # 4 Second Timeout for Speed
        response = requests.post(API_URL, headers=headers, json=payload, timeout=4)

        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and 'generated_text' in result[0]:
                reply = result[0]['generated_text'].strip()
            else:
                reply = get_fallback_reply(user_message)
        else:
            print(f"HF Status: {response.status_code}")
            reply = get_fallback_reply(user_message)

    except Exception as e:
        print(f"Error or Timeout: {e}")
        reply = get_fallback_reply(user_message)

    return jsonify({"reply": reply})

# Vercel Entry Point
if __name__ == '__main__':
    app.run(port=9292)