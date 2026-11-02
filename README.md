# Montgomery County Supplier Share: Summer 2019 vs Summer 2026

**[View the Tableau dashboard](TABLEAU_PUBLIC_LINK)**

## Findings
<!-- 3–5 bullets: the headline share shifts, top gainers/losers, add/drop highlights, a modest recommendation -->

## Question
How did supplier share of beer, wine and liquor sales in Montgomery County, MD change between summer 2019 and summer 2026, and which products were added or dropped?

## Data
- Source: Montgomery County Open Data, *Warehouse and Retail Sales* (dataset `v76h-r7br`)
- Downloaded: DOWNLOAD_DATE (the county updates this dataset; re-running may change counts)
- Analysis window: June–August 2019 and June–August 2026, BEER / WINE / LIQUOR

## Cleaning log
Counts below are printed by `clean.py` (run on the DOWNLOAD_DATE file).

| Step                                                                                                                      | Rows after |
| ------------------------------------------------------------------------------------------------------------------------- | ---------- |
| Raw                                                                                                                       | 341,037    |
| Drop placeholder rows (blank retail sales: COUPON, RMS ITEM)                                                              | 341,031    |
| Keep BEER, WINE, LIQUOR (drops KEGS 11,051 · NON-ALCOHOL 2,602 · STR_SUPPLIES 471 · REF 132 · DUNNAGE 107 · blank type 1) | 326,667    |
| Drop blank-supplier store catch-all (item 172000, "STORE SPECIAL DISTRESSED RTD")                                         | 326,664    |
| Drop rows where retail sales, transfers and warehouse sales are all 0                                                     | 325,619    |
| Keep Jun 2019 - Aug 2019 and Jun 2026 - Aug 2026                                                                          | 67,163     |

**Decisions**
- **Negatives kept.** Values written as `(x)` are returns/adjustments; converted to `-x` and kept so totals net out. They are under 0.05% of any measure in the analysis window.
- **Supplier credited at time of sale.** Each sale counts for the supplier listed that month, so distributor moves between 2019 and 2026 are part of the change.
- **Text normalized.** Tabs, line breaks and repeated spaces collapsed in supplier and description.
- **Item codes reviewed.** 1,827 codes had more than one description. Each was reviewed (`data/reference/item_code_review.csv`): *align* = same product renamed (uses the latest description); *keep separate* = the code was reused for a different product. Evidence per code is in the `decided_by`, `review_note` and `review_source` columns (rules, web and archive pages, TTB label registry). Products are keyed on item code + description.

## Data gaps
The dataset covers Jun 2017–Feb 2018, Jan–Nov 2019, Jan/Mar/Jul/Sep 2020, and Jun–Aug 2026. **Nothing exists for 2021–2025**, so this is a two-point comparison, not a trend.

## Re-run
```
pip install -r requirements.txt
python clean.py            # downloads the latest data
python clean.py file.csv   # or use a file you already have
```
