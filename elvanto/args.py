from argparse import ArgumentParser

def parser():
    args = ArgumentParser()
    args.add_argument("--groups_csv", type=str, default="groups.csv")
    args.add_argument("--name", type=str, default=None)

    # flag arguments
    args.add_argument("--active", action="store_true")
    args.add_argument("--suspended", action="store_true")
    args.add_argument("--archived", action="store_true")
    
    return args.parse_known_args()[0]