import requests
from urllib.parse import urljoin
from pandas import read_csv


# get channels
class ElvantoQuery():
    def __init__(self, 
                 key, 
                 user_id=None, 
                 datatype="json", 
                 csv_path=None,
                 sub_api=""):
        """
        Parameters
        ----------
        key : str
            Elvanto API key retrieved via environment config.
        user_id : str
            Elvanto user id?
        datatype : str
            Data type to return from API. Default is JSON.
        csv_path : str
            Path to csv file containing group ids. If not provided, will retrieve all groups from Elvanto API.  
        """
        self.key = key
        self.base_url = urljoin("https://api.elvanto.com/v1/", sub_api)
        self.headers = {"accept": "application/json"}
                        # "Authorization": f"Bearer {self.key}"} #OAuth2 tag
        self.datatype = datatype
    

    def get(self, url):
        return requests.get(url+f".{self.datatype}", headers=self.headers, auth=(self.key, ''))
    
    def post(self, url, payload=None):
        return requests.post(url+f".{self.datatype}", headers=self.headers, json=payload, auth=(self.key, ''))

    def put(self, url, payload):
        return requests.put(url+f".{self.datatype}", headers=self.headers, json=payload, auth=(self.key, ''))
    
    def delete(self, url):
        return requests.delete(url+f".{self.datatype}", headers=self.headers, auth=(self.key, ''))

    @staticmethod
    def load_db(path):
        df = read_csv(path, index_col=0)

        # if csv is not empty
        if len(df) > 0:
            return df.to_dict(orient='index'), df
        else:
            return None, None
