import pandas as pd
import urllib.request
from datetime import datetime, timedelta

STATES = ["AK", "AL", "AR", "AS", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "GU", "HI", "IA", "ID", "IL", "IN", "KS",
          "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MP", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY",
          "OH", "OK", "OR", "PA", "PR", "RI", "SC", "SD", "TN", "TX", "UM", "UT", "VA", "VI", "VT", "WA", "WI", "WV", "WY"]
## we gonna ignore alaska and hawaii cuz cmon bro

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

adj_map = get_adjacency()
# Keep states that are in adjacency map and ignore AK, HI
valid_states = [s for s in STATES if s in adj_map and s not in ["AK", "HI"]]



def run_simulation(start_state: str):
    # dataframe with the states as rows and cols being datetimes
    pop = pd.DataFrame(index=valid_states)
    
    start_date = datetime.now().date()
    pop[f"{start_date}_infected"] = 0.0
    
    def get_initial_population(state: str):
        # Populate all valid states to js have 100k pop for now
        # update this later with the acc data
        return float(100000)
        
    pop[f"{start_date}_population"] = [get_initial_population(state) for state in pop.index]
    
    def select_state(state: str, date):
        if state not in pop.index:
            print("Error: State name incorrect. Maybe you forgot capitalization?")
            return
        pop.loc[state, f"{date}_infected"] = 1.0  # Start with 1 person infected
        
    # takes the state to select adn then calls select state
    select_state(start_state, start_date)
    
    def infect(state: str, date):
        # ill updatye this later with the regression
        return pop.loc[state, f"{date}_infected"] * 1.1
        
    def spread(state: str, date, adjacency_map):
        # Calculates infections spreading
        spread_amount = 0.0
        for neighbor in adjacency_map.get(state, []):
            if neighbor in pop.index:
                inf_neighbor = pop.loc[neighbor, f"{date}_infected"]
                if inf_neighbor == 0:
                    continue
                    
                inf_state = pop.loc[state, f"{date}_infected"]
                pop_neighbor = pop.loc[neighbor, f"{date}_population"]
                pop_state = pop.loc[state, f"{date}_population"]
                
                uninf_neighbor = max(0, pop_neighbor - inf_neighbor)
                uninf_state = max(0, pop_state - inf_state)
                
                total_uninfected = uninf_state + uninf_neighbor
                if total_uninfected > 0:

                    # update this logic later with stringency and whatever
                    # same as the #infected in state/ total uninvected in both states
                    chance = inf_neighbor / total_uninfected
                    # spread like 100 people * chance
                    spread_amount += chance * 100
                    
        return spread_amount

    def get_death_rate(state: str):
        # update this later with whaetver
        # make teh death rate a function of stringency r smtjh
        return 0.02

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
            new_pop = calculate_deaths(state, current_date)
            new_population_col.append(new_pop)
            
            # Update infected
            base_inf = infect(state, current_date) if pop.loc[state, f"{current_date}_infected"] > 0 else 0
            spread_inf = spread(state, current_date, adjacency_map)
            
            total_inf = base_inf + spread_inf
            new_infected_col.append(min(total_inf, new_pop))
            
        new_cols_df = pd.DataFrame({
            f"{next_date}_infected": new_infected_col,
            f"{next_date}_population": new_population_col
        }, index=pop.index)
        
        pop = pd.concat([pop, new_cols_df], axis=1)

    # loop params, terminates if entire us is infected
    max_iters = 1000
    curr_date = start_date
    
    print("Running simulation...")
    for i in range(max_iters):
        next_date = curr_date + timedelta(days=1)
        step(curr_date, next_date, adj_map)
        
        total_infected = pop[f"{next_date}_infected"].sum()
        total_population = pop[f"{next_date}_population"].sum()
        
        if total_population == 0 or total_infected >= total_population * 0.999:
            print(f"THEY ALL DIED womp womp womp or maybe they all js infected so sorry")
            break
            
        curr_date = next_date

    return pop

if __name__ == "__main__":
    final_df = run_simulation("NY")
    print(final_df.iloc[:, [-4, -3, -2, -1]].head())
