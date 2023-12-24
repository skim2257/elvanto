import os, json
import pandas as pd
from elvanto import ElvantoQuery
from dotenv import load_dotenv
from urllib.parse import urljoin

load_dotenv(".env")

elv = ElvantoQuery(os.getenv('ELVANTO_KEY'), sub_api="peopleFlows/")
url = urljoin(elv.base_url, "getAll")

# for i in range(1000): # ASSUMPTION: max 1,000,000 groups
    # payload = {"page": i+1,
    #             "page_size": 1000, #1000 is max. If we have more than 1000 CGs, we need to add a for loop to parse all pages.
    #             "fields": fields}
groups = elv.post(url) #, payload=payload)
with open("db/people_flows.json", "w") as f:
    json.dump(groups.json(), f, indent=4)

