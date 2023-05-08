import tweepy
import requests
import time
import os
import random
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(filename="artwork.log", level=logging.DEBUG, format="%(asctime)s:%(levelname)s:%(message)s")

# Set up the authentication parameters
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

# Authenticate with the Twitter API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Set the time interval for posting tweets (in seconds)
post_interval = 36000 # 10 hours

def get_metropolitan_artwork_data():
    # API endpoint and parameters
    endpoint = "https://collectionapi.metmuseum.org/public/collection/v1/search"
    params = {"q": "hasImages=true", "hasImages": "true"}

    try:
        # Make request to get object IDs
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()

        # Get a random object ID that has a primary image
        while True:
            object_id = random.choice(data["objectIDs"])
            object_endpoint = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
            object_response = requests.get(object_endpoint)
            object_data = object_response.json()

            if "primaryImage" in object_data:
                break

        # Get data fields from object
        primary_image_url = object_data["primaryImageSmall"]
        object_url = object_data["objectURL"]
        object_name = object_data["classification"]
        object_title = object_data["title"]
        object_date = object_data["objectDate"]
        object_artist = object_data.get("artistDisplayName", "Unknown")

        return primary_image_url, object_url, object_name, object_title, object_artist, object_date
    
    except (requests.exceptions.RequestException, ValueError) as error:
        logging.error("Error occurred while getting artwork data: %s", error)

        # Wait for a shorter time before trying to get the artwork data again
        time.sleep(50)

def make_tweet(artwork_data):
    # Unpack the tuple
    primary_image_url, object_url, object_name, object_title, object_artist, object_date = artwork_data

    # Compose a tweet from the artwork data
    tweet = f"Check out this artwork from the Metropolitan Museum of Art! It's titled '{object_title}' ({object_url})"

    # Add object name if available
    if object_name:
        tweet += f", classified as {object_name}"

    # Add object artist if available
    if object_artist and object_artist != "Unknown" and len(object_artist) > 3:
        tweet += f", created by {object_artist}"

    # Add object date if available
    if object_date != "unknown" and len(object_date) > 3:
        tweet += f", dated {object_date}"

    # Check if tweet exceeds the character limit
    if len(tweet) > 280:
        tweet = tweet[:276] + "..."
        logging.warning("Tweet was truncated to 280 characters")

    # Log the composed tweet
    logging.info(f"Composed tweet: {tweet}")

    # Return the composed tweet
    print(tweet)
    return tweet


def post_tweet(tweet):
    try:
        # Post the tweet to Twitter
        api.update_status_with_media(filename="artwork.jpg", status=tweet)

        # Wait for the specified interval before posting the next tweet
        time.sleep(post_interval)
        logging.info(f"Tweet successfully posted!")

    except AttributeError:
        logging.error(f"Error occurred while posting tweet: The filename parameter was not provided")
        # Wait for a shorter time before trying to post the next tweet
        time.sleep(60)

# Loop indefinitely, posting a tweet every 10 hours
while True:
    # Get data about a random artwork from the Metropolitan Museum of Art API
    artwork_data = get_metropolitan_artwork_data()

    # Download the primary image for the artwork, if it exists
    image_url = artwork_data[0]
    if image_url:
        try:
            image_data = requests.get(image_url).content
        except (requests.exceptions.RequestException, ValueError) as error:
            logging.error("Error occurred while downloading image: %s", error)

            # Wait for a shorter time before trying to download the image again
            time.sleep(50)
            continue

        with open("artwork.jpg", "wb") as f:
            f.write(image_data)

        # Compose a tweet from the artwork data
        tweet = make_tweet(artwork_data)

        # Post the tweet to Twitter
        post_tweet(tweet)

        try:
            # Delete the image file to save space
            os.remove("artwork.jpg")
            logging.info(f"Image successfully deleted!")
        except OSError as e:
            logging.error("Error deleting image file:: %s", error)

    # Wait for the specified interval before posting the next tweet
    time.sleep(post_interval)