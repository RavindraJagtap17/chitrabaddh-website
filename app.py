
import os
import smtplib
from email.message import EmailMessage
from urllib.parse import quote

from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
import mysql.connector
from mysql.connector import errorcode
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load .env file from the project folder
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-secret-key")

# Google Maps link for our location (Contact section)
MAP_URL = "https://maps.app.goo.gl/NdSchyGmmvv7dekL7"


# ---------------- ARTWORKS ----------------
# Single list used by the home page preview, the collection page
# and the order route.

ARTWORKS = [
    {"id": "B1", "category": "botanical", "name": "Botanical Frame", "description": "Handmade floral and green leaf artwork", "price": 2500, "image": "art2.jpeg.jpeg"},
    {"id": "B2", "category": "botanical", "name": "Green Leaf Painting", "description": "Beautiful handmade leaf painting", "price": 2200, "image": "art3.jpeg.jpeg"},
    {"id": "B3", "category": "botanical", "name": "Wild Flower Frame", "description": "Delicate wild flower artwork", "price": 2300, "image": "art5.jpeg.jpeg"},
    {"id": "B4", "category": "botanical", "name": "Tropical Leaves", "description": "Decorative tropical leaf painting", "price": 2800, "image": "art6.jpeg.jpeg"},
    {"id": "B5", "category": "botanical", "name": "Yellow Blossom", "description": "Hand painted yellow floral artwork", "price": 2400, "image": "art7.jpeg.jpeg"},
    {"id": "B6", "category": "botanical", "name": "Pink Flower Garden", "description": "Beautiful pink flower painting", "price": 2600, "image": "art8.jpeg.jpeg"},
    {"id": "B7", "category": "botanical", "name": "Nature Collection", "description": "Nature inspired handmade wall art", "price": 3000, "image": "art9.jpeg.jpeg"},
    {"id": "B8", "category": "botanical", "name": "Botanical Beauty", "description": "Elegant botanical decorative frame", "price": 2700, "image": "art10.jpeg.jpeg"},
    {"id": "B9", "category": "botanical", "name": "Floral Branches", "description": "Handmade branches and flower painting", "price": 2500, "image": "art11.jpeg.jpeg"},
    {"id": "B10", "category": "botanical", "name": "Nature Wall Frame", "description": "Premium handmade nature artwork", "price": 3200, "image": "art12.jpeg.jpeg"},
    {"id": "F1", "category": "floral", "name": "Floral Stories", "description": "Elegant handmade floral wall art", "price": 3000, "image": "art13.jpeg.jpeg"},
    {"id": "F2", "category": "floral", "name": "Garden Flowers", "description": "Decorative handmade garden painting", "price": 2800, "image": "art14.jpeg.jpeg"},
    {"id": "F3", "category": "floral", "name": "Blossom Wall Art", "description": "Beautiful floral decorative artwork", "price": 3200, "image": "art15.jpeg.jpeg"},
    {"id": "F4", "category": "floral", "name": "Pink Floral Design", "description": "Hand painted pink flower design", "price": 2600, "image": "art16.jpeg.jpeg"},
    {"id": "F5", "category": "floral", "name": "Flower Garden Panel", "description": "Decorative handmade flower panel", "price": 3500, "image": "art17.jpeg.jpeg"},
    {"id": "F6", "category": "floral", "name": "Traditional Floral Art", "description": "Traditional handmade floral design", "price": 3300, "image": "art18.jpeg.jpeg"},
    {"id": "F7", "category": "floral", "name": "Golden Flower Art", "description": "Elegant decorative golden floral art", "price": 3800, "image": "art19.jpeg.jpeg"},
    {"id": "F8", "category": "floral", "name": "Decorative Floral Frame", "description": "Beautiful handmade decorative frame", "price": 2900, "image": "art20.jpeg.jpeg"},
    {"id": "F9", "category": "floral", "name": "Floral Heritage", "description": "Traditional floral inspired wall painting", "price": 3600, "image": "art21.jpeg.jpeg"},
    {"id": "F10", "category": "floral", "name": "Royal Flower Panel", "description": "Premium handmade floral wall panel", "price": 4000, "image": "art22.jpeg.jpeg"},
    {"id": "P1", "category": "pichwai", "name": "Pichwai Inspired", "description": "Traditional Indian cow and lotus artwork", "price": 4500, "image": "art4.jpeg"},
    {"id": "P2", "category": "pichwai", "name": "Sacred Cow Painting", "description": "Traditional cow inspired handmade art", "price": 4200, "image": "art23.jpeg.jpeg"},
    {"id": "P3", "category": "pichwai", "name": "Lotus Garden", "description": "Beautiful traditional lotus painting", "price": 4000, "image": "art24.jpeg.jpeg"},
    {"id": "P4", "category": "pichwai", "name": "Krishna Inspired Art", "description": "Traditional Indian devotional artwork", "price": 5000, "image": "art25.jpeg.jpeg"},
    {"id": "P5", "category": "pichwai", "name": "Cow and Lotus Art", "description": "Handmade traditional cow and lotus design", "price": 4800, "image": "art26.jpeg.jpeg"},
    {"id": "P6", "category": "pichwai", "name": "Indian Heritage Painting", "description": "Traditional Indian decorative painting", "price": 4600, "image": "art27.jpeg.jpeg"},
    {"id": "P7", "category": "pichwai", "name": "Royal Pichwai Art", "description": "Premium traditional handmade artwork", "price": 5500, "image": "art28.jpeg.jpeg"},
    {"id": "P8", "category": "pichwai", "name": "Lotus Pond Painting", "description": "Traditional lotus pond inspired artwork", "price": 4300, "image": "art29.jpeg.jpeg"},
    {"id": "P9", "category": "pichwai", "name": "Traditional Cow Frame", "description": "Decorative Indian cow painting", "price": 4700, "image": "art30.jpeg.jpeg"},
    {"id": "P10", "category": "pichwai", "name": "Pichwai Heritage Panel", "description": "Handmade traditional Indian wall panel", "price": 5800, "image": "art31.jpeg.jpeg"},
]

ARTWORKS_BY_ID = {art["id"]: art for art in ARTWORKS}

# Shown in the collection preview on the home page (two from each category)
FEATURED_IDS = ["B1", "B4", "F1", "F7", "P1", "P4"]


# ---------------- SITE CONTACT DETAILS ----------------

def get_whatsapp_number():
    return os.getenv("WHATSAPP_NUMBER", "919834541457").strip()


@app.context_processor
def contact_details():
    return {
        "whatsapp_number": get_whatsapp_number(),
        "contact_email": os.getenv("CONTACT_EMAIL", "").strip(),
        "instagram_url": os.getenv("INSTAGRAM_URL", "").strip(),
        "map_url": MAP_URL,
    }


# ---------------- SAFE REDIRECT AFTER LOGIN ----------------

def safe_next_url(target):
    # Only allow paths on this website, never another domain
    if target and target.startswith("/") and not target.startswith("//") and "\\" not in target:
        return target

    return None


# ---------------- DATABASE CONNECTION ----------------

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "chitrabaddh")
    )


# ---------------- HOME ----------------

@app.route("/")
def index():
    return redirect(url_for("home"))


@app.route("/home")
def home():
    featured = [ARTWORKS_BY_ID[art_id] for art_id in FEATURED_IDS]
    return render_template("index.html", artworks=featured)


# ---------------- AUTH PAGE ----------------

@app.route("/auth")
def auth():
    next_url = safe_next_url(request.args.get("next"))
    return render_template("auth.html", next_url=next_url)


# ---------------- REGISTER ----------------

@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    next_url = safe_next_url(request.form.get("next"))

    if not all([name, email, phone, password]):
        flash("Please fill all required fields.", "register_error")
        return redirect(url_for("auth", form="register", next=next_url))

    hashed_password = generate_password_hash(password)

    db = None

    try:
        db = get_db_connection()
        cursor = db.cursor()

        query = """
            INSERT INTO users (name, email, phone, password)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(query, (name, email, phone, hashed_password))
        db.commit()

        # Log the new user in straight away
        session["user_id"] = cursor.lastrowid
        session["name"] = name
        session["email"] = email

        flash(f"Welcome to Chitrabaddh, {name}!", "site_success")
        return redirect(next_url or url_for("home"))

    except mysql.connector.Error as error:
        if error.errno == errorcode.ER_DUP_ENTRY:
            flash("An account with this email already exists. Please login.", "register_error")
        else:
            app.logger.exception("Registration failed")
            flash("We could not create your account right now. Please try again later.", "register_error")

        return redirect(url_for("auth", form="register", next=next_url))

    finally:
        if db is not None:
            db.close()


# ---------------- LOGIN ----------------

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    next_url = safe_next_url(request.form.get("next"))

    try:
        db = get_db_connection()

        try:
            cursor = db.cursor(dictionary=True)

            cursor.execute(
                "SELECT * FROM users WHERE email = %s",
                (email,)
            )

            user = cursor.fetchone()

        finally:
            db.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["user_id"]
            session["name"] = user["name"]
            session["email"] = user["email"]

            return redirect(next_url or url_for("home"))

        flash("Invalid email or password.", "login_error")
        return redirect(url_for("auth", next=next_url))

    except mysql.connector.Error:
        app.logger.exception("Login failed")
        flash("We could not log you in right now. Please try again later.", "login_error")
        return redirect(url_for("auth", next=next_url))


# ---------------- COLLECTION ----------------
# Everyone can browse. Login is only needed to order (see /order).

@app.route("/collection")
def collection():
    return render_template("collection.html", artworks=ARTWORKS)


# ---------------- ORDER ----------------

@app.route("/order/<art_id>")
def order(art_id):
    art = ARTWORKS_BY_ID.get(art_id)

    if art is None:
        abort(404)

    if "user_id" not in session:
        flash("Please login or create an account to place your order.", "auth_info")
        return redirect(url_for("auth", next=url_for("order", art_id=art_id)))

    message = (
        f"Hello Chitrabaddh, I am {session.get('name')} "
        f"and I am interested in {art['name']} ({art['id']}) "
        f"priced at ₹{art['price']:,}."
    )

    return redirect(f"https://wa.me/{get_whatsapp_number()}?text={quote(message)}")


# ---------------- STORY ----------------

@app.route("/story")
def story():
    return render_template("story.html")


# ---------------- PROCESS ----------------

@app.route("/process")
def process():
    return render_template("process.html")


# ---------------- CONTACT ----------------

@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "GET":
        return render_template("contact.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    subject = request.form.get("subject", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not email or not message:
        return render_template(
            "contact.html",
            error="Please fill in your name, email and message.",
            form=request.form
        ), 400

    gmail_user = os.getenv("GMAIL_USER", "").strip()
    gmail_app_password = os.getenv(
        "GMAIL_APP_PASSWORD", ""
    ).replace(" ", "").strip()

    receiver_email = os.getenv("RECEIVER_EMAIL", "").strip()
    whatsapp_number = os.getenv("WHATSAPP_NUMBER", "").strip()

    # Check email configuration
    if not all([gmail_user, gmail_app_password, receiver_email]):
        app.logger.error("Gmail configuration is missing in .env")
        return render_template(
            "contact.html",
            error="Sorry, we could not send your message right now. Please reach us on WhatsApp instead.",
            form=request.form
        ), 500

    # Prepare email
    email_message = EmailMessage()
    email_message["Subject"] = f"New Contact Enquiry: {subject}"
    email_message["From"] = gmail_user
    email_message["To"] = receiver_email
    email_message["Reply-To"] = email

    email_message.set_content(f"""
New enquiry received from Chitrabaddh website.

Customer Name: {name}
Customer Email: {email}
Customer Phone: {phone}
Subject: {subject}

Message:
{message}
""")

    try:
        # Gmail SMTP using STARTTLS - Port 587
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()

            smtp.login(gmail_user, gmail_app_password)
            smtp.send_message(email_message)

        # Prepare WhatsApp message
        whatsapp_text = f"""New Chitrabaddh Enquiry

Name: {name}
Email: {email}
Phone: {phone}
Subject: {subject}

Message: {message}"""

        whatsapp_url = None

        if whatsapp_number:
            whatsapp_url = (
                f"https://wa.me/{whatsapp_number}"
                f"?text={quote(whatsapp_text)}"
            )

        return render_template(
            "contact_success.html",
            whatsapp_url=whatsapp_url
        )

    except Exception:
        app.logger.exception("EMAIL SENDING FAILED")
        return render_template(
            "contact.html",
            error="Sorry, we could not send your message right now. Please try again or reach us on WhatsApp.",
            form=request.form
        ), 500


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    app.run(debug=True)
