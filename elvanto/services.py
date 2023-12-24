
import os
import pandas as pd
from urllib.parse import urljoin
from .main import ElvantoQuery

class Services(ElvantoQuery):
    def __init__(self, 
                 services_csv=None,
                 start_date="2023-01-01",
                 end_date="2023-12-31",
                 **kwargs):
        
        super(Services, self).__init__(sub_api="services/", **kwargs)

        # this attribute determines which fields are saved to the self.services / db
        # NOTE: it's different from fields of self.get_services, which is the API parameter
        self.services_fields = ["name", "series_name", 
                                "date", "description", 
                                "service_type.id", 
                                "service_type.name", 
                                "location.id", 
                                "location.name",
                                "service_times.service_time.id"]
        
        if services_csv is not None and os.path.exists(services_csv):
            self.services, self.services_df = self.load_db(services_csv)
        else:
            self.get_services(start_date=start_date, end_date= end_date)
        
    def get_services(self, 
                     start_date="2023-01-01",
                     end_date="2023-12-31",
                     fields=['series_name', 'service_times', 'volunteers', 'plans']):
        """
        Parameters
        ----------
        start_date: str
            Start date of services to retrieve.
        end_date: str
            End date of services to retrieve.
        fields: list[str]
            List of fields to retrieve for each group.
        
        Returns
        -------
        services : dict
            Dictionary of services {service_id: service_info} 
            < BEWARE > it's very very nested. Refer to: https://www.elvanto.com/api/services/getAll/
        volunteers : dict
            Dictionary of volunteers {service_id: volunteer_info}

        Retrieves ALL services between start_date to end_date in Elvanto database.
        """
        url = urljoin(self.base_url, "getAll")
        self.services, self.volunteers = {}, {}
        for i in range(1000): # ASSUMPTION: max 1,000,000 entries
            payload = {"page": i+1,
                       "page_size": 1000, #1000 is max. If we have more than 1000 CGs, we need to add a for loop to parse all pages.
                       "start": start_date,
                       "end": end_date,
                    #    "all": "yes",
                       "fields": fields}
            response = self.post(url, payload=payload)

            # if good response
            if response.status_code == 200:
                services = response.json()

                # assert "services" dictionary exists
                assert "services" in services, print(response)
                
                # assert "service" list exists
                if services["services"]["on_this_page"] < 1: break

                # turn service list into dictionary
                services_page, volunteers_page = {}, {}
                for service in services["services"]["service"]: 
                    s_id = service.pop('id')
                    services_page[s_id] = {}
                    for field in self.services_fields:
                        nested_fields = field.split(".")
                        if len(nested_fields) > 1:
                            if "service_times" in field:
                                for n, service_time in enumerate(service[nested_fields[0]][nested_fields[1]]):
                                    services_page[s_id][field+f"_{n}"] = service_time["id"]
                            else:
                                services_page[s_id][field] = service[nested_fields[0]][nested_fields[1]]
                        else:
                            services_page[s_id][field] = service[field]
                    
                    volunteers_serv = self.get_volunteers(service['volunteers'])
                    ## UPDATE cuz there's a LOT of redundant names (501 vs 6900+ rows)
                    if s_id not in volunteers_page:
                        volunteers_page[s_id] = volunteers_serv
                    else:
                        volunteers_page[s_id] = {**volunteers_page[s_id], **volunteers_serv} 
                        
                self.services = {**self.services, **services_page}
                self.volunteers = {**self.volunteers, **volunteers_page}

            else: #if bad response
                print(f"Page {i+1}, Response Type:", response.status_code)
                break

        return self.services, self.volunteers
    
    @staticmethod
    def get_volunteers(volunteers: dict):
        """
        Parameters
        ----------
        volunteers: dict
            Dictionary of volunteers of a specific service according to: https://www.elvanto.com/api/services/getAll/
        
        Returns
        -------
        volunteers : dict
            Dictionary of volunteers {}
        """
        volunteers_page = {}
        plans = volunteers["plan"]   
        for n, plan in enumerate(plans):
            time_id = plan["time_id"]
            if time_id not in volunteers_page:
                volunteers_page[time_id] = {}
            if "positions" in plan:
                for position in plan["positions"]["position"]:
                    if "volunteers" in position and position["volunteers"] != "":
                        volunteers = position.pop("volunteers")
                        if "volunteer" in volunteers:
                            for volunteer in volunteers["volunteer"]:
                                person = volunteer["person"]
                                p_id   = person.pop("id")
                                volunteers_page[time_id][p_id] = {**position, 
                                                                  **person, 
                                                                  "status": volunteer["status"]}
                    else:
                        pass
            else:
                print(f"'positions' key not found in plan id: {plan}. \nThese are the keys of the 'plan' dictionary.", [k for k in plan])
                break
        
        # temporary for verbose debugging
        def get_nested_keys(d):
            return [k for k in d] + [inner_key for inner_dict in d.values() for inner_key in get_nested_keys(inner_dict)] if isinstance(d, dict) else []

        print('final', len(get_nested_keys(volunteers_page)))
        return volunteers_page

    def get_service_info(self, 
                         id, 
                         fields=['series_name', 'service_times', 'volunteers']):
        """
        Parameters
        ----------
        id: str
            Service ID.
        fields: list[str]
            List of fields to retrieve for each service.
        
        Returns
        -------
        services : dict
            Dictionary of service info {service_id: service_info}

        Retrieves info for a single person in the Elvanto database.
        """
        url = urljoin(self.base_url, 'getInfo')
        payload = {"id": id,
                   "fields": fields}
        
        info = self.post(url, payload=payload)

        # if good response
        if info.status_code == 200:
            info = info.json()

            # assert that it returned a good response
            assert info["status"] == "ok", f"Something ain't right. Response: {info}"
            
            # assert that it only found one service
            assert len(info["service"]) == 1
            serv_info = info["service"][0]

            # assert that the group retrieved has the right id
            assert serv_info['id'] == id

            # returns info of the group
            return serv_info
        else:
            print(f"Service id: {id}, \tResponse Type:", info.status_code)
            return

    @staticmethod
    def parse_services(dictionary):
        return pd.DataFrame.from_dict(dictionary, orient='index')

    @staticmethod
    def parse_teams(dictionary):
        """
        Returns a melted dataframe of the volunteers dictionary.
        """
        melted_dict = {}
        n = 1
        for a in dictionary:
            for b in dictionary[a]:
                for c in dictionary[a][b]:
                    melted_dict[n] = {'serv_id': a, 'time_id': b, 'vol_id': c, **dictionary[a][b][c]}
                    n += 1
        return pd.DataFrame.from_dict(melted_dict, orient='index')

    # @staticmethod
    # def parse_threads(threads):
    #     df_threads = pd.DataFrame(threads)
    #     df_threads['userName'] = df_threads.user.apply(lambda x: x['name'])
    #     df_threads['userEmail'] = df_threads.user.apply(lambda x: x['email'])
    #     df_threads.drop(['user', 'comments'], axis=1, inplace=True)

    #     return df_threads


