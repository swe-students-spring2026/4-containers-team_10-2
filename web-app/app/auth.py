"""Authentication routes for the web application."""

from datetime import datetime, timezone

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import (
    create_user,
    find_user_by_email,
    find_user_by_username,
)
from app.models import User

auth = Blueprint("auth", __name__)


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    """Render and handle the sign-up page."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return render_template("signup.html")

        if find_user_by_username(username):
            flash("Username already exists.", "error")
            return render_template("signup.html")

        if find_user_by_email(email):
            flash("Email already exists.", "error")
            return render_template("signup.html")

        password_hash = generate_password_hash(password)

        user_document = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        inserted_id = create_user(user_document)
        user = User(str(inserted_id), username, email)
        login_user(user)

        flash("Account created successfully.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("signup.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    """Render and handle the login page."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user_document = find_user_by_email(email)

        if not user_document or not check_password_hash(
            user_document["password_hash"], password
        ):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        user = User.from_document(user_document)
        login_user(user)

        flash("Logged in successfully.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():
    """Log the user out."""
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))
