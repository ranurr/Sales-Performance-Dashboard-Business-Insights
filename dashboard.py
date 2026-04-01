# dashboard.py
# streamlit dashboard for the superstore sales data
# run with: streamlit run dashboard.py
# make sure to run sales_analysis.py first to generate the data files!

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os

# page config - has to be first streamlit command
st.set_page_config(page_title="Sales Performance Dashboard", layout="wide")

# paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dataDir = os.path.join(BASE_DIR, "data")
RAW_PATH = os.path.join(dataDir, "superstore_real.csv")
IMG_DIR = os.path.join(BASE_DIR, "images")
OUT_DIR = os.path.join(BASE_DIR, "output")


# load the raw dataset
@st.cache_data
def load_raw_data():
    my_data = pd.read_csv(RAW_PATH, encoding='latin-1')
    my_data["Order Date"] = pd.to_datetime(my_data["Order Date"])
    my_data["Ship Date"] = pd.to_datetime(my_data["Ship Date"])
    my_data["year"] = my_data["Order Date"].dt.year
    my_data["month"] = my_data["Order Date"].dt.month
    my_data["year_month"] = my_data["Order Date"].dt.to_period("M").astype(str)
    # compute profit margin - same as in the analysis script
    my_data["profit_margin"] = np.where(
        my_data["Sales"] != 0,
        round(my_data["Profit"] / my_data["Sales"] * 100, 2),
        0
    )
    return my_data

raw_df = load_raw_data()

# load metrics json if it exists
@st.cache_data
def loadMetrics():
    metrics_path = os.path.join(dataDir, "metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            return json.load(f)
    return None

metrics_data = loadMetrics()

# load the business insights report
@st.cache_data
def load_report():
    report_path = os.path.join(OUT_DIR, "business_insights_report.txt")
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            return f.read()
    return None


# ---- sidebar ----
st.sidebar.title("Sales Dashboard")
st.sidebar.markdown("---")
st.sidebar.markdown("**Project 2: Sales Performance Analysis**")
st.sidebar.markdown("Dataset: Superstore ({:,} records)".format(len(raw_df)))
st.sidebar.markdown("Built with Streamlit + Plotly")
st.sidebar.markdown("---")

# sidebar filters
st.sidebar.header("Filters")

available_years = sorted(raw_df["year"].unique())
selected_years = st.sidebar.multiselect(
    "Select Year(s)",
    options=available_years,
    default=available_years
)

available_regions = sorted(raw_df["Region"].unique())
selected_regions = st.sidebar.multiselect(
    "Select Region(s)",
    options=available_regions,
    default=available_regions
)

available_categories = sorted(raw_df["Category"].unique())
selected_categories = st.sidebar.multiselect(
    "Select Category(ies)",
    options=available_categories,
    default=available_categories
)

# apply the filters
filtered_df = raw_df[
    (raw_df["year"].isin(selected_years)) &
    (raw_df["Region"].isin(selected_regions)) &
    (raw_df["Category"].isin(selected_categories))
]

# make sure we actually have data after filtering
if len(filtered_df) == 0:
    st.warning("No data matches the selected filters. Please adjust your selections.")
    st.stop()


# ---- main title ----
st.title("Sales Performance Dashboard")
st.markdown("Interactive analysis of Superstore sales data")
st.markdown("---")


# =============================================
# Row 1: KPI Cards
# =============================================
st.header("Key Performance Indicators")

totalSales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
profitMarginPct = total_profit / totalSales * 100 if totalSales > 0 else 0
total_orders = filtered_df["Order ID"].nunique()

# 4 columns for the KPI cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Sales", "${:,.0f}".format(totalSales))
with col2:
    st.metric("Total Profit", "${:,.0f}".format(total_profit))
with col3:
    st.metric("Profit Margin", "{:.1f}%".format(profitMarginPct))
with col4:
    st.metric("Total Orders", "{:,}".format(total_orders))

st.markdown("---")


# =============================================
# Row 2: Monthly Sales Trend (plotly line chart)
# =============================================
st.header("Monthly Sales Trend")

monthly = (filtered_df.groupby("year_month")
           .agg(monthly_sales=("Sales", "sum"), monthly_profit=("Profit", "sum"))
           .reset_index()
           .sort_values("year_month"))

fig_monthly = px.line(
    monthly, x="year_month", y="monthly_sales",
    title="Monthly Sales Over Time",
    labels={"year_month": "Month", "monthly_sales": "Sales ($)"},
    markers=True
)
fig_monthly.update_layout(
    xaxis_tickangle=-45,
    yaxis_tickformat="$,.0f",
    height=450
)
# show every few ticks so it doesnt get too crowded
tickStep = max(1, len(monthly) // 15)
tick_vals = monthly["year_month"].iloc[::tickStep].tolist()
fig_monthly.update_xaxes(tickvals=tick_vals)

st.plotly_chart(fig_monthly, use_container_width=True)

st.markdown("---")


# =============================================
# Row 3: Regional Analysis (bar + pie)
# =============================================
st.header("Regional Analysis")

region_stats = (filtered_df.groupby("Region")
                .agg(total_sales=("Sales", "sum"), total_profit=("Profit", "sum"))
                .reset_index())
region_stats["profit_margin"] = round(
    region_stats["total_profit"] / region_stats["total_sales"] * 100, 2)
region_stats = region_stats.sort_values("total_sales", ascending=False)

col_left, col_right = st.columns(2)

with col_left:
    # grouped bar chart for sales and profit by region
    fig_region_bar = go.Figure()
    fig_region_bar.add_trace(go.Bar(
        name="Sales", x=region_stats["Region"], y=region_stats["total_sales"],
        marker_color="#2196F3"
    ))
    fig_region_bar.add_trace(go.Bar(
        name="Profit", x=region_stats["Region"], y=region_stats["total_profit"],
        marker_color="#FF9800"
    ))
    fig_region_bar.update_layout(
        barmode="group",
        title="Sales & Profit by Region",
        yaxis_tickformat="$,.0f",
        height=400
    )
    st.plotly_chart(fig_region_bar, use_container_width=True)

with col_right:
    # pie chart for sales share
    fig_region_pie = px.pie(
        region_stats, values="total_sales", names="Region",
        title="Sales Share by Region",
        color_discrete_sequence=["#2196F3", "#4CAF50", "#FF9800", "#E91E63"]
    )
    fig_region_pie.update_layout(height=400)
    st.plotly_chart(fig_region_pie, use_container_width=True)

st.markdown("---")


# =============================================
# Row 4: Category & Sub-Category (horizontal bar)
# =============================================
st.header("Category Analysis")

subcat = (filtered_df.groupby(["Category", "Sub-Category"])
          .agg(total_sales=("Sales", "sum"), total_profit=("Profit", "sum"))
          .reset_index())
subcat["profit_margin"] = round(subcat["total_profit"] / subcat["total_sales"] * 100, 2)
subcat = subcat.sort_values("total_sales", ascending=True)

cat_color_map = {"Furniture": "#FF9800", "Office Supplies": "#2196F3", "Technology": "#4CAF50"}

fig_subcat = px.bar(
    subcat, x="total_sales", y="Sub-Category", color="Category",
    orientation="h",
    title="Sales by Sub-Category (colored by Category)",
    labels={"total_sales": "Sales ($)", "Sub-Category": ""},
    color_discrete_map=cat_color_map
)
fig_subcat.update_layout(
    xaxis_tickformat="$,.0f",
    height=500
)
st.plotly_chart(fig_subcat, use_container_width=True)

# also show category level stats side by side
cat_stats = (filtered_df.groupby("Category")
             .agg(total_sales=("Sales", "sum"), total_profit=("Profit", "sum"))
             .reset_index())
cat_stats["profit_margin"] = round(
    cat_stats["total_profit"] / cat_stats["total_sales"] * 100, 2)

col_a, col_b = st.columns(2)

with col_a:
    fig_cat_margin = px.bar(
        cat_stats, x="Category", y="profit_margin",
        title="Profit Margin by Category",
        labels={"profit_margin": "Profit Margin (%)"},
        color="Category",
        color_discrete_map=cat_color_map
    )
    fig_cat_margin.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_cat_margin, use_container_width=True)

with col_b:
    fig_cat_sales = px.bar(
        cat_stats, x="Category", y="total_sales",
        title="Total Sales by Category",
        labels={"total_sales": "Sales ($)"},
        color="Category",
        color_discrete_map=cat_color_map
    )
    fig_cat_sales.update_layout(height=400, yaxis_tickformat="$,.0f", showlegend=False)
    st.plotly_chart(fig_cat_sales, use_container_width=True)

st.markdown("---")


# =============================================
# Row 5: Discount Impact (scatter + bar)
# =============================================
st.header("Discount Impact Analysis")

col_disc1, col_disc2 = st.columns(2)

with col_disc1:
    # scatter plot - discount vs profit
    # sample if too many points so plotly doesnt lag
    sample_size = min(3000, len(filtered_df))
    if len(filtered_df) > 3000:
        sampleDf = filtered_df.sample(sample_size, random_state=42)
    else:
        sampleDf = filtered_df

    fig_scatter = px.scatter(
        sampleDf, x="Discount", y="Profit",
        color="profit_margin",
        color_continuous_scale="RdYlGn",
        title="Discount vs Profit (colored by margin)",
        labels={"Discount": "Discount", "Profit": "Profit ($)", "profit_margin": "Margin %"},
        opacity=0.5
    )
    fig_scatter.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.7)
    fig_scatter.update_layout(height=450)
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_disc2:
    # avg profit by discount level bar chart
    discount_pct_col = (filtered_df["Discount"] * 100).astype(int)
    disc_grouped = (filtered_df.assign(discount_pct=discount_pct_col)
                    .groupby("discount_pct")
                    .agg(avg_profit=("Profit", "mean"))
                    .reset_index())

    # color bars green if positive, red if negative
    disc_grouped["color"] = disc_grouped["avg_profit"].apply(
        lambda x: "Positive" if x >= 0 else "Negative"
    )

    fig_disc_bar = px.bar(
        disc_grouped, x="discount_pct", y="avg_profit",
        color="color",
        color_discrete_map={"Positive": "#4CAF50", "Negative": "#F44336"},
        title="Average Profit by Discount Level",
        labels={"discount_pct": "Discount (%)", "avg_profit": "Avg Profit ($)"}
    )
    fig_disc_bar.update_layout(height=450, showlegend=False)
    st.plotly_chart(fig_disc_bar, use_container_width=True)

st.markdown("---")


# =============================================
# Row 6: Customer Segment Analysis
# =============================================
st.header("Customer Segment Analysis")

seg = (filtered_df.groupby("Segment")
       .agg(total_sales=("Sales", "sum"),
            total_profit=("Profit", "sum"),
            orders=("Order ID", "nunique"),
            customers=("Customer ID", "nunique"))
       .reset_index())
seg["avg_order_value"] = round(seg["total_sales"] / seg["orders"], 2)
seg["orders_per_customer"] = round(seg["orders"] / seg["customers"], 2)
seg = seg.sort_values("total_sales", ascending=False)

# 3 metric cards for the segments
seg_cols = st.columns(len(seg))
for i, (idx, row) in enumerate(seg.iterrows()):
    with seg_cols[i]:
        st.subheader(row["Segment"])
        st.metric("Sales", "${:,.0f}".format(row["total_sales"]))
        st.metric("Profit", "${:,.0f}".format(row["total_profit"]))
        st.metric("Avg Order Value", "${:,.0f}".format(row["avg_order_value"]))

# segment bar charts
seg_colors = ["#2196F3", "#4CAF50", "#FF9800"]

col_s1, col_s2, col_s3 = st.columns(3)

with col_s1:
    fig_seg1 = px.bar(
        seg, x="Segment", y="total_sales",
        title="Sales by Segment",
        labels={"total_sales": "Sales ($)"},
        color="Segment",
        color_discrete_sequence=seg_colors
    )
    fig_seg1.update_layout(height=350, yaxis_tickformat="$,.0f", showlegend=False)
    st.plotly_chart(fig_seg1, use_container_width=True)

with col_s2:
    fig_seg2 = px.bar(
        seg, x="Segment", y="avg_order_value",
        title="Avg Order Value by Segment",
        labels={"avg_order_value": "AOV ($)"},
        color="Segment",
        color_discrete_sequence=seg_colors
    )
    fig_seg2.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig_seg2, use_container_width=True)

with col_s3:
    fig_seg3 = px.bar(
        seg, x="Segment", y="orders_per_customer",
        title="Order Frequency per Customer",
        labels={"orders_per_customer": "Orders / Customer"},
        color="Segment",
        color_discrete_sequence=seg_colors
    )
    fig_seg3.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig_seg3, use_container_width=True)

st.markdown("---")


# =============================================
# Row 7: Top 10 / Bottom 10 Products Table
# =============================================
st.header("Top & Bottom Products by Profit")

product_stats = (filtered_df.groupby("Product Name")
                 .agg(total_profit=("Profit", "sum"), total_sales=("Sales", "sum"))
                 .reset_index()
                 .sort_values("total_profit", ascending=False))

col_top, col_bot = st.columns(2)

with col_top:
    st.subheader("Top 10 Products")
    top10_products = product_stats.head(10).copy()
    top10_display = top10_products.copy()
    top10_display["Product Name"] = top10_display["Product Name"].str[:50]
    top10_display["total_profit"] = top10_display["total_profit"].map("${:,.2f}".format)
    top10_display["total_sales"] = top10_display["total_sales"].map("${:,.2f}".format)
    top10_display.columns = ["Product", "Profit", "Sales"]
    st.dataframe(top10_display, use_container_width=True, hide_index=True)

with col_bot:
    st.subheader("Bottom 10 Products")
    bottom10_products = product_stats.tail(10).sort_values("total_profit").copy()
    bottom10_display = bottom10_products.copy()
    bottom10_display["Product Name"] = bottom10_display["Product Name"].str[:50]
    bottom10_display["total_profit"] = bottom10_display["total_profit"].map("${:,.2f}".format)
    bottom10_display["total_sales"] = bottom10_display["total_sales"].map("${:,.2f}".format)
    bottom10_display.columns = ["Product", "Profit", "Sales"]
    st.dataframe(bottom10_display, use_container_width=True, hide_index=True)

st.markdown("---")


# =============================================
# Row 8: Business Insights (from report file)
# =============================================
st.header("Business Insights")

report_text = load_report()

if report_text is not None:
    # show the report in an expander so its not super long
    with st.expander("Click to view full Business Insights Report", expanded=True):
        st.text(report_text)
else:
    st.warning("Business insights report not found. Please run sales_analysis.py first to generate it.")
    st.info("Run: `python sales_analysis.py`")

st.markdown("---")


# ---- footer ----
st.markdown(
    "<div style='text-align: center; color: gray; padding: 20px;'>"
    "Dashboard built with Streamlit and Plotly | Data: Superstore Dataset | Project 2"
    "</div>",
    unsafe_allow_html=True
)
