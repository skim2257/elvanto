import json
from elvanto import Coach
from .globals import HEADS

class SetEncoder(json.JSONEncoder):
    """
    json encoder that handles attributes of 'set' type
    """
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def load_triple(path):
    # manipulate coaches json
    coaches_db = load_coaches(path)
    heads      = get_head_coaches(coaches_db)
    coaches    = get_coaches(coaches_db)
    all_leads  = coaches_db.keys()

    return coaches_db, heads, coaches, all_leads


def get_names(name_unclean):
    """
    Parameters
    ----------
    name_unclean: str
        assumes it is all uppercase and stripped of whitespace

    Returns
    -------
    names: list or str
        list of parsed names (1 or 2)
    """
    # iterate through all names if list is passed in 
    if isinstance(name_unclean, list) or isinstance(name_unclean, set):
        return [j for i in name_unclean for j in get_names(i)]
    
    # if a couples' name to be separated into two names
    if " & " in name_unclean:
        names = name_unclean.split(" & ")
    elif " AND " in name_unclean:
        names = name_unclean.split(" AND ")
    else:
        names = [name_unclean.strip()]
    
    if len(names) > 1:
        counts = [len(i.strip().split()) for i in names]
        if 2 in counts and sum(counts) == 3:
            idx = counts.index(2)
            full_name = names.pop(idx)
            last = full_name.split()[1]
            other_name = names[0] + " " + last
            names = [full_name, other_name]
    
    return names


def update_safe(coaches, name_unclean, parents, children):
    """
    Parameters
    ----------
    coaches: dict
        dictionary of coaches
    name_unclean: str
    """
    names = get_names(name_unclean)

    for name in names:
        coaches[name] = search_coach(coaches, name, parents, children)


def vacuum(name):
    return name.upper().strip()


def search_coach(coaches, name, parents, children):
    if name in coaches:
        return coaches[name].update(parents, children)
    else:
        return Coach(name, parents, children)


def get_subidxs(df):
    """ 
    different parsing for HC tables vs Coach tables
    this should eventually be deprecated to backend managed, 
    but for now i'll pretend to monka and parse like this
    """
    idxs = df[df.eq("NOTES / IF MOVING TO ANOTHER GROUP NOTE NEW HC/COACH").any(axis=1)].index
    if len(idxs) < 1: 
        idxs = df[df.eq("Discipleship Forms Complete Fall 2023").any(axis=1)].index
    
    return idxs


def parse_coaches(dfs: list):
    """
    dfs: list
        list of DataFrames containing pandas (ideally starting from leaf nodes and working up to head coaches)

    """
    coaches = {}
    for n, df_focus in enumerate(dfs):
        idxs = get_subidxs(df_focus).tolist()
        idxs.append(-1)
        print(len(idxs))
        for n, idx in enumerate(idxs):
            if n == len(idxs) - 1:
                break

            # grab all rows between prev_idx and idx
            df_c = df_focus.iloc[idx:idxs[n+1]]
            print('\n', n, df_c)

            # only grab list of names
            names = [vacuum(i) for i in df_c[2].dropna().tolist() if i != '']
            if len(names) > 1:
                lead = names.pop(0)
                print(lead, names)
                update_safe(coaches, lead, [], names)
                for name in names:
                    update_safe(coaches, name, [lead], [])

    return coaches


def load_coaches(path):
    with open(path, "r") as f:
        coaches = json.load(f)
    return coaches


def get_head_coaches(coaches):
    head_coaches = []
    for coach in coaches:
        if len(coaches[coach]["parents"]) < 1:
            head_coaches.append(coach)
    return head_coaches


def get_coaches(coaches): 
    # Codex prompt: if both parents and children have elements, it's a coach
    coach_names = []
    for name in coaches:
        if len(coaches[name]["parents"]) > 0 and len(coaches[name]["children"]) > 0:
            coach_names.append(name)
    return coach_names  


def coaches_df(coaches):
    import pandas as pd
    # turn coaches into a dataframe
    df = pd.DataFrame.from_dict(coaches, orient="index")
    df['parents'] = df['parents'].apply(lambda x: x[0] if len(x) > 0 else "")
    return df.drop(columns=["name"])


def search_tree(coaches, names):
    all_children = set()
    for name in get_names(names):
        children = Coach.from_dict(coaches[name]).children  # this should be using the Coach object
        all_children |= children
        all_children |= search_tree(coaches, children)
    
    return all_children