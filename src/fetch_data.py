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
reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent="social-trends")

# Azure Blob Storage Setup
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION)
container_name = "filesyssocialtrend"

# Azure Event Hub Setup
producer = EventHubProducerClient.from_connection_string(AZURE_EVENT_HUB_CONNECTION, eventhub_name="social-data-stream")


def fetch_twitter_data():
    """Fetches latest 5 tweets based on AI/Machine Learning keywords."""
    query = "AI OR Machine Learning -is:retweet lang:en"

    try:
        tweets = twitter_client.search_recent_tweets(query=query, max_results=10)
        if tweets.data:
            data = [{"source": "twitter", "text": tweet.text} for tweet in tweets.data]
            store_data_in_blob("twitter", data)
            send_to_eventhub(data)
            print("✅ Successfully fetched and stored 5 tweets.")
        else:
            print("⚠ No tweets found in this run.")
    except Exception as e:
        print(f"❌ Twitter API Error: {e}")


def fetch_reddit_data():
    """Fetches latest 5 Reddit posts from r/technology."""
    subreddits = ["technology", "artificialintelligence"]
    all_posts = []

    try:
        for subreddit in subreddits:
            posts = [post for post in reddit.subreddit(subreddit).new(limit=5)]
            subreddit_posts = [{"source": "reddit", "subreddit": subreddit, "text": post.title} for post in posts]
            all_posts.extend(subreddit_posts)

        if all_posts:
            store_data_in_blob("reddit", all_posts)
            send_to_eventhub(all_posts)
            print("✅ Successfully fetched and stored 10 Reddit posts (5 from each subreddit).")
        else:
            print("⚠ No Reddit posts found in this run.")
    except Exception as e:
        print(f"❌ Reddit API Error: {e}")


def store_data_in_blob(platform, data):
    """Uploads the collected data to Azure Blob Storage."""
    try:
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=f"{platform}/{platform}_data.json"
        )
        blob_client.upload_blob(json.dumps(data), overwrite=True)
        print(f"✅ Data stored in Azure Blob Storage for {platform}.")
    except Exception as e:
        print(f"❌ Azure Blob Storage Error for {platform}: {e}")


def send_to_eventhub(data):
    """Sends data to Azure Event Hub."""
    try:
        event_data_batch = producer.create_batch()
        for item in data:
            event_data_batch.add(EventData(json.dumps(item)))
        producer.send_batch(event_data_batch)
        print("✅ Data sent to Azure Event Hub.")
    except Exception as e:
        print(f"❌ Event Hub Error: {e}")


if __name__ == "__main__":
    fetch_twitter_data()
    fetch_reddit_data()
    producer.close()
