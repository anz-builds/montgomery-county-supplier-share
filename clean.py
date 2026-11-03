"""Clean Montgomery County (MD) Warehouse and Retail Sales for a
summer 2019 vs summer 2026 supplier-share comparison.

Run:  python clean.py                 (downloads the latest data)
      python clean.py path/to/file.csv (uses a file you already have)
Every step prints a row count; those counts are the cleaning log in README.md.
"""
import sys
from datetime import date
import pandas as pd

URL = "https://data.montgomerycountymd.gov/api/views/v76h-r7br/rows.csv?accessType=DOWNLOAD"
LOOKUP = "data/reference/item_code_lookup.csv"
OUT = "data/clean/sales_clean.csv"
NUM = ["RETAIL SALES", "RETAIL TRANSFERS", "WAREHOUSE SALES"]
TEXT = ["SUPPLIER", "ITEM DESCRIPTION"]


def log(step, df):
    print(f"{step:<55} {len(df):>8,} rows")
    return df


# 0. Load: download from the county portal, or read a local file
if len(sys.argv) > 1:
    raw = pd.read_csv(sys.argv[1], dtype=str, keep_default_na=False)
    print(f"Source: {sys.argv[1]}")
else:
    raw = pd.read_csv(URL, dtype=str, keep_default_na=False)
    raw.to_csv(f"data/raw/sales_{date.today()}.csv", index=False)
    print(f"Source: county portal, downloaded {date.today()}")
df = log("0. raw", raw)

# 1. Numbers: accounting negatives "(0.17)" -> -0.17, strip commas, cast
for c in NUM:
    s = df[c].str.strip().str.replace(",", "", regex=False)
    s = s.str.replace(r"^\((.*)\)$", r"-\1", regex=True)
    df[c] = pd.to_numeric(s, errors="coerce")
print(f"   negatives kept (returns/adjustments): " +
      ", ".join(f"{c} {int((df[c] < 0).sum())}" for c in NUM))

# 2. Drop placeholder rows (blank retail sales: COUPON, RMS ITEM)
df = log("2. drop rows with blank RETAIL SALES (placeholders)", df[df["RETAIL SALES"].notna()])

# 3. Keep product types only
dropped = df.loc[~df["ITEM TYPE"].isin(["BEER", "WINE", "LIQUOR"]), "ITEM TYPE"].value_counts()
print("   dropping types:", dropped.to_dict())
df = log("3. keep BEER, WINE, LIQUOR", df[df["ITEM TYPE"].isin(["BEER", "WINE", "LIQUOR"])])

# 4. Text: tabs/line breaks -> space, collapse spaces, trim
for c in TEXT:
    df[c] = df[c].str.replace(r"\s+", " ", regex=True).str.strip()
# Blank-supplier rows left after the type filter were reviewed by hand:
# item 172000 "STORE SPECIAL DISTRESSED RTD" is a store markdown catch-all, not a product.
blank_sup = df["SUPPLIER"] == ""
print("   blank-SUPPLIER rows:", df.loc[blank_sup, "ITEM DESCRIPTION"].value_counts().to_dict())
df = log("4b. drop blank-SUPPLIER store catch-all rows", df[~blank_sup])

# 5. Drop all-zero rows
df = log("5. drop rows where all three measures are 0", df[(df[NUM].fillna(0) != 0).any(axis=1)])

# 6. Product key from the item-code lookup (one row per code + description)
#    align -> the code's latest description; keep separate or not in lookup -> the row's own description
lk = pd.read_csv(LOOKUP, dtype={"item_code": str}, keep_default_na=False)
lk = lk[["item_code", "description", "decision", "product_description"]]
df["desc_upper"] = df["ITEM DESCRIPTION"].str.upper()
df = df.merge(lk, left_on=["ITEM CODE", "desc_upper"], right_on=["item_code", "description"], how="left")
df["product_description"] = df["product_description"].fillna(df["desc_upper"])
df["product_key"] = df["ITEM CODE"] + " | " + df["product_description"]
print(f"   rows on reviewed codes: align {int((df['decision'] == 'align').sum()):,}, "
      f"keep separate {int((df['decision'] == 'keep separate').sum()):,}")

# 7. Decisions: negatives kept (step 1); supplier credited at time of sale (no remap)

# 8. Analysis window: Jun-Aug 2019 and Jun-Aug 2026
df = log("8. keep Jun-Aug 2019 and Jun-Aug 2026",
         df[df["YEAR"].isin(["2019", "2026"]) & df["MONTH"].isin(["6", "7", "8"])])

# 9. Save
cols = ["YEAR", "MONTH", "SUPPLIER", "ITEM CODE", "product_key", "product_description",
        "ITEM TYPE"] + NUM
df[cols].to_csv(OUT, index=False)
print(f"Saved {OUT}")
