import json
import os
from datetime import datetime, timedelta, timezone

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
container_name = "social-data-trends"


def fetch_twitter_data():
    """Fetches latest tweets based on AI/Machine Learning keywords and includes timestamp."""
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    start_time_str = one_hour_ago.isoformat()
    query = "#ArtificialIntelligence OR #Technology -is:retweet lang:en -has:links -has:media"

    try:
        tweets = twitter_client.search_recent_tweets(
            query=query,
            max_results=10,
            tweet_fields=["created_at", "public_metrics"],
            start_time=start_time_str,
            sort_order="relevancy",
        )

        if tweets.data:
            filtered_tweets = sorted(
                [
                    {
                        "source": "twitter",
                        "text": tweet.text,
                        "timestamp": tweet.created_at.replace(tzinfo=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "likes": tweet.public_metrics.get("like_count", 0),
                        "retweets": tweet.public_metrics.get("retweet_count", 0),
                    }
                    for tweet in tweets.data
                    if tweet.text.strip()
                ],
                key=lambda x: (x["likes"], x["retweets"]),
                reverse=True,
            )

            if filtered_tweets:
                store_data_in_blob("twitter", filtered_tweets)
                print("✅ Successfully fetched and stored relevant tweets from the last hour.")
            else:
                print("⚠ No high-quality tweets found in this run.")

        else:
            print("⚠ No tweets found in the last hour.")
    except Exception as e:
        print(f"❌ Twitter API Error: {e}")


def fetch_reddit_data():
    """Fetches latest few posts each from r/technology and r/artificialinteligence and includes timestamp."""
    subreddits = ["technology", "artificialinteligence"]
    all_posts = []

    try:
        for subreddit in subreddits:
            try:
                posts = list(reddit.subreddit(subreddit).new(limit=5))
                subreddit_posts = [
                    {
                        "source": "reddit",
                        "subreddit": subreddit,
                        "title": post.title,
                        "text": post.selftext if post.selftext.strip() else post.title,
                        "timestamp": datetime.fromtimestamp(post.created_utc, timezone.utc).strftime(
                            "%Y-%m-%d %H:%M:%S UTC"
                        ),
                        "upvotes": post.score,
                        "comments": post.num_comments,
                    }
                    for post in posts
                ]
                all_posts.extend(subreddit_posts)
            except Exception as e:
                print(f"⚠ Error accessing subreddit r/{subreddit}: {e}")

        if all_posts:
            store_data_in_blob("reddit", all_posts)
            print("✅ Successfully fetched and stored Reddit posts.")
        else:
            print("⚠ No Reddit posts found in this run.")

    except Exception as e:
        print(f"❌ Reddit API Error: {e}")


def store_data_in_blob(platform, data):
    """Uploads the collected data to Azure Blob Storage."""
    try:
        timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        blob_name = f"{platform}/{platform}_data_{timestamp_str}.json"

        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(json.dumps(data), overwrite=True)

        print(f"✅ Data stored in Azure Blob Storage for {platform} with filename: {blob_name}")
    except Exception as e:
        print(f"❌ Azure Blob Storage Error for {platform}: {e}")


if __name__ == "__main__":
    fetch_twitter_data()
    fetch_reddit_data()
