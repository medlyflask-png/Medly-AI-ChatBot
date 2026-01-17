from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# --- 1. CORS CONFIGURATION ---
# Allows your Shopify store to talk to this backend
CORS(app, resources={
    r"/*": {
        "origins": ["https://mymedly.in", "http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# --- 2. THE LOGIC (The Brain) ---
def get_rule_based_reply(user_message):
    # Convert message to lowercase to make matching easier
    msg = user_message.lower()

    # --- GREETINGS ---
    if any(word in msg for word in ["hi", "hello", "hey", "start", "good morning", "good evening"]):
        return "Hello! Welcome to Medly. I can help you with Warranty, Shipping, Prices, or Product details. What would you like to know?"

    # --- WARRANTY (The "Build It" Promise) ---
    if any(word in msg for word in ["warranty", "guarantee", "lifetime", "claim", "replacement"]):
        return ("Medly offers a **Lifetime Warranty** on heat/cold retention! "
                "If your bottle stops working, we replace it. "
                "(Note: Physical damage/dents are not covered).")

    # --- SHIPPING & DELIVERY ---
    if any(word in msg for word in ["shipping", "ship", "delivery", "deliver", "arrive", "reach", "track", "time"]):
        return ("We offer **Free Shipping** across India! "
                "Deliveries typically take **2-4 business days** for metro cities. "
                "You will receive a tracking link via SMS/Email once dispatched.")

    # --- PAYMENT & COD ---
    if any(word in msg for word in ["cod", "cash", "pay", "payment", "card", "upi"]):
        return ("Yes! **Cash on Delivery (COD)** is available. "
                "You can order today and pay when the bottle arrives at your doorstep.")

    # --- PRICE & COST ---
    if any(word in msg for word in ["price", "cost", "how much", "rate", "rupees", "rs"]):
        return ("Our prices range from **₹799** (Classic) to **₹2,000** (Sports). "
                "Please check the 'Shop' page for the latest discounts and deals!")

    # --- PRODUCT FEATURES (Hot/Cold) ---
    if any(word in msg for word in ["hot", "cold", "hour", "temperature", "warm", "cool"]):
        return ("Our ZeroAir™ vacuum technology keeps drinks **Hot for 20 Hours** and **Cold for 24 Hours**. "
                "Perfect for any weather!")

    # --- SPECIFIC MODELS ---
    if "classic" in msg:
        return "The **Classic** is our everyday favorite. Compact, stylish, and starts at ₹799."
    if "prime" in msg:
        return "The **Prime** is our premium model with a sleek finish, priced around ₹1,300."
    if "sports" in msg or "gym" in msg:
        return "The **Sports** bottle is built for endurance. Rugged, larger capacity, and ready for action."
    if "tumbler" in msg:
        return "The **Tumbler** is perfect for coffee or tea on the go."

    # --- RETURNS & REFUNDS ---
    if any(word in msg for word in ["return", "refund", "exchange", "broken", "damage", "defect"]):
        return ("We have a **7-Day Easy Return Policy** for manufacturing defects or wrong products. "
                "Just email us a photo/video, and we'll arrange a free reverse pickup.")

    # --- CONTACT SUPPORT ---
    if any(word in msg for word in ["contact", "support", "email", "phone", "call", "number", "talk", "human"]):
        return ("We are here 24/7! Call us at **8744048726** or email **support@mymedly.in**.")

    # --- CLEANING & CARE ---
    if any(word in msg for word in ["clean", "wash", "smell", "care", "soap"]):
        return "Hand wash your Medly bottle with warm soapy water. Do not put it in the dishwasher or freezer to maintain the vacuum seal."

    # --- DEFAULT (Unknown Query) ---
    return ("I'm not sure about that, but I'd love to help! "
            "Please ask about Warranty, Shipping, or Prices, or email support@mymedly.in.")

# --- ROUTES ---
@app.route('/', methods=['GET'])
def home():
    return "Medly Rule-Based Chatbot is Running."

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    # Handle Preflight for CORS
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({"error": "Empty message"}), 400

        # Get the strict rule-based reply
        bot_reply = get_rule_based_reply(user_message)

        return jsonify({"reply": bot_reply})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Server Error"}), 500

# Required for Vercel
if __name__ == '__main__':
    app.run(port=9292)