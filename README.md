# Project 2: Sales Performance Dashboard & Business Insights

A comprehensive data analysis project that explores a retail sales dataset to uncover revenue trends, regional performance gaps, product profitability, and actionable business recommendations.

Built as part of a **Computer Science with Data Analytics** portfolio.

---

## Project Structure

```
Project2_Sales_Dashboard/
├── data/
│   ├── generate_sales_data.py   # Generates the synthetic dataset
│   ├── sales_data.csv           # Generated CSV (5,000 rows)
│   └── sales_data.xlsx          # Generated Excel file
├── images/                      # All charts saved here (auto-created)
├── output/
│   └── business_insights_report.txt   # Final text report
├── sales_analysis.py            # Main analysis script (8 steps)
├── sql_queries.sql              # 12 SQL queries for data extraction
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate the Dataset

```bash
python data/generate_sales_data.py
```

This creates `data/sales_data.csv` and `data/sales_data.xlsx` with 5,000 realistic retail transaction records spanning January 2023 to December 2024.

### 3. Run the Analysis

```bash
python sales_analysis.py
```

This runs all eight analysis steps, prints results to the console, saves nine charts to `images/`, and writes a business insights report to `output/`.

---

## Dataset Description

| Column | Description |
|--------|-------------|
| `order_id` | Unique order identifier |
| `order_date` | Date the order was placed (2023-01-01 to 2024-12-31) |
| `ship_date` | Date the order was shipped |
| `customer_id` | Unique customer identifier |
| `customer_name` | Customer full name |
| `segment` | Consumer, Corporate, or Home Office |
| `region` | East, West, South, or North |
| `state` | US state |
| `city` | City name |
| `category` | Furniture, Office Supplies, or Technology |
| `sub_category` | Detailed product type (14 sub-categories) |
| `product_name` | Product name |
| `quantity` | Units ordered |
| `unit_price` | Price per unit |
| `discount` | Discount applied (0% to 40%) |
| `revenue` | Total revenue after discount |
| `cost` | Total cost of goods |
| `profit` | Revenue minus cost |

**Realistic patterns baked into the data:**
- Technology products have the highest margins (25-40%)
- Furniture products occasionally generate losses, especially with heavy discounts
- Q4 (Oct-Dec) has a seasonal sales spike simulating holiday shopping
- The South region deliberately underperforms due to higher logistics costs

---

## Analysis Steps

| Step | What It Does | Key Output |
|------|-------------|------------|
| 1. Data Loading | Load CSV, inspect shape, dtypes, summary stats | Console output |
| 2. Data Cleaning | Handle missing values, parse dates, add calculated columns | Enriched DataFrame |
| 3. Revenue & Profit | KPIs, monthly trend, quarterly comparison | 2 charts |
| 4. Regional Analysis | Revenue/profit by region, pie chart, margin comparison | 3 charts |
| 5. Category Analysis | Sub-category revenue, top/bottom products | 3 charts |
| 6. Segment Analysis | Consumer vs Corporate vs Home Office | 1 chart |
| 7. Discount Impact | Correlation analysis, scatter plot, margin erosion | 2 charts |
| 8. Business Insights | Top 5 actionable recommendations | Text report |

---

## SQL Queries Explanation

The `sql_queries.sql` file contains 12 queries designed to demonstrate proficiency with SQL for data extraction and aggregation. These queries are written as if running against a `sales_data` table and can be executed in any SQL engine (SQLite, MySQL, PostgreSQL).

| Query | Purpose | Business Value |
|-------|---------|---------------|
| 1 | Executive summary KPIs | Baseline metrics for all analysis |
| 2 | Monthly revenue trend | Seasonality and growth tracking |
| 3 | Revenue/profit by region | Geographic performance comparison |
| 4 | Top 10 products by revenue | Identify cash-cow products |
| 5 | Category and sub-category breakdown | Product line health check |
| 6 | Customer segment analysis | Tailor strategy per segment |
| 7 | Underperforming regions | Flag regions below 10% margin |
| 8 | Year-over-year growth | Demonstrate business trajectory |
| 9 | Discount impact by bucket | Find the discount threshold that destroys margins |
| 10 | Customer retention tiers | One-time vs returning vs loyal customers |
| 11 | Shipping efficiency by region | Identify logistics bottlenecks |
| 12 | Best quarter by category | Seasonal inventory planning |

---

## Expected Outputs

### Charts (saved to `images/`)

1. `monthly_revenue_trend.png` - Line chart showing revenue over 24 months
2. `quarterly_revenue_comparison.png` - Bar chart comparing Q1-Q4 across both years
3. `region_revenue_profit.png` - Grouped bar chart of revenue and profit per region
4. `region_revenue_pie.png` - Pie chart of revenue share by region
5. `region_profit_margin.png` - Horizontal bar chart with 10% threshold line
6. `subcategory_revenue.png` - Horizontal bar chart for all 14 sub-categories
7. `category_profit_margin.png` - Bar chart comparing margins across 3 categories
8. `top_bottom_products_profit.png` - Side-by-side top 10 and bottom 10 products
9. `segment_analysis.png` - Three-panel chart (revenue, AOV, frequency by segment)
10. `discount_vs_profit_scatter.png` - Scatter plot colored by profit margin
11. `avg_profit_by_discount.png` - Bar chart showing profit erosion at each discount level

### Report (saved to `output/`)

`business_insights_report.txt` contains KPIs, five actionable insights with recommendations, and regional/category breakdowns.

---

## Tools & Technologies

- **Python 3.x** - Core programming language
- **pandas** - Data manipulation and aggregation
- **NumPy** - Numerical computations
- **Matplotlib** - Base plotting library
- **Seaborn** - Statistical visualization themes
- **SQL** - Data querying (demonstrated in sql_queries.sql)

---

## Key Findings (Preview)

1. **Q4 seasonal spike** - Holiday shopping drives significantly higher revenue in Oct-Dec
2. **South region underperformance** - Lower margins due to higher logistics costs
3. **Discount erosion** - Discounts above 20-25% sharply reduce or eliminate profitability
4. **Technology leads margins** - Highest profit margin category; expand this line
5. **Loss-making Furniture orders** - Heavily discounted Furniture sells below cost

---

## Author

Ravneet - Computer Science with Data Analytics, 2nd Year Undergraduate
