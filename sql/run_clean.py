import sqlite3
import pandas as pd

con = sqlite3.connect("data/sales.db")
pd.read_csv("data/raw/Warehouse_and_Retail_Sales_20261102.csv", dtype=str, keep_default_na=False).to_sql("raw", con, index=False, if_exists="replace")
pd.read_csv("data/reference/item_code_lookup.csv", dtype=str, keep_default_na=False).to_sql("lookup", con, index=False, if_exists="replace")
con.executescript(open("sql/clean.sql").read())
pd.read_sql("SELECT * FROM sales_clean", con).to_csv("data/clean/sales_clean_sql.csv", index=False)