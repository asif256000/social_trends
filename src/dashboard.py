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
else:
    st.success("✅ Connection string found!")

container_name = "social-data-trends"


# Load Sentiment Data from Azure Storage (Handles Partitioned Parquet Data)
def load_sentiment_data(platform):
    try:
        # Create Azure Blob Service Client
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

        # Read all partitioned parquet files into a DataFrame
        df_list = []
        for blob_name in blob_list:
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            parquet_data = blob_client.download_blob().readall()
            df = pd.read_parquet(BytesIO(parquet_data))

            # Extract creation_time from the file path
            match = re.search(r"creation_time=(\d{4}-\d{2}-\d{2}_\d{2}-\d{2})", blob_name)
            if match:
                df["creation_time"] = match.group(1)  # Add it as a column

            df_list.append(df)

        # Merge all partitions into a single DataFrame
        return pd.concat(df_list, ignore_index=True)
    except Exception as e:
        st.error(f"❌ Error loading {platform} sentiment data: {str(e)}")
        return pd.DataFrame()  # Return an empty DataFrame to prevent app crash


# Streamlit UI
st.title("📊 Social Media Sentiment Trends")

pf = st.selectbox("Select Platform", ["Twitter", "Reddit"])
df = load_sentiment_data(pf.lower())

if not df.empty:
    # Ensure the correct column name exists
    time_column = "creation_time" if "creation_time" in df.columns else "timestamp"

    fig = px.line(df, x=time_column, y="sentiment_score", title=f"{pf} Sentiment Trend")
    st.plotly_chart(fig)

    st.write("✅ Data refreshed from Azure Blob Storage!")
else:
    st.warning("⚠ No sentiment data available for the selected platform.")
