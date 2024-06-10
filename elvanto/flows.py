
import os
import pandas as pd
from urllib.parse import urljoin
from .main import ElvantoQuery

class Flows(ElvantoQuery):
    def __init__(self, 
                 flows_csv=None,
                 **kwargs):
        
        super().__init__(sub_api="peopleFlows/", **kwargs)

        if flows_csv is not None and os.path.exists(flows_csv):
            self.flows, self.flows_df = self.load_db(flows_csv)
        else:
            self.get_flows()

            # get the DataFrame
            self.flows_df = pd.DataFrame.from_dict(self.flows, orient='index')
            self.flows_df.to_csv("db/flows.csv")

    def get_flows(self):
        
        """
        Parameters
        ----------
        fields: list[str]
            List of fields to retrieve for each group.
        
        Returns
        -------
        groups : dict
            Dictionary of groups {group_id: group_info}

        Retrieves ALL historical groups in Elvanto database.
        """
        url = urljoin(self.base_url, "getAll")
        # for i in range(1000): # ASSUMPTION: max 1,000,000 entries
        response = self.post(url)

        # if good response
        if response.status_code == 200:
            info = response.json()
            
            # assert "people_flows" dictionary exists
            assert info["people_flows"] 
            
            # assert "people_flows" list exists
            if info["people_flows"]["on_this_page"] < 1: return

            # turn group list into dictionary
            self.flows = {i.pop('id'): i for i in info["people_flows"]["people_flow"]} 

        else: #if bad response
            print(f"People Flows getAll, Response Type:", response.status_code)

        return self.flows
    
    def get_step_people(self,
                        id):
        url = urljoin(self.base_url, 'steps/people')
        payload = {"step_id": id}
        
        response = self.post(url, payload=payload)
        if response.status_code == 200:
            if response.json()["status"] == "ok":   
                info = response.json()["people_flow_step_members"]
                
                # if there are any people in this step:
                if len(info["people_flow_step_member"]) > 0:
                    return {i.pop('id'): i for i in info["people_flow_step_member"]}
                else:
                    return {}
        else:
            print(f"Step id: {id}, \tResponse Type:", response.status_code)
            return
            
    def add_step_person(self,
                        id):
        return NotImplementedError

    def get_steps(self,
                  steps: list):
        all_steps = {}
        for step in steps:
            children = step.pop("steps")
            all_steps[step["id"]] = step
            if len(children) > 0:
                all_steps = {**all_steps, **self.get_steps(children)}

        return all_steps

    def get_flow_steps(self, 
                       id):
        """
        Parameters
        ----------
        id: str
            Flow ID.
        
        Returns
        -------
        all_steps : dict
            Dictionary of all steps within the flow {step_id: step_info}

        Retrieves all steps for a single flow in the Elvanto database.
        """
        url = urljoin(self.base_url, 'steps/getAll')
        payload = {"flow_id": id}
        response = self.post(url, payload=payload)

        # if good response
        if response.status_code == 200:
            if response.json()["status"] == "ok":
                # get the steps
                info = response.json()["people_flow_steps"]

                # assert that it found an existing group
                assert len(info["people_flow_step"]) > 0, "People Flow not found."
                
                # turn group list into dictionary
                steps_page = {k: v for i in info["people_flow_step"] for k, v in self.get_steps([i]).items()}   

                # returns info of the group
                return steps_page

        print(f"Flow id: {id}, \tResponse Type:", response.json())        
        return {}


    # @staticmethod
    # def parse_threads(threads):
    #     df_threads = pd.DataFrame(threads)
    #     df_threads['userName'] = df_threads.user.apply(lambda x: x['name'])
    #     df_threads['userEmail'] = df_threads.user.apply(lambda x: x['email'])
    #     df_threads.drop(['user', 'comments'], axis=1, inplace=True)

    #     return df_threads


