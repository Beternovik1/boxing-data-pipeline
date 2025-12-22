import streamlit as st # Framework for building web apps
import pandas as pd
from pymongo import MongoClient # To connect to the cloud database
import plotly.express as px # For creating charts
import os # To access system environment variables

# Page Configuration
# Sets the browser tab title and favicon
st.set_page_config(page_title="Boxing Dashboard", page_icon="🥊", layout="wide")

# @st.cache_resource is a "Decorator".
# It tells Streamlit: "Run this function only once and keep the connection in memory".
# Without this, Python would reconnect to Mongo from scratch on every reload, 
# slowing down the app significantly.
@st.cache_resource
def init_connection():
    # Try to read the secret from environment variables
    uri = os.environ.get("MONGO_URI")

    if not uri:
        # Fallback for local development
        uri = "mongodb+srv://edgaralfarohernandez15_db_user:ICN30t2E4rZPcxKt@cluster0.lueezcu.mongodb.net/?appName=Cluster0"
        
    return MongoClient(uri)

# Store the active connection in the 'client' variable
client = init_connection()

def get_data():
    # Select the database and collection
    # Note: Keeping DB names as is to match MongoDB
    db = client["campeones_mundiales"]
    col = db["Campeones"]

    # .find() retrieves all documents.
    # {"_id": 0} filters out the '_id' field (not needed for the dataframe)
    items = list(col.find({}, {"_id":0}))

    # Convert the list of dictionaries into a DataFrame
    return pd.DataFrame(items)

# Main Title
st.title("World Boxing Champions Dashboard")
st.markdown("### Real-time Analysis of WBA, WBC, IBF, and WBO")

# Call get_data to fill the df variable with real data
df = get_data()

# METRICS SECTION (KPIs) 
# st.columns(3) divides the screen into 3 invisible columns
col1, col2, col3 = st.columns(3)

# Metric 1: Total rows in DF (Total categories)
col1.metric("Weight Categories", len(df))

# Metric 2: Fixed data
col2.metric("Organizations", "4 (WBA, WBC, IBF, WBO)")

# Metric 3: Complex calculation
# Search for the word "vacant" across the entire DF and count occurrences.
total_vacant = df.apply(lambda x: x.astype(str).str.contains('vacant', case=False).sum(), axis=1).sum()
col3.metric("Vacant Titles", total_vacant)

# Visual divider
st.divider()

# st.sidebar places elements in the left sidebar
st.sidebar.header("Filters")

# Get unique list of categories (Heavyweight, Welter, etc.) for the menu
categories = df["Category"].unique()

# selectbox creates a dropdown menu.
# User selection is stored INSTANTLY in 'selected_category'
selected_category = st.sidebar.selectbox("Select a Category:", categories)

# Show filtered table
st.subheader(f"Champions in: {selected_category}")

# Pandas Filter: Return rows where Category matches user selection
filtered_df = df[df["Category"] == selected_category]

# Render the table. hide_index=True removes row numbers (0, 1, 2...)
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

## BAR CHART SECTION
st.divider()
st.subheader("Vacant Titles by Organization")

# Prepare data for the chart
# Manually counting "Vacant" entries for each column (WBA, WBC, WBO, IBF)
counts = {
    "WBA": df["WBA"].str.contains("vacant", case=False).sum(),
    "WBC": df["WBC"].str.contains("vacant", case=False).sum(),
    "IBF": df["IBF"].str.contains("vacant", case=False).sum(),
    "WBO": df["WBO"].str.contains("vacant", case=False).sum(),
}

# Convert dictionary to a mini DataFrame for plotting
chart_df = pd.DataFrame(list(counts.items()), columns=["Organization", "Vacant_Titles"])

# Use Plotly Express (px) to create the bar chart
fig = px.bar(
    chart_df,
    x="Organization",
    y="Vacant_Titles",
    color="Organization",
    text="Vacant_Titles",
    template="plotly_dark" # Dark mode style
)

# Display the chart
st.plotly_chart(fig, use_container_width=True)