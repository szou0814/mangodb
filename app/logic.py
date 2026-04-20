import pandas as pd
import random as r
import urllib.request
from datetime import datetime, timedelta
from build_db import get_statestats, get_initstringency
from random import random

import json
import os

_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_dir, 'static', 'prompts.json'), 'r') as _f:
    _data = json.load(_f)

prompts = _data["prompts"]
prompt_reqs = _data["prompt_reqs"]
high_dens = set(_data["high_dens"])
low_dens = set(_data["low_dens"])
can_fail = set(tuple(x) for x in _data["can_fail"])

STATES = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY",
          "LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND",
          "OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"]
STATE_NAMES = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho",
    "Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri",
    "Montana","Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon",
    "Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington","West Virginia",
    "Wisconsin","Wyoming"]

def convert(state: str):
    return STATE_NAMES[STATES.index(state)]

def limit(stringency, svi):
    return (max(10, min(90, stringency)), max(0.05, min(0.95, svi)))

def is_prompt_tick(tick):
    return tick > 0 and tick % 8 == 0

def get_prompt(tick, state, dens, stringency, svi, seen_prompts):
    poss = []
    for key, prompt_dict in prompts.items():
        if key in seen_prompts: continue
        if key in high_dens and dens < 200: continue
        if key in low_dens and dens > 150: continue
        if key in prompt_reqs:
            if not any(p in seen_prompts for p in prompt_reqs[key]): continue
        choiceValid = False
        for choice in prompt_dict["choices"].values():
            newStringency = stringency + choice["stringency_change"]
            newSvi = svi + choice["svi_change"]
            if (10 < newStringency < 90 and 0.05 < newSvi < 0.95):
                choiceValid = True
                break
        if not choiceValid: continue
        poss.append(key)
    if not poss: return None
    prompt = r.choice(poss)
    return prompt, prompts[prompt]

def handle_choice(prompt, choice, stringency, svi, seen_prompts):
    picked = prompts[prompt]["choices"][choice]
    stringencyChange = picked["stringency_change"]
    sviChange = picked["svi_change"]
    failed = False
    msg = ""
    if (prompt, choice) in can_fail:
        if r.random() < 0.20:
            failed = True
            stringencyChange = stringencyChange // 2
            sviChange = -(sviChange * 0.5)
            msg = "Your policy was not well-received by the public and had limited effects."
    newStringency, newSvi = limit(stringency + stringencyChange, svi + sviChange)
    return newStringency, newSvi, failed, message


def get_adjacency():
    url = "https://gist.githubusercontent.com/longbai/44f446bc907ada728948e4c15aca252e/raw"
    with urllib.request.urlopen(url) as response:
        content = response.read().decode('utf-8')

    adj_map = {}
    for line in content.splitlines():
        if line and not line.startswith('#'):
            parts = line.strip().split(',')
            state = parts[0]
            neighbors = parts[1:] if len(parts) > 1 else []
            adj_map[state] = neighbors
    return adj_map

class Simulation:
    def __init__(self, start_state: str, adj_map, covid_models=None):
        self.start_state = start_state
        self.adj_map = adj_map
        self.covid_models = covid_models

        self.pop = pd.DataFrame(index=STATES)
        self.start_date = datetime(2020, 1, 20)
        self.pop[f"{self.start_date}_infected"] = 0.0
        self.pop[f"{self.start_date}_resistant"] = 0.0

        self.vulnerability_index = []
        self.population_density = []
        self.stringency_index = []

        self.pop[f"{self.start_date}_population"] = [self.get_initial_population(state) for state in self.pop.index]
        self.select_state(start_state, self.start_date)

        self.curr_stringency = self.stringency_index[STATES.index(start_state)] if self.stringency_index else 50.0
        self.curr_svi = self.vulnerability_index[STATES.index(start_state)] if self.vulnerability_index else 0.5
        self.start_density = self.population_density[STATES.index(start_state)] if self.population_density else 100.0

        self.seen_prompts = set()
        self.pending_prompts = []

        self.tick_count = 0
        self.curr_date = self.start_date
        print("Simulation initialized.")

    def get_initial_population(self, state: str):
        return get_statestats(convert(state))[1]

    def load_state_info(self, state: str):
        state_info = [get_statestats(s) for s in STATE_NAMES if s]
        str_info = [get_initstringency(s) for s in STATE_NAMES if s]
        self.vulnerability_index = [s[0] for s in state_info]
        self.population_density = [s[2] for s in state_info]
        self.stringency_index = [s[0] if s else 0.0 for s in str_info]

    def select_state(self, state: str, date):
        if state not in self.pop.index:
            print("Error: State name incorrect. Maybe you forgot capitalization?")
            return
        self.pop.loc[state, f"{date}_infected"] = 1.0
        self.load_state_info(state)

    def infect(self, state: str, date):
        idx = STATES.index(state)
        curr_inf = self.pop.loc[state, f"{date}_infected"]
        curr_pop = self.pop.loc[state, f"{date}_population"]
        curr_res = self.pop.loc[state, f"{date}_resistant"]
        eff_pop = max(0, curr_pop - curr_res)

        if self.covid_models is not None:
             new_infections = self.covid_models.predict_new_infections(eff_pop, self.population_density[idx], curr_inf, self.vulnerability_index[idx], self.stringency_index[idx])
             return curr_inf + new_infections
        return curr_inf * (1 + ((self.vulnerability_index[idx]*10)/self.population_density[idx])) + self.population_density[idx]

    def spread(self, state: str, date, inf_state):
        spread_amount = 0.0
        pop_state = self.pop.loc[state, f"{date}_population"]
        res_state = self.pop.loc[state, f"{date}_resistant"]
        eff_pop_state = max(0, pop_state - res_state)
        susceptible = max(0, eff_pop_state - inf_state)

        for neighbor in self.adj_map.get(state, []):
            if neighbor not in self.pop.index:
                continue

            inf_neighbor = self.pop.loc[neighbor, f"{date}_infected"]
            if inf_neighbor <= 0:
                continue

            pop_neighbor = self.pop.loc[neighbor, f"{date}_population"]
            res_neighbor = self.pop.loc[neighbor, f"{date}_resistant"]
            eff_pop_neighbor = max(0, pop_neighbor - res_neighbor)
            susceptible_neighbor = max(0, eff_pop_neighbor - inf_neighbor)

            total_susceptible = susceptible + susceptible_neighbor
            if total_susceptible == 0:
                continue

            combined_eff_pop = eff_pop_state + eff_pop_neighbor
            idx = STATES.index(state)

            if self.covid_models is not None:
                total_new = self.covid_models.predict_new_infections(combined_eff_pop, self.population_density[idx], inf_neighbor, self.vulnerability_index[idx], self.stringency_index[idx])
            else:
                total_new = inf_neighbor * ((self.vulnerability_index[idx]*10)/self.population_density[idx]) + self.population_density[idx]

            share_to_state = susceptible / total_susceptible
            spread_amount += total_new * share_to_state
        return min(susceptible, spread_amount * 0.01)

    def get_deaths_for_state(self, state: str, curr_pop, past_infected):
        idx = STATES.index(state)
        if self.covid_models is not None:
            return self.covid_models.predict_deaths(curr_pop, self.population_density[idx], past_infected, self.vulnerability_index[idx], self.stringency_index[idx])
        return past_infected * (random() * 0.023 + 0.0015)

    def calculate_deaths_and_resistance(self, state: str, current_date):
        week_ago = current_date - timedelta(days=7)
        curr_pop = self.pop.loc[state, f"{current_date}_population"]
        curr_res = self.pop.loc[state, f"{current_date}_resistant"]

        col_week_ago = f"{week_ago}_infected"
        if col_week_ago in self.pop.columns:
            past_infected = self.pop.loc[state, col_week_ago]
            deaths = self.get_deaths_for_state(state, curr_pop, past_infected)

            survivors = max(0, past_infected - deaths)
            new_pop = max(0, curr_pop - deaths)
            new_res = min(new_pop, round(curr_res + survivors / 2))
            return new_pop, new_res, survivors / 2

        return curr_pop, curr_res, 0

    def step(self, current_date, next_date):
        new_infected_col = []
        new_population_col = []
        new_resistant_col = []

        for state in self.pop.index:
            new_pop, new_res, resolved_infections = self.calculate_deaths_and_resistance(state, current_date)
            new_population_col.append(new_pop)
            new_resistant_col.append(new_res)

            base_inf = self.infect(state, current_date) if self.pop.loc[state, f"{current_date}_infected"] > 0 else 0
            spread_inf = self.spread(state, current_date, base_inf)

            total_inf = round(base_inf + spread_inf - resolved_infections)
            new_infected_col.append(max(0, min(total_inf, new_pop - new_res)))

        new_cols_df = pd.DataFrame({
            f"{next_date}_infected": new_infected_col,
            f"{next_date}_resistant": new_resistant_col,
            f"{next_date}_population": new_population_col
        }, index=self.pop.index)

        self.pop = pd.concat([self.pop, new_cols_df], axis=1)

    def tick(self):
        next_date = self.curr_date + timedelta(days=7)
        self.step(self.curr_date, next_date)

        total_infected = self.pop[f"{next_date}_infected"].sum()
        total_resistant = self.pop[f"{next_date}_resistant"].sum()
        total_population = self.pop[f"{next_date}_population"].sum()

        if total_population == 0 or (total_infected + total_resistant) >= total_population * 0.999:
            print("THEY ALL DIED womp womp womp or maybe they all js infected so sorry")

        result = None if not is_prompt_tick(self.tick_count) else get_prompt(self.tick_count, self.start_state, self.start_density, self.curr_stringency, self.curr_svi, self.seen_prompts)
        if result:
            prompt, prompt_dict = result
            self.seen_prompts.add(prompt)
            self.pending_prompts.append({ "tick": self.tick_count, "date": str(next_date.date()), "key": prompt, "prompt": prompt_dict})

        self.curr_date = next_date
        self.tick_count += 1

        return self.pop

if __name__ == "__main__":
    from model import get_models
    import os


    models = get_models()
    adj_map = get_adjacency()

    sim = Simulation("NY", adj_map, covid_models=models)
    for _ in range(152):
        final_df, next_cols = sim.tick()

    print(final_df.iloc[:, -6:])
