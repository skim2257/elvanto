from elvanto import People, parser
from dotenv import load_dotenv
import os

def main():
    load_dotenv(".env")

    # args = parser()

    elv = People(key=os.getenv('ELVANTO_KEY'))#,
    # services = elv.get_services()
    # elv.services_df   = elv.json_to_services(services).to_csv("services.csv")
    # elv.volunteers_df = elv.json_to_services(elv.volunteers).to_csv("volunteers.csv")
    
    import json
    with open("db/people.json", "w") as f:
        json.dump(elv.people, f, indent=4)

    # df = elv.services_df

    # if args.active:
    #     df = df[df['status'] == 'Active']
    # if args.name:
    #     df = df[df['name'].str.contains(args.name)]

    # df.sort_values(by=['name'], inplace=True)
    # df.to_csv("search_results.csv")    

    # for i in groups:
    #     print(i)
    #     info = elv.get_group_info(groups[i])
    #     print(info)
    #     break

if __name__ == "__main__":  
    main()
