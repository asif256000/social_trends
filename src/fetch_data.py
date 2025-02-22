import json
import os
from datetime import datetime, timezone

import praw
import tweepy
from azure.storage.blob import BlobServiceClient

# Load credentials from GitHub Secrets
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
AZURE_STORAGE_CONNECTION = os.getenv("AZURE_STORAGE_CONNECTION")

# Twitter API Setup
twitter_client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

# Reddit API Setup
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent="my_sentiment_analysis_app"
)

# Azure Blob Storage Setup
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION)
container_name = "filesyssocialtrend"  # Change if using a different container


def fetch_twitter_data():
    """Fetches latest tweets based on AI/Machine Learning keywords and includes timestamp."""
    query = "AI OR Machine Learning -is:retweet lang:en -has:links -has:media"

    try:
        tweets = twitter_client.search_recent_tweets(query=query, max_results=10, tweet_fields=["created_at"])
        if tweets.data:
            data = [
                {
                    "source": "twitter",
                    "text": tweet.text,
                    "timestamp": tweet.created_at.replace(tzinfo=timezone.utc).strftime(
                        "%Y-%m-%d %H:%M:%S UTC"
                    ),  # Ensure UTC format
                }
                for tweet in tweets.data
            ]
            store_data_in_blob("twitter", data)
            print("✅ Successfully fetched and stored tweets.")
        else:
            print("⚠ No tweets found in this run.")
    except Exception as e:
        print(f"❌ Twitter API Error: {e}")


def fetch_reddit_data():
    """Fetches latest few posts each from r/technology and r/artificialintelligence and includes timestamp."""
    subreddits = ["technology", "artificialintelligence"]
    all_posts = []

    try:
        for subreddit in subreddits:
            posts = [post for post in reddit.subreddit(subreddit).new(limit=5)]
            subreddit_posts = [
                {
                    "source": "reddit",
                    "subreddit": subreddit,
                    "text": post.title,
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),  # Correct UTC format
                }
                for post in posts
            ]
            all_posts.extend(subreddit_posts)

        if all_posts:
            store_data_in_blob("reddit", all_posts)
            print("✅ Successfully fetched and stored few Reddit posts with timestamps.")
        else:
            print("⚠ No Reddit posts found in this run.")
    except Exception as e:
        print(f"❌ Reddit API Error: {e}")


def store_data_in_blob(platform, data):
    """Uploads the collected data to Azure Blob Storage."""
    try:
        timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")  # Correct UTC filename format
        blob_name = f"{platform}/{platform}_data_{timestamp_str}.json"

        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(json.dumps(data), overwrite=True)

        print(f"✅ Data stored in Azure Blob Storage for {platform} with filename: {blob_name}")
    except Exception as e:
        print(f"❌ Azure Blob Storage Error for {platform}: {e}")


if __name__ == "__main__":
    fetch_twitter_data()
    fetch_reddit_data()
