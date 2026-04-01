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
    c.execute (f"CREATE TABLE IF NOT EXISTS STATES(state_id TEXT PRIMARY KEY, vulnerability_index INTEGER, population INTEGER, population_density FLOAT)")
    c.execute (f"CREATE TABLE IF NOT EXISTS stringency(stringency_id INTEGER PRIMARY KEY AUTOINCREMENT, state_id TEXT, date DATE, stringency_index FLOAT, FOREIGN KEY (statesid) REFERENCES states(state_id))")
    c.execute (f"CREATE TABLE IF NOT EXISTS covid_stats(stats_id INTEGER PRIMARY KEY AUTOINCREMENT, state_id TEXT, date DATE, infected INTEGER, dead INTEGER, FOREIGN KEY (state_id) REFERENCES states(state_id))")
    c.execute (f"CREATE TABLE IF NOT EXISTS runs(run_id INTEGER PRIMARY KEY AUTOINCREMENT, state_id TEXT, total_infected INTEGER, total_dead INTEGER, FOREIGN_KEY(state_id) REFERENCES states(state_id))")

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
