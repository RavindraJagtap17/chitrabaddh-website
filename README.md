# 🎨 Chitrabhdha

Chitrabhdha is a web-based platform designed to showcase art, creativity, stories, and collections through an interactive and user-friendly website.

## 🛠️ Technologies Used

- **HTML5** – Used to create the structure and content of web pages.
- **CSS3** – Used for styling, layouts, colors, animations, and responsive design.
- **JavaScript** – Used to add interactivity and handle user-side actions.
- **Python** – Used for backend development and application logic.
- **Flask** – Used as the Python web framework for routing and connecting frontend with backend.
- **Jinja2** – Used for rendering dynamic HTML templates with Flask.
- **MySQL** – Used to store and manage application data in a relational database.
- **Git & GitHub** – Used for version control and project management.

## ✨ Features

- 🏠 Home page
- 🔐 User Authentication
- 🎨 Art Collection
- 📖 Stories
- ⚙️ Art Process Section
- 📩 Contact Page
- 🗄️ MySQL Database Integration
- 🌐 Flask Backend
- 📱 User-friendly Web Interface

## 📁 Project Structure

```
chitrabaddh-website/
│
├── app.py
├── schema.sql
├── requirements.txt
├── .env.example
│
├── static/
│   ├── style.css
│   └── image/
│
├── templates/
│   ├── index.html
│   ├── auth.html
│   ├── collection.html
│   ├── contact.html
│   ├── contact_success.html
│   ├── process.html
│   └── story.html
│
└── README.md
```

## 🚀 Running Locally

**Requirements:** Python 3.10+ and MySQL (for example from XAMPP).

1. **Install the Python packages**

   ```bash
   pip install -r requirements.txt
   ```

2. **Create the database** (safe to run again; it never deletes data)

   ```bash
   mysql -u root -p < schema.sql
   ```

   With XAMPP on Windows: `C:\xampp\mysql\bin\mysql.exe -u root -p < schema.sql`

3. **Create your `.env` file**

   Copy `.env.example` to `.env` and fill in your own values. `.env` is ignored by git, so never commit it.

   | Variable | What it is |
   |---|---|
   | `SECRET_KEY` | Long random string. Generate one with `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `DB_ENGINE` | `mysql` (default) or `sqlite`. With `sqlite` no MySQL is needed: the database is the file `chitrabaddh.db`, created automatically (useful for free hosting such as PythonAnywhere) |
   | `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | MySQL connection (only for `DB_ENGINE=mysql`). Defaults: `localhost`, `3306`, `root`, empty, `chitrabaddh` |
   | `GMAIL_USER`, `GMAIL_APP_PASSWORD` | Gmail account that sends contact-form emails. Needs a 16-letter [Google app password](https://myaccount.google.com/apppasswords), not the normal Gmail password |
   | `RECEIVER_EMAIL` | Inbox that receives contact-form enquiries |
   | `WHATSAPP_NUMBER` | WhatsApp number with country code, digits only (e.g. `91XXXXXXXXXX`) |
   | `CONTACT_EMAIL`, `INSTAGRAM_URL` | Shown on the Contact page. Leave blank to hide |

4. **Start the website**

   ```bash
   python app.py
   ```

   Open **http://localhost:5000** (plain `http://localhost` opens XAMPP instead).
