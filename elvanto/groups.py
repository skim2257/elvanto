
import os
import pandas as pd
from urllib.parse import urljoin
from .main import ElvantoQuery

class Groups(ElvantoQuery):
    def __init__(self, 
                 groups_csv=None,
                 **kwargs):
        
        super(self).__init__(sub_api="groups/", **kwargs)

        if os.path.exists(groups_csv):
            self.groups, self.groups_df = self.load_db(groups_csv)

    def get_groups(self, 
                   fields=['people', 'categories', 'departments', 'demographics', 'locations']):
        
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
        self.groups = {}
        for i in range(1000): # ASSUMPTION: max 1,000,000 groups
            payload = {"page": i+1,
                       "page_size": 1000, #1000 is max. If we have more than 1000 CGs, we need to add a for loop to parse all pages.
                       "fields": fields}
            groups = self.post(url, payload=payload)

            # if good response
            if groups.status_code == 200:
                groups = groups.json()
                
                # assert "groups" dictionary exists
                assert groups["groups"] 
                
                # assert "group" list exists
                if groups["groups"]["on_this_page"] < 1: break

                # turn group list into dictionary
                groups_page = {i.pop('id'): i for i in groups["groups"]["group"]}
                self.groups = {**self.groups, **groups_page}
            else: #if bad response
                print(f"Page {i+1}, Response Type:", groups.status_code)
                break
        return self.groups
    
    def get_group_info(self, 
                       id, 
                       fields=['people', 'categories', 'departments', 'demographics', 'locations']):
        """
        Parameters
        ----------
        id: str
            Group ID.
        fields: list[str]
            List of fields to retrieve for each group.
        
        Returns
        -------
        groups : dict
            Dictionary of group info {group_id: group_info}

        Retrieves info for a single group in Elvanto database.
        """
        url = urljoin(self.base_url, 'getInfo')
        payload = {"id": id,
                   "fields": fields}
        
        info = self.post(url, payload=payload)

        # if good response
        if info.status_code == 200:
            info = info.json()

            # assert that it found an existing group
            assert info["status"] == "ok" and info["groups"]["on_this_page"] > 0, "Group not found."
            
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

    @staticmethod
    def json_to_df(dictionary):
        return pd.DataFrame.from_dict(dictionary, orient='index')
    # @staticmethod
    # def parse_threads(threads):
    #     df_threads = pd.DataFrame(threads)
    #     df_threads['userName'] = df_threads.user.apply(lambda x: x['name'])
    #     df_threads['userEmail'] = df_threads.user.apply(lambda x: x['email'])
    #     df_threads.drop(['user', 'comments'], axis=1, inplace=True)

    #     return df_threads


