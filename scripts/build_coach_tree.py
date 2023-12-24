from elvanto.utils import load_coaches, get_head_coaches, get_coaches, coaches_df, get_names, search_tree, SetEncoder, HEADS

def main():
    # manipulate coaches json
    coaches_db = load_coaches("db/coaches.json")
    h_coaches  = get_head_coaches(coaches_db)
    coaches    = get_coaches(coaches_db)
    all_leads  = coaches_db.keys()
    
    assert len(h_coaches) == 9, f"There are {len(h_coaches)}, but should be 9 head coaches"
    assert len(coaches) == 41, f"There are {len(coaches)}, but should be 41 coaches"
    coaches.remove("BRIAN MAHER")  # 41 includes Brian Maher due to heuristic. 
    assert len(all_leads) == 213, f"There are {len(all_leads)}, but should be 213 leads"

    # save to dataframe/csv
    df_coaches = coaches_df(coaches_db)
    df_coaches.to_csv("db/coaches.csv")

    # sanity check: get all coaches with more than 1 parent (SHOULD BE EMPTY)
    for i in coaches_db:
        if len(coaches_db[i]["parents"]) > 1:
            print(coaches_db[i])

    # these are hardcoded here for now, but should be pulled from the coaches.json file
    # perhaps we need to find a way to save leader level as an attribute + save couples
    
    
    hc_tree = {}
    for hc in HEADS:
        names = get_names(hc)
        leads = set()
        for name in names:
            leads |= search_tree(coaches_db, name)
        hc_tree[hc] = leads
    
    c_tree = {}
    for coach in coaches:
        leads = set()
        names = get_names(coach)
        for name in names:
            leads |= search_tree(coaches_db, name)
        c_tree[coach] = leads

    # dump dictionary of head coaches and all their leaves to json file
    import json
    with open("db/hc_tree.json", "w") as f:
        json.dump(hc_tree, f, indent=4, cls=SetEncoder)
    with open("db/coaches_tree.json", "w") as f:
        json.dump(c_tree, f, indent=4, cls=SetEncoder)

    
if __name__ == "__main__":
    main()
