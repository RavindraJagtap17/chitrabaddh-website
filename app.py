
import os
import smtplib
from email.message import EmailMessage
from urllib.parse import quote

from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-secret-key")


# ---------------- DATABASE CONNECTION ----------------

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="chitrabaddh"
    )


# ---------------- HOME ----------------

@app.route("/")
def index():
    return redirect(url_for("home"))


@app.route("/home")
def home():
    return render_template("index.html")


# ---------------- AUTH PAGE ----------------

@app.route("/auth")
def auth():
    return render_template("auth.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")

    if not all([name, email, phone, password]):
        return "Please fill all required fields."

    hashed_password = generate_password_hash(password)

    try:
        db = get_db_connection()
        cursor = db.cursor()

        query = """
            INSERT INTO users (name, email, phone, password)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(query, (name, email, phone, hashed_password))
        db.commit()

        cursor.close()
        db.close()

        return redirect(url_for("auth"))

    except mysql.connector.Error as error:
        app.logger.exception("Registration failed")
        return f"Registration error: {error}"


# ---------------- LOGIN ----------------

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["user_id"]
            session["name"] = user["name"]
            session["email"] = user["email"]

            return redirect(url_for("home"))

        return "Invalid email or password."

    except mysql.connector.Error as error:
        app.logger.exception("Login failed")
        return f"Login error: {error}"


# ---------------- COLLECTION ----------------

@app.route("/collection")
def collection():
    if "user_id" not in session:
        return redirect(url_for("auth"))

    return render_template("collection.html")


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
        return "Please fill in your name, email and message."

    gmail_user = os.getenv("GMAIL_USER", "").strip()
    gmail_app_password = os.getenv(
        "GMAIL_APP_PASSWORD", ""
    ).replace(" ", "").strip()

    receiver_email = os.getenv("RECEIVER_EMAIL", "").strip()
    whatsapp_number = os.getenv("WHATSAPP_NUMBER", "").strip()

    # Check email configuration
    if not all([gmail_user, gmail_app_password, receiver_email]):
        app.logger.error("Gmail configuration is missing in .env")
        return "Email settings are missing. Please check your .env file.", 500

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

    except Exception as error:
        app.logger.exception("EMAIL SENDING FAILED")
        return f"Email Error: {error}", 500


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    app.run(debug=True)