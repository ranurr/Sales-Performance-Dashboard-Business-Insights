# sales_analysis.py
# full analysis of the superstore dataset
# run this to generate all the charts and stuff for the dashboard
# Ravneet - Project 2

import os
import math
import json
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
# tried seaborn for this but matplotlib looked better for most charts
import seaborn as sns

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", palette="Set2", font_scale=1.1)
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["figure.dpi"] = 150
plt.rcParams["savefig.bbox"] = "tight"

# paths setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "superstore_real.csv")
IMG_DIR = os.path.join(BASE_DIR, "images")
OUT_DIR = os.path.join(BASE_DIR, "output")
dataDir = os.path.join(BASE_DIR, "data")  # yeah i know inconsistent naming lol

os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)


# =====================================================
# STEP 1 - Load the CSV
# =====================================================
print("\n" + "=" * 70)
print("  STEP 1: Data Loading & Overview")
print("=" * 70)

sales_dataframe = pd.read_csv(DATA_PATH, encoding='latin-1')
print()
print("Dataset shape: {} rows x {} columns".format(sales_dataframe.shape[0], sales_dataframe.shape[1]))
print()
print("Column types:")
print(sales_dataframe.dtypes)
print()
print("First 5 rows:")
print(sales_dataframe.head().to_string(index=False))
print()

# quick summary stats
print("Summary statistics:")
print(sales_dataframe.describe().round(2).to_string())

numberOfRows = len(sales_dataframe)
print(f"\nTotal rows loaded: {numberOfRows}")


# =====================================================
# STEP 2 - Clean and prepare the data
# =====================================================
print("\n" + "=" * 70)
print("  STEP 2: Data Cleaning & Preparation")
print("=" * 70)

# check for missing values first
missing_vals = sales_dataframe.isnull().sum()
total_missing = missing_vals.sum()
if total_missing == 0:
    print("\nNo missing values - nice!")
else:
    print(f"\nFound {total_missing} missing values:")
    print(missing_vals[missing_vals > 0])
    # fill them in with median/mode
    for col in sales_dataframe.columns:
        if sales_dataframe[col].isnull().any():
            if sales_dataframe[col].dtype in ["float64", "int64"]:
                sales_dataframe[col].fillna(sales_dataframe[col].median(), inplace=True)
            else:
                sales_dataframe[col].fillna(sales_dataframe[col].mode()[0], inplace=True)
    print("Filled missing values with median/mode.")

# parse date columns - format is like 11/8/2017
sales_dataframe["Order Date"] = pd.to_datetime(sales_dataframe["Order Date"])
sales_dataframe["Ship Date"] = pd.to_datetime(sales_dataframe["Ship Date"])
print("Parsed Order Date and Ship Date as datetime.")

# add some calculated columns for the analysis
# profit_margin = Profit / Sales * 100 (gotta watch out for zero sales tho)
sales_dataframe["profit_margin"] = np.where(
    sales_dataframe["Sales"] != 0,
    round(sales_dataframe["Profit"] / sales_dataframe["Sales"] * 100, 2),
    0
)
sales_dataframe["month"] = sales_dataframe["Order Date"].dt.month
sales_dataframe["quarter"] = sales_dataframe["Order Date"].dt.quarter
sales_dataframe["year"] = sales_dataframe["Order Date"].dt.year
sales_dataframe["day_of_week"] = sales_dataframe["Order Date"].dt.day_name()
sales_dataframe["year_month"] = sales_dataframe["Order Date"].dt.to_period("M")

# tried computing shipping days but it gave weird results for some rows
# sales_dataframe["ship_days"] = (sales_dataframe["Ship Date"] - sales_dataframe["Order Date"]).dt.days

print("Added columns: profit_margin, month, quarter, year, day_of_week, year_month")
print(f"Final shape: {sales_dataframe.shape[0]} rows x {sales_dataframe.shape[1]} columns")

# shortcut variable because typing sales_dataframe is annoying
df = sales_dataframe


# =====================================================
# STEP 3 - Revenue & Profit Analysis
# =====================================================
print("\n" + "=" * 70)
print("  STEP 3: Revenue & Profit Analysis")
print("=" * 70)

totalSales = df["Sales"].sum()
total_profit = df["Profit"].sum()
overall_margin = total_profit / totalSales * 100
total_orders = df["Order ID"].nunique()
avgOrderVal = df.groupby("Order ID")["Sales"].sum().mean()

print(f"\n  Total Sales        : ${totalSales:>14,.2f}")
print(f"  Total Profit       : ${total_profit:>14,.2f}")
print(f"  Overall Margin     : {overall_margin:>13.2f}%")
print("  Total Orders       : {:>14,}".format(total_orders))
print(f"  Avg Order Value    : ${avgOrderVal:>14,.2f}")
print()

# 3a - monthly sales trend chart
monthly_data = (df.groupby("year_month")["Sales"]
                .sum()
                .reset_index()
                .rename(columns={"Sales": "monthly_sales"}))
monthly_data["year_month"] = monthly_data["year_month"].astype(str)

# also grab monthly profit for saving
monthly_profit_data = (df.groupby(df["year_month"].astype(str))["Profit"]
                       .sum()
                       .reset_index()
                       .rename(columns={"Profit": "monthly_profit"}))

monthly_trend = monthly_data.copy()
monthly_trend["monthly_profit"] = monthly_profit_data["monthly_profit"].values

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(monthly_data["year_month"], monthly_data["monthly_sales"],
        marker="o", linewidth=2, markersize=5, color="#2196F3")
ax.fill_between(range(len(monthly_data)), monthly_data["monthly_sales"],
                alpha=0.15, color="#2196F3")
ax.set_title("Monthly Sales Trend", fontsize=15, fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Sales ($)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
# show every 3rd label so it doesnt get too crowded
ax.set_xticks(range(0, len(monthly_data), 3))
ax.set_xticklabels(monthly_data["year_month"].iloc[::3], rotation=45, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "monthly_revenue_trend.png"))
plt.close()
print("  [Saved] images/monthly_revenue_trend.png")

# save the monthly trend data
monthly_trend.to_csv(os.path.join(dataDir, "monthly_trend.csv"), index=False)
print("  [Saved] data/monthly_trend.csv")

# 3b - quarterly sales comparison
quarterly = (df.groupby(["year", "quarter"])
             .agg(sales=("Sales", "sum"), profit=("Profit", "sum"))
             .reset_index())
quarterly["label"] = quarterly.apply(
    lambda r: "{} Q{}".format(int(r['year']), int(r['quarter'])), axis=1)

fig, ax = plt.subplots(figsize=(12, 5))
x = range(len(quarterly))
bars = ax.bar(x, quarterly["sales"], color="#4CAF50", edgecolor="white", width=0.6)
ax.set_xticks(list(x))
ax.set_xticklabels(quarterly["label"], rotation=45, ha="right")
ax.set_title("Quarterly Sales Comparison", fontsize=15, fontweight="bold")
ax.set_ylabel("Sales ($)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

for bar, val in zip(bars, quarterly["sales"]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1000,
            f"${val:,.0f}", ha="center", va="bottom", fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "quarterly_revenue_comparison.png"))
plt.close()
print("  [Saved] images/quarterly_revenue_comparison.png")


# =====================================================
# STEP 4 - Regional Analysis
# =====================================================
print("\n" + "=" * 70)
print("  STEP 4: Regional Analysis")
print("=" * 70)

region_stats = (df.groupby("Region")
                .agg(total_sales=("Sales", "sum"),
                     total_profit=("Profit", "sum"),
                     orders=("Order ID", "nunique"))
                .reset_index())
region_stats["profit_margin"] = round(
    region_stats["total_profit"] / region_stats["total_sales"] * 100, 2)
region_stats = region_stats.sort_values("total_sales", ascending=False)

print("\n  Sales & Profit by Region:")
print("  " + "-" * 65)
print(f"  {'Region':<10} {'Sales':>14} {'Profit':>14} {'Margin':>8} {'Orders':>8}")
print("  " + "-" * 65)
for idx, r in region_stats.iterrows():
    # wow south region really underperforms
    flag = " ** LOW" if r["profit_margin"] < 10 else ""
    print(f"  {r['Region']:<10} ${r['total_sales']:>13,.2f} ${r['total_profit']:>13,.2f}"
          f" {r['profit_margin']:>7.2f}% {r['orders']:>7}{flag}")

print()

# save region stats csv
region_stats.to_csv(os.path.join(dataDir, "region_stats.csv"), index=False)
print("  [Saved] data/region_stats.csv")

# 4a - grouped bar chart for sales vs profit
fig, ax = plt.subplots(figsize=(10, 5))
x = np.arange(len(region_stats))
w = 0.35
ax.bar(x - w / 2, region_stats["total_sales"], w, label="Sales", color="#2196F3")
ax.bar(x + w / 2, region_stats["total_profit"], w, label="Profit", color="#FF9800")
ax.set_xticks(x)
ax.set_xticklabels(region_stats["Region"])
ax.set_title("Sales & Profit by Region", fontsize=15, fontweight="bold")
ax.set_ylabel("Amount ($)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "region_revenue_profit.png"))
plt.close()
print("  [Saved] images/region_revenue_profit.png")

# 4b - pie chart for regional sales share
fig, ax = plt.subplots(figsize=(7, 7))
colors_pie = ["#2196F3", "#4CAF50", "#FF9800", "#E91E63"]
wedges, texts, autotexts = ax.pie(
    region_stats["total_sales"], labels=region_stats["Region"],
    autopct="%1.1f%%", colors=colors_pie, startangle=140,
    textprops={"fontsize": 12})
for at in autotexts:
    at.set_fontweight("bold")
ax.set_title("Sales Share by Region", fontsize=15, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "region_revenue_pie.png"))
plt.close()
print("  [Saved] images/region_revenue_pie.png")

# 4c - profit margin by region horizontal bars
fig, ax = plt.subplots(figsize=(8, 5))
colors_margin = ["#4CAF50" if m >= 10 else "#F44336"
                 for m in region_stats["profit_margin"]]
ax.barh(region_stats["Region"], region_stats["profit_margin"],
        color=colors_margin, edgecolor="white", height=0.5)
ax.axvline(x=10, color="gray", linestyle="--", linewidth=1, label="10% threshold")
ax.set_title("Profit Margin by Region", fontsize=15, fontweight="bold")
ax.set_xlabel("Profit Margin (%)")
ax.legend()
for i, v in enumerate(region_stats["profit_margin"]):
    ax.text(v + 0.3, i, f"{v:.1f}%", va="center", fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "region_profit_margin.png"))
plt.close()
print("  [Saved] images/region_profit_margin.png")


# =====================================================
# STEP 5 - Product Category Analysis
# =====================================================
print("\n" + "=" * 70)
print("  STEP 5: Product Category Analysis")
print("=" * 70)

# 5a - breakdown by category and sub-category
subcat = (df.groupby(["Category", "Sub-Category"])
          .agg(total_sales=("Sales", "sum"), total_profit=("Profit", "sum"))
          .reset_index())
subcat["profit_margin"] = round(subcat["total_profit"] / subcat["total_sales"] * 100, 2)
subcat = subcat.sort_values("total_sales", ascending=True)

fig, ax = plt.subplots(figsize=(12, 8))
cat_colors = {"Furniture": "#FF9800", "Office Supplies": "#2196F3", "Technology": "#4CAF50"}
bar_colors = [cat_colors[cat] for cat in subcat["Category"]]
ax.barh(subcat["Sub-Category"], subcat["total_sales"], color=bar_colors, edgecolor="white")
ax.set_title("Sales by Sub-Category", fontsize=15, fontweight="bold")
ax.set_xlabel("Sales ($)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

from matplotlib.patches import Patch
legend_items = [Patch(facecolor=c, label=k) for k, c in cat_colors.items()]
ax.legend(handles=legend_items, loc="lower right")
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "subcategory_revenue.png"))
plt.close()
print("\n  [Saved] images/subcategory_revenue.png")

# category level stats
cat_stats = (df.groupby("Category")
             .agg(total_sales=("Sales", "sum"), total_profit=("Profit", "sum"))
             .reset_index())
cat_stats["profit_margin"] = round(
    cat_stats["total_profit"] / cat_stats["total_sales"] * 100, 2)
cat_stats = cat_stats.sort_values("profit_margin", ascending=False)

print("\n  Profit Margin by Category:")
print("  " + "-" * 50)
for idx, r in cat_stats.iterrows():
    # this is interesting - technology has way higher margin
    print(f"  {r['Category']:<18} Margin: {r['profit_margin']:>7.2f}%"
          f"  Sales: ${r['total_sales']:>12,.2f}")

# save category stats
cat_stats.to_csv(os.path.join(dataDir, "category_stats.csv"), index=False)
print("\n  [Saved] data/category_stats.csv")

# profit margin bar chart by category
fig, ax = plt.subplots(figsize=(8, 5))
bar_c = [cat_colors.get(c, "#999") for c in cat_stats["Category"]]
ax.bar(cat_stats["Category"], cat_stats["profit_margin"], color=bar_c,
       edgecolor="white", width=0.5)
ax.set_title("Profit Margin by Category", fontsize=15, fontweight="bold")
ax.set_ylabel("Profit Margin (%)")
for i, (cat, m) in enumerate(zip(cat_stats["Category"], cat_stats["profit_margin"])):
    ax.text(i, m + 0.3, f"{m:.1f}%", ha="center", fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "category_profit_margin.png"))
plt.close()
print("  [Saved] images/category_profit_margin.png")

# 5b - top and bottom products by profit
product_profit = (df.groupby("Product Name")
                  .agg(total_profit=("Profit", "sum"), total_sales=("Sales", "sum"))
                  .reset_index()
                  .sort_values("total_profit", ascending=False))

top10 = product_profit.head(10)
bottom10 = product_profit.tail(10).sort_values("total_profit", ascending=True)

print("\n  Top 10 Products by Profit:")
for idx, r in top10.iterrows():
    productNameShort = r["Product Name"][:40]
    print(f"    {productNameShort:<42} Profit: ${r['total_profit']:>10,.2f}")

print()
print("  Bottom 10 Products by Profit:")
for idx, r in bottom10.iterrows():
    productNameShort = r["Product Name"][:40]
    print(f"    {productNameShort:<42} Profit: ${r['total_profit']:>10,.2f}")

# TODO: maybe add a treemap for categories later

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

axes[0].barh(top10["Product Name"].str[:30], top10["total_profit"], color="#4CAF50", edgecolor="white")
axes[0].set_title("Top 10 Products by Profit", fontweight="bold")
axes[0].set_xlabel("Profit ($)")
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
axes[0].invert_yaxis()

axes[1].barh(bottom10["Product Name"].str[:30], bottom10["total_profit"], color="#F44336", edgecolor="white")
axes[1].set_title("Bottom 10 Products by Profit", fontweight="bold")
axes[1].set_xlabel("Profit ($)")
axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "top_bottom_products_profit.png"))
plt.close()
print("  [Saved] images/top_bottom_products_profit.png")


# =====================================================
# STEP 6 - Customer Segment Analysis
# =====================================================
print("\n" + "=" * 70)
print("  STEP 6: Customer Segment Analysis")
print("=" * 70)

seg = (df.groupby("Segment")
       .agg(total_sales=("Sales", "sum"),
            total_profit=("Profit", "sum"),
            orders=("Order ID", "nunique"),
            customers=("Customer ID", "nunique"))
       .reset_index())
seg["avg_order_value"] = round(seg["total_sales"] / seg["orders"], 2)
seg["orders_per_customer"] = round(seg["orders"] / seg["customers"], 2)
seg = seg.sort_values("total_sales", ascending=False)

print("\n  Customer Segment Breakdown:")
print("  " + "-" * 75)
print(f"  {'Segment':<15} {'Sales':>13} {'Profit':>13} {'AOV':>10}"
      f" {'Orders':>7} {'Freq':>6}")
print("  " + "-" * 75)
for idx, r in seg.iterrows():
    print(f"  {r['Segment']:<15} ${r['total_sales']:>12,.2f} ${r['total_profit']:>12,.2f}"
          f" ${r['avg_order_value']:>9,.2f} {r['orders']:>7}"
          f" {r['orders_per_customer']:>5.1f}")

# save segment stats csv
seg.to_csv(os.path.join(dataDir, "segment_stats.csv"), index=False)
print("\n  [Saved] data/segment_stats.csv")

# segment comparison charts - 3 side by side
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
seg_colors = ["#2196F3", "#4CAF50", "#FF9800"]

axes[0].bar(seg["Segment"], seg["total_sales"], color=seg_colors, edgecolor="white")
axes[0].set_title("Sales by Segment", fontweight="bold")
axes[0].set_ylabel("Sales ($)")
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

axes[1].bar(seg["Segment"], seg["avg_order_value"], color=seg_colors, edgecolor="white")
axes[1].set_title("Avg Order Value by Segment", fontweight="bold")
axes[1].set_ylabel("Avg Order Value ($)")

axes[2].bar(seg["Segment"], seg["orders_per_customer"], color=seg_colors, edgecolor="white")
axes[2].set_title("Order Frequency per Customer", fontweight="bold")
axes[2].set_ylabel("Orders / Customer")

plt.suptitle("Customer Segment Analysis", fontsize=15, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "segment_analysis.png"))
plt.close()
print("  [Saved] images/segment_analysis.png")


# =====================================================
# STEP 7 - Discount Impact Analysis
# =====================================================
print("\n" + "=" * 70)
print("  STEP 7: Discount Impact Analysis")
print("=" * 70)

# check correlation between discount and profit margin
corr_value = df[["Discount", "profit_margin"]].corr().iloc[0, 1]
print(f"\n  Correlation (Discount vs profit_margin): {corr_value:.4f}")
if corr_value < -0.3:
    print("  Strong negative correlation - discounts are hurting margins!")
elif corr_value < 0:
    print("  Weak negative correlation.")
else:
    print("  No clear negative correlation found.")

print()

# group by discount level (as percentage)
# discount in dataset is 0-0.8 range so multiply by 100 to get pct
discount_pct_col = (df["Discount"] * 100).astype(int)
disc_impact = (df.assign(discount_pct=discount_pct_col)
               .groupby("discount_pct")
               .agg(avg_profit=("Profit", "mean"),
                    avg_margin=("profit_margin", "mean"),
                    count=("Order ID", "count"))
               .reset_index())

print("  Avg Profit & Margin at Each Discount Level:")
print("  " + "-" * 55)
print(f"  {'Discount':>8} {'Avg Profit':>12} {'Avg Margin':>12} {'# Orders':>10}")
print("  " + "-" * 55)
for idx, r in disc_impact.iterrows():
    print(f"  {r['discount_pct']:>7}% ${r['avg_profit']:>11,.2f}"
          f" {r['avg_margin']:>11.2f}% {r['count']:>10}")

# save discount impact data
disc_impact.to_csv(os.path.join(dataDir, "discount_impact.csv"), index=False)
print("\n  [Saved] data/discount_impact.csv")

# 7a - scatter plot of discount vs profit
fig, ax = plt.subplots(figsize=(10, 6))
sample_size = min(2000, len(df))
sample = df.sample(sample_size, random_state=42)
scatter = ax.scatter(sample["Discount"] * 100, sample["Profit"],
                     c=sample["profit_margin"], cmap="RdYlGn",
                     alpha=0.5, s=20, edgecolors="none")
ax.axhline(y=0, color="red", linestyle="--", linewidth=1, alpha=0.7)
ax.set_title("Discount vs Profit (colored by margin)", fontsize=15, fontweight="bold")
ax.set_xlabel("Discount (%)")
ax.set_ylabel("Profit ($)")
plt.colorbar(scatter, label="Profit Margin (%)")
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "discount_vs_profit_scatter.png"))
plt.close()
print("  [Saved] images/discount_vs_profit_scatter.png")

# 7b - bar chart showing average profit at each discount level
fig, ax = plt.subplots(figsize=(10, 5))
bar_colors_disc = ["#4CAF50" if p >= 0 else "#F44336" for p in disc_impact["avg_profit"]]
ax.bar(disc_impact["discount_pct"].astype(str) + "%",
       disc_impact["avg_profit"], color=bar_colors_disc, edgecolor="white")
ax.axhline(y=0, color="black", linewidth=0.8)
ax.set_title("Average Profit by Discount Level", fontsize=15, fontweight="bold")
ax.set_xlabel("Discount (%)")
ax.set_ylabel("Average Profit ($)")
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "avg_profit_by_discount.png"))
plt.close()
print("  [Saved] images/avg_profit_by_discount.png")


# =====================================================
# STEP 8 - Business Insights & Report Generation
# =====================================================
print("\n" + "=" * 70)
print("  STEP 8: Key Business Insights Summary")
print("=" * 70)

# compute the numbers we need for the insights
region_data = (df.groupby("Region")
               .agg(total_sales=("Sales", "sum"), total_profit=("Profit", "sum"))
               .reset_index())
region_data["margin"] = region_data["total_profit"] / region_data["total_sales"] * 100
worst_region = region_data.loc[region_data["margin"].idxmin()]
best_region = region_data.loc[region_data["margin"].idxmax()]

cat_data = (df.groupby("Category")
            .agg(total_sales=("Sales", "sum"), total_profit=("Profit", "sum"))
            .reset_index())
cat_data["margin"] = cat_data["total_profit"] / cat_data["total_sales"] * 100
best_cat = cat_data.loc[cat_data["margin"].idxmax()]
worst_cat = cat_data.loc[cat_data["margin"].idxmin()]

# discount impact numbers - high vs low discount
high_disc = df[df["Discount"] >= 0.30]
low_disc = df[df["Discount"] <= 0.05]

# TODO: maybe add more granular discount buckets later
high_disc_margin = 0
low_disc_margin = 0
if high_disc["Sales"].sum() > 0:
    high_disc_margin = high_disc["Profit"].sum() / high_disc["Sales"].sum() * 100
if low_disc["Sales"].sum() > 0:
    low_disc_margin = low_disc["Profit"].sum() / low_disc["Sales"].sum() * 100

# check if q4 has a seasonal spike
q4_sales = df[df["quarter"] == 4]["Sales"].sum()
non_q4_avg = df[df["quarter"] != 4].groupby("quarter")["Sales"].sum().mean()
q4_lift = (q4_sales - non_q4_avg) / non_q4_avg * 100 if non_q4_avg > 0 else 0

# year over year growth
yearly_sales = df.groupby("year")["Sales"].sum()
yoy_growth = 0
if len(yearly_sales) >= 2:
    sorted_years = yearly_sales.sort_index()
    yoy_growth = (sorted_years.iloc[-1] - sorted_years.iloc[0]) / sorted_years.iloc[0] * 100

# loss making orders - how many are losing money?
loss_orders = df[df["Profit"] < 0]
loss_pct = len(loss_orders) / len(df) * 100
loss_total = loss_orders["Profit"].sum()

my_insights = [
    f"1. SEASONAL Q4 SPIKE: Q4 sales is {q4_lift:.1f}% higher than the "
    f"average of other quarters. Recommendation: Stock up inventory and "
    f"increase marketing spend before October.",

    f"2. REGIONAL UNDERPERFORMANCE: The {worst_region['Region']} region has the "
    f"lowest profit margin at {worst_region['margin']:.1f}% vs. "
    f"{best_region['Region']}'s {best_region['margin']:.1f}%. "
    f"Recommendation: Investigate logistics costs and pricing strategy.",

    f"3. DISCOUNT EROSION: Orders with 30%+ discounts have a margin of "
    f"{high_disc_margin:.1f}%, compared to {low_disc_margin:.1f}% for "
    f"orders with 0-5% discount. Recommendation: Cap standard discounts at "
    f"20% and require approval for anything higher.",

    f"4. {best_cat['Category'].upper()} IS THE MARGIN LEADER: "
    f"{best_cat['Category']} achieves a {best_cat['margin']:.1f}% margin, "
    f"while {worst_cat['Category']} only achieves {worst_cat['margin']:.1f}%. "
    f"Recommendation: Expand {best_cat['Category']} and review {worst_cat['Category']} pricing.",

    f"5. LOSS-MAKING ORDERS: {loss_pct:.1f}% of line items ({len(loss_orders):,}) "
    f"generate negative profit, totaling ${abs(loss_total):,.2f} in losses. "
    f"Recommendation: Implement a minimum-margin policy to prevent selling below cost.",
]

print()
for insight in my_insights:
    print(f"  {insight}\n")

# save metrics as json for the dashboard
metrics_dict = {
    "total_sales": round(totalSales, 2),
    "total_profit": round(total_profit, 2),
    "overall_margin": round(overall_margin, 2),
    "total_orders": int(total_orders),
    "avg_order_value": round(avgOrderVal, 2),
    "yoy_growth": round(yoy_growth, 2),
    "loss_making_pct": round(loss_pct, 2)
}

with open(os.path.join(dataDir, "metrics.json"), "w") as f:
    json.dump(metrics_dict, f, indent=2)
print("  [Saved] data/metrics.json")

# save the full report to a text file
report_path = os.path.join(OUT_DIR, "business_insights_report.txt")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("=" * 70 + "\n")
    f.write("  SALES PERFORMANCE DASHBOARD - BUSINESS INSIGHTS REPORT\n")
    f.write("=" * 70 + "\n\n")
    f.write("  Report generated from {} to {}\n".format(
        df["Order Date"].min().date(), df["Order Date"].max().date()))
    f.write(f"  Total records analyzed: {len(df):,}\n\n")

    f.write("-" * 70 + "\n")
    f.write("  KEY PERFORMANCE INDICATORS\n")
    f.write("-" * 70 + "\n")
    f.write(f"  Total Sales          : ${totalSales:>14,.2f}\n")
    f.write(f"  Total Profit         : ${total_profit:>14,.2f}\n")
    f.write(f"  Overall Profit Margin: {overall_margin:>13.2f}%\n")
    f.write("  Total Orders         : {:>14,}\n".format(total_orders))
    f.write(f"  Unique Customers     : {df['Customer ID'].nunique():>14,}\n")
    f.write(f"  YoY Sales Growth     : {yoy_growth:>13.2f}%\n")
    f.write("\n")

    f.write("-" * 70 + "\n")
    f.write("  TOP 5 ACTIONABLE BUSINESS INSIGHTS\n")
    f.write("-" * 70 + "\n\n")
    for insight in my_insights:
        f.write(f"  {insight}\n\n")

    f.write("-" * 70 + "\n")
    f.write("  REGIONAL PERFORMANCE\n")
    f.write("-" * 70 + "\n")
    for idx, r in region_data.iterrows():
        f.write(f"  {r['Region']:<10} Sales: ${r['total_sales']:>12,.2f}  "
                f"Profit: ${r['total_profit']:>12,.2f}  Margin: {r['margin']:.1f}%\n")
    f.write("\n")

    f.write("-" * 70 + "\n")
    f.write("  CATEGORY PERFORMANCE\n")
    f.write("-" * 70 + "\n")
    for idx, r in cat_data.iterrows():
        f.write(f"  {r['Category']:<18} Sales: ${r['total_sales']:>12,.2f}  "
                f"Profit: ${r['total_profit']:>12,.2f}  Margin: {r['margin']:.1f}%\n")
    f.write("\n")

    f.write("=" * 70 + "\n")
    f.write("  End of Report\n")
    f.write("=" * 70 + "\n")

print(f"  [Saved] output/business_insights_report.txt")


# =====================================================
# done!
# =====================================================
print("\n" + "=" * 70)
print("  ANALYSIS COMPLETE")
print("=" * 70)
print(f"\n  All visualizations saved to: {IMG_DIR}/")
print(f"  Business report saved to:    {OUT_DIR}/business_insights_report.txt")
print(f"  Data files saved to:         {dataDir}/")
print(f"\n  Total charts generated: 9")
print("  This analysis is ready for the dashboard.\n")
