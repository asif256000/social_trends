import os

import pandas as pd
import plotly.express as px
import streamlit as st
from azure.storage.blob import BlobServiceClient

AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = "social-data-trends"


# Load Sentiment Data from Azure Storage
def load_sentiment_data(platform):
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"processed/{platform}_sentiment")

    with open(f"{platform}_sentiment.parquet", "wb") as f:
        f.write(blob_client.download_blob().readall())

    return pd.read_parquet(f"{platform}_sentiment")


# Streamlit UI
st.title("📊 Social Media Sentiment Trends")

pf = st.selectbox("Select Platform", ["Twitter", "Reddit"])
df = load_sentiment_data(pf.lower())

# Sentiment Trend Chart
fig = px.line(df, x="creation_time", y="sentiment_score", title=f"{pf} Sentiment Trend")
st.plotly_chart(fig)

st.write("✅ Data refreshed from Azure Blob Storage!")
