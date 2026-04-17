import pandas as pd
import urllib.request
from datetime import datetime, timedelta
from build_db import get_statestats, get_initstringency
from random import random

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

def run_simulation(start_state: str, adj_map, covid_models=None):
    pop = pd.DataFrame(index=STATES)

    start_date = datetime(2020,1,20)
    pop[f"{start_date}_infected"] = 0.0
    pop[f"{start_date}_resistant"] = 0.0

    def get_initial_population(state: str):
        return get_statestats(convert(state))[1]

    vulnerability_index = []
    population_density = []
    stringency_index = []
    
    def load_state_info(state:str):
        nonlocal vulnerability_index
        nonlocal population_density
        nonlocal stringency_index
        state_info = [get_statestats(state) for state in STATE_NAMES if state]
        str_info = [get_initstringency(state) for state in STATE_NAMES if state]
        vulnerability_index = [s[0] for s in state_info]
        population_density = [s[2] for s in state_info]
        stringency_index = [s[0] if s else 0.0 for s in str_info]

    pop[f"{start_date}_population"] = [get_initial_population(state) for state in pop.index]

    def select_state(state: str, date):
        if state not in pop.index:
            print("Error: State name incorrect. Maybe you forgot capitalization?")
            return
        pop.loc[state, f"{date}_infected"] = 1.0
        load_state_info(state)

    select_state(start_state, start_date)

    def infect(state: str, date):
        idx = STATES.index(state)
        curr_inf = pop.loc[state, f"{date}_infected"]
        curr_pop = pop.loc[state, f"{date}_population"]
        curr_res = pop.loc[state, f"{date}_resistant"]
        eff_pop = max(0, curr_pop - curr_res)
        
        if covid_models is not None:
             new_infections = covid_models.predict_new_infections(eff_pop, population_density[idx], curr_inf, vulnerability_index[idx], stringency_index[idx])
             return curr_inf + new_infections
        return curr_inf * (1 + ((vulnerability_index[idx]*10)/population_density[idx])) + population_density[idx]

    def spread(state: str, date, adjacency_map, inf_state):
        spread_amount = 0.0
        pop_state = pop.loc[state, f"{date}_population"]
        res_state = pop.loc[state, f"{date}_resistant"]
        eff_pop_state = max(0, pop_state - res_state)
        susceptible = max(0, eff_pop_state - inf_state)

        for neighbor in adjacency_map.get(state, []):
            if neighbor not in pop.index:
                continue

            inf_neighbor = pop.loc[neighbor, f"{date}_infected"]
            if inf_neighbor <= 0:
                continue

            pop_neighbor = pop.loc[neighbor, f"{date}_population"]
            res_neighbor = pop.loc[neighbor, f"{date}_resistant"]
            eff_pop_neighbor = max(0, pop_neighbor - res_neighbor)
            susceptible_neighbor = max(0, eff_pop_neighbor - inf_neighbor)

            total_susceptible = susceptible + susceptible_neighbor
            if total_susceptible == 0:
                continue

            combined_eff_pop = eff_pop_state + eff_pop_neighbor
            idx = STATES.index(state)

            if covid_models is not None:
                total_new = covid_models.predict_new_infections(combined_eff_pop, population_density[idx], inf_neighbor, vulnerability_index[idx], stringency_index[idx])
            else:
                total_new = inf_neighbor * ((vulnerability_index[idx]*10)/population_density[idx]) + population_density[idx]

            share_to_state = susceptible / total_susceptible
            spread_amount += total_new * share_to_state
        return min(susceptible, spread_amount * 0.01)
    def get_deaths_for_state(state: str, curr_pop, past_infected):
        idx = STATES.index(state)
        if covid_models is not None:
            return covid_models.predict_deaths(curr_pop, population_density[idx], past_infected, vulnerability_index[idx], stringency_index[idx])
        return past_infected * (random() * 0.023 + 0.0015)

    def calculate_deaths_and_resistance(state: str, current_date):
        week_ago = current_date - timedelta(days=7)
        curr_pop = pop.loc[state, f"{current_date}_population"]
        curr_res = pop.loc[state, f"{current_date}_resistant"]

        col_week_ago = f"{week_ago}_infected"
        if col_week_ago in pop.columns:
            past_infected = pop.loc[state, col_week_ago]
            deaths = get_deaths_for_state(state, curr_pop, past_infected)
                
            survivors = max(0, past_infected - deaths)
            new_pop = max(0, curr_pop - deaths)
            new_res = min(new_pop, round(curr_res + survivors / 2))
            return new_pop, new_res, survivors / 2
            
        return curr_pop, curr_res, 0

    def step(current_date, next_date, adjacency_map):
        nonlocal pop
        new_infected_col = []
        new_population_col = []
        new_resistant_col = []

        for state in pop.index:
            new_pop, new_res, resolved_infections = calculate_deaths_and_resistance(state, current_date)
            new_population_col.append(new_pop)
            new_resistant_col.append(new_res)

            base_inf = infect(state, current_date) if pop.loc[state, f"{current_date}_infected"] > 0 else 0
            spread_inf = spread(state, current_date, adjacency_map, base_inf)

            total_inf = round(base_inf + spread_inf - resolved_infections)
            new_infected_col.append(max(0, min(total_inf, new_pop - new_res)))

        new_cols_df = pd.DataFrame({
            f"{next_date}_infected": new_infected_col,
            f"{next_date}_resistant": new_resistant_col,
            f"{next_date}_population": new_population_col
        }, index=pop.index)

        pop = pd.concat([pop, new_cols_df], axis=1)

    max_iters = 156
    curr_date = start_date

    print("Running simulation...")
    for i in range(max_iters):
        next_date = curr_date + timedelta(days=7)
        step(curr_date, next_date, adj_map)

        total_infected = pop[f"{next_date}_infected"].sum()
        total_resistant = pop[f"{next_date}_resistant"].sum()
        total_population = pop[f"{next_date}_population"].sum()

        if total_population == 0 or (total_infected + total_resistant) >= total_population * 0.999:
            print("THEY ALL DIED womp womp womp or maybe they all js infected so sorry")
            break

        curr_date = next_date
    return pop

if __name__ == "__main__":
    from model import get_models
    import os
    
    # i need ts cuz its ugly
    pd.options.display.float_format = '{:.0f}'.format
    
    models = get_models()  
    adj_map = get_adjacency()
    
    final_df = run_simulation("NY", adj_map, covid_models=models)
    print(final_df.iloc[:, -6:])
