import os
import logging
from atproto import Client, client_utils
from dotenv import load_dotenv
import re

# Load environment variables from a .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def login_to_client():
    """
    Log in to the AT Proto client using environment variables.
    Returns:
        Client: Logged-in AT Proto client instance.
        Profile: Profile object for the logged-in user.
    """
    try:
        email = os.getenv("ATP_EMAIL")
        password = os.getenv("ATP_PASSWORD")
        if not email or not password:
            raise ValueError("Missing ATP_EMAIL or ATP_PASSWORD in environment variables.")

        client = Client()

        profile = client.login(email, password)
        logger.info("Login successful. Welcome, %s!", profile.display_name)
        return client, profile
    except Exception as e:
        logger.error("Failed to log in: %s", e)
        raise
 
emoticons_str = r"""
    (?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [D\)\]\(\]/\\OpP] # Mouth
    )"""
 
regex_str = [
    emoticons_str,
    r'<[^>]+>', # HTML tags
    r'(?:@[\w_]+)', # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', # URLs
 
    r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])", # words with - and '
    r'(?:[\w_]+)', # other words
    r'(?:\S)' # anything else
]
    
tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE)
emoticon_re = re.compile(r'^'+emoticons_str+'$', re.VERBOSE | re.IGNORECASE)
aux = ""

def tokenize(s):
    return tokens_re.findall(s)
 
def preprocess(s, lowercase=False):
    tokens = tokenize(s)
    if lowercase:
        tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
    return tokens
 

def list_all_posts(client, handle):
    """
    List up to 10 posts for the given BlueSky handle.

    Args:
        client (Client): Logged-in AT Proto client instance.
        handle (str): The handle of the user to retrieve posts for.
    """
    global aux
    try:
        i = 1
        cursor = ''
        while i <= 10:
            profile_feed = client.get_author_feed(actor=handle, limit=10, cursor=cursor)

            for feed_view in profile_feed.feed:
                aux += feed_view.post.record.text
                i += 1
                if i > 10:  # Stop after 10 posts
                    return 
    except Exception as e:
        logger.error("Failed to list posts: %s", e)
        raise




def main():
    """
    Main function to handle login, list posts, create a post, and delete it.
    """
    try:
        # Log in to the client and get the profile info.
        client, profile = login_to_client()

        # List all posts.
        list_all_posts(client, os.getenv("BLUESKY_USER"))

        
        print(preprocess(aux))

    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)


if __name__ == "__main__":
    main()