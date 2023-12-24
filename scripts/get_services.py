from elvanto import Services, parser
from dotenv import load_dotenv
import os

def main():
    load_dotenv(".env")

    # args = parser()

    # start_date="2023-01-01"
    # end_date="2023-12-31"
    elv = Services(key=os.getenv('ELVANTO_KEY'))
    # services = elv.get_services()
    elv.services_df   = elv.parse_services(elv.services)
    elv.teams_df      = elv.parse_teams(elv.volunteers)
    
    elv.services_df.to_csv("db/services.csv")
    elv.teams_df.to_csv("db/teams.csv")

    import json
    with open("db/services.json", "w") as f:
        json.dump(elv.services, f, indent=4)

    with open("db/teams.json", "w") as f:
        json.dump(elv.volunteers, f, indent=4)

    
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
