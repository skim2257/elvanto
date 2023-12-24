import pandas as pd

df = pd.read_csv("db/Group-People-History-Aug-28-2023-Sep-25-2023.csv")
df["Date Added"].value_counts().sort_index().to_csv("ask_why/cg_added.csv")
# print(df.groupby("Date Added").count())
