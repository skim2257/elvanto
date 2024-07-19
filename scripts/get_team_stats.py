import os, json
import pandas as pd
import numpy as np
from elvanto import Services
from dotenv import load_dotenv
from tqdm.auto import tqdm
import ast
import datetime as dt

today = dt.datetime.today().strftime("%Y%m%d-%H%M%p%Z")

load_dotenv(".env")

with open('db/people.json') as f:
    ppl = json.load(f)

db_serv = pd.read_csv('db/services.csv', index_col=0)
db_team = pd.read_csv('db/teams.csv', index_col=0)

# THIS IS THE UGLY FOR LOOP VERSION OF PARSING THIS DATA
# surely there's a better way... 

team_health = {}
positions   = {}
pos_fields  = ['department_name', 'sub_department_name', 'position_name']
for row in db_team.iterrows():
    n, info = row
    info = info.to_dict()
    
    vol_id, pos_id = info['vol_id'], info['position_id']
    if vol_id not in team_health:
        team_health[vol_id] = {}
    if pos_id not in positions:
        positions[pos_id] = {field: info[field] for field in pos_fields}
    team_health[vol_id][info['serv_id']] = pos_id + "_" + info["status"]

df = pd.DataFrame(team_health).T

teams = {'Hosting': 'Hosting Teams_Hosting', 
        'Hospitality': 'Hosting Teams_Hospitality', 
        'Cafe': 'Hosting Teams_Cafe', 
        'Kids': 'C3 Kids', 
        'Worship': 'Worship Team', 
        'Muscle': 'Muscle Team', 
        'Live Video': 'Creative_Live Video', 
        'Capture': 'Creative_Capture', 
        'Lights': 'Production_Lights', 
        'Screens': 'Production_Screens', 
        'Sound': 'Production_Sound', 
        'Service Production': 'Production_Service Production', 
        'Digital': 'Digital Team',
        'Live Lobby Host': 'Creative_Live Lobby'}

def parse_service(id, only_sunday=True):
    """
    Parameters
    ----------
    only_sunday: bool
        if True, only return sunday services
    """
    sunday_ids = ["4e5f5d79-b1b7-448a-b29e-36a0560e3509", # idk but it used to be there lol... easter?
                  "76e73d4a-36c3-4d16-8f24-f90da02e530f", # midtown
                  "3e965332-46fe-4278-afc1-ee6c7c5cea08", # hamilton
                  "b602936d-1180-402d-9f0d-e389c10b0338"] # downtown
    service = db_serv.loc[id]

    type_id = service['service_type.id']
    if only_sunday and type_id not in sunday_ids:
        return "", "", None, ""

    loc  = str(service['location.name'])
    name = str(service['name'])
    date = service['date'][:10]
    return id, loc, date, name

def filter_loc(id, location: str):
    """
    Parameters
    ----------
    location: str
        'Downtown' or 'Hamilton'
    
    Returns
    -------
    True if matching the location they're looking for
    """
    _, loc, _, _ = parse_service(id)

    return location in loc

def rename_team_member(id): 
    person = ppl[id]
    return f"{person['firstname']}_{person['lastname']}"

def rename_serv(id):
    """
    Returns
    -------
    {Date}_{Location}
    """
    _, loc, date, name = parse_service(id)

    if 'Downtown' in loc:
        location = 'DT'
    elif 'Hamilton' in loc:
        location = 'HAM'
    elif 'Midtown' in loc:
        location = "MT"
    else:
        location = loc
    
    return f"{date}_{location}"#_{id}"#_{name}"

def which_team(pos_id):
    return positions[pos_id]['department_name']

def which_subteam(pos_id):
    return positions[pos_id]['sub_department_name']

def which_role(pos_id):
    return positions[pos_id]['position_name']

def which_custom(pos_id, teams=teams):
    team_subteam = which_team(pos_id) + "_" + which_subteam(pos_id)
    for team in teams:
        if teams[team] in team_subteam:
            return team
    return team_subteam

def reduce_sunday(row):
    # print(row.values)
    teams = row.dropna().unique()
    if len(teams) == 1:
        return teams[0]
    elif len(teams) < 1:
        return np.nan
    else: # if serving on multiple teams
        print('\n SERVING TWICE:', row.name, teams)
        return str(teams)
    
def num_to_digits(num):
    return str(num).zfill(2)

dt_ids = [x for x in df.columns if filter_loc(x, 'Downtown')]
ham_ids = [x for x in df.columns if filter_loc(x, 'Hamilton')]
mt_ids = [x for x in df.columns if filter_loc(x, 'Midtown')]
df_dt  = df[dt_ids].rename(index=rename_team_member, columns=rename_serv)
df_ham = df[ham_ids].rename(index=rename_team_member, columns=rename_serv)
df_mt  = df[mt_ids].rename(index=rename_team_member, columns=rename_serv)

save_dir  = "exports/team_health"
locations = ["Downtown", "Hamilton", "Midtown"]


for n, df_loc in enumerate([df_dt, df_ham, df_mt]):
    df_team    = df_loc.applymap(lambda x: which_team(x.split("_")[0])+"_"+x.split("_")[1], na_action='ignore')
    df_subteam = df_loc.applymap(lambda x: which_subteam(x.split("_")[0])+"_"+x.split("_")[1], na_action='ignore')
    df_role    = df_loc.applymap(lambda x: which_role(x.split("_")[0])+"_"+x.split("_")[1], na_action='ignore')
    df_custom  = df_loc.applymap(lambda x: which_custom(x.split("_")[0])+"_"+x.split("_")[1], na_action='ignore')

    # df_confirm is NOT declined, not necessarily confirmed. 
    # Since there are lots of team members who don't confirm and still show up, we'll assume those as accepts/confirms as well.
    df_confirm = df_custom.applymap(lambda x: x.split("_")[0] if x.split("_")[1] != "Declined" else np.nan, na_action='ignore')
    df_decline = df_custom.applymap(lambda x: x.split("_")[0] if x.split("_")[1] == "Declined" else np.nan, na_action='ignore')

    df_confirm_unique_teams = pd.Series(df_confirm.to_numpy().flatten()).dropna().unique()
    df_decline_unique_teams = pd.Series(df_decline.to_numpy().flatten()).dropna().unique()

    # merge duplicate sundays (1st vs 2+3rd services) for DT
    sundays = sorted(set([i.split("_")[0] for i in df_confirm.columns]))
    df_confirm_weekly             = pd.DataFrame(index=df_confirm.index, columns=sundays)
    df_confirm_weekly_counts      = pd.DataFrame(index=df_confirm_unique_teams)
    # weekly parsing
    for sunday in tqdm(sundays):
        df_sundays                = df_confirm[[i for i in df_confirm.columns if sunday in i]]
        df_confirm_weekly[sunday] = df_sundays.apply(reduce_sunday, axis=1)
        df_confirm_weekly_counts[sunday]  = df_confirm_weekly[sunday].value_counts()
    
    df_confirm_monthly_counts     = pd.DataFrame(index=df_confirm_unique_teams)
    # monthly parsing
    for i in range(2023, 2025):
        for j in range(1, 13):
            year_month            = f"{i}-{num_to_digits(j)}"
            df_month              = df_confirm[[i for i in df_confirm.columns if year_month in i]].apply(reduce_sunday, axis=1).value_counts()
            df_month_clean        = pd.Series()
            for val, count in df_month.items():
                if val in df_confirm_unique_teams:
                    df_month_clean[val] = count
                else: # list of multiple teams served
                    for v in ast.literal_eval(val.replace("' '", "', '")):
                        if v in df_month_clean:
                            df_month_clean[v] += 1
                        else:
                            df_month_clean[v] = 1
            df_confirm_monthly_counts[year_month] = df_month_clean
            
    path_weekly  = os.path.join(save_dir, f"{today}_Team_Weekly_Counts.xlsx")
    path_monthly = os.path.join(save_dir, f"{today}_Team_Monthly_Counts.xlsx")

    if os.path.exists(path_weekly):
        mode = 'a'
        exist_behavior = 'replace'
    else:
        mode = 'w'
        exist_behavior = None
    with pd.ExcelWriter(path_weekly, mode=mode, if_sheet_exists=exist_behavior) as w:  
        df_confirm_weekly_counts.to_excel(w, sheet_name=locations[n])

    if os.path.exists(path_monthly):
        mode = 'a'
        exist_behavior = 'replace'
    else:
        mode = 'w'
        exist_behavior = None
    with pd.ExcelWriter(path_monthly, mode=mode, if_sheet_exists=exist_behavior) as w:  
        df_confirm_monthly_counts.to_excel(w, sheet_name=locations[n])