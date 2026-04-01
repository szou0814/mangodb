import pandas as pd

STATES = ["AK", "AL", "AR", "AS", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "GU", "HI", "IA", "ID", "IL", "IN", "KS",
          "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MP", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY",
          "OH", "OK", "OR", "PA", "PR", "RI", "SC", "SD", "TN", "TX", "UM", "UT", "VA", "VI", "VT", "WA", "WI", "WV", "WY"]
## we gonna ignore alaska and hawaii cuz cmon bro
##https://gist.github.com/longbai/44f446bc907ada728948e4c15aca252e
pop = pd.DataFrame(index = STATES)
pop.insert(pop.shape[1], "infected", [0]*48)
infected_states =[]
def select_state(state: str):
    # make sure this matches the states array.
    if state not in STATES:
        print("Error: State name incorrect. Maybe you forgot capitalization?")
        return
    infected_states.append(state)
select_state("NY")
print(infected)
def get_adjacency():
    return
def spread():
    return
def step(date):
    pop.insert(pop.shape[1],date, [0]*48)
    for state in infected_states:
        return
