# Pandemic Simulator by mangodb

## Roster:
- PM: Sarah Zou
- dev1: Joyce Lin
- dev2: Wesley Leon
- dev3: Mottaqi Abedin

## Description:
This project is an interactive, story-like Pandemic Simulator that incorporates both user data exploration and visualization to understand how different non-health factors and actions like population density, policy, and environmental and social vulnerability affect outbreaks Using Covid-19 data, the simulator has base outbreak infection and mortality rates that change based on user decisions and actions and are weighted based on correlations between the outbreak data and the factors, as well as some level of randomness. 

#### Visit our live site at [http://142.93.67.48/](http://142.93.67.48/)

## Install Guide:
Pre-requisites:
- python3 installed
- git installed

Clone and enter repo:
```
git clone git@github.com:szou0814/mangodb.git
cd mangodb
```

Create virtual environment:
```
python -m venv venv_name
```

Enter virtual environment 
(macOs & Linux):
```
source venv_name/bin/activate
```
(Windows):
```
venv_name\Scripts\activate
```

Install packages and libraries:
```
pip install -r requirements.txt
```

Exit virtual environment:
```
deactivate
```

## Launch Codes:
In terminal, access directory where project is stored and run the command:

```
cd mangodb/app
python build_db.py
python __init__.py
```
Then click the link:
```
http://127.0.0.1:5000
```

### FEATURE SPOTLIGHT
* trained a regression model using datasets in pytorch, in model.py
* prompts: prompts occur every 25 ticks (12.5 seconds) and are randomly selected, the prompts that come up depend on a state's population density and previous prompts, some choices with positive effects can fail which either negates or decreases the change on stringency/vulnerability index 
* interactive stacked line graph: click on a state name to see the # of infected/week in that state, click the state again to see a stacked line graph of the total # of infected nationally / week and how many # of infected each state contributes / week
* animations!

### KNOWN BUGS/ISSUES
* issue: no reset button after a simulation run/exit 
* no known bugs (as of yet)