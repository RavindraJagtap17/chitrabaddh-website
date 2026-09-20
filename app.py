from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Session साठी secret key
app.secret_key = "chitrabaddh_secret_key"


# ==============================
# MYSQL CONNECTION
# ==============================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="snehal@12",
    database="chitrabaddh"
)


# ==============================
# LOGIN / REGISTER PAGE
# ==============================

@app.route("/")
def auth():
    return render_template("auth.html")


# ==============================
# REGISTER
# ==============================

@app.route("/register", methods=["POST"])
def register():

    name = request.form["name"].strip()
    email = request.form["email"].strip()
    phone = request.form["phone"].strip()
    password = request.form["password"]

    # Password secure hash
    hashed_password = generate_password_hash(password)

    cursor = db.cursor()

    # Email already exists?
    cursor.execute(
        "SELECT user_id FROM users WHERE email = %s",
        (email,)
    )

    existing_user = cursor.fetchone()

    if existing_user:

        cursor.close()

        return """
        <script>
            alert("Email already registered!");
            window.location.href = "/";
        </script>
        """

    # Save new user
    cursor.execute(
        """
        INSERT INTO users (name, email, phone, password)
        VALUES (%s, %s, %s, %s)
        """,
        (name, email, phone, hashed_password)
    )

    db.commit()
    cursor.close()

    return """
    <script>
        alert("Registration successful! Please login.");
        window.location.href = "/";
    </script>
    """


# ==============================
# LOGIN
# ==============================

@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"].strip()
    password = request.form["password"]

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE email = %s",
        (email,)
    )

    user = cursor.fetchone()

    cursor.close()

    # Check email and password
    if user and check_password_hash(user["password"], password):

        session["user_id"] = user["user_id"]
        session["name"] = user["name"]
        session["email"] = user["email"]

        return redirect(url_for("home"))

    return """
    <script>
        alert("Invalid email or password!");
        window.location.href = "/";
    </script>
    """


# ==============================
# HOME
# ==============================

@app.route("/home")
def home():

    if "user_id" not in session:
        return redirect(url_for("auth"))

    return render_template("index.html")


# ==============================
# COLLECTION
# ==============================

@app.route("/collection")
def collection():

    if "user_id" not in session:
        return redirect(url_for("auth"))

    return render_template("collection.html")


# ==============================
# OUR STORY
# ==============================

@app.route("/story")
def story():

    if "user_id" not in session:
        return redirect(url_for("auth"))

    return render_template("story.html")


# ==============================
# PROCESS
# ==============================

@app.route("/process")
def process():

    if "user_id" not in session:
        return redirect(url_for("auth"))

    return render_template("process.html")


# ==============================
# CONTACT
# ==============================

@app.route("/contact")
def contact():

    if "user_id" not in session:
        return redirect(url_for("auth"))

    return render_template("contact.html")


# ==============================
# LOGOUT
# ==============================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("auth"))


# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    app.run(debug=True)