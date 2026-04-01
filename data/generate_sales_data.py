"""
generate_sales_data.py
======================
Generates a realistic synthetic retail sales dataset with 5,000 rows.
The data mimics a mid-size retail company selling Furniture, Office Supplies,
and Technology products across four US regions over 2023-2024.

Realism built in:
  - Technology products carry higher margins (~25-40%)
  - Furniture occasionally produces losses (negative profit on some orders)
  - Q4 has a seasonal sales spike (holiday shopping)
  - The South region deliberately underperforms vs other regions
  - Discounts erode profit margins realistically
  - Ship dates are 1-7 days after order dates

Run:
    python data/generate_sales_data.py
Output:
    data/sales_data.csv
    data/sales_data.xlsx
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import timedelta

# ── reproducibility ──────────────────────────────────────────────────────────
random.seed(42)
np.random.seed(42)

# ── configuration ────────────────────────────────────────────────────────────
NUM_ROWS = 5000
START_DATE = pd.Timestamp("2023-01-01")
END_DATE = pd.Timestamp("2024-12-31")

# ── lookup tables ────────────────────────────────────────────────────────────

SEGMENTS = ["Consumer", "Corporate", "Home Office"]
SEGMENT_WEIGHTS = [0.52, 0.30, 0.18]          # Consumer-heavy, realistic split

REGIONS = {
    "East":  ["New York", "Philadelphia", "Boston", "Baltimore", "Richmond"],
    "West":  ["Los Angeles", "San Francisco", "Seattle", "Denver", "Phoenix"],
    "South": ["Houston", "Dallas", "Atlanta", "Miami", "Nashville"],
    "North": ["Chicago", "Detroit", "Minneapolis", "Milwaukee", "Indianapolis"],
}

REGION_WEIGHTS = [0.30, 0.28, 0.20, 0.22]     # South gets fewer orders

STATE_MAP = {
    "New York": "New York", "Philadelphia": "Pennsylvania", "Boston": "Massachusetts",
    "Baltimore": "Maryland", "Richmond": "Virginia",
    "Los Angeles": "California", "San Francisco": "California", "Seattle": "Washington",
    "Denver": "Colorado", "Phoenix": "Arizona",
    "Houston": "Texas", "Dallas": "Texas", "Atlanta": "Georgia",
    "Miami": "Florida", "Nashville": "Tennessee",
    "Chicago": "Illinois", "Detroit": "Michigan", "Minneapolis": "Minnesota",
    "Milwaukee": "Wisconsin", "Indianapolis": "Indiana",
}

# Sub-categories with (base_price_low, base_price_high, cost_ratio, margin_label)
CATEGORY_MAP = {
    "Furniture": {
        "Chairs":      (100, 600,  0.70, "low"),
        "Tables":      (150, 900,  0.72, "low"),
        "Bookcases":   (80,  500,  0.75, "low"),
        "Furnishings": (20,  150,  0.65, "low"),
    },
    "Office Supplies": {
        "Paper":       (5,   50,   0.55, "mid"),
        "Binders":     (3,   30,   0.50, "mid"),
        "Pens":        (2,   20,   0.45, "mid"),
        "Storage":     (10,  120,  0.55, "mid"),
        "Envelopes":   (2,   15,   0.50, "mid"),
        "Labels":      (3,   25,   0.48, "mid"),
    },
    "Technology": {
        "Phones":      (100, 800,  0.55, "high"),
        "Accessories":  (10, 200,  0.40, "high"),
        "Copiers":     (200, 2000, 0.60, "high"),
        "Machines":    (80,  600,  0.55, "high"),
    },
}

# Sample product names per sub-category (we will pick randomly)
PRODUCT_NAMES = {
    "Chairs":       ["Executive Leather Chair", "Mesh Office Chair", "Ergonomic Task Chair",
                     "Stackable Conference Chair", "Adjustable Swivel Chair"],
    "Tables":       ["Standing Desk Pro", "Conference Table Oak", "Round Meeting Table",
                     "L-Shaped Computer Desk", "Folding Utility Table"],
    "Bookcases":    ["5-Shelf Wooden Bookcase", "Metal Storage Bookcase",
                     "Glass Door Bookcase", "Corner Bookcase Unit"],
    "Furnishings":  ["Desk Lamp Classic", "Wall Clock Modern", "Cork Board Large",
                     "Monitor Stand Bamboo", "Cable Management Kit"],
    "Paper":        ["Recycled Copy Paper 500pk", "Premium Laser Paper", "Cardstock Pack",
                     "Legal Size Paper Ream", "Colored Paper Assorted"],
    "Binders":      ["3-Ring Binder 2in", "Presentation Binder Set", "D-Ring Binder Heavy Duty",
                     "Clear View Binder Pack"],
    "Pens":         ["Ballpoint Pen 12pk", "Gel Pen Fine Tip", "Permanent Marker Set",
                     "Highlighter Variety Pack", "Fountain Pen Classic"],
    "Storage":      ["Plastic Storage Bins 6pk", "File Cabinet 3-Drawer", "Desktop Organizer",
                     "Hanging File Folders 25pk"],
    "Envelopes":    ["Business Envelopes #10", "Manila Envelope Large", "Security Envelopes 100pk",
                     "Padded Mailer Pack"],
    "Labels":       ["Address Labels Roll 500", "File Folder Labels", "Shipping Labels 200pk",
                     "Name Badge Labels"],
    "Phones":       ["Smartphone ProMax 14", "Business Desk Phone", "Wireless Headset BT",
                     "Conference Speakerphone", "VoIP Handset Pro"],
    "Accessories":  ["USB-C Hub 7-Port", "Wireless Mouse Ergonomic", "Mechanical Keyboard RGB",
                     "Laptop Stand Aluminum", "Webcam HD 1080p"],
    "Copiers":      ["Laser Printer All-in-One", "Color Copier Office", "Inkjet MFP Compact",
                     "High-Speed Document Scanner"],
    "Machines":     ["Paper Shredder Cross-Cut", "Laminator A3 Pro", "Label Maker Portable",
                     "Electric Stapler Desktop", "Binding Machine Heavy"],
}


def generate_customer_pool(n=800):
    """Create a pool of reusable customers so repeat purchases happen."""
    first_names = [
        "James", "Mary", "Robert", "Jennifer", "Michael", "Linda", "David", "Elizabeth",
        "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah",
        "Charles", "Karen", "Christopher", "Lisa", "Daniel", "Nancy", "Matthew", "Betty",
        "Anthony", "Margaret", "Mark", "Sandra", "Steven", "Ashley", "Paul", "Dorothy",
        "Andrew", "Kimberly", "Emily", "Donna", "Brian", "Michelle", "Kevin", "Carol",
        "Aarav", "Priya", "Wei", "Yuki", "Omar", "Fatima", "Raj", "Mei", "Carlos", "Elena",
    ]
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Patel",
        "Shah", "Kim", "Nguyen", "Chen", "Singh", "Kumar", "Ali", "Santos", "Muller",
    ]
    customers = []
    for i in range(1, n + 1):
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        customers.append((f"CUST-{i:04d}", f"{fname} {lname}"))
    return customers


def weighted_order_date():
    """
    Generate an order date between START_DATE and END_DATE.
    Q4 months (Oct-Dec) are ~40 % more likely to be sampled (holiday spike).
    """
    total_days = (END_DATE - START_DATE).days
    while True:
        day_offset = random.randint(0, total_days)
        date = START_DATE + timedelta(days=day_offset)
        month = date.month
        # Accept with higher probability in Q4
        if month in (10, 11, 12):
            if random.random() < 0.95:
                return date
        else:
            if random.random() < 0.68:
                return date


def generate_dataset():
    """Build the full 5,000-row sales DataFrame."""

    customers = generate_customer_pool()
    region_names = list(REGIONS.keys())
    records = []

    for i in range(1, NUM_ROWS + 1):
        # ── order basics ─────────────────────────────────────────────────
        order_id = f"ORD-{i:05d}"
        order_date = weighted_order_date()
        ship_days = random.choices([1, 2, 3, 4, 5, 6, 7],
                                   weights=[5, 15, 25, 25, 15, 10, 5])[0]
        ship_date = order_date + timedelta(days=ship_days)

        # ── customer ─────────────────────────────────────────────────────
        cust_id, cust_name = random.choice(customers)
        segment = random.choices(SEGMENTS, weights=SEGMENT_WEIGHTS)[0]

        # ── geography ────────────────────────────────────────────────────
        region = random.choices(region_names, weights=REGION_WEIGHTS)[0]
        city = random.choice(REGIONS[region])
        state = STATE_MAP[city]

        # ── product ──────────────────────────────────────────────────────
        category = random.choice(list(CATEGORY_MAP.keys()))
        sub_cat = random.choice(list(CATEGORY_MAP[category].keys()))
        price_lo, price_hi, cost_ratio, margin_label = CATEGORY_MAP[category][sub_cat]
        product_name = random.choice(PRODUCT_NAMES[sub_cat])

        # ── financials ───────────────────────────────────────────────────
        unit_price = round(random.uniform(price_lo, price_hi), 2)
        quantity = random.choices([1, 2, 3, 4, 5, 6, 7, 8],
                                  weights=[30, 25, 18, 12, 7, 4, 2, 2])[0]

        # Discount: 0 % most common, up to 40 % occasionally
        discount = random.choices(
            [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40],
            weights=[35, 15, 15, 10, 10, 6, 4, 3, 2],
        )[0]

        revenue = round(unit_price * quantity * (1 - discount), 2)

        # Cost depends on category margins
        # Add noise so some Furniture items go negative
        noise = np.random.normal(0, 0.05)
        effective_cost_ratio = cost_ratio + noise

        # South region: inflate costs slightly (logistics / lower demand)
        if region == "South":
            effective_cost_ratio += 0.04

        # Furniture: occasionally push cost > revenue to create losses
        if category == "Furniture" and discount >= 0.20:
            effective_cost_ratio += random.uniform(0.05, 0.15)

        cost = round(unit_price * quantity * effective_cost_ratio, 2)
        profit = round(revenue - cost, 2)

        records.append({
            "order_id": order_id,
            "order_date": order_date.strftime("%Y-%m-%d"),
            "ship_date": ship_date.strftime("%Y-%m-%d"),
            "customer_id": cust_id,
            "customer_name": cust_name,
            "segment": segment,
            "region": region,
            "state": state,
            "city": city,
            "category": category,
            "sub_category": sub_cat,
            "product_name": product_name,
            "quantity": quantity,
            "unit_price": unit_price,
            "discount": discount,
            "revenue": revenue,
            "cost": cost,
            "profit": profit,
        })

    df = pd.DataFrame(records)
    return df


# ── main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating synthetic sales dataset (5,000 rows) ...")
    df = generate_dataset()

    # Ensure the data directory exists
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "sales_data.csv")
    xlsx_path = os.path.join(script_dir, "sales_data.xlsx")

    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False, engine="openpyxl")

    print(f"  Saved {len(df)} rows to:")
    print(f"    {csv_path}")
    print(f"    {xlsx_path}")
    print(f"\n  Date range : {df['order_date'].min()} to {df['order_date'].max()}")
    print(f"  Categories : {df['category'].nunique()} ({', '.join(df['category'].unique())})")
    print(f"  Regions    : {df['region'].nunique()} ({', '.join(df['region'].unique())})")
    print(f"  Customers  : {df['customer_id'].nunique()}")
    print(f"  Total Rev  : ${df['revenue'].sum():,.2f}")
    print(f"  Total Profit: ${df['profit'].sum():,.2f}")
    print("\nDone!")
