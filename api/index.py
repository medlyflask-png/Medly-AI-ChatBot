from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# Initialize Flask
app = Flask(__name__)
CORS(app) # Allow Shopify to talk to this

# --- ROUTES ---

@app.route('/', methods=['GET'])
def home():
    return "Medly Chatbot is Alive and Running on Vercel!"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '').lower()
    
    # Simple Logic for Testing
    bot_reply = "I am not sure."
    
    if "warranty" in user_message:
        bot_reply = "Medly offers a 10-Year Warranty on heat retention."
    elif "shipping" in user_message:
        bot_reply = "We offer Free Shipping across India (2-4 days)."
    elif "hello" in user_message:
        bot_reply = "Hello! Welcome to Medly."
    else:
        bot_reply = "I am a test bot on Vercel. Ask me about Warranty!"

    return jsonify({"reply": bot_reply})

# This is for local testing only. Vercel ignores this part.
if __name__ == '__main__':
    app.run(debug=True, port=9292)