# Artwork Bot

Artwork Bot is a Python application that posts images and information about artworks from the Metropolitan Museum of Art and the Rijksmuseum on Twitter at regular intervals.

## Features

- Fetches random artwork data from the Metropolitan Museum of Art and the Rijksmuseum using their public APIs
- Composes a tweet containing information about the artwork and a link to the artwork page
- Posts the tweet along with the artwork image to Twitter
- Automatically resizes images larger than 5MB to comply with Twitter's image size limits
- Logs application activity, including posted tweets and errors

## Requirements

- Python 3.6 or higher
- tweepy
- requests
- python-dotenv
- Pillow

## Installation

1. Clone the repository:

git clone https://github.com/yourusername/artwork_bot.git
cd artwork_bot

2. Install the required packages:

pip install -r requirements.txt

3. Create a `.env` file in the project root directory with the following contents, replacing the placeholder values with your own API keys and access tokens:

CONSUMER_KEY=your_twitter_consumer_key
CONSUMER_SECRET=your_twitter_consumer_secret
ACCESS_TOKEN=your_twitter_access_token
ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
RIJKSMUSEUM_API_KEY=your_rijksmuseum_api_key

4. Run the application:

python artwork_bot.py

## Usage

After setting up the application, it will automatically fetch random artwork data from the Metropolitan Museum of Art and the Rijksmuseum, compose tweets, and post them to Twitter every 10 hours.

To change the posting interval, modify the `post_interval` variable in `artwork_bot.py`. The interval is specified in seconds.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [The Metropolitan Museum of Art Collection API](https://metmuseum.github.io/)
- [The Rijksmuseum API](https://www.rijksmuseum.nl/en/api)
