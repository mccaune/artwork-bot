# artwork-bot

This Python script utilizes the Tweepy library and the Metropolitan Museum of Art's API to periodically tweet information about a random piece of art, including its title, classification, artist, and date. The bot downloads and tweets an image of the artwork, then deletes the image file to save space. The script logs relevant events, such as composing and posting a tweet, or any errors that may occur.

## Requirements

To run this script, you'll need the following:

- Python 3.6 or higher
- Tweepy library
- Python-dotenv library
- Requests library
- A Twitter Developer account with API access

## Installation

1. Clone the repository:
git clone https://github.com/your-username/your-repo-name.git

2. Install the required libraries:
pip install tweepy python-dotenv requests

3. Create a `.env` file in the project directory and add your Twitter API credentials:
CONSUMER_KEY=your_consumer_key
CONSUMER_SECRET=your_consumer_secret
ACCESS_TOKEN=your_access_token
ACCESS_TOKEN_SECRET=your_access_token_secret

## Usage

1. Run the script:

The bot will begin posting tweets with information about random artworks from the Metropolitan Museum of Art every 10 hours. The time interval between tweets can be adjusted by modifying the `post_interval` variable in the script.
