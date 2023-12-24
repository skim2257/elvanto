
import os
import pandas as pd
from urllib.parse import urljoin
from .main import ElvantoQuery

class People(ElvantoQuery):
    def __init__(self, 
                 people_csv=None,
                 **kwargs):
        
        super().__init__(sub_api="people/", **kwargs)

        if people_csv is not None and os.path.exists(people_csv):
            self.people, self.people_df = self.load_db(people_csv)
        else:
            self.get_people()

    def get_people(self, 
                   fields=['gender', 'birthday', 'anniversary', 'marital_status', 'departments', 'locations', 'service_types']):
        
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
        self.people = {}
        for i in range(1000): # ASSUMPTION: max 1,000,000 entries
            payload = {"page": i+1,
                       "page_size": 1000, #1000 is max. If we have more than 1000 CGs, we need to add a for loop to parse all pages.
                       "fields": fields}
            people = self.post(url, payload=payload)

            # if good response
            if people.status_code == 200:
                people = people.json()
                
                # assert "groups" dictionary exists
                assert people["people"] 
                
                # assert "group" list exists
                if people["people"]["on_this_page"] < 1: break

                # turn group list into dictionary
                people_page = {i.pop('id'): i for i in people["people"]["person"]}
                self.people = {**self.people, **people_page}
            else: #if bad response
                print(f"Page {i+1}, Response Type:", people.status_code)
                break
        return self.people
    
    def get_person_info(self, 
                        id, 
                        fields=['gender', 'birthday', 'anniversary', 'marital_status', 'departments', 'locations', 'service_types']):
        """
        Parameters
        ----------
        id: str
            Person ID.
        fields: list[str]
            List of fields to retrieve for each group.
        
        Returns
        -------
        person : dict
            Dictionary of personal info {person_id: person_info}

        Retrieves info for a single person in the Elvanto database.
        """
        url = urljoin(self.base_url, 'getInfo')
        payload = {"id": id,
                   "fields": fields}
        
        info = self.post(url, payload=payload)

        # if good response
        if info.status_code == 200:
            info = info.json()

            # assert that it found an existing group
            assert info["status"] == "ok" and len(info["person"]) > 0, "Person not found."
            
            # assert that it only found one group
            assert len(info["group"]) == 1
            group_info = info["group"][0]

            # assert that the group retrieved has the right id
            assert group_info['id'] == id

            # returns info of the group
            return group_info
        else:
            print(f"Group id: {id}, \tResponse Type:", info.status_code)
            return


    # @staticmethod
    # def parse_threads(threads):
    #     df_threads = pd.DataFrame(threads)
    #     df_threads['userName'] = df_threads.user.apply(lambda x: x['name'])
    #     df_threads['userEmail'] = df_threads.user.apply(lambda x: x['email'])
    #     df_threads.drop(['user', 'comments'], axis=1, inplace=True)

    #     return df_threads


