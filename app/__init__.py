import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
import os
import datetime
import sys
import random
import datetime
import build_db as db
app = Flask(__name__)
app.secret_key = os.urandom(24)
DB_FILE="database.db"

@app.route("/", methods=["GET", "POST"])
def login():
    error_msg = ""
    if "user_id" in session:
        return redirect(url_for("start"))
    if request.method == "POST":
        username = request.form.get("user_id").strip()
        password = request.form.get("password").strip()

        if db.user_exists(username):
            if db.login(username, password):
                session["user_id"] = username
                return redirect(url_for("home"))
            else:
                error_msg = "Password is incorrect."
        else:
            error_msg = "User does not exist. Please register."
    return render_template("login.html", error = error_msg)

@app.route("/register", methods=["GET", "POST"])
def register():
    error_msg = ""
    if "user_id" in session:
        return redirect(url_for("start"))

    if request.method == "POST":
        username = request.form.get("user_id").strip()
        password = request.form.get("password").strip()

        result = db.register(username, password)
        if (result == "Registered"):
            session["user_id"] = username
            return redirect(url_for("home"))
        if (result == "Username cannot have special characters except '_'." or result == "Username is already taken." or result == "Username or password cannot be empty."):
            error_msg = result
    return render_template("register.html", error = error_msg)

@app.route("/logout", methods=["POST"])
def logout():
    if "user_id" in session:
        session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/start")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("start.html")

@app.route("/state_stats", methods=["POST"])
def state_stats():
    if "user_id" not in session:
        return redirect(url_for("login"))
    state_id = request.form.get("state_name")
    stats = db.get_statestats(state_id)
    stringency = db.get_initstringency(state_id)
    return render_template("start.html", state = state_id, population =  stats[1], population_density = stats[2], vulnerability_index = stats[0], stringency_index = stringency[0], stringency_date = stringency[1])

@app.route("/game", methods=["GET", "POST"])
def game():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        session["state_name"] = request.form.get("state_name")
    return render_template("game.html", state_name=session.get("state_name", ""))

if __name__ == "__main__":
    app.debug = True
    app.run()
