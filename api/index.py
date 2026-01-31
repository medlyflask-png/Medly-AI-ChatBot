from flask import Flask, request, jsonify
from flask_cors import CORS
import difflib
import re

app = Flask(__name__)

# ==============================================================================
# 1. CORS (Allows your website to talk to this bot)
# ==============================================================================
CORS(app, resources={
    r"/*": {
        "origins": ["https://www.mymedly.in", "https://mymedly.in", "http://localhost:3000", "*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# ==============================================================================
# 2. PRODUCT DATA (The "Cards" the bot can show)
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
# 3. KNOWLEDGE BASE (The Brain)
# ==============================================================================
KNOWLEDGE_BASE = [
    # --- A. GREETING (Clean & Simple) ---
    {
        "intent": "greeting",
        "keywords": ["hi", "hii", "hello", "hey", "namaste", "start", "medly"],
        "response": "Hello! Welcome to Medly. How can I assist you today?", 
        "card": None  # No product is shown here
    },

    # --- B. PRODUCTS (Show Card ONLY if asked) ---
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

    # --- C. SPECIFIC QUESTIONS (Car, Warranty, Shipping) ---
    {
        # This will ONLY trigger if user types "Car", "Cup holder", "Swift", etc.
        "intent": "car_cup_holder",
        "keywords": ["car", "cup holder", "swift", "creta", "driving", "fit"],
        "response": "**Car Fit:** Yes! The Medly Classic and Prime fit perfectly in standard car cup holders. (The Sports model is wider).",
        "card": None
    },
    {
        "intent": "warranty",
        "keywords": ["warranty", "waranty", "guarantee", "lifetime", "replace", "broken", "claim"],
        "response": "Medly offers a **Lifetime Warranty** on heat retention. If the vacuum fails, we replace it. Dents are not covered.",
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

# Context Memory (Resets on restart)
last_mentioned_product = None 

# ==============================================================================
# 4. LOGIC ENGINE (Fuzzy Logic + Fallback)
# ==============================================================================
def find_best_intent(user_message):
    global last_mentioned_product
    
    # 1. Clean Input
    cleaned_msg = re.sub(r'[^\w\s]', '', user_message.lower())
    user_words = cleaned_msg.split()
    
    best_score = 0
    best_result = None

    # 2. Check Knowledge Base
    for item in KNOWLEDGE_BASE:
        current_score = 0
        keywords = item['keywords']
        
        for word in user_words:
            if word in keywords:
                current_score += 10 # Exact match
            else:
                # Fuzzy Match (Handles typos like 'waranty')
                matches = difflib.get_close_matches(word, keywords, n=1, cutoff=0.80)
                if matches:
                    current_score += 8 
        
        if current_score > best_score:
            best_score = current_score
            best_result = item

    # 3. STRICT THRESHOLD (The Gatekeeper)
    # If score is less than 8, it means they didn't match any keyword properly.
    if best_score < 8:
        return None  # This triggers the "Contact Us" fallback

    # 4. Success! Save context and return
    if best_result:
        if best_result.get('card'):
            last_mentioned_product = best_result['card']
            
        return {
            "text": best_result['response'],
            "card": best_result.get('card'),      
            "carousel": best_result.get('carousel') 
        }

    return None

# ==============================================================================
# 5. SERVER ROUTES
# ==============================================================================
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({"error": "Empty message"}), 400

        # Run Logic
        intent_data = find_best_intent(user_message)
        
        if intent_data:
            # Match Found -> Send Answer
            return jsonify(intent_data)
        else:
            # NO Match -> Send "Contact Us" Fallback
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

if __name__ == '__main__':
    app.run(port=9292, debug=True)