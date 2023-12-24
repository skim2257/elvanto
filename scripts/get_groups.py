from elvanto import ElvantoQuery, parser
from dotenv import load_dotenv
import os

def main():
    load_dotenv(".env")

    args = parser()
    elv = ElvantoQuery(os.getenv('ELVANTO_KEY'),
                       groups_csv = args.groups_csv)

    if not hasattr(elv, "groups"):
        # should be run periodically to update the csv
        groups = elv.get_groups(fields=[], load_csv=True)
        elv.json_to_df(groups).to_csv("groups.csv")

    df = elv.groups_df

    if args.active:
        df = df[df['status'] == 'Active']
    if args.name:
        df = df[df['name'].str.contains(args.name)]

    df.sort_values(by=['name'], inplace=True)
    df.to_csv("search_results.csv")    

    # for i in groups:
    #     print(i)
    #     info = elv.get_group_info(groups[i])
    #     print(info)
    #     break

if __name__ == "__main__":  
    main()
