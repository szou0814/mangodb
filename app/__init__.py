import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from json import loads
import os
import datetime
import sys
import random
import datetime
import build_db as db
import logic as logic

app = Flask(__name__)
app.secret_key = 'hi'
DB_FILE="database.db"
cache = {}

@app.route("/", methods=["GET", "POST"])
def login():
    error_msg = ""
    if "user_id" in session:
        return redirect(url_for("home"))
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
            error_msg = "User does not exist."
    return render_template("login.html", error = error_msg)

@app.route("/register", methods=["GET", "POST"])
def register():
    error_msg = ""
    if "user_id" in session:
        return redirect(url_for("home"))

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
    prompt = True #edit this when we have prompts set up
    return render_template("start.html", state = state_id, population =  stats[1], population_density = stats[2], vulnerability_index = stats[0], stringency_index = stringency[0], stringency_date = stringency[1], prompt = prompt)

@app.route("/game", methods=["GET", "POST"])
def game():
    global cache;
    STATES = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY",
              "LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND",
              "OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"]
    STATE_NAMES = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho",
        "Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri",
        "Montana","Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon",
        "Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington","West Virginia",
        "Wisconsin","Wyoming"]

    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        reqs = request.headers

        if 'data' in reqs and 'data' in cache:
            data = cache['data']

            if reqs['data'] != 'start':
                prevData = loads(reqs['data'])

                i = data.index(prevData[0])
                i += len(STATES)
                if i > len(data):
                    return 'end'
            else:
                print('i got here!')
                i = 0

            print(data[i:len(STATES)+i])
            return jsonify(data[i:len(STATES)+i])

        if 'state_name' not in session or session["state_name"] != request.form.get("state_name"):
            session["state_name"] = STATES[STATE_NAMES.index(request.form.get("state_name"))]

    if cache.get('data') is None:
        map_adj = logic.get_adjacency()
        sim = logic.Simulation(session['state_name'], map_adj)

        # Tick the simulation
        print("tickin")
        for _ in range(152):
            df = sim.tick()
            if sim.pending_prompts:
                for prompt in sim.pending_prompts:
                    print(f"Prompt: {prompt['prompt']['question']}")
                sim.pending_prompts.clear()
        print("done tickin")
        data = []
        infected_cols = [c for c in df.columns if str(c).endswith("_infected")]
        print("data thing")
        for col in infected_cols:
            for state in STATES:
                state_name = STATE_NAMES[STATES.index(state)]
                date_str = str(col)[:10]
                infected = df.loc[state, col]
                data.append({
                    'state': state_name,
                    'date': date_str,
                    'infected': float(infected),
                })
        print("done data thing")
        cache['data'] = data

    populations = []
    for state in STATE_NAMES:
        populations.append(db.get_statestats(state)[1])

    return render_template("game.html", state_name=session.get("state_name", ""), pops=populations)

if __name__ == "__main__":
    app.debug = True
    app.run()
