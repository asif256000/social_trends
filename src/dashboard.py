import os
import re
from datetime import datetime, timedelta
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st
from azure.storage.blob import BlobServiceClient

# Retrieve Connection String Securely from Environment Variable
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

if not AZURE_CONNECTION_STRING:
    st.error("❌ AZURE_STORAGE_CONNECTION_STRING is not set! Check Azure App Configuration.")

container_name = "social-data-trends"


# Load Sentiment Data from Azure Storage
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
st.title("📊 Social Media Sentiment Analysis")

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

if df_twitter.empty and df_reddit.empty:
    st.warning("⚠ No sentiment data available.")
else:
    aggregation_columns = ["sentiment_score", "polarity", "subjectivity"]

    if not df_twitter.empty:
        df_twitter = df_twitter.groupby("creation_time")[aggregation_columns].mean().reset_index()

    if not df_reddit.empty:
        df_reddit = df_reddit.groupby("creation_time")[aggregation_columns].mean().reset_index()

    # Determine unique timestamps from both datasets
    unique_dates = sorted(
        set(df_twitter["creation_time"].tolist() if not df_twitter.empty else [])
        | set(df_reddit["creation_time"].tolist() if not df_reddit.empty else [])
    )

    unique_dates = [dt.to_pydatetime() if isinstance(dt, pd.Timestamp) else dt for dt in unique_dates]

    # Determine step size dynamically (smallest gap between timestamps)
    if len(unique_dates) > 1:
        step_size = min((unique_dates[i + 1] - unique_dates[i]) for i in range(len(unique_dates) - 1))
    else:
        step_size = timedelta(hours=6)

    # Sidebar: Date Range Filter (Slider with Min & Max Labels, and Ticks)
    if unique_dates:
        selected_range = st.sidebar.slider(
            "📅 Select Date Range",
            min_value=unique_dates[0],  # Min timestamp
            max_value=unique_dates[-1],  # Max timestamp
            value=(unique_dates[0], unique_dates[-1]),  # Default range
            step=step_size,
            format="YYYY-MM-DD HH:mm",
        )

        # Apply the Date Range Filter
        df_twitter_filtered = (
            df_twitter[
                (df_twitter["creation_time"] >= selected_range[0]) & (df_twitter["creation_time"] <= selected_range[1])
            ]
            if not df_twitter.empty
            else pd.DataFrame()
        )

        df_reddit_filtered = (
            df_reddit[
                (df_reddit["creation_time"] >= selected_range[0]) & (df_reddit["creation_time"] <= selected_range[1])
            ]
            if not df_reddit.empty
            else pd.DataFrame()
        )

    # Create Line Chart
    fig = px.line(title=f"📊 {metric} Over Time")

    # Add Twitter Data if Selected
    if show_twitter and not df_twitter_filtered.empty:
        fig.add_scatter(
            x=df_twitter_filtered["creation_time"],
            y=df_twitter_filtered[metric_column],
            mode="lines",
            name="Twitter",
            line=dict(color="blue"),
        )

    # Add Reddit Data if Selected
    if show_reddit and not df_reddit_filtered.empty:
        fig.add_scatter(
            x=df_reddit_filtered["creation_time"],
            y=df_reddit_filtered[metric_column],
            mode="lines",
            name="Reddit",
            line=dict(color="orange"),
        )

    # Show warning if no data in the selected range
    if df_twitter_filtered.empty and df_reddit_filtered.empty:
        st.warning("⚠ No data available in the selected date range.")

    st.plotly_chart(fig, use_container_width=True)

# Collapsible Explanation of Metrics
with st.expander("ℹ️ Understanding the Metrics (Click to Expand)"):
    st.markdown(
        """
        - **Sentiment Score (1-5 stars)**:
            - **1** ⭐️: Very Negative 😡
            - **2** ⭐️: Negative 😞
            - **3** ⭐️: Neutral 😐
            - **4** ⭐️: Positive 😊
            - **5** ⭐️: Very Positive 😃
        - **Polarity (ranges between -1 to 1)**:
            - **-1**: 🤬 Extremely Negative (conveys a negative opinion, dissatisfaction, anger, sadness, or some other negative emotion)
            - **+1**: 🤩 Extremely Positive (conveys a favorable opinion, joy, happiness, excitement, or some other positive emotion)
        - **Subjectivity (ranges between 0 to 1)**:
            - **0**: 🔎 Very Objective (i.e., mostly factual statements)
            - **1**: 💭 Highly Subjective (i.e., based on personal opinions, sentiments, or judgments)
        """
    )
