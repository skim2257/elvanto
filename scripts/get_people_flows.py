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
                csv_path="db/flows.csv")
    
    onboarding_flows = [flo.flows_df[flo.flows_df.name == name].index.values[0] for name in flo.flows_df.name if "TEAM ONBOARDING" in name]
    everyone = pd.DataFrame()

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
            pdf["flow_name"] = flo.flows[flow_id]["name"]

            single_flow = pd.concat([single_flow, pdf])
        
        return single_flow

    all_flows = Parallel(n_jobs=-1, verbose=10)(delayed(get_one_flow)(flow_id) for flow_id in tqdm(onboarding_flows))
    everyone = pd.concat(all_flows)

    everyone.to_csv("exports/Every_Person_In_People_Flows.csv")


if __name__ == "__main__":  
    main()