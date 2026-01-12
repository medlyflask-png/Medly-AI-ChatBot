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
# Using Mistral-7B-Instruct because it follows instructions well
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"

# The "Brain" for the AI
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

# --- THE BACKUP PLAN (Keyword Logic) ---
def get_fallback_reply(user_message):
    msg = user_message.lower()
    if "warranty" in msg:
        return "Medly offers a 10-Year Warranty on heat retention, backed by our 'Build It' promise."
    elif "shipping" in msg or "delivery" in msg:
        return "We offer Free Shipping across India! Deliveries typically take 2-4 business days."
    elif "return" in msg or "refund" in msg:
        return "We have a 7-day easy return policy for any manufacturing defects."
    elif "price" in msg or "cost" in msg:
        return "Please check the latest price directly on our product page."
    elif "hello" in msg or "hi" in msg:
        return "Hello! Welcome to Medly. How can I help you today?"
    else:
        # Generic fallback if neither AI nor keywords work
        return "I am currently upgrading my system. Please email support@mymedly.in for immediate help."

# --- MAIN CHAT ROUTE ---
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    reply = ""

    # 1. TRY THE SMART AI FIRST
    try:
        # Construct the specific prompt format for Mistral
        full_prompt = f"<s>[INST] {SYSTEM_CONTEXT} \n\n User Question: {user_message} [/INST]"
        
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 100,  # Keep answers short
                "return_full_text": False,
                "temperature": 0.3      # Low temperature = more factual
            }
        }

        # CRITICAL STEP: The Timeout
        # We give the AI exactly 4 seconds. If it doesn't reply, we cut it off.
        response = requests.post(API_URL, headers=headers, json=payload, timeout=4)

        # Check for "Model Loading" (503) or Success (200)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and 'generated_text' in result[0]:
                reply = result[0]['generated_text'].strip()
            else:
                # If AI returns empty gibberish, use fallback
                reply = get_fallback_reply(user_message)
        else:
            # If 503 (Loading) or 500 (Error), print log and use fallback
            print(f"HF Status: {response.status_code} - Switching to Fallback")
            reply = get_fallback_reply(user_message)

    except requests.exceptions.Timeout:
        # This runs if the AI takes longer than 4 seconds
        print("AI Timed Out (Cold Start) - Switching to Fallback")
        reply = get_fallback_reply(user_message)

    except Exception as e:
        print(f"General Error: {e}")
        reply = get_fallback_reply(user_message)

    return jsonify({"reply": reply})

# Vercel needs this 'app' variable
if __name__ == '__main__':
    app.run(port=9292)