import pandas as pd
import random as r
import urllib.request
from datetime import datetime, timedelta
from build_db import get_statestats, get_initstringency
from random import random

#kinda stupid to put them all here so feel free to move to a JSON file
#there are 15
prompts = {
    "school_closures": {
        "question": "Students and teachers are becoming sick and absent. What do you do?",
        "choices": {
            "A": {
                "label": "Close all schools",
                "stringency_change": +18,
                "svi_change": +0.02,  
            },
            "B": {
                "label": "Move to hybrid learning",
                "stringency_change": +8,
                "svi_change": +0.01,
            },
            "C": {
                "label": "Keep schools open",
                "stringency_change": -5,
                "svi_change": +0.0,
            },
        }
    },
    "mask_mandate": {
        "question": "A mask mandate is proposed. Do you support it?",
        "choices": {
            "A": {
                "label": "Enforce a statewide mask mandate",
                "stringency_change": +10,
                "svi_change": -0.01,  
            },
            "B": {
                "label": "Recommend masks but don't mandate it",
                "stringency_change": +3,
                "svi_change": +0.0,
            },
            "C": {
                "label": "Leave it to individual choice",
                "stringency_change": -8,
                "svi_change": +0.02,
            },
        }
    },
    "testing_expansion": {
        "question": "Testing is being developed but requires extensive resources. How do you allocate them?",
        "choices": {
            "A": {
                "label": "Fund free community testing centers statewide",
                "stringency_change": +5,
                "svi_change": -0.03, 
            },
            "B": {
                "label": "Expand testing only at hospitals",
                "stringency_change": +2,
                "svi_change": -0.01,
            },
            "C": {
                "label": "Rely on private testing, no state funding",
                "stringency_change": -3,
                "svi_change": +0.03, 
            },
        }
    },
    "stay_at_home": {
        "question": "Cases are rising. Your advisors recommend a stay-at-home order. Do you approve it?",
        "choices": {
            "A": {
                "label": "Issue a strict stay-at-home order",
                "stringency_change": +20,
                "svi_change": +0.02,  
            },
            "B": {
                "label": "Issue a limited order for high-risk groups only",
                "stringency_change": +8,
                "svi_change": +0.01,
            },
            "C": {
                "label": "Decline to issue any order",
                "stringency_change": -10,
                "svi_change": +0.03,
            },
        }
    },
    "healthcare_investment": {
        "question": "Hospitals are becoming too crowded. What's your response?",
        "choices": {
            "A": {
                "label": "Emergency fund community health clinics",
                "stringency_change": +3,
                "svi_change": -0.03,  
            },
            "B": {
                "label": "Redirect funds to ICU expansion only",
                "stringency_change": +2,
                "svi_change": -0.02,
            },
            "C": {
                "label": "No additional healthcare spending",
                "stringency_change": 0,
                "svi_change": +0.03,
            },
        }
    },
    "travel_restrictions": {
        "question": "Neighboring states are seeing rising infections. Do you restrict travel?", #maybe can do smth cool w the adjacency
        "choices": {
            "A": {
                "label": "Ban non-essential interstate travel",
                "stringency_change": +15,
                "svi_change": +0.01,
            },
            "B": {
                "label": "Require quarantine for travelers",
                "stringency_change": +7,
                "svi_change": +0.0,
            },
            "C": {
                "label": "No travel restrictions",
                "stringency_change": -5,
                "svi_change": +0.01,
            },
        }
    },
    "vaccine_accessibility": {
        "question": "A vaccine has been developled. How do you prioritize distributing it?",
        "choices": {
            "A": {
                "label": "Prioritize healthcare workers and the elderly",
                "stringency_change": -5,
                "svi_change": -0.04, 
            },
            "B": {
            "label": "Distribute evenly across all age groups",
            "stringency_change": 0,
            "svi_change": +0.01,
            },
            "C": {
                "label": "Let capitalism decide who gets the vaccine",
                "stringency_change": -8,
                "svi_change": +0.03,
            },
        }
    },
    "restaurant_closures": {
        "question": "Large groups of people are being infected due to indoor dining. What do you do?",
        "choices": {
            "A": {
                "label": "Close all indoor dining immediately",
                "stringency_change": +12,
                "svi_change": +0.02,
            },
            "B": {
                "label": "Reduce indoor capacity to 25%",
                "stringency_change": +6,
                "svi_change": +0.01,
            },
            "C": {
                "label": "Issue health guidelines but keep dining open",
                "stringency_change": -2,
                "svi_change": +0.01,
            },
        }
    },
    "essential_worker_protections": {
        "question": "Essential workers are getting sick. How do you respond?",
        "choices": {
            "A": {
                "label": "Mandate hazard pay for all essential workers",
                "stringency_change": +8,
                "svi_change": -0.04,
            },
            "B": {
                "label": "Issue guidelines but leave enforcement to employers",
                "stringency_change": +2,
                "svi_change": -0.01,
            },
            "C": {
                "label": "Take no additional action",
                "stringency_change": -2,
                "svi_change": +0.03,
            },
        }
    },
    "misinformation_response": {
        "question": "Misinformation about the outbreak is spreading rapidly online. How do you respond?",
        "choices": {
            "A": {
                "label": "Launch a state-funded public health media campaign",
                "stringency_change": +3,
                "svi_change": -0.03,
            },
            "B": {
                "label": "Partner with social platforms to flag misinformation",
                "stringency_change": +1,
                "svi_change": -0.01,
            },
            "C": {
                "label": "Take no official stance on misinformation",
                "stringency_change": -2,
                "svi_change": +0.02,
            },
        }
    },
    "unemployment_benefits": {
        "question": "Unemployment is rising due to closures. Do you expand benefits?",
        "choices": {
            "A": {
                "label": "Expand benefits to $600/week",
                "stringency_change": +3,
                "svi_change": -0.04,
            },
            "B": {
                "label": "Slightly expand benefits based on income",
                "stringency_change": +1,
                "svi_change": -0.02,
            },
            "C": {
                "label": "No change to unemployment policy",
                "stringency_change": -1,
                "svi_change": +0.03,
            },
        }
    },
    "outdoor_gathering_limits": {
        "question": "Summer is coming and people are starting to go outside for parties. Do you restrict outdoor events?",
        "choices": {
            "A": {
                "label": "Ban all outdoor gatherings over 10 people",
                "stringency_change": +10,
                "svi_change": +0.01,
            },
            "B": {
                "label": "Cap outdoor gatherings at 50 with distancing requirements",
                "stringency_change": +4,
                "svi_change": +0.0,
            },
            "C": {
                "label": "No outdoor gathering restrictions",
                "stringency_change": -5,
                "svi_change": +0.02,
            },
        }
    },
    "heat_wave": {
        "question": "A heat wave is forcing people to choose between COVID exposure and cooling. How do you respond?",
        "choices": {
            "A": {
                "label": "Open state-funded cooling centers with COVID safety protocols",
                "stringency_change": +6,
                "svi_change": -0.04,
            },
            "B": {
                "label": "Issue heat safety guidelines alongside existing COVID advice",
                "stringency_change": +2,
                "svi_change": -0.01,
            },
            "C": {
                "label": "Let them thug it out",
                "stringency_change": 0,
                "svi_change": +0.03,
            },
        }
    },
    "industrial_pollution": {
        "question": "Factories near low-income communities are linked to higher COVID mortality rates due to respiratory damage. Do you act?",
        "choices": {
            "A": {
                "label": "Temporarily shut down highest-polluting facilities near vulnerable communities",
                "stringency_change": +9,
                "svi_change": -0.04,
            },
            "B": {
                "label": "Issue emissions reduction orders but allow continued operation",
                "stringency_change": +4,
                "svi_change": -0.02,
            },
            "C": {
                "label": "No additional restrictions on industrial operations",
                "stringency_change": -2,
                "svi_change": +0.04,
            },
        }
    },
    "power_grid_failure": {
        "question": "Extreme weather has caused blackouts, disrupting cold storage for vaccines and medical equipment. What do you prioritize?",
        "choices": {
            "A": {
                "label": "Redirect emergency power to medical facilities and vaccine storage first",
                "stringency_change": +6,
                "svi_change": -0.03,
            },
            "B": {
                "label": "Distribute power evenly across all necessary infrastructure",
                "stringency_change": +3,
                "svi_change": -0.01,
            },
            "C": {
                "label": "Leave it to utility companies",
                "stringency_change": -1,
                "svi_change": +0.03,
            },
        }
    },
}
prompt_reqs = {
    "vaccine_accessibility": ["testing_expansion", "healthcare_investment"],
    "unemployment_benefits": ["stay_at_home", "restaurant_closures"],
    "power_grid_failure": ["heat_wave"],
    "outdoor_gathering_limits": ["stay_at_home", "mask_mandate"],
}   
high_dens = {
    "restaurant_closures", "misinformation_response"
    }
low_dens = {
    "industrial_pollution",
}
can_fail = {
    ("testing_expansion", "A"), ("vaccine_accessibility", "A"), ("misinformation_response", "A"), ("mask_mandate", "A"), ("essential_worker_protections", "A"), ("unemployment_benefits", "A"), ("healthcare_investment", "A"), ("heat_wave", "A"),
}

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

def show_prompt(tick):
    return tick > 0 and tick % 8 == 0

def get_prompt(tick, state, dens, stringency, svi, seen_prompts):
    if not show_prompt(tick): return None
    poss = []
    for key, prompt_dict in prompts.items():
        if key in seen_prompts: continue
        if key in high_dens and dens < 200: continue 
        if key in low_dens and dens > 150: continue
        if key in prompt_reqs: if not any(p in seen_prompts for p in prompt_reqs[key]): continue
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

    #HI THIS IS WHAT I WROTE
    curr_stringency = stringency_index[STATES.index(start_state)] if stringency_index else 50.0
    curr_svi = vulnerabilty_index[STATES.index(start_state)] if vulnerability_index else 0.5
    start_density = populaton_density[STATES.index(start_state)] if population_density else 100.0
    seen_prompts = set()
    pending_prompts = []
    #THIS IS THE END OF WHAT I WROTE
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

        #HI MORE OF WHAT I WROTE
        result = get_prompt(i, start_state, start_density, curr_stringency, curr_svi, seen_prompts)
        if result:
            prompt, prompt_dict = result
            seen_prompts.add(prompt)
            pending_prompts.append({ "tick": i, "date": str(next_date.date()), "key": prompt, "prompt": prompt_dict})
        #END OF WHAT I WROTE
        curr_date = next_date
    return pop, pending_prompts

if __name__ == "__main__":
    from model import get_models
    import os
    
    # i need ts cuz its ugly
    pd.options.display.float_format = '{:.0f}'.format
    
    models = get_models()  
    adj_map = get_adjacency()
    
    final_df = run_simulation("NY", adj_map, covid_models=models)
    print(final_df.iloc[:, -6:])
