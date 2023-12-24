import os, json
import pandas as pd
from elvanto import Services
from dotenv import load_dotenv

load_dotenv(".env")

with open('db/people.json') as f:
    ppl = json.load(f)

df_serv = pd.read_csv('db/services.csv', index_col=0)
df_team = pd.read_csv('db/teams.csv', index_col=0)

# THIS IS THE UGLY FOR LOOP VERSION OF PARSING THIS DATA
# surely there's a better way... 

team_health = {}
positions   = {}
pos_fields  = ['department_name', 'sub_department_name', 'position_name']
for row in df_team.iterrows():
    n, info = row
    info = info.to_dict()
    
    vol_id, pos_id = info['vol_id'], info['position_id']
    if vol_id not in team_health:
        team_health[vol_id] = {}
    if pos_id not in positions:
        positions[pos_id] = {field: info[field] for field in pos_fields}
    team_health[vol_id][info['serv_id']] = pos_id + "_" + info["status"]

def rename_team(id): 
    person = ppl[id]
    return f"{person['firstname']}_{person['lastname']}"

def rename_serv(id):
    """
    Returns
    -------
    {Date}_{Location}_{Which Service}
    """
    service = df_serv.loc[id]
    which = service['name'].split(" ")[0]
    loc  = str(service['location.name'])
    date = service['date'][:10]
    if 'Downtown' in loc:
        location = 'DT'
    elif 'Hamilton' in loc:
        location = 'HAM'
        which = ""
    else:
        location = loc
    
    return f"{date}_{location}_{which}"

def which_team(pos_id):
    return positions[pos_id]['department_name']

def which_subteam(pos_id):
    return positions[pos_id]['sub_department_name']

def which_role(pos_id):
    return positions[pos_id]['position_name']

df = pd.DataFrame(team_health).T

df2 = df.rename(index=rename_team, columns=rename_serv)
df2 = df2[sorted(df2.columns)]

df2_team    = df2.applymap(lambda x: which_team(x.split("_")[0]), na_action='ignore')
df2_subteam = df2.applymap(lambda x: which_subteam(x.split("_")[0]), na_action='ignore')
df2_role    = df2.applymap(lambda x: which_role(x.split("_")[0]), na_action='ignore')

import numpy as np
name_to_team = {}
for name in df2_team.index:
    their_teams = df2_team.T[name].dropna()
    unique_teams = their_teams.unique()
    unique_teams = np.delete(np.delete(unique_teams, np.where(unique_teams == 'EASTER FESTIVAL HAMITLON')), np.where(unique_teams == 'EASTER FESTIVAL DOWNTOWN'))
    
    if len(unique_teams) > 1:
        print(f"{name} is in multiple teams: {unique_teams}")
        name_to_team[name] = their_teams.value_counts().index[0]
    elif len(unique_teams) == 1:
        name_to_team[name] = unique_teams[0]
    else:
        name_to_team[name] = "EASTER FESTIVAL ONLY"
