from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from google import genai

# --- SAFE IMPORT FOR LOCAL TESTING ---
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# --- THE BRAIN (System Instructions) ---
# This is where we "Train" the AI with your Brand Rules
SYSTEM_INSTRUCTION = """
ROLE: You are the dedicated AI Customer Support Agent for "Medly".
BRAND TAGLINE: "Build It"
BRAND VIBE: Professional, Helpful, Premium, and Trustworthy.

### YOUR KNOWLEDGE BASE:

1. PRODUCT INFO:
   - Product: Medly Vacuum Flask Bottles.
   - Key Feature: Double-wall vacuum insulation.
   - Benefit: Keeps water Hot for 18+ hours and Cold for 24+ hours.
   - Colors: Primary Brand Color is Royal Blue (#044987).

2. WARRANTY POLICY (The "Build It" Promise):
   - Duration: LIFETIME WARRANTY.
   - Covers: Heat retention issues (if the bottle stops keeping water hot/cold).
   - Does NOT Cover: Physical damage, dents, or paint scratches from usage.
   - Claim Process: Customer must email support@mymedly.in with a video proof.

3. SHIPPING & DELIVERY:
   - Cost: FREE Shipping across India.
   - Timeline: 2-4 Business Days for metro cities, up to 6 days for remote areas.
   - Courier Partners: Bluedart, Delhivery, Xpressbees.

4. RETURNS & REFUNDS:
   - Policy: 7-Day Easy Return Policy.
   - Condition: Accepts returns only for manufacturing defects or wrong product received.
   - Process: We arrange a reverse pickup for free.

5. CONTACT:
   - Email: support@mymedly.in
   - Website: mymedly.in

### RULES FOR ANSWERING:
1. LENGTH: Keep answers SHORT (Max 2-3 sentences). This is a chat widget, not an email.
2. FORMATTING: Use **bold** for key details (like **Lifetime Warranty** or **Free Shipping**).
3. PRICE: Never invent a price. Say: "Please check the latest price on our product page."
4. TONE: Be polite but efficient. Do not be overly flowery.
5. UNKNOWN: If you don't know the answer, say: "I am not sure about that. Please email our team at support@mymedly.in."
"""

# --- BACKUP LOGIC (Safety Net) ---
# Runs if the AI fails or is missing the key
def get_fallback_reply(user_message):
    msg = user_message.lower()
    if "warranty" in msg:
        return "Medly offers a **Lifetime Warranty** on heat retention, backed by our 'Build It' promise."
    elif "shipping" in msg or "delivery" in msg:
        return "We offer **Free Shipping** across India! Deliveries typically take 2-4 business days."
    elif "return" in msg or "refund" in msg:
        return "We have a 7-day easy return policy for any manufacturing defects."
    elif "hello" in msg or "hi" in msg:
        return "Hello! Welcome to Medly. Ask me about our Lifetime Warranty!"
    else:
        return "Please email support@mymedly.in for immediate help."

# --- ROUTES ---

@app.route('/', methods=['GET'])
def home():
    return "Medly Gemini Chatbot is ALIVE and Ready!"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # Safety Check: Is the key missing?
    if not GEMINI_KEY:
        print("ERROR: GEMINI_API_KEY is missing in Vercel!")
        return jsonify({"reply": get_fallback_reply(user_message)})

    try:
        # Initialize Gemini Client (New Library)
        client = genai.Client(api_key=GEMINI_KEY)
        
        # Ask the AI
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=user_message,
            config={"system_instruction": SYSTEM_INSTRUCTION}
        )
        
        # Extract and Clean the Reply
        reply = response.text.strip()
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Gemini Error: {e}")
        # If the AI crashes, use the Backup Logic so the user gets an answer
        return jsonify({"reply": get_fallback_reply(user_message)})

# Vercel Entry Point
if __name__ == '__main__':
    app.run(port=9292)