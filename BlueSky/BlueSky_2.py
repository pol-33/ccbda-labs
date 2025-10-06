import os
import logging
from atproto import Client, client_utils
from dotenv import load_dotenv

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




def list_all_posts(client, handle):
    """
    List posts for the given BlueSky handle.

    Args:
        client (Client): Logged-in AT Proto client instance.
        handle (str): The handle of the user to retrieve posts for.
    """
    try:
        i = 1
        cursor = ''
        while True:
            profile_feed = client.get_author_feed(actor=handle, limit=100, cursor=cursor)
            cursor = profile_feed.cursor
            for feed_view in profile_feed.feed:
                print(f"\n\n{i}--------------------------------{feed_view.post.record.created_at}\n{feed_view.post.record.text}\n\n")
                i+=1
            if cursor is None:
                break
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

    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)


if __name__ == "__main__":
    main()
