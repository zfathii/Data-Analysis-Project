# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib
from function import DataAnalyzer, BrazilMapPlotter

# Set seaborn style
sns.set(style='dark')

# Load the main dataset
datetime_cols = [
    "order_approved_at", 
    "order_delivered_carrier_date", 
    "order_delivered_customer_date", 
    "order_estimated_delivery_date", 
    "order_purchase_timestamp", 
    "shipping_limit_date"
]
all_df = pd.read_csv("https://raw.githubusercontent.com/zfathii/bismillah/main/dashboard/df.csv")
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

# Load geolocation dataset and clean it
geolocation = pd.read_csv('https://raw.githubusercontent.com/zfathii/bismillah/main/dashboard/geolocation.csv')
data = geolocation.drop_duplicates(subset='customer_unique_id')

# Convert date columns to datetime format
for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

# Get minimum and maximum dates for the date range selection
min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Sidebar configuration
with st.sidebar:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(' ')
    with col2:
        st.image("https://raw.githubusercontent.com/zfathii/bismillah/main/dashboard/laptop.png", width=100)
    with col3:
        st.write(' ')

    # Date range selection for filtering the dataset
    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Filter the main DataFrame based on the selected date range
main_df = all_df[
    (all_df["order_approved_at"] >= str(start_date)) & 
    (all_df["order_approved_at"] <= str(end_date))
]

# Create analysis functions
function = DataAnalyzer(main_df)
map_plot = BrazilMapPlotter(data, plt, mpimg, urllib, st)

# Generate various dataframes for analysis
daily_orders_df = function.create_daily_orders_df()
sum_spend_df = function.create_sum_spend_df()
sum_order_items_df = function.create_sum_order_items_df()
review_score, common_score = function.review_score_df()
state, most_common_state = function.create_bystate_df()
order_status, common_status = function.create_order_status()

# Streamlit app title
st.title("Dicoding Project: E-Commerce Public Data Analysis")

# Dashboard description
st.write("**This is a dashboard for analyzing E-Commerce public data.**")
st.write("**By Fathimah Zulfah.**")


# Section for Daily Orders Delivered
st.subheader("Daily Orders Delivered")
col1, col2 = st.columns(2)

with col1:
    total_order = daily_orders_df["order_count"].sum()
    st.markdown(f"Total Order: **{total_order}**")

with col2:
    total_revenue = daily_orders_df["revenue"].sum()
    st.markdown(f"Total Revenue: **{total_revenue}**")

# Plot for daily orders delivered
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(
    x=daily_orders_df["order_approved_at"],
    y=daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Section for Customer Spending
st.subheader("Customer Spend Money")
col1, col2 = st.columns(2)

with col1:
    total_spend = sum_spend_df["total_spend"].sum()
    st.markdown(f"Total Spend: **{total_spend}**")

with col2:
    avg_spend = sum_spend_df["total_spend"].mean()
    st.markdown(f"Average Spend: **{avg_spend}**")

# Plot for customer spending
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(
    data=sum_spend_df,
    x="order_approved_at",
    y="total_spend",
    marker="o",
    linewidth=2,
    color="#90CAF9"
)

ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Section for Order Items
st.subheader("Order Items")
col1, col2 = st.columns(2)

with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.markdown(f"Total Items: **{total_items}**")

with col2:
    avg_items = sum_order_items_df["product_count"].mean()
    st.markdown(f"Average Items: **{avg_items}**")

# Plot for most and fewest sold products
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.head(5), palette="plasma", ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=80)
ax[0].set_title("Most Sold Products", loc="center", fontsize=90)
ax[0].tick_params(axis='y', labelsize=55)
ax[0].tick_params(axis='x', labelsize=50)

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), palette="plasma", ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=80)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Fewest Products Sold", loc="center", fontsize=90)
ax[1].tick_params(axis='y', labelsize=55)
ax[1].tick_params(axis='x', labelsize=50)

st.pyplot(fig)

# Section for Review Score
st.subheader("Review Score")
col1, col2 = st.columns(2)

with col1:
    avg_review_score = review_score.mean()
    st.markdown(f"Average Review Score: **{avg_review_score:.2f}**")

with col2:
    most_common_review_score = review_score.value_counts().idxmax()
    st.markdown(f"Most Common Review Score: **{most_common_review_score}**")

# Plot for review scores
fig, ax = plt.subplots(figsize=(12, 6))
colors = sns.color_palette("plasma", len(review_score))

sns.barplot(
    x=review_score.index,
    y=review_score.values,
    order=review_score.index,
    palette=colors
)

plt.title("Customer Review Scores for Service", fontsize=15)
plt.xlabel("Rating")
plt.ylabel("Count")
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

# Adding labels on top of each bar
for i, v in enumerate(review_score.values):
    ax.text(i, v + 5, str(v), ha='center', va='bottom', fontsize=12, color='black')

st.pyplot(fig)

# Section for Customer Demographic
st.subheader("Customer Demographic")
tab1, tab2 = st.tabs(["State", "Geolocation"])

# Tab for State
with tab1:
    most_common_state = state.customer_state.value_counts().index[0]
    st.markdown(f"Most Common State: **{most_common_state}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(
        x=state.customer_state.value_counts().index,
        y=state.customer_count.values, 
        data=state,
        palette="plasma"
    )

    plt.title("Number of Customers from Each State", fontsize=15)
    plt.xlabel("State")
    plt.ylabel("Number of Customers")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

    with st.expander("See Explanation"):
        st.write('Based on the generated graph, a higher concentration of customers is located in the southeast and southern regions. Additionally, a significant number of customers are found in major capital cities such as São Paulo, Rio de Janeiro, Porto Alegre, and others.')

# Tab for Geolocation
with tab2:
    map_plot.plot()

    with st.expander("See Explanation"):
        st.write('According the map provided, the geographical area with the highest number of customers appears to be concentrated in the southeastern region of Brazil. This area typically includes major cities such as São Paulo, Rio de Janeiro, Porto Alegre, and others, which are known for their significant populations and urban activity.')

# Copyright notice
st.caption('Copyright (C) Fathimah Zulfah 2024')
