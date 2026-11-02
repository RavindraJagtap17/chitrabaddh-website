
import os
import smtplib
import sqlite3
from email.message import EmailMessage
from urllib.parse import quote

from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import errorcode
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load .env file from the project folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-secret-key")


# ---------------- SITE CONTACT DETAILS ----------------

@app.context_processor
def contact_details():
    return {
        "whatsapp_number": os.getenv("WHATSAPP_NUMBER", "919834541457").strip(),
        "contact_email": os.getenv("CONTACT_EMAIL", "").strip(),
        "instagram_url": os.getenv("INSTAGRAM_URL", "").strip(),
    }


# ---------------- DATABASE CONNECTION ----------------

# "mysql" (default, for local XAMPP) or "sqlite" (for free hosting)
DB_ENGINE = os.getenv("DB_ENGINE", "mysql").strip().lower()
USE_SQLITE = DB_ENGINE == "sqlite"

SQLITE_PATH = os.getenv("SQLITE_PATH", "").strip() or os.path.join(BASE_DIR, "chitrabaddh.db")

# SQL placeholder style differs between the two databases
PLACEHOLDER = "?" if USE_SQLITE else "%s"

DB_ERRORS = (mysql.connector.Error, sqlite3.Error)


def get_db_connection():
    if USE_SQLITE:
        db = sqlite3.connect(SQLITE_PATH)
        db.row_factory = sqlite3.Row
        return db

    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "chitrabaddh")
    )


def get_dict_cursor(db):
    # SQLite rows already allow row["column"] because of row_factory
    return db.cursor() if USE_SQLITE else db.cursor(dictionary=True)


def is_duplicate_entry(error):
    if isinstance(error, sqlite3.IntegrityError):
        return True

    return getattr(error, "errno", None) == errorcode.ER_DUP_ENTRY


def create_sqlite_tables():
    db = sqlite3.connect(SQLITE_PATH)
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            email       TEXT NOT NULL UNIQUE,
            phone       TEXT NOT NULL,
            password    TEXT NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()
    db.close()


if USE_SQLITE:
    create_sqlite_tables()


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
        flash("Please fill all required fields.", "register_error")
        return redirect(url_for("auth", form="register"))

    hashed_password = generate_password_hash(password)

    db = None

    try:
        db = get_db_connection()
        cursor = db.cursor()

        query = f"""
            INSERT INTO users (name, email, phone, password)
            VALUES ({PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER})
        """

        cursor.execute(query, (name, email, phone, hashed_password))
        db.commit()

        flash("Account created successfully. Please login.", "login_success")
        return redirect(url_for("auth"))

    except DB_ERRORS as error:
        if is_duplicate_entry(error):
            flash("An account with this email already exists. Please login.", "register_error")
        else:
            app.logger.exception("Registration failed")
            flash("We could not create your account right now. Please try again later.", "register_error")

        return redirect(url_for("auth", form="register"))

    finally:
        # Always close, so a failed insert never leaves SQLite locked
        if db is not None:
            db.close()


# ---------------- LOGIN ----------------

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    try:
        db = get_db_connection()

        try:
            cursor = get_dict_cursor(db)

            cursor.execute(
                f"SELECT * FROM users WHERE email = {PLACEHOLDER}",
                (email,)
            )

            user = cursor.fetchone()

        finally:
            db.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["user_id"]
            session["name"] = user["name"]
            session["email"] = user["email"]

            return redirect(url_for("home"))

        flash("Invalid email or password.", "login_error")
        return redirect(url_for("auth"))

    except DB_ERRORS:
        app.logger.exception("Login failed")
        flash("We could not log you in right now. Please try again later.", "login_error")
        return redirect(url_for("auth"))


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