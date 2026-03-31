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
    tb_names = ["user", "states", "stringency", "covid_stats", "runs"] #runs is CHOPPING BLOCk]
    for tb in tb_names:
        c.execute(f"DROP TABLE IF EXISTS {tb}")

    c.execute (f"CREATE TABLE USER(user_id TEXT PRIMARY KEY, password TEXT)")
    c.execute (f"CREATE TABLE STATES(state_id TEXT PRIMARY KEY, vulnerability_index INTEGER, population INTEGER, population_density FLOAT)")
    c.execute (f"CREATE TABLE stringency(stringency_id INTEGER PRIMARY KEY AUTOINCREMENT, state_id TEXT, date DATE, stringency_index FLOAT, FOREIGN KEY (statesid) REFERENCES states(state_id))")
    c.execute (f"CREATE TABLE covid_stats(stats_id INTEGER PRIMARY KEY AUTOINCREMENT, state_id TEXT, date DATE, infected INTEGER, dead INTEGER, FOREIGN KEY (state_id) REFERENCES states(state_id))")
    c.execute (f"CREATE TABLE runs(run_id INTEGER PRIMARY KEY AUTOINCREMENT, state_id TEXT, total_infected INTEGER, total_dead INTEGER, FOREIGN_KEY(state_id) REFERENCES states(state_id))")

    db.commit()
    db.close()

if __name__ == "__main__":
    create_tbs()
    print("Database created.")