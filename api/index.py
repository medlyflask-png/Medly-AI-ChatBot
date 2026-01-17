from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import warnings
import google.generativeai as genai

# --- 1. SILENCE WARNINGS ---
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

app = Flask(__name__)

# --- 2. CRITICAL: CORS FIX ---
# This specific configuration is required to stop the "Blocked by CORS" error on Shopify.
CORS(app, resources={
    r"/*": {
        "origins": ["https://mymedly.in", "http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# --- 3. CONFIGURATION ---
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# --- 4. SYSTEM INSTRUCTION (Updated with Scraped Data) ---
SYSTEM_INSTRUCTION = """
ROLE: You are the dedicated AI Customer Support Agent for "Medly".
BRAND TAGLINE: "Build It" (Also: "One Flask. Endless Moments.")
BRAND VIBE: Professional, Helpful, Premium, and Trustworthy.

### YOUR KNOWLEDGE BASE (REAL DATA):

1. PRODUCT INFO:
   - Tech: ZeroAir™ Steel Bottles (Vacuum Insulated).
   - Models: 
     * Classic (₹799 - ₹999)
     * Prime (₹1,300)
     * Tumbler (₹1,399)
     * Sports (₹1,500 - ₹2,000)
   - Performance: Keeps water Hot for 20 Hours and Cold for 24 Hours.
   - Warranty: LIFETIME WARRANTY on heat retention.

2. PAYMENT & SHIPPING:
   - Payment: Cash on Delivery (COD) is Available.
   - Shipping: Calculated at checkout. Typically 2-4 days for metros.

3. CONTACT & SUPPORT:
   - Email: support@mymedly.in
   - Phone: 8744048726 (Available 24/7)
   - Address: A-13, Graphix Tower-2, Sector-62, Noida, Uttar Pradesh.

4. RETURNS:
   - Policy: 7-Day Easy Return (only for manufacturing defects or wrong product).

### RULES FOR ANSWERING:
1. LENGTH: Keep answers SHORT (Max 2-3 sentences).
2. FORMATTING: Use **bold** for key details like prices or warranty.
3. TONE: Be polite but efficient.
"""

# --- 5. ROBUST FALLBACK LOGIC (If Gemini Fails) ---
def get_fallback_reply(user_message):
    msg = user_message.lower()
    
    # Warranty Logic
    if "warranty" in msg or "guarantee" in msg:
        return "Medly offers a **Lifetime Warranty** on heat/cold retention. If your bottle stops working, we replace it. (Physical damage not covered)."
    
    # Shipping & Payment Logic
    elif "shipping" in msg or "delivery" in msg or "time" in msg:
        return "We deliver in **2-4 business days** to metro cities. **Cash on Delivery (COD)** is available!"
    
    # Price/Product Logic
    elif "price" in msg or "cost" in msg or "how much" in msg:
        return "Our bottles start from **₹799** (Classic) up to **₹2,000** (Sports). Check the 'Shop' page for today's deals."
        
    # Contact Logic
    elif "contact" in msg or "support" in msg or "phone" in msg or "email" in msg:
        return "You can reach us 24/7 at **8744048726** or email **support@mymedly.in**."
    
    # Default
    return "I am here to help! Please email support@mymedly.in for immediate assistance."

# --- ROUTES ---
@app.route('/', methods=['GET'])
def home():
    return "Medly Gemini Chatbot is ALIVE!"

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    # Handle Preflight for CORS
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.json
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # FALLBACK: If API Key is missing, use the If/Else Logic
    if not GEMINI_KEY:
        print("WARNING: GEMINI_API_KEY is missing. Using Fallback logic.")
        return jsonify({"reply": get_fallback_reply(user_message)})

    try:
        # Configure Gemini
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
        # FALLBACK: If Gemini crashes, use the If/Else Logic
        return jsonify({"reply": get_fallback_reply(user_message)})

# Required for Vercel
if __name__ == '__main__':
    app.run(port=9292)