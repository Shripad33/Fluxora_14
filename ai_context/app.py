from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
import math
import re
import uuid
import hashlib

app = Flask(__name__)
app.secret_key = "context_recovery_secret"

# ─────────────────────────────
# IN-MEMORY DATABASE
# ─────────────────────────────
USERS = {}
MEMORIES = {}
CONVERSATIONS = {}

# ─────────────────────────────
# PASSWORD HASH
# ─────────────────────────────
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ─────────────────────────────
# MEMORY SYSTEM
# ─────────────────────────────
def create_fragment(text, role="user"):
    return {
        "id": str(uuid.uuid4()),
        "text": text,
        "role": role,
        "timestamp": datetime.now().timestamp()
    }

def store_memory(username, text, role="user"):
    if username not in MEMORIES:
        MEMORIES[username] = []
    MEMORIES[username].append(create_fragment(text, role))

# ─────────────────────────────
# TOKENIZATION
# ─────────────────────────────
STOPWORDS = {"the","is","a","an","and","or","in","on","at","to","for","of","i","you"}

def tokenize(text):
    words = re.findall(r'\b[a-z]{2,}\b', text.lower())
    return [w for w in words if w not in STOPWORDS]

# ─────────────────────────────
# RELEVANCE + PRIORITY
# ─────────────────────────────
def relevance_score(query_tokens, text):
    t = set(tokenize(text))
    q = set(query_tokens)
    if not t or not q:
        return 0
    return len(t & q) / len(t | q)

def recency_weight(ts):
    age = (datetime.now().timestamp() - ts) / 60
    return math.exp(-0.02 * age)

def priority_score(rel, ts):
    return rel * 0.7 + recency_weight(ts) * 0.3

# ─────────────────────────────
# CONTEXT PIPELINE
# ─────────────────────────────
def retrieve_context(username, query):
    fragments = MEMORIES.get(username, [])
    tokens = tokenize(query)

    scored = []
    for f in fragments:
        rel = relevance_score(tokens, f["text"])
        pri = priority_score(rel, f["timestamp"])
        scored.append((pri, f))

    scored.sort(key=lambda x: x[0], reverse=True)

    top = [f for _, f in scored[:5]]
    top.sort(key=lambda x: x["timestamp"])
    return top

def reconstruct_context(frags):
    return "\n".join([f"{f['role']}: {f['text']}" for f in frags])

import random

def generate_response(username, user_message, context_fragments):

    user_lower = user_message.lower()

    # 🧠 Intent scoring
    intent_scores = {
        "greeting": 0,
        "project": 0,
        "problem": 0,
        "learning": 0,
        "general": 0
    }

    if any(w in user_lower for w in ["hello","hi","hey"]):
        intent_scores["greeting"] += 2

    if any(w in user_lower for w in ["project","build","app","system","code"]):
        intent_scores["project"] += 2

    if any(w in user_lower for w in ["error","issue","bug","fail","problem"]):
        intent_scores["problem"] += 2

    if any(w in user_lower for w in ["study","learn","exam","understand"]):
        intent_scores["learning"] += 2

    intent = max(intent_scores, key=intent_scores.get)

    # 🧠 Context extraction
    context_texts = [frag["text"] for frag in context_fragments[-2:]]

    # 🎲 RESPONSE POOLS (MULTIPLE VARIATIONS)

    responses = {
        "greeting": [
            "Hey! Good to see you again 😊 What are you working on?",
            "Hi there! Picking up from before—what do you need help with?",
            "Hello! I'm keeping track of our conversation—how can I assist you today?"
        ],

        "project": [
            "Looks like you're building something interesting. Try focusing on one component at a time.",
            "From your earlier work, you're progressing well—just keep refining step by step.",
            "You're in build mode 🚀—prioritize core features before polishing."
        ],

        "problem": [
            "That seems like a bug. Start by checking your latest changes and logs.",
            "Something’s off—debug step-by-step and isolate the issue.",
            "This might be a logic issue. Try tracing your execution flow carefully."
        ],

        "learning": [
            "You're learning something new 📚—break it down into small concepts.",
            "Focus on understanding, not memorizing—that’s how it sticks.",
            "You're on the right track—practice and repetition will help."
        ],

        "general": [
            "Let’s think this through step by step.",
            "Interesting point—let’s build on that.",
            "I see where you're going—here’s how to approach it."
        ]
    }

    # 🎲 Pick random base response
    base_response = random.choice(responses.get(intent, responses["general"]))

    # 🧠 Add context awareness dynamically
    context_part = ""
    if context_texts:
        context_sample = random.choice(context_texts)
        context_part = f" Earlier you mentioned '{context_sample}'."

    #  Add variation ending
    endings = [
        " Let’s move forward from here.",
        " This should help you progress.",
        " Try this approach and adjust as needed.",
        " Keep going—you’re close."
    ]

    ending = random.choice(endings)

    final_response = base_response + context_part + ending

    return final_response
def pipeline(username, msg):
    store_memory(username, msg, "user")

    past = MEMORIES.get(username, [])[:-1]
    context = retrieve_context(username, msg)

    response = generate_response(username, msg, context)

    store_memory(username, response, "assistant")

    if username not in CONVERSATIONS:
        CONVERSATIONS[username] = []

    CONVERSATIONS[username].append({"role":"user","text":msg})
    CONVERSATIONS[username].append({"role":"assistant","text":response})

    return response

# ─────────────────────────────
# ROUTES
# ─────────────────────────────

@app.route("/")
def home():
    if "username" in session:
        return redirect("/dashboard")
    return redirect("/login")

# LOGIN
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        data = request.get_json()
        u = data.get("username")
        p = data.get("password")

        if u in USERS and USERS[u] == hash_password(p):
            session["username"] = u
            return jsonify({"success": True, "redirect": "/onboarding"})
        return jsonify({"success": False, "message": "Invalid credentials"})

    return render_template("login.html")

# SIGNUP
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    u = data.get("username")
    p = data.get("password")

    if u in USERS:
        return jsonify({"success": False, "message": "User exists"})

    USERS[u] = hash_password(p)
    session["username"] = u

    return jsonify({"success": True, "redirect": "/onboarding"})

# ONBOARDING
@app.route("/onboarding")
def onboarding():
    if "username" not in session:
        return redirect("/login")
    return render_template("onboarding.html")

@app.route("/save-profile", methods=["POST"])
def save_profile():
    data = request.get_json()
    session["profile"] = data
    return jsonify({"success": True, "redirect": "/dashboard"})

# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/login")
    return render_template("dashboard.html")

# CHAT
@app.route("/chat", methods=["POST"])
def chat():
    if "username" not in session:
        return jsonify({"error":"Unauthorized"}), 401

    msg = request.get_json().get("message")
    res = pipeline(session["username"], msg)

    return jsonify({"response": res})

# HISTORY
@app.route("/history")
def history():
    user = session.get("username")
    return jsonify({"history": CONVERSATIONS.get(user, [])})

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ─────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)