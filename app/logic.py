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
## we gonna ignore alaska and hawaii cuz cmon bro
def convert(state: str):
    # convert between the abrv and the name
    return STATE_NAMES[STATES.index(state)]
def get_adjacency():
    # URL to the adjacency map
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






def run_simulation(start_state: str, adj_map):
    # dataframe with the states as rows and cols being datetimes
    valid_states = [s for s in STATES if s in adj_map]
    pop = pd.DataFrame(index=valid_states)

    start_date = datetime(2020,1,20)
    pop[f"{start_date}_infected"] = 0.0

    def get_initial_population(state: str):
        return get_statestats(convert(state))[1]

    vulnerability_index = []
    population_density = []
    def load_state_info(state:str):
        nonlocal vulnerability_index
        nonlocal population_density
        state_info = [get_statestats(state) for state in STATE_NAMES if state]
        vulnerability_index = [s[0] for s in state_info]
        population_density = [s[2] for s in state_info]

    pop[f"{start_date}_population"] = [get_initial_population(state) for state in pop.index]

    def select_state(state: str, date):
        if state not in pop.index:
            print("Error: State name incorrect. Maybe you forgot capitalization?")
            return
        pop.loc[state, f"{date}_infected"] = 1.0  # Start with 1 person infected
        load_state_info(state)

    # takes the state to select adn then calls select state
    select_state(start_state, start_date)

    def infect(state: str, date):
        idx = STATES.index(state)
        # ill updatye this later with the regression
        return pop.loc[state, f"{date}_infected"] * (1 + ((vulnerability_index[idx]*10)/population_density[idx])) + population_density[idx]

    def spread(state: str, date, adjacency_map, inf_state):
        # Calculates infections spreading
        spread_amount = 0.0
        for neighbor in adjacency_map.get(state, []):
            if neighbor in pop.index:
                inf_neighbor = pop.loc[neighbor, f"{date}_infected"]
                if inf_neighbor == 0:
                    continue

                pop_neighbor = pop.loc[neighbor, f"{date}_population"]
                pop_state = pop.loc[state, f"{date}_population"]

                uninf_neighbor = max(0, pop_neighbor - inf_neighbor)
                uninf_state = max(0, pop_state - inf_state)

                total_uninfected = uninf_state + uninf_neighbor
                if total_uninfected > 0:

                    # update this logic later with stringency and whatever
                    chance = inf_neighbor / total_uninfected
                    # spread like 1000 people * chance
                    spread_amount += round(chance * 2000)

        return spread_amount

    def get_death_rate(state: str):
        # update this later with whaetver
        # make teh death rate a function of stringency r smtjh
        return (random()* 0.023 + 0.0015)

    def calculate_deaths(state: str, current_date):
        week_ago = current_date - timedelta(days=7)
        curr_pop = pop.loc[state, f"{current_date}_population"]

        col_week_ago = f"{week_ago}_infected"
        if col_week_ago in pop.columns:
            past_infected = pop.loc[state, col_week_ago]
            deaths = past_infected * get_death_rate(state)
            return max(0, curr_pop - deaths)
        return curr_pop

    def step(current_date, next_date, adjacency_map):
        nonlocal pop
        new_infected_col = []
        new_population_col = []

        for state in pop.index:

            # Update population based on deaths
            new_pop = round(calculate_deaths(state, current_date))
            new_population_col.append(new_pop)

            # Update infected
            base_inf = infect(state, current_date) if pop.loc[state, f"{current_date}_infected"] > 0 else 0
            spread_inf = spread(state, current_date, adjacency_map, base_inf)

            total_inf = round(base_inf + spread_inf)
            new_infected_col.append((min(total_inf, new_pop)))

        new_cols_df = pd.DataFrame({
            f"{next_date}_infected": new_infected_col,
            f"{next_date}_population": new_population_col
        }, index=pop.index)

        pop = pd.concat([pop, new_cols_df], axis=1)

    # loop params, terminates if entire us is infected
    max_iters = 156
    curr_date = start_date

    print("Running simulation...")
    for i in range(max_iters):
        next_date = curr_date + timedelta(days=7)
        step(curr_date, next_date, adj_map)

        total_infected = pop[f"{next_date}_infected"].sum()
        total_population = pop[f"{next_date}_population"].sum()

        if total_population == 0 or total_infected >= total_population * 0.999:
            print(f"THEY ALL DIED womp womp womp or maybe they all js infected so sorry")
            break

        curr_date = next_date
    return pop

if __name__ == "__main__":
    adj_map = get_adjacency()
    final_df = run_simulation("NY", adj_map)
    #print(final_df)
    print(final_df.iloc[:, [-4, -3, -2, -1]])
#print(get_statestats(convert("NY"))[1])
