-- ============================================================================
-- SQL QUERIES FOR SUPERSTORE SALES ANALYSIS
-- ============================================================================
-- These queries are for a table called `superstore` that matches the
-- real Superstore dataset columns. Works with most SQL engines.
--
-- Columns: "Row ID", "Order ID", "Order Date", "Ship Date", "Ship Mode",
--          "Customer ID", "Customer Name", "Segment", "Country", "City",
--          "State", "Postal Code", "Region", "Product ID", "Category",
--          "Sub-Category", "Product Name", "Sales", "Quantity", "Discount",
--          "Profit"
-- ============================================================================


-- ---------------------------------------------------------------------------
-- QUERY 1: Executive Summary KPIs
-- ---------------------------------------------------------------------------
-- basic overview numbers that stakeholders always want to see first
-- ---------------------------------------------------------------------------
SELECT
    COUNT(DISTINCT "Order ID")            AS total_orders,
    COUNT(DISTINCT "Customer ID")         AS unique_customers,
    ROUND(SUM("Sales"), 2)                AS total_sales,
    ROUND(SUM("Profit"), 2)               AS total_profit,
    ROUND(SUM("Profit") / SUM("Sales") * 100, 2) AS overall_profit_margin_pct,
    ROUND(SUM("Sales") / COUNT(DISTINCT "Order ID"), 2) AS avg_order_value
FROM superstore;


-- ---------------------------------------------------------------------------
-- QUERY 2: Monthly Sales Trend
-- ---------------------------------------------------------------------------
-- shows seasonality and growth patterns month by month
-- ---------------------------------------------------------------------------
SELECT
    EXTRACT(YEAR FROM "Order Date")   AS order_year,
    EXTRACT(MONTH FROM "Order Date")  AS order_month,
    COUNT(DISTINCT "Order ID")        AS order_count,
    ROUND(SUM("Sales"), 2)            AS monthly_sales,
    ROUND(SUM("Profit"), 2)           AS monthly_profit
FROM superstore
GROUP BY order_year, order_month
ORDER BY order_year, order_month;


-- ---------------------------------------------------------------------------
-- QUERY 3: Sales and Profit by Region
-- ---------------------------------------------------------------------------
-- which regions are doing well and which need attention
-- ---------------------------------------------------------------------------
SELECT
    "Region",
    COUNT(DISTINCT "Order ID")                        AS order_count,
    ROUND(SUM("Sales"), 2)                            AS total_sales,
    ROUND(SUM("Profit"), 2)                           AS total_profit,
    ROUND(SUM("Profit") / SUM("Sales") * 100, 2)     AS profit_margin_pct
FROM superstore
GROUP BY "Region"
ORDER BY total_sales DESC;


-- ---------------------------------------------------------------------------
-- QUERY 4: Top 10 Products by Sales
-- ---------------------------------------------------------------------------
-- the highest grossing products - good to know for inventory
-- ---------------------------------------------------------------------------
SELECT
    "Product Name",
    "Category",
    "Sub-Category",
    SUM("Quantity")                                   AS units_sold,
    ROUND(SUM("Sales"), 2)                            AS total_sales,
    ROUND(SUM("Profit"), 2)                           AS total_profit,
    ROUND(SUM("Profit") / SUM("Sales") * 100, 2)     AS profit_margin_pct
FROM superstore
GROUP BY "Product Name", "Category", "Sub-Category"
ORDER BY total_sales DESC
LIMIT 10;


-- ---------------------------------------------------------------------------
-- QUERY 5: Sales by Category and Sub-Category
-- ---------------------------------------------------------------------------
-- two-level breakdown of product performance
-- ---------------------------------------------------------------------------
SELECT
    "Category",
    "Sub-Category",
    COUNT(DISTINCT "Order ID")                        AS order_count,
    ROUND(SUM("Sales"), 2)                            AS total_sales,
    ROUND(SUM("Profit"), 2)                           AS total_profit,
    ROUND(SUM("Profit") / SUM("Sales") * 100, 2)     AS profit_margin_pct
FROM superstore
GROUP BY "Category", "Sub-Category"
ORDER BY "Category", total_sales DESC;


-- ---------------------------------------------------------------------------
-- QUERY 6: Customer Segment Analysis
-- ---------------------------------------------------------------------------
-- Consumer vs Corporate vs Home Office comparison
-- ---------------------------------------------------------------------------
SELECT
    "Segment",
    COUNT(DISTINCT "Customer ID")                       AS unique_customers,
    COUNT(DISTINCT "Order ID")                          AS total_orders,
    ROUND(SUM("Sales"), 2)                              AS total_sales,
    ROUND(SUM("Profit"), 2)                             AS total_profit,
    ROUND(SUM("Sales") / COUNT(DISTINCT "Order ID"), 2)  AS avg_order_value,
    ROUND(SUM("Profit") / SUM("Sales") * 100, 2)        AS profit_margin_pct
FROM superstore
GROUP BY "Segment"
ORDER BY total_sales DESC;


-- ---------------------------------------------------------------------------
-- QUERY 7: Underperforming Regions (Margin Below 10%)
-- ---------------------------------------------------------------------------
-- flags regions that might need some attention
-- ---------------------------------------------------------------------------
SELECT
    "Region",
    ROUND(SUM("Sales"), 2)                            AS total_sales,
    ROUND(SUM("Profit"), 2)                           AS total_profit,
    ROUND(SUM("Profit") / SUM("Sales") * 100, 2)     AS profit_margin_pct
FROM superstore
GROUP BY "Region"
HAVING SUM("Profit") / SUM("Sales") * 100 < 10
ORDER BY profit_margin_pct ASC;


-- ---------------------------------------------------------------------------
-- QUERY 8: Year-over-Year Growth
-- ---------------------------------------------------------------------------
-- are we growing? compare years side by side
-- ---------------------------------------------------------------------------
SELECT
    EXTRACT(YEAR FROM "Order Date")                     AS order_year,
    COUNT(DISTINCT "Order ID")                          AS total_orders,
    COUNT(DISTINCT "Customer ID")                       AS unique_customers,
    ROUND(SUM("Sales"), 2)                              AS total_sales,
    ROUND(SUM("Profit"), 2)                             AS total_profit,
    ROUND(SUM("Profit") / SUM("Sales") * 100, 2)       AS profit_margin_pct
FROM superstore
GROUP BY order_year
ORDER BY order_year;


-- ---------------------------------------------------------------------------
-- QUERY 9: Discount Impact Analysis
-- ---------------------------------------------------------------------------
-- at what discount level do we start losing money?
-- ---------------------------------------------------------------------------
SELECT
    CASE
        WHEN "Discount" = 0    THEN '0% (No Discount)'
        WHEN "Discount" <= 0.10 THEN '1-10%'
        WHEN "Discount" <= 0.20 THEN '11-20%'
        WHEN "Discount" <= 0.30 THEN '21-30%'
        ELSE '31%+'
    END                                                 AS discount_bucket,
    COUNT(*)                                            AS order_count,
    ROUND(AVG("Discount") * 100, 1)                     AS avg_discount_pct,
    ROUND(SUM("Sales"), 2)                              AS total_sales,
    ROUND(SUM("Profit"), 2)                             AS total_profit,
    ROUND(SUM("Profit") / SUM("Sales") * 100, 2)       AS profit_margin_pct
FROM superstore
GROUP BY discount_bucket
ORDER BY avg_discount_pct;


-- ---------------------------------------------------------------------------
-- QUERY 10: Customer Retention / Repeat Purchase
-- ---------------------------------------------------------------------------
-- how many customers are one-time vs returning vs loyal
-- ---------------------------------------------------------------------------
SELECT
    purchase_tier,
    COUNT(*)                       AS customer_count,
    ROUND(AVG(total_orders), 1)    AS avg_orders,
    ROUND(AVG(total_spent), 2)     AS avg_lifetime_sales,
    ROUND(AVG(total_profit), 2)    AS avg_lifetime_profit
FROM (
    SELECT
        "Customer ID",
        COUNT(DISTINCT "Order ID")   AS total_orders,
        SUM("Sales")                 AS total_spent,
        SUM("Profit")                AS total_profit,
        CASE
            WHEN COUNT(DISTINCT "Order ID") = 1 THEN 'One-Time'
            WHEN COUNT(DISTINCT "Order ID") BETWEEN 2 AND 5 THEN 'Returning'
            ELSE 'Loyal (6+)'
        END AS purchase_tier
    FROM superstore
    GROUP BY "Customer ID"
) customer_summary
GROUP BY purchase_tier
ORDER BY avg_orders;


-- ---------------------------------------------------------------------------
-- QUERY 11: Shipping Speed by Region
-- ---------------------------------------------------------------------------
-- how fast are we shipping in each region
-- ---------------------------------------------------------------------------
SELECT
    "Region",
    COUNT(DISTINCT "Order ID")                                          AS order_count,
    ROUND(AVG(DATEDIFF("Ship Date", "Order Date")), 1)                  AS avg_ship_days,
    ROUND(MAX(DATEDIFF("Ship Date", "Order Date")), 0)                  AS max_ship_days
FROM superstore
GROUP BY "Region"
ORDER BY avg_ship_days DESC;


-- ---------------------------------------------------------------------------
-- QUERY 12: Best Quarter by Category
-- ---------------------------------------------------------------------------
-- which quarter does each category peak in
-- ---------------------------------------------------------------------------
SELECT
    "Category",
    CONCAT('Q', EXTRACT(QUARTER FROM "Order Date")) AS quarter,
    EXTRACT(YEAR FROM "Order Date")                  AS order_year,
    ROUND(SUM("Sales"), 2)                           AS quarterly_sales,
    ROUND(SUM("Profit"), 2)                          AS quarterly_profit
FROM superstore
GROUP BY "Category", order_year, quarter
ORDER BY "Category", order_year, quarter;
