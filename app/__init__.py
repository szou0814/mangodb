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

#writing them so far... only 6 need to work on more
# prompts = {
#     "school_closures": {
#         "question": "Students and teachers are becoming sick and absent. What do you do?",
#         "choices": {
#             "A": {
#                 "label": "Close all schools",
#                 "stringency_change": +18,
#                 "svi_change": +0.02,  
#             },
#             "B": {
#                 "label": "Move to hybrid learning",
#                 "stringency_change": +8,
#                 "svi_change": +0.01,
#             },
#             "C": {
#                 "label": "Keep schools open",
#                 "stringency_change": -5,
#                 "svi_change": +0.0,
#             },
#         }
#     },
#     "mask_mandate": {
#         "question": "A mask mandate is proposed. Do you support it?",
#         "choices": {
#             "A": {
#                 "label": "Enforce a statewide mask mandate",
#                 "stringency_change": +10,
#                 "svi_change": -0.01,  
#             },
#             "B": {
#                 "label": "Recommend masks but don't mandate",
#                 "stringency_change": +3,
#                 "svi_change": +0.0,
#             },
#             "C": {
#                 "label": "Leave it to individual choice",
#                 "stringency_change": -8,
#                 "svi_change": +0.02,
#             },
#         }
#     },
#     "testing_expansion": {
#         "question": "Testing is being developed but requires extensive resources. How do you allocate them?",
#         "choices": {
#             "A": {
#                 "label": "Fund free community testing centers statewide",
#                 "stringency_change": +5,
#                 "svi_change": -0.04, #kinda big so like maybe gate by stringency idk
#             },
#             "B": {
#                 "label": "Expand testing only at hospitals",
#                 "stringency_change": +2,
#                 "svi_change": -0.01,
#             },
#             "C": {
#                 "label": "Rely on private testing, no state funding",
#                 "stringency_change": -3,
#                 "svi_change": +0.03, 
#             },
#         }
#     },
#     "stay_at_home": {
#         "question": "Cases are rising. Your advisors recommend a stay-at-home order. Do you approve it?",
#         "choices": {
#             "A": {
#                 "label": "Issue a strict stay-at-home order",
#                 "stringency_change": +20,
#                 "svi_change": +0.03,  
#             },
#             "B": {
#                 "label": "Issue a limited order for high-risk groups only",
#                 "stringency_change": +8,
#                 "svi_change": +0.01,
#             },
#             "C": {
#                 "label": "Decline to issue any order",
#                 "stringency_change": -10,
#                 "svi_change": +0.02,
#             },
#         }
#     },
#     "healthcare_investment": {
#         "question": "Hospitals are becoming too crowded. What's your response?",
#         "choices": {
#             "A": {
#                 "label": "Emergency fund community health clinics",
#                 "stringency_change": +3,
#                 "svi_change": -0.05,  #prob gonna be affected by stringency too
#             },
#             "B": {
#                 "label": "Redirect funds to ICU expansion only",
#                 "stringency_change": +2,
#                 "svi_change": -0.02,
#             },
#             "C": {
#                 "label": "No additional healthcare spending",
#                 "stringency_change": 0,
#                 "svi_change": +0.03,
#             },
#         }
#     },
#     "travel_restrictions": {
#         "question": "Neighboring states are seeing rising infections. Do you restrict travel?", #maybe can do smth cool w the adjacency
#         "choices": {
#             "A": {
#                 "label": "Ban non-essential interstate travel",
#                 "stringency_change": +15,
#                 "svi_change": +0.01,
#             },
#             "B": {
#                 "label": "Require quarantine for travelers",
#                 "stringency_change": +7,
#                 "svi_change": +0.0,
#             },
#             "C": {
#                 "label": "No travel restrictions",
#                 "stringency_change": -5,
#                 "svi_change": +0.01,
#             },
#         }
#     },
# }

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
                i = 0

            return jsonify(data[i:len(STATES)+i])

        if 'state_name' not in session:
            session["state_name"] = STATES[STATE_NAMES.index(request.form.get("state_name"))]

    if 'data' not in cache:
        map = logic.get_adjacency();
        df = logic.run_simulation(session['state_name'], map);

        data = []
        for row in df.itertuples():
            state = row.Index
            dates = zip(df.columns[::2], row[1::2])

            for (date, infected) in dates:
                data.append({
                    'state' : STATE_NAMES[STATES.index(state)],
                    'date' : date[:10],
                    'infected' : infected,
                })
        cache['data'] = data

    populations = []
    for state in STATE_NAMES:
        populations.append(db.get_statestats(state)[1])

    return render_template("game.html", state_name=session.get("state_name", ""), pops=populations)

if __name__ == "__main__":
    app.debug = True
    app.run()

