import sys
import os
import pandas as pd
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.model import get_models
from app.logic import run_simulation, get_adjacency

def test_growth():
    models = get_models()
    adj_map = get_adjacency()
    
    state = "NY"
    print(f"Running simulation utilizing logic.py (Testing {state})...")
    
    pd.options.display.float_format = '{:.0f}'.format
    
    # Run the full actual logic pipeline
    df = run_simulation(state, adj_map, covid_models=models)
    
    ny_data = df.loc[state]
    
    print(f"\n--- Output Data for {state} ---")
    
    dates = []
    for col in df.columns:
        date_str = col.split("_")[0]
        if date_str not in dates:
            dates.append(date_str)
    
    total_deaths = 0
    for i, date in enumerate(dates):
        inf = ny_data[f"{date}_infected"]
        pop = ny_data[f"{date}_population"]
        res = ny_data[f"{date}_resistant"]
        
        if i == 0:
            past_pop = pop
            
        new_deaths = max(0, past_pop - pop)
        total_deaths += new_deaths
        past_pop = pop
        
        # Taking just the first part of date string (YYYY-MM-DD)
        formatted_date = date.split()[0]
            
        print(f"Week {i:02d} ({formatted_date}): Active Infected: {inf:,.0f} | Total Resistant: {res:,.0f} | Weekly Deaths: {new_deaths:,.0f} | Surviving Pop: {pop:,.0f}")

    print(f"\n--- Final Statistics for {state} ---")
    final_date = dates[-1]
    final_inf = ny_data[f"{final_date}_infected"]
    final_res = ny_data[f"{final_date}_resistant"]
    final_pop = ny_data[f"{final_date}_population"]
    
    print(f"Final Active Infected: {final_inf:,.0f}")
    print(f"Final Total Resistant: {final_res:,.0f}")
    print(f"Final Total Population: {final_pop:,.0f}")
    print(f"Total Deaths: {total_deaths:,.0f}")

if __name__ == "__main__":
    test_growth()
