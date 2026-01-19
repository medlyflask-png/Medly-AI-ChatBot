from flask import Flask, request, jsonify
from flask_cors import CORS
import difflib
import re
import random

app = Flask(__name__)

# ==============================================================================
# 1. CORS CONFIGURATION (FIXED)
# ==============================================================================
# FIX: Added 'https://www.mymedly.in' and set supports_credentials=True
# We also added "*" to ensure it works even if you test from other domains.
CORS(app, resources={
    r"/*": {
        "origins": ["https://www.mymedly.in", "https://mymedly.in", "http://localhost:3000", "*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Range", "X-Content-Range"]
    }
})

# ==============================================================================
# 2. THE KNOWLEDGE BASE (THE BRAIN)
# ==============================================================================

KNOWLEDGE_BASE = [
    # --- GREETINGS & BASICS ---
    {
        "intent": "greeting",
        "keywords": [
            "hi", "hii","hello", "hey", "hie", "hy", "hiya", "good morning", "good evening", 
            "good afternoon", "namaste", "start", "yo", "bot", "assistant", "chat"
        ],
        "response": [
            "Hello! Welcome to Medly. I'm here to help you #BuildIt. Ask me about Warranty, Shipping, or our Products!",
            "Hi there! I'm the Medly Assistant. How can I help you stay hydrated today?",
            "Hey! Welcome to the world of Medly. Looking for a new bottle or need help with an order?"
        ]
    },
    {
        "intent": "gratitude",
        "keywords": ["thank", "thanks", "thx", "thnks", "cool", "great", "awesome", "good job", "nice"],
        "response": ["You're very welcome!", "Happy to help! Keep building.", "Glad I could assist!"]
    },
    {
        "intent": "goodbye",
        "keywords": ["bye", "goodbye", "cya", "see ya", "end", "stop", "exit", "quit"],
        "response": ["Goodbye! Stay hydrated.", "See you soon! Don't forget to #BuildIt."]
    },
    
    # --- BRAND IDENTITY ---
    {
        "intent": "brand_info",
        "keywords": [
            "who are you", "medly", "brand", "company", "owner", "located", "where", "location", 
            "indian", "china", "manufacture", "origin", "about us"
        ],
        "response": [
            "Medly Style Pvt. Ltd. is a proud Indian brand based in **Noida, Uttar Pradesh**. Our tagline is **'Build It'**.",
            "We are Medly! We engineer premium vacuum-insulated bottles designed for endurance. We are headquartered in Noida, India."
        ]
    },

    # --- WARRANTY (CORE FEATURE) ---
    {
        "intent": "warranty_policy",
        "keywords": [
            "warranty", "waranty", "warrnty", "guarantee", "guaranty", "lifetime", "life time", 
            "promise", "assurance", "insure", "insurance"
        ],
        "response": [
            "🛡️ **Medly Lifetime Warranty**: We guarantee our flasks will keep your drinks Hot/Cold for life! If the vacuum insulation fails, we replace it for free.",
            "We offer a **Lifetime Warranty** on heat retention! Note: This covers technical failures, not physical damage like dents or scratches."
        ]
    },
    {
        "intent": "warranty_claim",
        "keywords": [
            "claim", "not working", "fails", "failed", "cold", "hot", "issue", "problem", 
            "defective", "stopped", "stop working", "heat loss"
        ],
        "response": [
            "To claim your warranty, simply email a video of the issue to **support@mymedly.in**. Our team will approve the replacement within 24 hours!",
            "Facing an issue? Don't worry. Email us at **support@mymedly.in** with your order details and a small video proof."
        ]
    },
    {
        "intent": "warranty_exclusions",
        "keywords": [
            "dent", "scratch", "paint", "broken", "fell", "drop", "dropped", "damage", "chip", "peel"
        ],
        "response": [
            "⚠️ Please note: Our Lifetime Warranty covers **Vacuum Insulation** (temperature retention) only. Physical damage like **dents, paint scratches, or breakage** from dropping the bottle is not covered."
        ]
    },

    # --- SHIPPING & DELIVERY ---
    {
        "intent": "shipping_time",
        "keywords": [
            "ship", "shipping", "deliver", "delivery", "arrive", "reach", "time", "days", "long", 
            "when", "expected", "duration", "fast"
        ],
        "response": [
            "🚚 **Free Shipping across India!** Orders typically reach Metro cities in **2-4 business days**. Remote areas may take up to 6 days.",
            "We dispatch within 24 hours! You can expect your Medly bottle in **2-4 days**."
        ]
    },
    {
        "intent": "tracking",
        "keywords": ["track", "tracking", "order status", "where is my order", "shipped yet", "awb", "courier"],
        "response": [
            "Once your order is dispatched, you will receive a **Tracking Link via SMS and Email**. You can use that to see exactly where your bottle is!",
            "Check your email/SMS for the Bluedart/Delhivery tracking link. If you didn't get it, email support@mymedly.in."
        ]
    },

    # --- PAYMENT ---
    {
        "intent": "payment_methods",
        "keywords": ["cod", "cash", "pay", "payment", "upi", "card", "credit", "debit", "wallet", "online"],
        "response": [
            "💳 We accept **Cash on Delivery (COD)**, UPI, Credit/Debit Cards, and Net Banking. You can choose your preferred method at checkout!",
            "Yes! **COD is available**. You can pay cash when the delivery agent hands over your Medly bottle."
        ]
    },

    # --- PRODUCT SPECS ---
    {
        "intent": "thermal_performance",
        "keywords": ["hot", "cold", "warm", "cool", "hour", "hr", "temp", "temperature", "insulation", "vacuum"],
        "response": [
            "🔥❄️ **ZeroAir™ Technology**: Keeps water **Hot for 20 Hours** and **Cold for 24 Hours**. No matter the weather outside!",
            "Our bottles are masterfully engineered to lock in temperature. Hot stays hot for 20hrs, Cold stays cold for 24hrs."
        ]
    },
    {
        "intent": "materials",
        "keywords": ["material", "steel", "plastic", "metal", "grade", "bpa", "safe", "food", "304", "316"],
        "response": [
            "We use premium **18/8 (304 Grade) Stainless Steel**. It is 100% BPA-Free, Rust-Free, and Food Grade safe.",
            "Built for endurance: High-grade Stainless Steel inside and out. No plastic touches your water."
        ]
    },
    {
        "intent": "leak_proof",
        "keywords": ["leak", "spill", "tight", "seal", "bag", "proof"],
        "response": [
            "✅ Yes! All Medly bottles are **100% Leak-Proof**. You can toss them in your bag without worrying about spills."
        ]
    },

    # --- SPECIFIC MODELS ---
    {
        "intent": "model_classic",
        "keywords": ["classic", "basic", "standard", "799", "999"],
        "response": ["The **Classic** is our fan-favorite. Minimalist design, fits in car cup holders, and starts at just **₹799**."]
    },
    {
        "intent": "model_prime",
        "keywords": ["prime", "premium", "sleek", "1300"],
        "response": ["The **Prime** (₹1,300) features a sophisticated silhouette and premium finish. Perfect for the office or meetings."]
    },
    {
        "intent": "model_sports",
        "keywords": ["sports", "gym", "workout", "run", "running", "active", "2000", "1500"],
        "response": ["The **Sports** edition (₹1,500 - ₹2,000) is built rugged for athletes. High capacity and grip-friendly."]
    },
    {
        "intent": "model_tumbler",
        "keywords": ["tumbler", "coffee", "mug", "cup", "tea", "1399"],
        "response": ["The **Tumbler** (₹1,399) is your perfect coffee companion. Keeps your brew hot while you commute."]
    },

    # --- PRICING ---
    {
        "intent": "price_query",
        "keywords": ["price", "cost", "how much", "rate", "money", "expensive", "cheap", "discount", "offer", "coupon"],
        "response": [
            "Our bottles range from **₹799 to ₹2,000** depending on the model. Check the website header for today's special offers!",
            "We offer premium quality at honest prices starting from **₹799**. "
        ]
    },

    # --- RETURNS & CANCELLATION ---
    {
        "intent": "returns",
        "keywords": ["return", "exchange", "refund", "back", "reverse", "policy", "change"],
        "response": [
            "🔄 **7-Day Easy Returns**: If you received a wrong or defective product, we will replace it for free. We arrange the reverse pickup for you.",
            "We accept returns for manufacturing defects within 7 days. Just email us at support@mymedly.in."
        ]
    },
    {
        "intent": "cancel",
        "keywords": ["cancel", "cancellation", "mistake", "wrong order"],
        "response": [
            "To cancel an order, please email **support@mymedly.in** or call us immediately. If it hasn't shipped yet, we will cancel it instantly."
        ]
    },

    # --- SUPPORT ---
    {
        "intent": "contact_info",
        "keywords": [
            "contact", "support", "call", "phone", "number", "mobile", "email", "mail", "talk", "speak", "human", "agent"
        ],
        "response": [
            "📞 **24/7 Support**: Call us at **8744048726**.\n📧 Email: **support@mymedly.in**\n📍 Address: A-13, Graphix Tower-2, Sector-62, Noida.",
            "We are always here! Call **8744048726** or drop an email to **support@mymedly.in**."
        ]
    },

    # --- CARE INSTRUCTIONS ---
    {
        "intent": "care_instructions",
        "keywords": ["wash", "clean", "soap", "smell", "odor", "dishwasher", "freezer", "fridge", "microwave"],
        "response": [
            "🧽 **Care Tips**: Hand wash with warm soapy water. \n🚫 **Don'ts**: Do not put in Dishwasher, Freezer, or Microwave (it damages the vacuum seal).",
            "To remove odors, let the bottle sit with warm soapy water and vinegar for 10 minutes, then rinse."
        ]
    }
]

# ==============================================================================
# 3. THE MATCHING ENGINE
# ==============================================================================

def find_best_intent(user_message):
    """
    Analyzes the user message to find the best matching intent.
    """
    cleaned_msg = user_message.lower()
    cleaned_msg = re.sub(r'[^\w\s]', '', cleaned_msg) # Remove punctuation
    user_words = cleaned_msg.split()

    best_score = 0
    best_intent = None

    for item in KNOWLEDGE_BASE:
        score = 0
        keywords = item['keywords']
        
        for word in user_words:
            # Exact Match
            if word in keywords:
                score += 10 
            # Fuzzy Match
            else:
                matches = difflib.get_close_matches(word, keywords, n=1, cutoff=0.85)
                if matches:
                    score += 8 

        if score > best_score:
            best_score = score
            best_intent = item

    if best_score > 0 and best_intent:
        if isinstance(best_intent['response'], list):
            return random.choice(best_intent['response'])
        return best_intent['response']

    return None

# ==============================================================================
# 4. FLASK ROUTES
# ==============================================================================

@app.route('/', methods=['GET'])
def home():
    return "Medly Mega-Bot is Running (Rule-Based v2.0)"

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    # Handle Preflight for CORS explicitly if the decorator misses it
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({"error": "Empty message"}), 400

        # --- RUN THE LOGIC ---
        reply = find_best_intent(user_message)

        # --- FALLBACK RESPONSE ---
        if not reply:
            reply = ("I'm not sure about that, but I'd love to help! "
                     "You can ask me about **Warranty**, **Shipping**, **Price**, or **Returns**. "
                     "Or email us at support@mymedly.in.")

        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# Required for Vercel
if __name__ == '__main__':
    app.run(port=9292)