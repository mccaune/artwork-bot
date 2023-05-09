import tweepy
import requests
import time
import os
import random
import logging
from dotenv import load_dotenv
from PIL import Image

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(filename="artwork.log", level=logging.DEBUG, format="%(asctime)s:%(levelname)s:%(message)s")

# Set up the authentication parameters
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

# Set up Rijksmuseum parameters
RIJKSMUSEUM_API_KEY = os.getenv("RIJKSMUSEUM_API_KEY")

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

def get_rijksmuseum_artwork_data():
    endpoint = "https://www.rijksmuseum.nl/api/en/collection"
    random_page = random.randint(1, 10000)  # Get a random page number between 1 and 100
    params = {
        "key": RIJKSMUSEUM_API_KEY,
        "format": "json",
        "imgonly": True,
        "ps": 1,
        "toppieces": False,
        "p": random_page  # Add the random page parameter
    }

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()

        artwork = random.choice(data['artObjects'])

        primary_image_url = artwork['webImage']['url']
        object_url = artwork['links']['web']
        object_name = artwork['longTitle']
        object_title = artwork['title']
        object_date = artwork['id']
        object_artist = artwork['principalOrFirstMaker']

        return primary_image_url, object_url, object_name, object_title, object_artist, object_date

    except (requests.exceptions.RequestException, ValueError) as error:
        logging.error("Error occurred while getting artwork data: %s", error)
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

def make_rijksmuseum_tweet(artwork_data):
    primary_image_url, object_url, object_name, object_title, object_artist, object_date = artwork_data

    tweet = f"Check out this artwork from the Rijksmuseum! It's titled '{object_title}' ({object_url})"

    if len(tweet) > 280:
        tweet = tweet[:276] + "..."
        logging.warning("Tweet was truncated to 280 characters")

    logging.info(f"Composed tweet: {tweet}")
    print(tweet)
    return tweet


def post_tweet(tweet):
    try:
        # Check if the image size is within Twitter's allowed limit (5MB)
        if os.path.getsize("artwork.jpg") > 1 * 1024 * 1024:
            print("Error occurred while posting tweet: The image is still larger than 5MB after resizing")
            logging.error("Error occurred while posting tweet: The image is still larger than 5MB after resizing")
            return

        # Post the tweet to Twitter
        api.update_status_with_media(filename="artwork.jpg", status=tweet)

        # Wait for the specified interval before posting the next tweet
        time.sleep(post_interval)
        logging.info(f"Tweet successfully posted!")

    except AttributeError:
        logging.error(f"Error occurred while posting tweet: The filename parameter was not provided")
        # Wait for a shorter time before trying to post the next tweet
        time.sleep(60)

def get_random_museum_artwork_data():
    museum_function, make_tweet_function = random.choice(museum_api_functions)
    return museum_function(), make_tweet_function


def download_image(image_url):
    try:
        image_data = requests.get(image_url).content
        with open("artwork.jpg", "wb") as f:
            f.write(image_data)

        # Resize the image if it's larger than 5MB
        resize_image("artwork.jpg")

        # Check if the image size is within Twitter's allowed limit (5MB)
        if os.path.getsize("artwork.jpg") > 5 * 1024 * 1024:
            print("Error occurred while downloading image: The image is still larger than 5MB after resizing")
            logging.error("Error occurred while downloading image: The image is still larger than 5MB after resizing")
            return False

    except (requests.exceptions.RequestException, ValueError) as error:
        logging.error("Error occurred while downloading image: %s", error)
        time.sleep(50)
        return False
    return True


def resize_image(image_path, max_size=1 * 1024 * 1024):
    img = Image.open(image_path)
    img_size = os.path.getsize(image_path)

    if img_size > max_size:
        scaling_factor = (max_size / img_size) ** 0.5
        new_width = int(img.width * scaling_factor)
        new_height = int(img.height * scaling_factor)
        img = img.resize((new_width, new_height), Image.LANCZOS)
        img.save(image_path, optimize=True, quality=85)

    img.close()


# List of museum API functions and their corresponding make_tweet functions
museum_api_functions = [
    (get_metropolitan_artwork_data, make_tweet),
    (get_rijksmuseum_artwork_data, make_rijksmuseum_tweet)
]

# Loop indefinitely, posting a tweet every 10 hours
while True:
    # Get data about a random artwork from a random museum API
    artwork_data, make_tweet_function = get_random_museum_artwork_data()

    # Download the primary image for the artwork, if it exists
    image_url = artwork_data[0]
    if image_url and download_image(image_url):
        # Compose a tweet from the artwork data
        tweet = make_tweet_function(artwork_data)

        # Post the tweet to Twitter
        post_tweet(tweet)

        try:
            # Delete the image file to save space
            os.remove("artwork.jpg")
            logging.info(f"Image successfully deleted!")
        except OSError as e:
            logging.error("Error deleting image file:: %s", e)

    # Wait for the specified interval before posting the next tweet
    time.sleep(post_interval)
