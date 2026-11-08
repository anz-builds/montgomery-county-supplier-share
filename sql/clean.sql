-- 1. Numbers: "(0.17)" -> -0.17, strip commas, cast; blanks -> NULL
CREATE TABLE step1 AS
SELECT
  YEAR, MONTH, "ITEM CODE", "ITEM TYPE",
  SUPPLIER, "ITEM DESCRIPTION",
  CASE WHEN TRIM("RETAIL SALES") = '' THEN NULL
       WHEN TRIM("RETAIL SALES") LIKE '(%)' THEN -CAST(REPLACE(REPLACE(REPLACE(TRIM("RETAIL SALES"), '(', ''), ')', ''), ',', '') AS REAL)
       ELSE CAST(REPLACE(TRIM("RETAIL SALES"), ',', '') AS REAL) END AS "RETAIL SALES",
  CASE WHEN TRIM("RETAIL TRANSFERS") = '' THEN NULL
       WHEN TRIM("RETAIL TRANSFERS") LIKE '(%)' THEN -CAST(REPLACE(REPLACE(REPLACE(TRIM("RETAIL TRANSFERS"), '(', ''), ')', ''), ',', '') AS REAL)
       ELSE CAST(REPLACE(TRIM("RETAIL TRANSFERS"), ',', '') AS REAL) END AS "RETAIL TRANSFERS",
  CASE WHEN TRIM("WAREHOUSE SALES") = '' THEN NULL
       WHEN TRIM("WAREHOUSE SALES") LIKE '(%)' THEN -CAST(REPLACE(REPLACE(REPLACE(TRIM("WAREHOUSE SALES"), '(', ''), ')', ''), ',', '') AS REAL)
       ELSE CAST(REPLACE(TRIM("WAREHOUSE SALES"), ',', '') AS REAL) END AS "WAREHOUSE SALES"
FROM raw;

-- 4. Text: tabs/line breaks -> space, collapse runs of spaces, trim
UPDATE step1 SET
  SUPPLIER = REPLACE(REPLACE(REPLACE(SUPPLIER, char(9), ' '), char(10), ' '), char(13), ' '),
  "ITEM DESCRIPTION" = REPLACE(REPLACE(REPLACE("ITEM DESCRIPTION", char(9), ' '), char(10), ' '), char(13), ' ');
-- SQLite has no regex replace: each pass turns double spaces into single; 5 passes cover runs up to 32 spaces
UPDATE step1 SET SUPPLIER = REPLACE(SUPPLIER, '  ', ' '), "ITEM DESCRIPTION" = REPLACE("ITEM DESCRIPTION", '  ', ' ');
UPDATE step1 SET SUPPLIER = REPLACE(SUPPLIER, '  ', ' '), "ITEM DESCRIPTION" = REPLACE("ITEM DESCRIPTION", '  ', ' ');
UPDATE step1 SET SUPPLIER = REPLACE(SUPPLIER, '  ', ' '), "ITEM DESCRIPTION" = REPLACE("ITEM DESCRIPTION", '  ', ' ');
UPDATE step1 SET SUPPLIER = REPLACE(SUPPLIER, '  ', ' '), "ITEM DESCRIPTION" = REPLACE("ITEM DESCRIPTION", '  ', ' ');
UPDATE step1 SET SUPPLIER = REPLACE(SUPPLIER, '  ', ' '), "ITEM DESCRIPTION" = REPLACE("ITEM DESCRIPTION", '  ', ' ');
UPDATE step1 SET SUPPLIER = TRIM(SUPPLIER), "ITEM DESCRIPTION" = TRIM("ITEM DESCRIPTION");

-- 4c. Merge supplier renames (same company, same item codes)
UPDATE step1 SET SUPPLIER = 'FIFTH GENERATION DISTILLED SPIRITS, INC' WHERE SUPPLIER = 'FIFTH GENERATION INC';

-- 2, 3, 4b, 5, 8. Filters
CREATE TABLE step2 AS
SELECT * FROM step1
WHERE "RETAIL SALES" IS NOT NULL
  AND "ITEM TYPE" IN ('BEER', 'WINE', 'LIQUOR')
  AND SUPPLIER <> ''
  AND (COALESCE("RETAIL SALES",0) <> 0 OR COALESCE("RETAIL TRANSFERS",0) <> 0 OR COALESCE("WAREHOUSE SALES",0) <> 0)
  AND YEAR IN ('2019', '2026') AND MONTH IN ('6', '7', '8');

-- 6. Product key from the item-code lookup (one row per code + description)
--    align -> the code's latest description; keep separate or not in lookup -> the row's own description
CREATE TABLE sales_clean AS
SELECT s.YEAR, s.MONTH, s.SUPPLIER, s."ITEM CODE",
  s."ITEM CODE" || ' | ' || COALESCE(l.product_description, UPPER(s."ITEM DESCRIPTION")) AS product_key,
  COALESCE(l.product_description, UPPER(s."ITEM DESCRIPTION")) AS product_description,
  s."ITEM TYPE", s."RETAIL SALES", s."RETAIL TRANSFERS", s."WAREHOUSE SALES"
FROM step2 s
LEFT JOIN lookup l
  ON l.item_code = s."ITEM CODE"
 AND l.description = UPPER(s."ITEM DESCRIPTION");
