import json
import os

import praw
import tweepy
from azure.eventhub import EventData, EventHubProducerClient
from azure.storage.blob import BlobServiceClient

# Load credentials from GitHub Secrets
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
AZURE_STORAGE_CONNECTION = os.getenv("AZURE_STORAGE_CONNECTION")
AZURE_EVENT_HUB_CONNECTION = os.getenv("AZURE_EVENT_HUB_CONNECTION")

# Twitter API Setup
twitter_client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

# Reddit API Setup
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent="my_sentiment_analysis_app"
)

# Azure Blob Storage Setup
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION)
container_name = "social-media-raw"

# Azure Event Hub Setup
producer = EventHubProducerClient.from_connection_string(AZURE_EVENT_HUB_CONNECTION, eventhub_name="social-data-stream")


def fetch_twitter_data():
    query = "AI OR Machine Learning -is:retweet lang:en"
    tweets = twitter_client.search_recent_tweets(query=query, max_results=10)

    data = [{"source": "twitter", "text": tweet.text} for tweet in tweets.data]
    store_data_in_blob("twitter", data)
    send_to_eventhub(data)


def fetch_reddit_data():
    subreddit = reddit.subreddit("technology")

    data = [{"source": "reddit", "text": post.title} for post in subreddit.new(limit=10)]
    store_data_in_blob("reddit", data)
    send_to_eventhub(data)


def store_data_in_blob(platform, data):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"{platform}/{platform}_data.json")
    blob_client.upload_blob(json.dumps(data), overwrite=True)


def send_to_eventhub(data):
    event_data_batch = producer.create_batch()
    for item in data:
        event_data_batch.add(EventData(json.dumps(item)))
    producer.send_batch(event_data_batch)


if __name__ == "__main__":
    fetch_twitter_data()
    fetch_reddit_data()
    producer.close()
