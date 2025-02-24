import os
import re
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st
from azure.storage.blob import BlobServiceClient

# 🔐 Retrieve Connection String Securely from Environment Variable
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

if not AZURE_CONNECTION_STRING:
    st.error("❌ AZURE_STORAGE_CONNECTION_STRING is not set! Check Azure App Configuration.")

container_name = "social-data-trends"


# Load Sentiment Data from Azure Storage (Handles Partitioned Parquet Data)
def load_sentiment_data(platform):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(container_name)

        # Get list of blobs (parquet partitioned files)
        blob_list = [
            blob.name
            for blob in container_client.list_blobs(name_starts_with=f"processed/{platform}_sentiment/")
            if blob.name.endswith(".parquet")
        ]

        if not blob_list:
            st.warning(f"⚠ No sentiment data found for {platform}.")
            return pd.DataFrame()

        df_list = []
        for blob_name in blob_list:
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            parquet_data = blob_client.download_blob().readall()
            df = pd.read_parquet(BytesIO(parquet_data))

            # Extract creation_time from the file path
            match = re.search(r"creation_time=(\d{4}-\d{2}-\d{2}_\d{2}-\d{2})", blob_name)
            if match:
                df["creation_time"] = match.group(1)

            df_list.append(df)

        df = pd.concat(df_list, ignore_index=True)

        # Convert `creation_time` to datetime object
        df["creation_time"] = pd.to_datetime(df["creation_time"], format="%Y-%m-%d_%H-%M")

        return df

    except Exception as e:
        st.error(f"❌ Error loading {platform} sentiment data: {str(e)}")
        return pd.DataFrame()


# Streamlit UI
st.title("📊 Social Media Sentiment Analysis Dashboard")

# Sidebar: Select Data Sources to Display
st.sidebar.header("Select Data Sources")
show_twitter = st.sidebar.checkbox("Show Twitter Data (🔵)", value=True)
show_reddit = st.sidebar.checkbox("Show Reddit Data (🟠)", value=True)

# Sidebar: Select Metric to Display
metric = st.sidebar.selectbox("Select Metric to Display", ["Sentiment Score", "Polarity", "Subjectivity"])
metric_map = {"Sentiment Score": "sentiment_score", "Polarity": "polarity", "Subjectivity": "subjectivity"}
metric_column = metric_map[metric]

# Load Data for Both Twitter & Reddit
df_twitter = load_sentiment_data("twitter")
df_reddit = load_sentiment_data("reddit")

# Check if data exists
if df_twitter.empty and df_reddit.empty:
    st.warning("⚠ No sentiment data available.")
else:
    if not df_twitter.empty:
        df_twitter = (
            df_twitter.groupby("creation_time")
            .agg({col: "mean" for col in df_twitter.select_dtypes(include="number").columns})
            .reset_index()
        )

    if not df_reddit.empty:
        df_reddit = (
            df_reddit.groupby("creation_time")
            .agg({col: "mean" for col in df_reddit.select_dtypes(include="number").columns})
            .reset_index()
        )

    # Sidebar: Date Range Filter
    min_date = min(df_twitter["creation_time"].min(), df_reddit["creation_time"].min())
    max_date = max(df_twitter["creation_time"].max(), df_reddit["creation_time"].max())

    date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

    # Apply Date Range Filter
    if isinstance(date_range, list) and len(date_range) == 2:
        df_twitter = df_twitter[
            (df_twitter["creation_time"].dt.date >= date_range[0])
            & (df_twitter["creation_time"].dt.date <= date_range[1])
        ]
        df_reddit = df_reddit[
            (df_reddit["creation_time"].dt.date >= date_range[0])
            & (df_reddit["creation_time"].dt.date <= date_range[1])
        ]

    # Create Line Chart
    fig = px.line(title=f"📊 {metric} Over Time")

    # Add Twitter Data if Selected
    if show_twitter and not df_twitter.empty:
        fig.add_scatter(
            x=df_twitter["creation_time"],
            y=df_twitter[metric_column],
            mode="lines",
            name="Twitter",
            line=dict(color="blue"),
        )

    # Add Reddit Data if Selected
    if show_reddit and not df_reddit.empty:
        fig.add_scatter(
            x=df_reddit["creation_time"],
            y=df_reddit[metric_column],
            mode="lines",
            name="Reddit",
            line=dict(color="orange"),
        )

    st.plotly_chart(fig, use_container_width=True)

# Explanation of Metrics
st.markdown(
    """
### ℹ️ **Understanding the Metrics**
- **Sentiment Score (1-5 stars)**:
    - **1**: Very Negative 😡
    - **2**: Negative 😞
    - **3**: Neutral 😐
    - **4**: Positive 😊
    - **5**: Very Positive 😃
- **Polarity (-1 to 1)**:
    - **-1**: Extremely Negative
    - **0**: Neutral
    - **+1**: Extremely Positive
- **Subjectivity (0 to 1)**:
    - **0**: Very Objective
    - **1**: Highly Subjective
"""
)

st.write("✅ Data refreshed from Azure Data Storage!")
