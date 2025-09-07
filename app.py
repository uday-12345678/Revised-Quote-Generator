from flask import Flask, render_template, request, redirect
import hashlib
import os
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

app = Flask(__name__)

# MongoDB connection (uses MONGODB_URI env var if present; otherwise uses the provided URI)
MONGODB_URI = os.environ.get(
    "MONGODB_URI",
    "mongodb+srv://vivekvardhannada:UFSMQM0yn26DfeCu@cluster0.4xn2v.mongodb.net/QuoteGenerator"
)
client = MongoClient(MONGODB_URI)
db = client["QuoteGenerator"]  # database name from your URI
users = db.users

# ✅ Create unique index on phone if not exists
def init_db():
    users.create_index("phone", unique=True)

init_db()

# ✅ Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 🟢 Login Page
@app.route("/")
def home():
    return render_template("login.html")

# 🟢 Signup Page
@app.route("/signup")
def signup_page():
    return render_template("signup.html")

# 🟢 Handle Signup
@app.route("/do_signup", methods=["POST"])
def do_signup():
    phone = request.form.get("phone")
    password = request.form.get("password")

    if not phone or not password:
        return render_template("error.html", message="⚠ Phone & Password required")

    try:
        users.insert_one({"phone": phone, "password": hash_password(password)})
        return redirect("/")  # after signup → login
    except DuplicateKeyError:
        return render_template("error.html", message="⚠ Phone already registered. Please login.")

# 🟢 Handle Login
@app.route("/login", methods=["POST"])
def login():
    phone = request.form.get("phone")
    password = request.form.get("password")

    user = users.find_one({"phone": phone})

    if not user:
        # phone not found
        return render_template("error.html", message="⚠ Phone not registered. Please sign up first.")

    if user.get("password") == hash_password(password):
        # ✅ Redirect to Quote Generator App
        return redirect("https://quote-generator-blond-seven.vercel.app/")
    else:
        return render_template("error.html", message="❌ Invalid password!")

if __name__ == "__main__":
    app.run(debug=True)
