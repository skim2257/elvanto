from elvanto.utils import load_coaches, get_head_coaches, get_names, get_coaches, HEADS
from elvanto import DiscipleshipForms
import pandas as pd
import json
import os
from tqdm import tqdm

def nice_name(name: str):
    names = name.split(' ')
    new_name = ""
    for n, name in enumerate(names):
        name_lower = name.lower()
        new_name += name[0].upper() + name_lower[1:]
        if n < len(names) - 1:
            new_name += " "

    return new_name

def main():
    forms = DiscipleshipForms(self_path="exports/Form-Submissions_Leader-Self-Assessment-Form-2023_2023-12-13.csv", \
                              coach_path="exports/Form-Submissions_Coach-Discipleship-Form-2023_2023-12-13.csv", \
                              heads_path="exports/Form-Submissions_Head-Coach-Discipleship-Form-2023_2023-12-13.csv", \
                              verbose=False)
    forms.filter_date(start="2023-11-01")

    db    = load_coaches("db/coaches.json")
    heads = get_head_coaches(db)
    db_cs = get_coaches(db)

    # HEAD COACHES
    print("Starting HEAD COACHES now...")
    with open("db/hc_tree.json", "r") as f:
        hc_tree = json.load(f)
        # NOTE: added BRIAN MAHER to ANNIE & BRIAN MAHER's tree, for Brian's coach forms to show up

    for head in tqdm(hc_tree):
        df_self = pd.DataFrame()
        df_coach = pd.DataFrame()
        df_heads = pd.DataFrame()
        
        for one_head in get_names(head):
            if one_head in heads:
                df_heads = pd.concat([df_heads, forms.get_head_forms(one_head)], ignore_index=True)

        for lead in hc_tree[head]:
            df_self = pd.concat([df_self, forms.get_self_form(lead)], ignore_index=True)
            df_coach = pd.concat([df_coach, forms.get_coach_forms(lead)], ignore_index=True)

        df_self = df_self.sort_values("Date Submitted", ascending=False).reset_index(drop=True)
        df_coach = df_coach.sort_values("Date Submitted", ascending=False).reset_index(drop=True)
        df_heads = df_heads.sort_values("Date Submitted", ascending=False).reset_index(drop=True)

        hc_path = "outputs/Head Coaches"
        if not os.path.exists(hc_path):
            os.makedirs(hc_path)

        with pd.ExcelWriter(os.path.join(hc_path, f'{nice_name(head)} - 2023 Fall.xlsx')) as w:  
            df_self.to_excel(w, sheet_name='Leader Self Assessments')
            df_coach.to_excel(w, sheet_name='Coach Reports')
            df_heads.to_excel(w, sheet_name='Head Coach Reports')
    

    # COACHES
    print("Starting COACHES now...")
    with open("db/coaches_tree.json", "r") as f:
        coaches_tree = json.load(f)
        # NOTE: manually removed ANNIE's girls on BRIAN MAHER's coach tree, for Annie's coach forms to NOT show up on Josh/Maree's sheet

    for coach in tqdm(coaches_tree):
        df_self = pd.DataFrame()
        df_coach = pd.DataFrame()

        for one_head in get_names(coach):
            if one_head in db_cs:
                df_coach = pd.concat([df_coach, forms.get_coach_forms(one_head)], ignore_index=True)

        for lead in coaches_tree[coach]:
            df_self = pd.concat([df_self, forms.get_self_form(lead)], ignore_index=True)
            df_coach = pd.concat([df_coach, forms.get_coach_forms(lead)], ignore_index=True)
        
        df_self = df_self.sort_values("Date Submitted", ascending=False).reset_index(drop=True)
        df_coach = df_coach.sort_values("Date Submitted", ascending=False).reset_index(drop=True)
        
        coach_path = "outputs/Coaches"
        if not os.path.exists(coach_path):
            os.makedirs(coach_path)
            
        with pd.ExcelWriter(os.path.join(coach_path, f'{nice_name(coach)} - 2023 Fall.xlsx')) as w:  
            df_self.to_excel(w, sheet_name='Lead Self Assessments')
            df_coach.to_excel(w, sheet_name='Coach Reports')

if __name__ == "__main__":
    pd.options.mode.chained_assignment = None  # mutes many warnings!
    main()
    
