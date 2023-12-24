import os
import json
from dotenv import load_dotenv
import pandas as pd
import gspread as gs
from elvanto.utils import parse_coaches, SetEncoder

load_dotenv(".env")

def main():
    # load coach spreadsheet
    gc = gs.service_account("gcp_credentials.json")
    coach_spread = gc.open_by_key(os.environ["COACH_SHEET_ID"])
    coach_sheet  = coach_spread.worksheet("Coach Groups Fall 2023").get_all_values() 
    df = pd.DataFrame(coach_sheet)

    # separate head coach, coach, and coach-in-training tables
    split_one = df[df.eq("Connect and Team Coach Groups").any(axis=1)].index[0]
    split_two = df[df.eq("Leads given Coaching responsibility").any(axis=1)].index[0]

    df_heads = df[:split_one].reset_index(drop=True)
    df_coach = df[split_one:split_two].reset_index(drop=True)
    df_leads = df[split_two:].reset_index(drop=True)

    print(df_leads)

    coaches = parse_coaches([df_leads, df_coach, df_heads])
    coaches_db = {i: coaches[i].__dict__ for i in coaches}

    import json
    with open("db/coaches.json", "w") as f:
        json.dump(coaches_db, f, indent=4, cls=SetEncoder)

if __name__ == "__main__":
    main()
    