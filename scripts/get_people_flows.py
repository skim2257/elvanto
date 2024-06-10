import os, json
import pandas as pd
from elvanto import Flows, parser
from dotenv import load_dotenv
from urllib.parse import urljoin

def main():
    load_dotenv(".env")

    # args = parser()

    flo = Flows(key=os.getenv('ELVANTO_KEY'),
                csv_path="db/flows.csv")
    
    onboarding_flows = [flo.flows_df[flo.flows_df.name == name].index.values[0] for name in flo.flows_df.name if "TEAM ONBOARDING" in name]
    everyone = pd.DataFrame()

    for flow_id in onboarding_flows:
        steps = flo.get_flow_steps(flow_id)
        for step in steps:
            people = flo.get_step_people(step)
            pdf = pd.DataFrame.from_dict(people, orient='index')
            for col in steps[step]:
                val = steps[step][col]
                if val is isinstance(val, str):
                    pdf[col] = val
                else:
                    pdf[col] = str(val)
            everyone = pd.concat([everyone, pdf])
        break

    everyone.to_csv("exports/Every_Person_In_People_Flows.csv")
    # with open("db/people.json", "w") as f:
    # json.dump(elv.people, f, indent=4)

if __name__ == "__main__":  
    main()