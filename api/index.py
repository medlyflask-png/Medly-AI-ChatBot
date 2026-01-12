from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai

# --- SAFE IMPORT ---
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
# Get the Google Key from Vercel/Environment
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# Configure the Gemini Library
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

# --- THE BRAIN (System Instructions) ---
SYSTEM_INSTRUCTION = """
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

# --- BACKUP LOGIC (Safety Net) ---
def get_fallback_reply(user_message):
    msg = user_message.lower()
    if "warranty" in msg:
        return "Medly offers a 10-Year Warranty on heat retention, backed by our 'Build It' promise."
    elif "shipping" in msg or "delivery" in msg:
        return "We offer Free Shipping across India! Deliveries typically take 2-4 business days."
    elif "return" in msg or "refund" in msg:
        return "We have a 7-day easy return policy for any manufacturing defects."
    else:
        return "Please email support@mymedly.in for immediate help."

# --- ROUTES ---
@app.route('/', methods=['GET'])
def home():
    return "Medly Gemini Chatbot is ALIVE!"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    if not GEMINI_KEY:
        print("ERROR: GEMINI_API_KEY is missing!")
        return jsonify({"reply": get_fallback_reply(user_message)})

    try:
        # Initialize the Model with System Instructions
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )

        # Ask Gemini (Timeout 10s is plenty for Flash)
        response = model.generate_content(user_message)
        
        # Get the text answer
        reply = response.text.strip()
        
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Gemini Error: {e}")
        # If Gemini fails (rare), use backup
        return jsonify({"reply": get_fallback_reply(user_message)})

# Vercel Entry Point
if __name__ == '__main__':
    app.run(port=9292)