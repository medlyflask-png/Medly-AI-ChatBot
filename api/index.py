from flask import Flask, request, jsonify
from flask_cors import CORS
import difflib
import re
import random

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
# 3. TOP 1% KNOWLEDGE BASE
# ==============================================================================
KNOWLEDGE_BASE = [
    # --- A. PERSONA, CHIT-CHAT & IDENTITY ---
    {
        "intent": "greeting",
        "keywords": ["hi", "hii", "hello", "hey", "namaste", "morning", "evening", "yo", "sup", "howdy", "greetings", "start"],
        "responses": [
            "Hello! Welcome to Medly. How can I help you 'Build It' today?",
            "Hey there! Looking for the perfect vacuum flask?",
            "Hi! I'm the Medly Assistant. What can I help you find today?",
            "Namaste! Ready to upgrade your hydration gear?"
        ],
        "card": None
    },
    {
        "intent": "who_are_you",
        "keywords": ["who", "are", "you", "bot", "ai", "real", "human", "name", "robot", "yourself", "identity", "chatgpt"],
        "responses": [
            "I'm the Medly Digital Assistant! I'm an AI built to help you find the best gear, track orders, or claim warranties.",
            "I am Medly's AI assistant. While I don't drink water myself, I know everything about keeping yours cold for 24 hours!",
            "You can call me the Medly Bot. I'm a virtual assistant here to help with our products, shipping, and brand policies."
        ],
        "card": None
    },
    {
        "intent": "creator",
        "keywords": ["who", "made", "created", "coded", "built", "owner", "founder", "invented"],
        "responses": [
            "I was developed by the awesome tech team at Medly to ensure you get 24/7 support.",
            "The Medly crew built me! They focus on crafting the best steel flasks, and I focus on helping you find them."
        ],
        "card": None
    },
    {
        "intent": "capabilities",
        "keywords": ["what", "can", "do", "help", "work", "purpose", "job", "features", "how"],
        "responses": [
            "I can help you pick the right flask, compare models, track your shipping, or explain our Lifetime Warranty. What do you need?",
            "My job is to make your shopping experience seamless. Ask me about our Classic or Prime series, payment options, or how to clean your bottle!"
        ],
        "card": None
    },
    {
        "intent": "gratitude",
        "keywords": ["thanks", "thank", "appreciate", "good", "great", "awesome", "smart", "cool", "best", "perfect", "nice"],
        "responses": [
            "You're very welcome! Let me know if you need anything else.",
            "Happy to help! We keep our standards high, just like our temperature retention.",
            "Anytime! Anything else I can assist you with today?"
        ],
        "card": None
    },
    {
        "intent": "insult_handling",
        "keywords": ["stupid", "bad", "useless", "dumb", "hate", "worst", "idiot", "sucks", "trash"],
        "responses": [
            "I'm still learning and evolving! If I'm missing the mark, please call our human support team directly at +918744048726.",
            "My apologies! Sometimes my circuits get crossed. Let me get you to a human: email support@mymedly.in or call 8744048726."
        ],
        "card": None
    },
    {
        "intent": "farewell",
        "keywords": ["bye", "goodbye", "later", "cya", "leave", "quit", "exit", "close"],
        "responses": [
            "Goodbye! Stay hydrated and keep building it.",
            "Catch you later! Don't forget your Medly bottle on the way out.",
            "Bye! Feel free to chat again if you have more questions."
        ],
        "card": None
    },

    # --- B. PRODUCT CATALOG & PRICING ---
    {
        "intent": "product_classic",
        "keywords": ["classic", "standard", "750ml", "1000ml", "1l", "basic", "799", "simple", "water", "everyday"],
        "responses": [
            "Here is the Medly Classic. 24 hours Cold, 12 hours Hot. Great for everyday use.",
            "The Medly Classic is our flagship. Built with 18/8 stainless steel, it's perfect for daily hydration.",
            "Looking for the classic? It comes in 750ml and 1L sizes and fits right in your car cup holder."
        ],
        "card": PRODUCTS["classic"]
    },
    {
        "intent": "product_prime",
        "keywords": ["prime", "office", "sleek", "1300", "professional", "strap", "work", "corporate", "premium"],
        "responses": [
            "Here is the Medly Prime Series. It features a sleek design with a carry strap, perfect for the office.",
            "The Prime Series is all about aesthetics and performance. Great for work setups.",
            "Checking out the Prime? It's priced at ₹1,300 and offers a premium matte finish."
        ],
        "card": PRODUCTS["prime"]
    },
    {
        "intent": "product_sports",
        "keywords": ["sports", "gym", "rugged", "hike", "1500", "workout", "run", "cycle", "quicksip", "sip", "active"],
        "responses": [
            "Here is the Medly Sports Rugged. Built for the grind with a quick-sip lid.",
            "Hitting the gym? The Sports model features a tough exterior and a one-handed sip lid.",
            "The Medly Sports bottle is built tough. Perfect for hiking, cycling, or intense workouts."
        ],
        "card": PRODUCTS["sports"]
    },
    {
        "intent": "product_tumbler",
        "keywords": ["tumbler", "coffee", "tea", "mug", "1399", "travel", "cup", "brew", "caffeine"],
        "responses": [
            "Here is the Medly Coffee Tumbler. Keeps your brew hot for hours while you commute.",
            "Need your caffeine fix on the go? Our Tumbler keeps coffee hot for 6+ hours and fits perfectly in your car."
        ],
        "card": PRODUCTS["tumbler"]
    },
    {
        "intent": "price_general",
        "keywords": ["price", "cost", "how", "much", "rate", "money", "discount", "rupees", "rs", "pricing", "cheap", "expensive"],
        "responses": [
            "Our premium vacuum flasks start at just ₹799 for the Classic model, going up to ₹1,500 for the Rugged Sports edition.",
            "Pricing ranges from ₹799 to ₹1,500 depending on the model. Are you looking for a specific size or style?",
            "We offer great value! The Classic is ₹799, the Prime is ₹1,300, and the Sports model is ₹1,500."
        ],
        "card": PRODUCTS["classic"]
    },

    # --- C. COMPARISONS & DEEP SPECS ---
    {
        "intent": "compare_products",
        "keywords": ["compare", "difference", "versus", "vs", "which", "better", "choose"],
        "responses": [
            "The Classic is your everyday go-to. The Prime is sleeker with a strap for the office. The Sports model has a rugged build and a quick-sip lid. Which fits your vibe?",
            "It depends on your lifestyle! The Classic is versatile, Prime is professional, and Sports is built for the gym."
        ],
        "card": None
    },
    {
        "intent": "vs_market",
        "keywords": ["milton", "cello", "thermosteel", "market", "competitor", "hydro", "flask", "yeti", "brand", "why"],
        "responses": [
            "Legacy brands are good, but Medly is built for the new age. We offer a true Lifetime Warranty on heat retention, superior matte grip, and modern aesthetics.",
            "Unlike standard flasks, Medly uses thicker 18/8 steel, premium powder coating that won't sweat, and we back it with a Lifetime Warranty."
        ],
        "card": None
    },
    {
        "intent": "retention_time",
        "keywords": ["hot", "cold", "hours", "time", "long", "duration", "warm", "ice", "melt", "retain", "temperature"],
        "responses": [
            "**Temperature Lock:** Our vacuum technology keeps water **Cold for 24 Hours** and **Hot for 12+ Hours**.",
            "You can expect your icy drinks to stay cold for up to 24 hours, and your hot tea/coffee to stay piping hot for 12 to 14 hours."
        ],
        "card": None
    },
    {
        "intent": "material_quality",
        "keywords": ["material", "steel", "plastic", "quality", "metal", "grade", "bpa", "toxic", "rust", "safe", "health"],
        "responses": [
            "**Premium Build:** We use high-grade **18/8 Stainless Steel (304 grade)**. It is 100% rust-free, BPA-free, and won't transfer flavors.",
            "All Medly flasks are made from food-grade 304 stainless steel. They are totally safe, BPA-free, and highly durable."
        ],
        "card": None
    },
    {
        "intent": "lid_types",
        "keywords": ["lid", "cap", "straw", "chug", "mouth", "wide", "sip", "drink"],
        "responses": [
            "The Classic and Prime come with airtight screw-on caps. The Sports model features a quick-sip chug lid for one-handed drinking.",
            "We offer standard wide-mouth lids on our Classic/Prime, and a specialized sports lid on the Rugged model for active hydration."
        ],
        "card": None
    },
    {
        "intent": "dimensions_weight",
        "keywords": ["heavy", "weight", "light", "dimension", "size", "tall", "height", "fit", "grams"],
        "responses": [
            "Our bottles are designed to be lightweight yet durable. The 750ml Classic weighs about 380g, making it easy to carry all day.",
            "They are lightweight! The vacuum insulation is highly efficient, keeping the bottle slim and easy to hold without adding bulk."
        ],
        "card": None
    },
    {
        "intent": "car_cup_holder",
        "keywords": ["car", "cup", "holder", "driving", "fit", "drive", "console"],
        "responses": [
            "**Car Fit:** Yes! The Medly Classic and Prime fit perfectly in standard car cup holders. (Note: The 1L Sports model is a bit wider).",
            "You can take it on the road! The base of our Classic and Prime models is designed to slot right into most car cup holders."
        ],
        "card": None
    },
    {
        "intent": "bag_leak",
        "keywords": ["bag", "backpack", "leak", "spill", "upside", "proof", "tight"],
        "responses": [
            "**100% Leakproof:** You can toss any Medly bottle into your bag upside down. Zero spills, guaranteed.",
            "Don't worry about your laptop! Our lids feature a deep silicone seal making them completely leakproof."
        ],
        "card": None
    },

    # --- D. POLICIES, PAYMENTS & SUPPORT ---
    {
        "intent": "warranty",
        "keywords": ["warranty", "waranty", "guarantee", "lifetime", "replace", "broken", "claim", "damage", "defect"],
        "responses": [
            "We stand by our gear. Medly offers a **Lifetime Warranty** on heat retention. If the vacuum seal fails naturally, we replace the bottle. (Accidental dents/scratches excluded).",
            "Our Lifetime Warranty covers any manufacturing defects or loss of vacuum insulation. Just email support to file a claim!"
        ],
        "card": None
    },
    {
        "intent": "shipping",
        "keywords": ["ship", "delivery", "track", "where", "order", "status", "arrive", "location", "delhi", "mumbai", "courier", "days", "dispatch"],
        "responses": [
            "We ship all over India! Metro cities take 2-3 days. Rest of India takes 5-7 days. You'll receive a tracking link via SMS once dispatched.",
            "Shipping is fast and tracked. Expect 2-3 days for metros and up to 7 days elsewhere. Check your email or SMS for the tracking link!"
        ],
        "card": None
    },
    {
        "intent": "returns_refunds",
        "keywords": ["return", "refund", "exchange", "cancel", "back", "policy", "wrong", "defective"],
        "responses": [
            "We have a 7-day hassle-free return and exchange policy for unused items. If you received a defective product, let us know within 48 hours and we'll swap it out!",
            "Need to return something? As long as it's unused and in its original packaging, you can return it within 7 days. Email support@mymedly.in to initiate."
        ],
        "card": None
    },
    {
        "intent": "payment_methods",
        "keywords": ["pay", "payment", "cod", "cash", "delivery", "credit", "card", "upi", "emi", "gpay", "phonepe"],
        "responses": [
            "We accept all major secure payments: UPI (GPay, PhonePe), Credit/Debit Cards, Net Banking, and **Cash on Delivery (COD)** is also available!",
            "You can pay via UPI, cards, or choose Cash on Delivery at checkout. We've got all secure options covered."
        ],
        "card": None
    },
    {
        "intent": "bulk_orders",
        "keywords": ["bulk", "wholesale", "distributor", "retailer", "quantity", "corporate", "dealership", "b2b", "gift", "custom"],
        "responses": [
            "Yes! We do corporate gifting and B2B bulk orders (with custom logo engraving). Please email support@mymedly.in for our B2B price list.",
            "Looking to buy for your team? We offer great discounts on bulk corporate orders. Drop us an email to get a custom quote!"
        ],
        "card": None
    },

    # --- E. LIQUIDS & MAINTENANCE ---
    {
        "intent": "liquid_milk_chai",
        "keywords": ["milk", "dairy", "chai", "coffee", "smell", "spoil", "sour"],
        "responses": [
            "**Milk/Chai:** You *can* store them, but please wash the bottle with warm water and soap within 4-6 hours to avoid spoiling or lingering smells.",
            "Yes, it's great for chai! Just remember to clean it out thoroughly at the end of the day so the dairy doesn't spoil."
        ],
        "card": None
    },
    {
        "intent": "liquid_carbonated",
        "keywords": ["soda", "coke", "beer", "fizzy", "gas", "carbonated", "sparkling"],
        "responses": [
            "**Not Recommended:** Carbonated drinks build pressure inside the vacuum seal. This can make the lid extremely hard to open or damage the seal.",
            "We advise against fizzy drinks! The gas buildup in an airtight vacuum flask can cause a pressure lock."
        ],
        "card": None
    },
    {
        "intent": "cleaning",
        "keywords": ["wash", "clean", "smell", "soap", "dishwasher", "stink", "maintenance", "brush"],
        "responses": [
            "**Care:** Hand wash with warm soapy water and a bottle brush. Do NOT use a dishwasher or freezer, as extreme external temperatures can ruin the vacuum seal.",
            "To clean: Use warm water, mild dish soap, and a soft brush. For stubborn stains or smells, try a mix of baking soda and warm water. No dishwashers!"
        ],
        "card": None
    }
]

# ==============================================================================
# 4. MEMORY & LOGIC ENGINE (Fuzzy + Multi-Intent)
# ==============================================================================
USER_MEMORY = {}

def find_best_intent(user_message, session_id="default"):
    cleaned_msg = re.sub(r'[^\w\s]', '', user_message.lower())
    user_words = cleaned_msg.split()
    
    scored_intents = []

    # 1. SCORE ALL INTENTS
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
        
        if current_score > 0:
            scored_intents.append({
                "intent": item["intent"],
                "score": current_score,
                "responses": item["responses"], 
                "card": item.get("card")
            })

    # Sort intents by highest score
    scored_intents.sort(key=lambda x: x["score"], reverse=True)

    # 2. CONTEXT & MEMORY FALLBACK
    last_context = USER_MEMORY.get(session_id, {}).get("last_intent")
    
    if (not scored_intents or scored_intents[0]["score"] < 8) and last_context:
        follow_up_words = ["it", "this", "that", "cost", "leak", "buy"]
        if any(w in user_words for w in follow_up_words):
            return {
                "text": f"Are you still asking about the {last_context.replace('product_', '').title()}? Let me know what specific detail you need!",
                "card": USER_MEMORY[session_id].get("last_card")
            }

    # STRICT THRESHOLD
    if not scored_intents or scored_intents[0]["score"] < 8:
        return None

    # 3. MULTI-INTENT PARSING
    results_text = []
    final_card = None
    
    top_intent = scored_intents[0]
    results_text.append(random.choice(top_intent["responses"]))
    if top_intent["card"]:
        final_card = top_intent["card"]

    if len(scored_intents) > 1:
        second_intent = scored_intents[1]
        if second_intent["score"] >= 16 and second_intent["intent"] != top_intent["intent"]:
            results_text.append(random.choice(second_intent["responses"]))
            if not final_card and second_intent["card"]:
                final_card = second_intent["card"]

    # 4. SAVE TO MEMORY
    USER_MEMORY[session_id] = {
        "last_intent": top_intent["intent"],
        "last_card": final_card
    }

    return {
        "text": " ".join(results_text),
        "card": final_card
    }

# ==============================================================================
# 5. SERVER ROUTES
# ==============================================================================
@app.route('/', methods=['GET'])
def home():
    return "Medly Chatbot is LIVE"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default_user')

        if not user_message:
            return jsonify({"error": "Empty message"}), 400

        intent_data = find_best_intent(user_message, session_id)
        
        if intent_data:
            return jsonify(intent_data)
        else:
            # UPGRADED FALLBACK
            fallback_responses = [
                "I'm not entirely sure about that one! Would you like to talk to our human support team?",
                "Hmm, my circuits are a bit crossed on that topic. Should I get you our contact details?",
                "I might need a human to answer that for you. Here is our contact info!"
            ]
            return jsonify({
                "text": random.choice(fallback_responses),
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