# Montgomery County Supplier Share: Summer 2019 vs Summer 2026

**[View the Tableau dashboard](https://public.tableau.com/app/profile/.nza/viz/MontgomeryCountyMD-A-BevDashboard/Dashboard-ShareChange)**

## Findings

- **Wine's biggest shift was an acquisition, not a consumer switch:** E. & J. Gallo grew from 16.7% to 25.2% of summer wine sales (+8.5 pts) while Constellation Brands fell from 13.6% to 1.8% (-11.8 pts). Gallo bought 30+ Constellation wine brands in January 2021 ([Gallo](https://www.gallo.com/press/2021-01-05-ej-gallo-winery-completes-acquisition)). Consequently, the same brands appear under Constellation in 2019 and under Gallo in 2026.
- **For Beer, Crown Imports took the lead:** Crown Imports rose from 17.6% to 22.2% (+4.6 pts) and Boston Beer from 7.8% to 10.4% (+2.6 pts), while Anheuser-Busch (-2.8), Miller (-1.7) and Heineken (-1.7) lost share.
- **Liquor: Sazerac is the biggest gainer.** Sazerac grew from 8.8% to 14.6% (+5.9 pts); Jim Beam (-5.0) and Diageo (-3.7) lost the most.
- **Concentration held steady, while the leaders reshuffled:** The top 5 suppliers' combined share barely moved beer 67.6% → 68.6%, liquor 45.5% → 44.9%, wine 51.1% → 48.9%. Share moved between the big suppliers rather than to or from smaller ones.
- **Recommendation:** When reading supplier share across years, separate ownership changes (acquisitions/switching distributors) from real shifts in what shoppers buy. Here, the largest wine swing comes from a deal, while the beer and liquor gains (Crown, Sazerac) are the shifts worth investigating for assortment and promo planning.
## Question
How did supplier share of beer, wine and liquor sales in Montgomery County (MD) develop between summer 2019 and summer 2026, and what are the observed new products and the deletes? 

## Data
- Source: Montgomery County Open Data, *Warehouse and Retail Sales* (*dataset v76h-r7br*)
- Downloaded: 11/02/2026 *(Data may be updated by the county in the future)*
- Analysis window: June 2019 - August 2019 and June 2026 - August 2026
- Categories: Beer, Wine, and Liquor

## Cleaning log
Counts below are printed by `clean.py` (run on the DOWNLOAD_DATE file).

| Step                                                                                                                      | Rows after |
| ------------------------------------------------------------------------------------------------------------------------- | ---------- |
| Raw                                                                                                                       | 341,037    |
| Drop placeholder rows (blank retail sales: COUPON, RMS ITEM)                                                              | 341,031    |
| Keep BEER, WINE, LIQUOR (drops KEGS 11,051 · NON-ALCOHOL 2,602 · STR_SUPPLIES 471 · REF 132 · DUNNAGE 107 · blank type 1) | 326,667    |
| Drop blank-supplier store catch-all (item 172000, "STORE SPECIAL DISTRESSED RTD")                                         | 326,664    |
| Drop rows where retail sales, transfers and warehouse sales are all 0                                                     | 325,619    |
| Keep Jun–Aug 2019 and Jun–Aug 2026                                                                                        | 67,163     |

**Decisions**
- **Negatives values were kept.** Values written as *"x"* are returns/adjustments, which were converted to *"-x"* and kept for an accurate total net down. 
- **Supplier credited at time of sale.** Sales will go towards the supplier listed in the corresponding time of sale, as crediting an item's current distributor for both 2019 and 2026 results in an inaccurate picture
- **Text normalized.** Tabs, line breaks and redundant spaces were trimmed in supplier and description. 
- **Item codes reviewed.** 1,827 codes had more than one description. Each was reviewed (`data/reference/item_code_review.csv`): 
	- *align* = same product renamed (uses the latest description); 
	- *keep separate* = the code was reused for a different product. 
	- Evidence per code is in the `decided_by`, `review_note` and `review_source` columns 

**Item Code Review Process**

1,583 records were aligned, 222 kept separate: each code's deciding method is in the `decided_by` column, with the evidence and source link in the decision table: `references/item_code_lookup.csv`
1. **Flag codes:** Used `difflib.SequenceMatcher` to comparer two string character by character and return a score with a recommendation label: "align", "keep separate", "review".
2. **Rule checks:** Compared each description to the code's latest one on item type, size (converted to ml), package, pack count, and brand/variety (after expanding abbreviations). Result: 1,394 align, 169 keep separate, 264 unclear. Text similarity alone was tried first and dropped: it missed package changes like bottle → can.
3. **Web checks:** For unclear codes active in summer 2019 or 2026, searched for a rename or a distinct product, then checked whether the differing words appear on the other product's own page (e.g. "Madeira finished" on the Limited Release gin page). A search with no result was treated as unclear, not as "different."
4. **Primary sources and own data:** Checked the TTB label registry (COLA) for beer, spirits and sangria, and archived producer pages (Wayback Machine) for wines. In the data itself, an old name still selling under another code marked two separate products.
5. **Final calls:** Recipe tweaks were treated as the same product. The last few codes were decided by hand from packaging photos, archived pages and producer bios.


## Data gaps
The dataset covers Jun 2017 - Feb 2018, Jan 2019 - Nov 2019, Jan/Mar/Jul/Sep 2020, and Jun - Aug 2026. **Nothing exists for 2021–2025**, so this is a two-point comparison, not a trend.

## Re-run
```
pip install -r requirements.txt
python clean.py            # downloads the latest data
python clean.py file.csv   # or use a file you already have
```
