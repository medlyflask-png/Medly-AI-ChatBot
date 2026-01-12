from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import warnings

# --- 1. SILENCE THE WARNINGS ---
# This hides the "FutureWarning" so your logs stay clean
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# --- 2. OLD RELIABLE IMPORT ---
import google.generativeai as genai

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# --- SYSTEM INSTRUCTION (Context) ---
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
1. LENGTH: Keep answers SHORT (Max 2-3 sentences).
2. FORMATTING: Use **bold** for key details.
3. PRICE: "Please check the latest price on our product page."
4. TONE: Be polite but efficient.
"""

# --- BACKUP LOGIC ---
def get_fallback_reply(user_message):
    msg = user_message.lower()
    if "warranty" in msg:
        return "Medly offers a **Lifetime Warranty** on heat retention, backed by our 'Build It' promise."
    elif "shipping" in msg or "delivery" in msg:
        return "We offer **Free Shipping** across India! Deliveries typically take 2-4 business days."
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
        # Configure Old Library
        genai.configure(api_key=GEMINI_KEY)
        
        # Create Model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )

        # Generate Response
        response = model.generate_content(user_message)
        reply = response.text.strip()
        
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Gemini Error: {e}")
        return jsonify({"reply": get_fallback_reply(user_message)})

if __name__ == '__main__':
    app.run(port=9292)