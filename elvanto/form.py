import pandas as pd
from thefuzz import process
from thefuzz.fuzz import token_set_ratio

class DiscipleshipForms():
    def __init__(self, 
                 self_path: str = None, 
                 coach_path: str = None, 
                 heads_path: str = None,
                 verbose: bool = False):
        """
        Parameters
        ----------
        self_path: str
            Path to leader self-assessment forms
        coach_path: str
            Path to coach assessment form
        
        """
        self.df_self  = self.clean_df(pd.read_csv(self_path)) if self_path is not None else None
        self.df_coach = self.clean_df(pd.read_csv(coach_path)) if coach_path is not None else None
        self.df_heads = self.clean_df(pd.read_csv(heads_path)) if heads_path is not None else None
        self.v = verbose

    @staticmethod
    def clean_df(df):
        df['Date Submitted'] = pd.to_datetime(df['Date Submitted'])
        df['Name_in_form'] = df['Your First Name'].str.upper() + " " + df['Your Last Name'].str.upper()
        return df

    @staticmethod
    def match(name, candidates):
        return process.extractOne(name, candidates, scorer=token_set_ratio)

    @staticmethod
    def match_all(name, candidates):
        matches = process.extract(name, candidates, limit=200, scorer=token_set_ratio)
        return list(set(matches))

    @staticmethod
    def get_match_df(match_fn, name, df, verbose=False):
        match     = match_fn(name, df['Name_in_form'].tolist())
        if isinstance(match, tuple):  # single hit
            # if match score too low, print error
            if match[1] < 85:
                try:
                    raise ValueError(f"For {name}: the fuzzy matching score is {match[1]}. Found {match[0]} but score is too low.")
                except ValueError as e:
                    pass
            match = [match]

        df_match  = pd.DataFrame(match, columns=['match', 'score'])
        df_match['name'] = name
        
        names_to_match = df_match[df_match['score'] >= 85]
        names_almost   = df_match[(df_match['score'] < 85) & (df_match['score'] >= 79)]
        df_matches = df[df['Name_in_form'].isin(names_to_match['match'])]
        df_return = pd.merge(df_match, df_matches, left_on='match', right_on='Name_in_form', how='left')
        if not verbose: 
            df_return = df_return.drop(['match', 'score'], axis=1)
        
        return df_return

    @staticmethod
    def filter_one(df, start, end):
        return df[(start < df['Date Submitted']) & (df['Date Submitted'] < end)] if isinstance(df, pd.DataFrame) else df
    
    def filter_date(self, 
                    start: str = "1899-01-01", 
                    end: str = "2999-12-31"):
        self.df_self  = self.filter_one(self.df_self, start, end)
        self.df_coach = self.filter_one(self.df_coach, start, end)
        self.df_heads = self.filter_one(self.df_heads, start, end)

    def get_self_form(self, name):
        """
        Parameters
        ----------
        name: str
            Name of leader to get self form for
        """
        return self.get_match_df(self.match, name, self.df_self, self.v)

    def get_coach_forms(self, name):
        """
        Parameters
        ----------
        name: str
            Name of leader to get (multiple) coach forms for
        """
        return self.get_match_df(self.match, name, self.df_coach, self.v)

    def get_head_forms(self, name):
        """
        Parameters
        ----------
        name: str
            Name of leader to get (multiple) head forms for
        """
        return self.get_match_df(self.match_all, name, self.df_heads, self.v)