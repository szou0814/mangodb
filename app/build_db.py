# mangodb: Sarah Zou, Joyce Lin, Wesley Leon, Mottaqi Abedin
# P04: Makers Makin' It, Act II -- The Seequel
# SoftDev 2026
# time spent:

#datasets we're using:
#COVID-19 CASES BY STATE-LEVEL
#https://github.com/nytimes/covid-19-data?tab=readme-ov-file
#USA COVID POLICY:
#https://github.com/OxCGRT/USA-covid-policy/tree/master
#SOCIAL VULNERABILUTY INDEX:
#https://www.atsdr.cdc.gov/place-health/php/svi/svi-data-documentation-download.html
#STATE POP, POP DENSITY, AND TRENDS (has a lot of diff attributes that might be interesting to include but not necessary, CHOPPING BLOCK):
#https://www.kaggle.com/datasets/ankithasridhar/us-state-trends-csv


import sqlite3
import csv

DB_FILE = "database.db"

def create_tbs():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute (f"CREATE TABLE IF NOT EXISTS USER(user_id TEXT PRIMARY KEY, password TEXT)")
    c.execute (f"CREATE TABLE IF NOT EXISTS STATES(state_id TEXT PRIMARY KEY, vulnerability_index FLOAT, population INTEGER, population_density FLOAT)")
    c.execute (f"CREATE TABLE IF NOT EXISTS stringency(stringency_id INTEGER PRIMARY KEY AUTOINCREMENT, state_id TEXT, date DATE, stringency_index FLOAT, FOREIGN KEY (state_id) REFERENCES states(state_id))")
    c.execute (f"CREATE TABLE IF NOT EXISTS covid_stats(stats_id INTEGER PRIMARY KEY AUTOINCREMENT, state_id TEXT, date DATE, infected INTEGER, dead INTEGER, FOREIGN KEY (state_id) REFERENCES states(state_id))")
    c.execute (f"CREATE TABLE IF NOT EXISTS runs(run_id INTEGER PRIMARY KEY AUTOINCREMENT, state_id TEXT, total_infected INTEGER, total_dead INTEGER, FOREIGN KEY (state_id) REFERENCES states(state_id))")

    db.commit()
    db.close()

def load_states():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    with open("data/SVI2020_US_COUNTY.csv", newline="") as f:
        reader = csv.DictReader(f)
        states_totpop = {}
        states_totarea = {}
        states_totsvi = {}
        states_numcounties = {}
        for row in reader:
            state_id = row["STATE"].strip() #WESLEY: all the datsets have the full state name, so change logic.py to use full name instead of abbreviations 
            try:
                vulnerability_index = float(row["RPL_THEMES"]) #rpl gives the percentile of vulnerability, spl gives the raw score but i think better to use rpl so we dont have to do additional math to normalize
                population = int(row["E_TOTPOP"]) #E means estimate, the other field is M which is the margin of error 
                area = float(row["AREA_SQMI"])
            except (ValueError, TypeError):
                continue 
            if population <= 0 or area <= 0:
                continue
            if state not in states_totpop:
                states_totpop[state_id] = 0
                states_totarea[state_id] = 0.0
                states_totsvi[state_id] = 0.0
                states_numcounties[state_id] = 0
            states_totpop[state_id] += population
            states_totarea[state_id] += area
            states_totsvi[state_id] += vulnerability_index
            states_numcounties[state_id] += 1
        for state in states_totpop:
            avg_vulnerability_index = states_totsvi[state] / states_numcounties[state]
            population_density = states_totpop[state] / states_totarea[state]
            c.execute("INSERT INTO STATES (state_id, vulnerability_index, population, population_density) VALUES (?, ?, ?, ?)", (state_id, avg_vulnerability_index, states_totpop[state], population_density))

    db.commit()
    db.close()

def format_date(date):
    #oxford stringency dataset date format: 
    #YYYY MM DD 
    return f"{date[:4]}-{date[4:6]}-{date[6:]}"

def load_stringency():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    with open("data/OxCGRT_US_latest.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            state_id = row["RegionName"]
            if not state_id:
                continue
            try:
                date = format_date(row["Date"])
                stringency_index = float(row["StringencyIndex"])
            except (ValueError, TypeError):
                continue
            c.execute("INSERT INTO stringency(state_id, date, stringency_index) VALUES (?, ?, ?)", (state_id, date, stringency_index))

    db.commit()
    db.close()

def load_covid():
    #    c.execute (f"CREATE TABLE IF NOT EXISTS covid_stats(stats_id INTEGER PRIMARY KEY AUTOINCREMENT, state_id TEXT, date DATE, infected INTEGER, dead INTEGER, 
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    with open("data/us-states.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            state_id = row["state"]
            try:
                date = row["date"]
                infected = int(row["cases"])
                dead = int(row["deaths"])
            except (ValueError, TypeError):
                continue
            c.execute("INSERT INTO covid_stats (state_id, date, infected, dead) VALUES (?, ?, ?, ?)", (state_id, date, infected, dead))

    db.commit()
    db.close()

#USER#############################################################################################
#checks if username already in db
def user_exists(username):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("SELECT * FROM user WHERE user_id = ?", (username,))
    result = c.fetchone() != None
    db.close()
    return result

#checks if username input has special characters besides _
def user_valid(username):
    for charac in username:
        if not (charac.isalnum() or charac == "_"):
            return False
    return True

#checks if password input matches password in db
def login(username, password):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("SELECT password FROM user where user_id = ?", (username,))
    pw = c.fetchone()[0]
    db.close()
    return pw == password

#checks if username is taken, is valid, and adds username and password input to db
def register(username, password):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    if (username.strip() == "" or password.strip() == ""):
        db.close()
        return "Username or password cannot be empty."
    if not user_valid(username):
        db.close()
        return "Username cannot have special characters except '_'."
    if user_exists(username):
        db.close()
        return "Username is already taken."
    c.execute("INSERT INTO user (user_id, password) VALUES (?, ?)", (username, password))
    db.commit()
    db.close()
    return "Registered"

#deletes account
def delete_acc(username):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("DELETE FROM user WHERE user_id = ?", (username,))
    c.execute("DELETE FROM blog WHERE user_id = ?", (username,))
    c.execute("DELETE FROM page WHERE user_id = ?", (username,))
    db.commit()
    db.close()
##################################################################################################
if __name__ == "__main__":
    create_tbs()
    print("Database created.")
