import os, json
import pandas as pd
from elvanto import Flows, parser
from dotenv import load_dotenv
from urllib.parse import urljoin
from tqdm.auto import tqdm
from joblib import Parallel, delayed

def main():
    load_dotenv(".env")

    # args = parser()

    flo = Flows(key=os.getenv('ELVANTO_KEY'),
                flows_csv="db/flows.csv")
    
    onboarding_flows = [flo.flows_df[flo.flows_df.name == name].index.values[0] for name in flo.flows_df.name if "TEAM ONBOARDING" in name]
    everyone  = pd.DataFrame()
    locations = ["DOWNTOWN", "MIDTOWN", "HAMILTON"]
    columns   = ["flow_name", "member_firstname", "member_lastname", "date_added", "step_name", "location", "step_priority", "status", "completed_date"]

    def get_one_flow(flow_id):
        single_flow = pd.DataFrame()
        steps = flo.get_flow_steps(flow_id)
        for step in steps:
            people = flo.get_step_people(step)
            pdf = pd.DataFrame.from_dict(people, orient='index')
            
            # Add step information
            for col in steps[step]:
                val = steps[step][col]
                if val is isinstance(val, str):
                    pdf[f"step_{col}"] = val
                else:
                    pdf[f"step_{col}"] = str(val)
            
            # Add flow information
            pdf["flow_id"] = flow_id
            name = flo.flows[flow_id]["name"]
            pdf["flow_name"] = name

            # Add location column for easier sorting later
            for location in locations:
                if location in name:
                    pdf["location"] = location
            if "location" not in pdf.columns:
                pdf["location"] = "GENERAL"
            
            single_flow = pd.concat([single_flow, pdf])
        
        return single_flow


    # Output one flow for debugging    
    # print(get_one_flow(onboarding_flows[0]))

    all_flows   = Parallel(n_jobs=-1, verbose=10)(delayed(get_one_flow)(flow_id) for flow_id in tqdm(onboarding_flows))
    everyone    = pd.concat(all_flows)#[columns]
    everyone['date_added']      = pd.to_datetime(everyone['date_added'])
    everyone['time_elapsed']    = pd.Timestamp.now() - everyone['date_added']
    everyone['days_elapsed']    = everyone['time_elapsed'].dt.total_seconds() / (3600 * 24)

    # with pd.ExcelWriter("exports/People_Flows_by_Location_New.xlsx") as w:  
    #     for location in locations:
    #         everyone[everyone.location == location].to_excel(w, sheet_name=location)
        
    #     all_location_regex = "|".join(locations)
    #     everyone[~everyone.location.str.contains(all_location_regex)].to_excel(w, sheet_name="GENERAL")

    import datetime as dt
    today = dt.datetime.today().strftime("%Y%m%d-%H%M%p%Z")
    everyone.to_csv(f"exports/people_flows/{today}.csv")


if __name__ == "__main__":  
    main()