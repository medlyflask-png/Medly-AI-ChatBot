from flask import Flask, request, jsonify
from flask_cors import CORS
import difflib
import re
import random

app = Flask(__name__)

# ==============================================================================
# 1. CORS CONFIGURATION (CRITICAL)
# ==============================================================================
CORS(app, resources={
    r"/*": {
        "origins": ["https://www.mymedly.in", "https://mymedly.in", "http://localhost:3000", "*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Range", "X-Content-Range"]
    }
})

# ==============================================================================
# 2. MEDLY PRODUCT CATALOG
# ==============================================================================
# The central source of truth for your products.
PRODUCTS = {
    "classic": {
        "name": "Medly Classic (750ml/1000ml)",
        "price": "₹799",
        "image": "https://cdn.shopify.com/s/files/1/0641/9215/1686/files/medly-classic-500ml-double-wall-vacuum-flask-silver.png?v=1768887094", 
        "url": "https://www.mymedly.in/products/classic"
    },
    "prime": {
        "name": "Medly Prime Series",
        "price": "₹1,300",
        "image": "https://cdn.shopify.com/s/files/1/0641/9215/1686/files/medly-prime-550ml-portable-thermos-bottle-strap-black.png?v=1768887219",
        "url": "https://www.mymedly.in/products/prime"
    },
    "sports": {
        "name": "Medly Sports Rugged",
        "price": "₹1,500",
        "image": "https://cdn.shopify.com/s/files/1/0641/9215/1686/files/medly-quicksip-1l-sports-water-bottle-leakproof-red.png?v=1768887449",
        "url": "https://www.mymedly.in/products/quicksip"
    },
    "tumbler": {
        "name": "Medly Coffee Tumbler",
        "price": "₹1,399",
        "image": "https://cdn.shopify.com/s/files/1/0641/9215/1686/files/medly-tumbler-1200ml-travel-mug-iced-coffee-cup-black.png?v=1768887556",
        "url": "https://www.mymedly.in/products/tumbler"
    }
}

# ==============================================================================
# 3. THE "10K" KNOWLEDGE BASE (MEGA MERGE)
# ==============================================================================

KNOWLEDGE_BASE = [
    # --------------------------------------------------------------------------
    # A. GREETINGS & BASICS
    # --------------------------------------------------------------------------
    {
        "intent": "greeting",
        "keywords": ["hi", "hii", "hello", "hey", "hie", "hy", "hiya", "good morning", "good evening", "namaste", "start", "medly", "bot"],
        "response": "Hello! Welcome to Medly. I'm here to help you #BuildIt. Ask me about **Warranty**, **Car Fit**, or check out our **Classic Bottle**!",
        "card": PRODUCTS["classic"]
    },
    {
        "intent": "gratitude",
        "keywords": ["thank", "thanks", "thx", "cool", "great", "good job", "awesome"],
        "response": "You're very welcome! Happy to help you #BuildIt. "
    },
    {
        "intent": "goodbye",
        "keywords": ["bye", "goodbye", "cya", "end", "stop", "exit"],
        "response": "Goodbye! Stay hydrated. See you soon!"
    },
    {
        "intent": "bot_identity",
        "keywords": ["who are you", "are you human", "robot", "real person"],
        "response": "I'm the **Medly Assistant**, trained to think like a hydration expert! But if you need a human, just ask for 'Contact'."
    },

    # --------------------------------------------------------------------------
    # B. SALES & RECOMMENDATIONS (Rich Media)
    # --------------------------------------------------------------------------
    {
        "intent": "show_bestseller",
        "keywords": ["best", "top", "popular", "selling", "favorite", "recommend", "classic", "standard", "799"],
        "response": "Our community favorite is the **Medly Classic**. It fits everywhere, keeps water cold for 24 hours, and starts at an unbeatable **₹799**.",
        "card": PRODUCTS["classic"]
    },
    {
        "intent": "show_office",
        "keywords": ["office", "work", "meeting", "formal", "desk", "corporate", "prime", "sleek", "1300"],
        "response": "For the workspace, I recommend the **Medly Prime** (₹1,300). It has a sophisticated silhouette that looks great in meetings.",
        "card": PRODUCTS["prime"]
    },
    {
        "intent": "show_gym",
        "keywords": ["gym", "workout", "running", "hike", "active", "sports", "rugged", "1500"],
        "response": "Crushing a workout? You need the **Medly Sports** edition. High capacity, easy grip, and rugged build.",
        "card": PRODUCTS["sports"]
    },
    {
        "intent": "show_coffee",
        "keywords": ["coffee", "tea", "caffeine", "mug", "travel mug", "tumbler", "1399"],
        "response": "Keep your brew hot while you commute! The **Medly Tumbler** is designed for coffee lovers.",
        "card": PRODUCTS["tumbler"]
    },
    {
        "intent": "show_catalog",
        "keywords": ["catalog", "list", "products", "buy", "shop", "collection", "range", "show me bottles"],
        "response": "Here is the full Medly lineup. #BuildIt",
        "carousel": [PRODUCTS["classic"], PRODUCTS["prime"], PRODUCTS["sports"], PRODUCTS["tumbler"]]
    },
    {
        "intent": "discount_hunt",
        "keywords": ["coupon", "code", "discount", "promo", "offer", "sale", "deal", "cheap"],
        "response": "Psst! Use code **MEDLY10** at checkout for an instant **10% OFF**. Don't tell anyone I gave you this!",
        "card": {
            "name": "Apply 10% OFF",
            "price": "Code: MEDLY10",
            "image": "https://www.mymedly.in/cdn/shop/files/classic.jpg",
            "url": "https://www.mymedly.in/discount/MEDLY10"
        }
    },
    {
        "intent": "stock_urgency",
        "keywords": ["available", "in stock", "stock", "left", "inventory"],
        "response": "**Stock Alert:** The Black Matte Classic is selling very fast. We have only a few units left in the current batch. #BuildIt before it's gone."
    },

    # --------------------------------------------------------------------------
    # C. "REAL LIFE" SCENARIOS (The Smart Stuff)
    # --------------------------------------------------------------------------
    {
        "intent": "car_cup_holder",
        "keywords": ["car", "cup holder", "swift", "creta", "driving", "drive", "holder", "fit"],
        "response": "**Car Fit:** Yes! The **Medly Classic** and **Prime** models are designed to fit perfectly in standard car cup holders. The Sports model is wider and might not fit small holders."
    },
    {
        "intent": "bag_leak",
        "keywords": ["bag", "backpack", "purse", "laptop bag", "leak", "spill", "upside down"],
        "response": "**100% Leakproof:** You can toss any Medly bottle into your laptop bag or purse upside down. The precision silicone seal ensures zero spills."
    },
    {
        "intent": "ice_cubes",
        "keywords": ["ice", "cubes", "wide mouth", "opening", "put ice"],
        "response": "**Ice Friendly:** Yes, standard ice cubes fit easily into the Classic and Prime models. The Sports model has a wider mouth for even faster filling!"
    },
    {
        "intent": "kids_school",
        "keywords": ["kid", "child", "school", "boy", "girl", "daughter", "son", "heavy for kid"],
        "response": "For school kids, I recommend the **Medly Classic 750ml**. It fits in school bag side pockets, isn't too heavy, and withstands rough use!"
    },
    {
        "intent": "flight_travel",
        "keywords": ["flight", "plane", "airport", "security", "carry on", "travel", "fly"],
        "response": " **Travel Tip:** You can take empty Medly bottles through airport security. Once inside, fill them up at a water station to avoid buying expensive plastic bottles!"
    },
    {
        "intent": "hiking_trekking",
        "keywords": ["hike", "trek", "mountain", "climb", "outdoor", "camping"],
        "response": "Going to the mountains? The **Medly Sports** is your best friend. It holds more water (keeps it cold for 24h) and has a rugged exterior that handles rocks and drops better."
    },
    {
        "intent": "elderly_use",
        "keywords": ["old", "elderly", "senior", "grandma", "grandpa", "arthiritis", "grip"],
        "response": "For seniors, weight matters. The **Classic 750ml** is easy to hold. The lid is designed to open with minimal force, so it's arthritis-friendly."
    },

    # --------------------------------------------------------------------------
    # D. COMPETITOR COMPARISONS (Why Us?)
    # --------------------------------------------------------------------------
    {
        "intent": "vs_milton",
        "keywords": ["milton", "thermosteel", "older brand"],
        "response": "Milton is a classic, but Medly is the upgrade. \n1. **Lifetime Warranty** (they usually give 1 year).\n2. **Modern Powder Coat** (better grip than plain steel).\n3. **ZeroAir™ Tech** (keeps water hot longer)."
    },
    {
        "intent": "vs_cello",
        "keywords": ["cello", "duro", "flip style"],
        "response": "Cello makes good bottles, but Medly focuses on **Premium Build**. We use thicker 18/8 steel which resists dents better, and our design is made for modern aesthetics, not just utility."
    },
    {
        "intent": "vs_plastic_fridge",
        "keywords": ["tupperware", "aquasafe", "fridge bottle", "plastic", "pet"],
        "response": "Why drink from plastic? Medly keeps your water **cold on your desk**. You don't need to run to the fridge every time. Plus, no micro-plastics in your water!"
    },

    # --------------------------------------------------------------------------
    # E. LIQUID COMPATIBILITY
    # --------------------------------------------------------------------------
    {
        "intent": "liquid_milk",
        "keywords": ["milk", "dairy", "baby", "formula", "chai", "coffee milk"],
        "response": "**Milk/Chai:** You *can*, but please be careful. Milk can spoil quickly if left too long. **Tip:** Wash strictly within 4-6 hours to keep it fresh."
    },
    {
        "intent": "liquid_carbonated",
        "keywords": ["soda", "coke", "pepsi", "beer", "alcohol", "fizzy", "carbonated", "gas"],
        "response": "**Not Recommended:** Carbonated drinks (Soda/Beer) build up pressure inside the vacuum seal. This can make the lid jam or pop open forcefully. Stick to water, tea, coffee, or juice!"
    },

    # --------------------------------------------------------------------------
    # F. DURABILITY & QUALITY
    # --------------------------------------------------------------------------
    {
        "intent": "paint_scratch",
        "keywords": ["paint", "scratch", "peel", "coating", "color fade", "powder"],
        "response": "**Durability:** We use a high-quality **Powder Coat** finish (on colored bottles) which is chip-resistant and provides extra grip. However, sharp keys or dropping it on concrete can cause scratches."
    },
    {
        "intent": "material_safety",
        "keywords": ["material", "steel", "grade", "304", "316", "food safe", "plastic", "bpa"],
        "response": "We use premium **18/8 (304 Grade) Stainless Steel**. It is 100% BPA-Free, Rust-Free, and Food Grade safe. No plastic touches your water inside the bottle."
    },
    
    # --------------------------------------------------------------------------
    # G. WARRANTY & SUPPORT
    # --------------------------------------------------------------------------
    {
        "intent": "warranty_policy",
        "keywords": ["warranty", "waranty", "guarantee", "lifetime", "promise", "assurance"],
        "response": " **Medly Lifetime Warranty:** We guarantee heat retention for life! If the vacuum fails (bottle gets hot from outside), we replace it. (Note: Dents/Scratches are not covered)."
    },
    {
        "intent": "warranty_claim",
        "keywords": ["claim", "not working", "fails", "defective", "heat loss", "problem"],
        "response": "To claim warranty, email a **video** of the issue to **support@mymedly.in**. We approve replacements within 24 hours."
    },
    {
        "intent": "contact_info",
        "keywords": ["contact", "support", "call", "phone", "number", "email", "talk", "agent"],
        "response": "Call: **8744048726** (10AM-7PM)\n Email: **support@mymedly.in**\n HQ: Noida, Uttar Pradesh."
    },

    # --------------------------------------------------------------------------
    # H. LOGISTICS (Shipping & Delivery)
    # --------------------------------------------------------------------------
    {
        "intent": "shipping_metro",
        "keywords": ["delhi", "mumbai", "bangalore", "noida", "gurgaon", "metro", "city"],
        "response": "For Metro cities, delivery is super fast! Expect it in **2-3 business days**."
    },
    {
        "intent": "shipping_village",
        "keywords": ["village", "remote", "assam", "kashmir", "rural", "pincode"],
        "response": "We deliver to 19,000+ pincodes! For remote areas, please allow **5-7 days** for delivery."
    },
    {
        "intent": "tracking",
        "keywords": ["track", "tracking", "order status", "where is my order"],
        "response": "You will receive a **Tracking Link via SMS/Email** once dispatched. If missing, email **support@mymedly.in**."
    },

    # --------------------------------------------------------------------------
    # I. PAYMENT & RETURNS
    # --------------------------------------------------------------------------
    {
        "intent": "payment_methods",
        "keywords": ["cod", "cash", "pay", "payment", "upi", "card", "online"],
        "response": " We accept **Cash on Delivery (COD)**, UPI, Credit/Debit Cards, and Net Banking. You can choose your preferred method at checkout!"
    },
    {
        "intent": "returns",
        "keywords": ["return", "exchange", "refund", "broken", "damaged"],
        "response": "**7-Day Easy Returns**: If you received a wrong or defective product, email **support@mymedly.in**. We will arrange a free reverse pickup and replacement."
    },

    # --------------------------------------------------------------------------
    # J. TROUBLESHOOTING
    # --------------------------------------------------------------------------
    {
        "intent": "care_instructions",
        "keywords": ["wash", "clean", "soap", "dishwasher", "freezer", "microwave"],
        "response": "**Care:** Hand wash with warm soapy water. \n **Avoid:** Dishwashers, Freezers, and Microwaves (these damage the vacuum seal)."
    },
    {
        "intent": "smell_issue",
        "keywords": ["smell", "stink", "odor", "bad smell", "weird taste"],
        "response": "New bottle smell? Or leftover coffee smell? \n**Fix:** Fill with warm water + 1 tsp baking soda (or vinegar). Let sit overnight. Rinse well. It'll be fresh!"
    },
    {
        "intent": "lid_stuck",
        "keywords": ["stuck", "lid", "cap", "open", "jammed"],
        "response": "Lid stuck? This happens due to vacuum pressure. Run **warm water** over the cap for 30 seconds to expand it, then twist. It opens easily!"
    },

    # --------------------------------------------------------------------------
    # K. EMOTIONAL & CONVERSATIONAL
    # --------------------------------------------------------------------------
    {
        "intent": "compliment_bot",
        "keywords": ["smart", "intelligent", "good bot", "love you", "cool feature"],
        "response": "Aw, shucks!  I'm just a few lines of code trying to help you stay hydrated. #BuildIt"
    },
    {
        "intent": "angry_customer",
        "keywords": ["stupid", "useless", "worst", "hate", "bad service", "fraud", "cheat"],
        "response": "I am so sorry I couldn't help. I'm just a bot. Please escalate this immediately by calling our human manager at **8744048726**. We want to fix this."
    },
    {
        "intent": "joke",
        "keywords": ["joke", "funny", "laugh", "bored"],
        "response": "Why did the water bottle break up with the cup? \nBecause it wanted a *transparent* relationship!  (Okay, I'll stick to selling bottles)."
    },

    # --------------------------------------------------------------------------
    # L. UPCOMING SERVICES
    # --------------------------------------------------------------------------
    {
        "intent": "custom_engraving",
        "keywords": ["engrave", "name", "personalize", "custom", "logo", "print name"],
        "response": " **Coming Soon!** We are setting up our Laser Engraving station. You will soon be able to permanently engrave your name on any Medly bottle."
    },
    {
        "intent": "gift_wrapping",
        "keywords": ["gift wrap", "wrapping", "gift", "present", "birthday"],
        "response": " **Gift Wrapping is launching soon!** For now, all bottles ship in our premium eco-friendly box, perfect for gifting."
    },
    
    # --------------------------------------------------------------------------
    # M. UNIVERSAL FALLBACKS
    # --------------------------------------------------------------------------
    {
        "intent": "price_general",
        "keywords": ["price", "cost", "how much", "rate", "money"],
        "response": "Our range starts from **₹799**. Check out the Classic model!",
        "card": PRODUCTS["classic"]
    }
]

# ==============================================================================
# 4. LOGIC ENGINE (CONTEXT AWARE)
# ==============================================================================

# Note: In a real serverless deployment, global variables might reset.
# But this works for quick sessions.
last_mentioned_product = None 

def find_best_intent(user_message):
    global last_mentioned_product
    cleaned_msg = re.sub(r'[^\w\s]', '', user_message.lower())
    user_words = cleaned_msg.split()
    
    best_score = 0
    best_result = None

    # --- 1. SMART CONTEXT CHECK ---
    # If user asks about "it" or "this", recall the last product.
    if ("it" in user_words or "this" in user_words) and last_mentioned_product:
        if "price" in user_words or "cost" in user_words:
             return {
                "text": f"The **{last_mentioned_product['name']}** is priced at **{last_mentioned_product['price']}**.",
                "card": last_mentioned_product
            }
        if "buy" in user_words or "link" in user_words:
             return {
                "text": f"Here is the link to buy the {last_mentioned_product['name']}:",
                "card": last_mentioned_product
            }

    # --- 2. STANDARD INTENT SEARCH ---
    for item in KNOWLEDGE_BASE:
        score = 0
        keywords = item['keywords']
        
        for word in user_words:
            if word in keywords:
                score += 10 # Exact match
            else:
                matches = difflib.get_close_matches(word, keywords, n=1, cutoff=0.85)
                if matches:
                    score += 8 # Fuzzy match

        if score > best_score:
            best_score = score
            best_result = item

    if best_score > 0 and best_result:
        # SAVE CONTEXT if a product is shown
        if best_result.get('card'):
            last_mentioned_product = best_result['card']
            
        return {
            "text": best_result['response'],
            "card": best_result.get('card'),      
            "carousel": best_result.get('carousel') 
        }
    
    return None

# ==============================================================================
# 5. FLASK ROUTES
# ==============================================================================

@app.route('/', methods=['GET'])
def home():
    return "Medly Mega-Bot is Running (Rule-Based v3.0 Ultimate)"

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

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
                "text": "I'm not sure about that. Try asking about **Warranty**, **Car Fit**, or **Shipping**! Or email us at support@mymedly.in.",
                "card": None
            })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# Required for Vercel
if __name__ == '__main__':
    app.run(port=9292)