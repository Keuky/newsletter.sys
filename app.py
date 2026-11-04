from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import SECRET_KEY
from db import fetch, execute
from security import hash_password, check_password

app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))

        existing = fetch("SELECT user_id FROM users WHERE email = %s", (email,))
        if existing:
            flash("Email already registered.", "error")
            return redirect(url_for("register"))

        existing_user = fetch("SELECT user_id FROM users WHERE username = %s", (username,))
        if existing_user:
            flash("Username already taken.", "error")
            return redirect(url_for("register"))

        password_hash = hash_password(password)
        success = execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",(username, email, password_hash))

        if success:
            flash("Account created successfully! You can now log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("Something went wrong. Please try again.", "error")
            return redirect(url_for("register"))

    return render_template("register.html")





@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_input = request.form.get("login_input", "").strip()
        password = request.form.get("password", "")

        if not login_input or not password:
            flash("Please enter both email/username and password.", "error")
            return redirect(url_for("login"))

        user = fetch("SELECT user_id, username, password_hash FROM users WHERE email = %s OR username = %s", (login_input.lower(), login_input))

        if user and check_password(password, user[0]["password_hash"]):
            session["user_id"] = user[0]["user_id"]
            session["username"] = user[0]["username"]
            flash(f"Welcome back, {user[0]['username']}!", "success")
            return redirect(url_for("index")) 
        else:
            flash("Incorrect credentials. Please try again.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)