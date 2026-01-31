from flask import Flask, request, jsonify
from flask_cors import CORS
import difflib
import re

# Vercel looks for this specific variable name 'app'
app = Flask(__name__)

# ==============================================================================
# 1. CORS CONFIGURATION (Double Safety)
# ==============================================================================
# Even though vercel.json handles it, we keep this for local testing safety.
CORS(app, resources={r"/*": {"origins": "*"}})

# ==============================================================================
# 2. PRODUCT DATA
# ==============================================================================
PRODUCTS = {
    "classic": {
        "id": "classic",
        "name": "Medly Classic (750ml)",
        "price": "₹799",
        "image": "https://cdn.shopify.com/s/files/1/0641/9215/1686/files/medly-classic-500ml-double-wall-vacuum-flask-silver.png", 
        "url": "https://www.mymedly.in/products/classic"
    },
    "prime": {
        "id": "prime",
        "name": "Medly Prime Series",
        "price": "₹1,300",
        "image": "https://cdn.shopify.com/s/files/1/0641/9215/1686/files/medly-prime-550ml-portable-thermos-bottle-strap-black.png",
        "url": "https://www.mymedly.in/products/prime"
    },
    "sports": {
        "id": "sports",
        "name": "Medly Sports Rugged",
        "price": "₹1,500",
        "image": "https://cdn.shopify.com/s/files/1/0641/9215/1686/files/medly-quicksip-1l-sports-water-bottle-leakproof-red.png",
        "url": "https://www.mymedly.in/products/quicksip"
    },
    "tumbler": {
        "id": "tumbler",
        "name": "Medly Coffee Tumbler",
        "price": "₹1,399",
        "image": "https://cdn.shopify.com/s/files/1/0641/9215/1686/files/medly-tumbler-1200ml-travel-mug-iced-coffee-cup-black.png",
        "url": "https://www.mymedly.in/products/tumbler"
    }
}

# ==============================================================================
# 3. KNOWLEDGE BASE
# ==============================================================================
KNOWLEDGE_BASE = [
    {
        "intent": "greeting",
        "keywords": ["hi", "hii", "hello", "hey", "namaste", "start", "medly"],
        "response": "Hello! Welcome to Medly. How can I assist you today?", 
        "card": None 
    },
    {
        "intent": "product_classic",
        "keywords": ["classic", "standard", "750ml", "basic bottle", "799"],
        "response": "Here is the Medly Classic.",
        "card": PRODUCTS["classic"]
    },
    {
        "intent": "product_prime",
        "keywords": ["prime", "office", "sleek", "1300", "professional"],
        "response": "Here is the Medly Prime Series.",
        "card": PRODUCTS["prime"]
    },
    {
        "intent": "product_sports",
        "keywords": ["sports", "gym", "rugged", "hike", "1500", "workout"],
        "response": "Here is the Medly Sports Rugged.",
        "card": PRODUCTS["sports"]
    },
    {
        "intent": "car_cup_holder",
        "keywords": ["car", "cup holder", "swift", "creta", "driving", "fit"],
        "response": "**Car Fit:** Yes! The Medly Classic and Prime fit perfectly in standard car cup holders.",
        "card": None
    },
    {
        "intent": "warranty",
        "keywords": ["warranty", "waranty", "guarantee", "lifetime", "replace", "broken", "claim"],
        "response": "Medly offers a **Lifetime Warranty** on heat retention. If the vacuum fails, we replace it.",
        "card": None
    },
    {
        "intent": "shipping",
        "keywords": ["ship", "delivery", "track", "where", "order", "status", "arrive"],
        "response": "Metro cities: 2-3 days. Rest of India: 5-7 days. Check your SMS for the tracking link.",
        "card": None
    },
    {
        "intent": "price_general",
        "keywords": ["price", "cost", "how much", "rate", "money"],
        "response": "Our range starts from **₹799**. Check out the Classic model below.",
        "card": PRODUCTS["classic"]
    }
]

# ==============================================================================
# 4. LOGIC ENGINE
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
                current_score += 10
            else:
                matches = difflib.get_close_matches(word, keywords, n=1, cutoff=0.80)
                if matches:
                    current_score += 8 
        
        if current_score > best_score:
            best_score = current_score
            best_result = item

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

# Home Route - Essential for Vercel to know the app is alive
@app.route('/', methods=['GET'])
def home():
    return "Medly Chatbot is Running!"

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
            return jsonify({
                "text": "I didn't quite catch that. Would you like to talk to our team directly?",
                "card": {
                    "name": "Contact Support",
                    "price": "Call / Email",
                    "image": "https://cdn-icons-png.flaticon.com/512/3059/3059502.png",
                    "url": "tel:+918744048726",
                    "description": "Call: 8744048726 \nEmail: support@mymedly.in"
                }
            })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Server Error"}), 500

# Vercel ENTRY POINT
# The 'app' variable is automatically picked up by Vercel.
# This block only runs if you type 'python index.py' locally.
if __name__ == '__main__':
    app.run(port=9292, debug=False)