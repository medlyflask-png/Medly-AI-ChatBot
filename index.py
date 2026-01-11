import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables (for when you add the API Key later)
load_dotenv()

app = Flask(__name__)
# Allow your Shopify store to talk to this server
CORS(app) 

# --- CONFIGURATION ---
# Set this to True to use Real AI (requires API Key)
# Set this to False to use Free Test Mode
USE_REAL_AI = False 

# --- YOUR KNOWLEDGE BASE (The "Mini-RAG") ---
# This is the "Cheat Sheet" the bot will read.
SYSTEM_PROMPT = """
You are the AI Assistant for Medly, a premium Indian vacuum flask brand.
Your Tone: Helpful, professional, and concise.

FACTS SHEET:
1. BRAND: Medly (Tagline: "Build It").
2. PRODUCT: Vacuum Flask Bottles (Keep hot/cold for 12+ hours).
3. WARRANTY: 10 Years on heat retention (The "Build It" Promise).
4. SHIPPING: Free shipping across India. Delivery in 2-4 business days.
5. RETURNS: 7-day easy return policy for manufacturing defects.
6. CONTACT: support@mymedly.in
7. COLOR: Our signature color is Royal Blue.

INSTRUCTION: 
- If the user asks about price, say "Please check the latest price on our product page."
- Keep answers under 3 sentences.
"""

# Initialize OpenAI (Will only be used if USE_REAL_AI is True)
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/', methods=['GET'])
def home():
    return "Medly Chatbot Server is Running!"

@app.route('/chat', methods=['POST'])
def chat():
    print("--- New Message Received ---")
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    bot_reply = ""

    # --- LOGIC SWITCH ---
    if USE_REAL_AI:
        try:
            # THIS IS THE REAL AI PART (Uncomment later)
            # response = client.chat.completions.create(
            #     model="gpt-4o-mini",
            #     messages=[
            #         {"role": "system", "content": SYSTEM_PROMPT},
            #         {"role": "user", "content": user_message}
            #     ]
            # )
            # bot_reply = response.choices[0].message.content
            pass
        except Exception as e:
            bot_reply = f"Error: {str(e)}"
            
    else:
        # --- FREE TEST MODE (Mock Logic) ---
        # This simulates the RAG by manually checking keywords
        print(f"User asked: {user_message}")
        time.sleep(1) # Fake thinking delay
        
        user_text = user_message.lower()
        
        if "warranty" in user_text:
            bot_reply = "Medly offers a Lifetime Warranty on heat retention, backed by our 'Build It' promise."
        elif "shipping" in user_text or "delivery" in user_text:
            bot_reply = "We offer Free Shipping across India! Your order typically arrives in 2-4 business days."
        elif "price" in user_text or "cost" in user_text:
            bot_reply = "Please check the latest price directly on our product page."
        elif "hello" in user_text or "hi" in user_text:
            bot_reply = "Hello! Welcome to Medly. How can I help you today?"
        else:
            bot_reply = "I am in Test Mode. I can answer questions about 'Warranty' or 'Shipping' to prove I am working!"

    return jsonify({"reply": bot_reply})

# if __name__ == '__main__':
#     # Run the server on Port 5000
#     app.run(debug=True, port=9292)

if __name__ == '__main__':
    # host='0.0.0.0' forces the server to be visible to ngrok
    app.run(host='0.0.0.0', port=9292, debug=True)