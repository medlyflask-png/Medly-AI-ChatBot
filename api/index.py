from flask import Flask, request, jsonify
from flask_cors import CORS
import difflib
import re

app = Flask(__name__)

# ==============================================================================
# 1. CORS CONFIGURATION (ALLOW ALL)
# ==============================================================================
CORS(app, resources={r"/*": {"origins": "*"}})

# ==============================================================================
# 2. FULL PRODUCT CATALOG
# ==============================================================================
PRODUCTS = {
    "classic": {
        "id": "classic",
        "name": "Medly Classic (750ml/1000ml)",
        "price": "₹799",
        "url": "https://www.mymedly.in/products/classic"
    },
    "prime": {
        "id": "prime",
        "name": "Medly Prime Series",
        "price": "₹1,300",
        "url": "https://www.mymedly.in/products/prime"
    },
    "sports": {
        "id": "sports",
        "name": "Medly Sports Rugged",
        "price": "₹1,500",
        "url": "https://www.mymedly.in/products/quicksip"
    },
    "tumbler": {
        "id": "tumbler",
        "name": "Medly Coffee Tumbler",
        "price": "₹1,399",
        "url": "https://www.mymedly.in/products/tumbler"
    }
}

# ==============================================================================
# 3. THE KNOWLEDGE BASE
# ==============================================================================
KNOWLEDGE_BASE = [
    # --- A. IDENTITY & PERSONALITY ---
    {
        "intent": "who_are_you",
        "keywords": ["who", "are", "you", "bot", "ai", "real", "human", "name", "robot"],
        "response": "I am the Medly Digital Assistant. My mission is to help you find the gear to 'Build It'. I can help with products, warranty, or order tracking.",
        "card": None
    },
    {
        "intent": "about_brand",
        "keywords": ["brand", "company", "about", "story", "founder", "medly", "mission"],
        "response": "Medly is a performance lifestyle brand. We build vacuum-insulated gear for explorers and creators. Our philosophy is simple: Build It.",
        "card": None
    },
    {
        "intent": "compliment",
        "keywords": ["good", "great", "awesome", "smart", "cool", "best", "thanks", "thank"],
        "response": "Appreciate that! We keep our standards high, just like our temperature retention. Anything else you need?",
        "card": None
    },
    {
        "intent": "insult_handling",
        "keywords": ["stupid", "bad", "useless", "dumb", "hate", "worst"],
        "response": "I'm still learning and evolving. If I can't help, please call our human support team directly at +918744048726.",
        "card": None
    },

    # --- B. BUSINESS & DISTRIBUTION ---
    {
        "intent": "bulk_orders",
        "keywords": ["bulk", "wholesale", "distributor", "retailer", "quantity", "corporate", "dealership", "b2b"],
        "response": "Yes! We operate as both a retailer and distributor. For bulk orders or dealership inquiries, please email support@mymedly.in for our B2B price list.",
        "card": None
    },

    # --- C. GREETINGS ---
    {
        "intent": "greeting",
        "keywords": ["hi", "hii", "hello", "hey", "namaste", "start", "morning", "evening", "yo"],
        "response": "Hello! Welcome to Medly. How can I assist you today? (Ask about Warranty, Shipping, or our Bottles!)", 
        "card": None 
    },

    # --- D. PRODUCTS (Specific Requests) ---
    {
        "intent": "product_classic",
        "keywords": ["classic", "standard", "750ml", "basic", "799", "simple", "water"],
        "response": "Here is the Medly Classic. 24 hours Cold, 12 hours Hot. Great for everyday use.",
        "card": PRODUCTS["classic"]
    },
    {
        "intent": "product_prime",
        "keywords": ["prime", "office", "sleek", "1300", "professional", "strap", "work"],
        "response": "Here is the Medly Prime Series. Sleek design with a strap, perfect for the office.",
        "card": PRODUCTS["prime"]
    },
    {
        "intent": "product_sports",
        "keywords": ["sports", "gym", "rugged", "hike", "1500", "workout", "run", "cycle"],
        "response": "Here is the Medly Sports Rugged. Built for the grind with a quick-sip lid.",
        "card": PRODUCTS["sports"]
    },
    {
        "intent": "product_tumbler",
        "keywords": ["tumbler", "coffee", "tea", "mug", "1399", "travel", "sip", "cup"],
        "response": "Here is the Medly Coffee Tumbler. Keeps your brew hot for hours while you commute.",
        "card": PRODUCTS["tumbler"]
    },

    # --- E. REAL LIFE SCENARIOS & SPECS ---
    {
        "intent": "retention_time",
        "keywords": ["hot", "cold", "hours", "time", "long", "duration", "warm"],
        "response": "**Temperature Lock:** Our vacuum technology keeps water **Cold for 24 Hours** and **Hot for 12+ Hours**.",
        "card": None
    },
    {
        "intent": "material_quality",
        "keywords": ["material", "steel", "plastic", "quality", "metal", "grade"],
        "response": "**Premium Build:** We use high-grade **18/8 Stainless Steel** (304 grade) which is rust-free and BPA-free.",
        "card": None
    },
    {
        "intent": "car_cup_holder",
        "keywords": ["car", "cup", "holder", "swift", "creta", "driving", "fit", "drive"],
        "response": "**Car Fit:** Yes! The Medly Classic and Prime fit perfectly in standard car cup holders. (The Sports model is wider).",
        "card": None
    },
    {
        "intent": "bag_leak",
        "keywords": ["bag", "backpack", "leak", "spill", "upside", "proof"],
        "response": "**100% Leakproof:** You can toss any Medly bottle into your bag upside down. Zero spills.",
        "card": None
    },
    {
        "intent": "ice_cubes",
        "keywords": ["ice", "cubes", "wide", "mouth", "cold", "summer"],
        "response": "**Ice Friendly:** Yes, standard ice cubes fit easily into the Classic and Prime models.",
        "card": None
    },

    # --- F. COMPETITOR COMPARISONS ---
    {
        "intent": "vs_market",
        "keywords": ["milton", "cello", "thermosteel", "market", "better", "why", "brand"],
        "response": "Legacy brands are good, but Medly is built for the new age. We offer a **Lifetime Warranty** on heat retention and a superior grip.",
        "card": None
    },

    # --- G. LIQUIDS & SAFETY ---
    {
        "intent": "liquid_milk",
        "keywords": ["milk", "dairy", "chai", "coffee", "smell"],
        "response": "**Milk/Chai:** You *can*, but please wash it within 4-6 hours to avoid spoiling or lingering smells.",
        "card": None
    },
    {
        "intent": "liquid_carbonated",
        "keywords": ["soda", "coke", "beer", "fizzy", "gas"],
        "response": "**Not Recommended:** Carbonated drinks build pressure inside the vacuum seal and can jam the lid.",
        "card": None
    },

    # --- H. WARRANTY & SUPPORT ---
    {
        "intent": "warranty",
        "keywords": ["warranty", "waranty", "guarantee", "lifetime", "replace", "broken", "claim"],
        "response": "Medly offers a **Lifetime Warranty** on heat retention. If the vacuum fails, we replace it. (Dents/Scratches excluded).",
        "card": None
    },
    {
        "intent": "shipping",
        "keywords": ["ship", "delivery", "track", "where", "order", "status", "arrive", "location", "delhi", "mumbai"],
        "response": "We ship all over India! Metro cities: 2-3 days. Rest of India: 5-7 days. Check your SMS for the tracking link.",
        "card": None
    },
    {
        "intent": "price_general",
        "keywords": ["price", "cost", "how", "much", "rate", "money", "discount"],
        "response": "Our range starts from **₹799**. Check out the Classic model below.",
        "card": PRODUCTS["classic"]
    },
    
    # --- I. MAINTENANCE ---
    {
        "intent": "cleaning",
        "keywords": ["wash", "clean", "smell", "soap", "dishwasher", "stink"],
        "response": "**Care:** Hand wash with warm soapy water. Do NOT use a dishwasher or freezer as it affects the vacuum seal.",
        "card": None
    }
]

# ==============================================================================
# 4. LOGIC ENGINE (Fuzzy + Threshold)
# ==============================================================================
def find_best_intent(user_message):
    cleaned_msg = re.sub(r'[^\w\s]', '', user_message.lower())
    user_words = cleaned_msg.split()
    
    best_score = 0
    best_result = None

    for item in KNOWLEDGE_BASE:
        current_score = 0
        keywords = item['keywords']
        for word in user_words:
            if word in keywords:
                current_score += 10 # Exact Match
            else:
                matches = difflib.get_close_matches(word, keywords, n=1, cutoff=0.80)
                if matches:
                    current_score += 8 # Fuzzy Match
        
        if current_score > best_score:
            best_score = current_score
            best_result = item

    # STRICT THRESHOLD (Needs at least one solid match)
    if best_score < 8:
        return None

    return {
        "text": best_result['response'],
        "card": best_result.get('card'),      
        "carousel": best_result.get('carousel') 
    }

# ==============================================================================
# 5. SERVER ROUTES
# ==============================================================================

# ROOT ROUTE (Health Check)
@app.route('/', methods=['GET'])
def home():
    return "Medly Chatbot is LIVE"

# CHAT ROUTE
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({"error": "Empty message"}), 400

        intent_data = find_best_intent(user_message)
        
        if intent_data:
            return jsonify(intent_data)
        else:
            # FALLBACK
            return jsonify({
                "text": "I didn't quite catch that. Would you like to talk to our team directly?",
                "card": {
                    "name": "Contact Support",
                    "price": "Call / Email",
                    "url": "tel:+918744048726",
                    "description": "Call: 8744048726 \nEmail: support@mymedly.in"
                }
            })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Server Error"}), 500

if __name__ == '__main__':
    app.run(port=9292)