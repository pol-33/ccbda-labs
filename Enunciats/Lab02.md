# Lab session #2: Doors in the Cloud

In this session, we’ll explore the structure of a [BlueSky](https://bsky.app/) post—a popular alternative to Twitter/X—and how to pre-process its text for analysis. While tokenization is a fundamental task in text processing, it can be surprisingly tricky when dealing with BlueSky data. Before diving in, we’ll set up a Python development environment, which will be useful for this and future labs.
   
## Setting Up Your Environment for BlueSky

Modern cloud applications thrive on user interaction and content generation. These apps often integrate multiple services and systems using **Application Programming Interfaces (APIs)**—a key enabler of interoperability.

APIs let computer systems communicate and interact. You’ve likely encountered them before in the context of operating systems, which expose APIs to let applications interact with files, memory, and display systems.

Since this course focuses on cloud technologies, we’ll narrow in on **web APIs**—APIs built over HTTP, used by web servers and browsers alike. Web APIs are a core part of today’s cloud ecosystem, enabling developers to tap into third-party services to enhance their own applications.

One such example is the [BlueSky API](https://docs.bsky.app/docs/get-started). The [BlueSky API SDK](https://docs.bsky.app/) allows developers to access posts by a user, find posts matching specific terms, filter by topic and date, and much more—all in your language of choice.

> [!Tip]
> If you don’t yet have a BlueSky account, create one and store your credentials securely using a [password manager](https://en.wikipedia.org/wiki/Password_manager). See this [guide to the best password managers for 2025](https://www.pcmag.com/picks/the-best-password-managers) for recommendations.

## Lab Tasks Overview

- [**Task 2.1: Deepen Your AWS Cloud Knowledge**](#Task21)
- [**Task 2.2: Geting Started with NLTK**](#Task22)
- [**Task 2.3: Using the BlueSky API in Python**](#Task23)
- [**Task 2.4: Posts pre-processing**](#Task24)

<a id="Task21" />

## Task 2.1: Deepen Your AWS Cloud Knowledge

Study the following AWS Academy modules and complete the associated labs:

> [!Important]
> Each student must **individually** complete the AWS Academy knowledge checks as part of the course requirements.
> 
> Complete only the modules, activities, and laboratories specified below.

- **Module 5 – Networking and Content Delivery**  
  > :question: **Question 1:** Include screenshots of key steps and briefly explain what you learned or observed.
  
  > :test_tube: **Laboratory 2:** *Build Your VPC and Launch a Web Server*  

- **Module 6 – Compute**  
  > :question: **Question 2:** Include screenshots of key steps and briefly explain what you learned or observed.
  
  > :test_tube: **Laboratory 3:** *Introduction to Amazon EC2*

  > :microscope: **Activity:** *AWS Lambda*

  > :microscope: **Activity:** *AWS Elastic Beanstalk*

- **Module 7 – Storage**  
  
  > :question: **Question 3:** Include screenshots of key steps and briefly explain what you learned or observed.

  > :test_tube: **Laboratory 4:** *Working with EBS*
  
<a id="Task22" />

## Task 2.2: Getting Started with NLTK

The [Natural Language Toolkit (NLTK)](http://www.nltk.org) is a widely used Python library for NLP (Natural Language Processing). It provides tools for core NLP tasks and access to lexical resources and datasets.

A foundational step in NLP is **tokenization**, which splits text into smaller units—typically words. Let’s walk through a simple use of NLTK to tokenize a book and analyze word frequency.

Ensure NLTK is installed:

```python
_$ import nltk
```
If you encounter issues installing packages, check: [https://www.nltk.org/data.html](https://www.nltk.org/data.html)

> [!Note]
> NLTK includes built-in data like corpora, grammars, and models, which you’ll need to download separately.  
> Full download (`nltk.download('all')`) is ~3.5GB.  
> For English tokenization only: `nltk.download('punkt_tab')`.

Here’s an example using the book *[First Contact with TensorFlow](http://www.jorditorres.org/Tensorflow)* ([`FirstContactWithTensorFlow.txt`](Lab02/FirstContactWithTensorFlow.txt)):

> [!Note]
> Code uses `logging` for status updates and includes exception handling for robustness.

```python
import nltk
from nltk.tokenize import word_tokenize
from collections import Counter
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Download the tokenizer only if not available
nltk.download('punkt_tab', quiet=True)


def get_tokens(file_path):
    """
    Reads the content of a file, tokenizes the text, and returns the tokens.

    Args:
        file_path (str): The path to the text file.

    Returns:
        list: A list of tokens extracted from the file.
    """
    try:
        logger.info("Attempting to read the file: %s", file_path)
        with open(file_path, 'r', encoding='utf-8') as file:  # Explicit encoding for better compatibility
            text = file.read()
            logger.info("File read successfully. Preprocessing text...")
            text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
            tokens = word_tokenize(text)
            logger.info("Text tokenized successfully. Number of tokens: %d", len(tokens))
            return tokens
    except FileNotFoundError:
        logger.error("File not found: %s", file_path)
        return []
    except Exception as e:
        logger.error("An unexpected error occurred while processing the file: %s", e)
        return []


def get_most_common_words(tokens, n=10):
    """
    Counts the frequency of tokens and returns the most common ones.

    Args:
        tokens (list): List of tokens.
        n (int): Number of most common words to return.

    Returns:
        list: A list of tuples containing the n most common tokens and their counts.
    """
    try:
        logger.info("Counting token frequencies...")
        count = Counter(tokens)
        most_common = count.most_common(n)
        logger.info("Successfully retrieved the %d most common words.", n)
        return most_common
    except Exception as e:
        logger.error("An unexpected error occurred while counting tokens: %s", e)
        return []


def main():
    """
    Main function to tokenize a file and display the most common words.
    """
    logger.info("Starting the program...")

    # Tokenize the file
    tokens = get_tokens('../FirstContactWithTensorFlow.txt')

    if tokens:
        # Get the 10 most common words
        most_common_words = get_most_common_words(tokens)
        print("The 10 most common words are:")
        for word, freq in most_common_words:
            print(f"'{word}' appears {freq} times.")
    else:
        logger.warning("No tokens found. Please check the file or input.")

    logger.info("Program completed.")


if __name__ == "__main__":
    main()
```
<sub>Using `logging` helps you trace issues and understand what your script is doing. Clean code and documentation help maintain it over time.</sub>

### Word Count v1

Download and run [`WordCountTensorFlow_1.py`](Lab02/WordCountTensorFlow_1.py) from the repository.  
Add a line that prints the total number of words in the book.

> :question: **Question 4**: Add your comments to `README.md

### Remove punctuation

Improve the tokenizer by removing punctuation using regex inside `get_tokens()`:

```python
    lowers = text.lower()
    no_punctuation = re.sub(r'[^\w\s]',' ',lowers)
    tokens = nltk.word_tokenize(no_punctuation)
```

> :question: **Question 5**: Add the code to `WordCountTensorFlow_2.py` and your comments to `README.md
    
### Stop Words

> :question: **Question 6**: Why isn’t "TensorFlow" the most frequent word?  

> :question: **Question 7**: Which are the Stop Words? 


To remove stop words:

```python
from nltk.corpus import stopwords
nltk.download('stopwords') 

tokens = get_tokens()
# the lambda expression below this comment
# stores stopwords in a variable for eficiency: 
# it avoids retrieving them from ntlk for each iteration
sw = stopwords.words('english')
filtered = [w for w in tokens if not w in sw]
count = Counter(filtered)
```

Create a new script to perform this process and display the 10 most common words and the total word count **after** removing stop words.

> :question: **Question 8**: Add the code to `WordCountTensorFlow_3.py` and your comments to `README.md

Now "TensorFlow" should be one of the top words—makes more sense, right?

<a id="Task23" />

## Task 2.3: Using the BlueSky API in Python

Let’s explore how to interact with BlueSky using Python.


### Install Required Libraries

BlueSky API is built on top of a decentralized protocol for large-scale social web applications named [AT Protocol](https://atproto.com/guides/overview). Install the Python package:

As a good practice, never hardcode sensitive data into our code. We'll be using [Python dotenv](https://pypi.org/project/python-dotenv/) to keep the values.

```bash
_$ pip install atproto python-dotenv
```

Set up your credentials securely in a `.env` file:

```bash
_$ cat .env
ATP_EMAIL=<YOUR_EMAIL@DOMAIN.COM>
ATP_PASSWORD=<YOUR_PASSWORD>
```
> [!important]
> Never commit `.env` to your repository.  
> Use a `.gitignore` file to exclude it.  
> Learn more: [GitHub Docs on `.gitignore`](https://docs.github.com/en/get-started/getting-started-with-git/ignoring-files)

Here’s a script that logs in and posts a message:

```python
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


def create_and_post_text(client):
    """
    Build and send a post using the AT Proto client.
    Args:
        client (Client): Logged-in AT Proto client instance.
    """
    try:
        text = client_utils.TextBuilder().text("Hello World from ").link("Python SDK", "https://atproto.blue")
        post = client.send_post(text)
        logger.info("Post sent successfully: %s", post.uri)
        return post
    except Exception as e:
        logger.error("Failed to send post: %s", e)
        raise


def like_post(client, post):
    """
    Like a post using the AT Proto client.
    Args:
        client (Client): Logged-in AT Proto client instance.
        post: Post object to like.
    """
    try:
        client.like(post.uri, post.cid)
        logger.info("Post liked successfully: %s", post.uri)
    except Exception as e:
        logger.error("Failed to like post: %s", e)
        raise


def main():
    """
    Main entry point for the script.
    Handles login, posting, and liking a post.
    """
    try:
        client, profile = login_to_client()
        post = create_and_post_text(client)
        like_post(client, post)
    except Exception as e:
        logger.error("An error occurred: %s", e)


if __name__ == "__main__":
    main()
```

<img alt="Lab02-BlueSky.png" src="images/Lab02-BlueSky.png" width="50%"/>

### REST vs Streaming APIs

- **REST API**: Retrieve existing posts (look into the past).
- **Streaming API**: Get new posts in real-time (look into the future).

Use the REST API for historical data (e.g., by user). Use the Streaming API for tracking live activity.

Run [`BlueSky_1.py`](Lab02/BlueSky_1.py) to test post publishing.

> :question: **Question 9**: Did the data print correctly?


### Accessing Posts

By default, a request returns 10 Posts. If you want more than 10 Posts per request, you can specify that using the max_results parameter. The maximum Posts per request is 100.

The code below uses `BLUESKY_USER`that needs to be instantiated in the `.env` file.

```python
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

```

Create a new script and use the previous API presented to obtain information about the posts of a given handle (i.e. for https://bsky.app/profile/upc.edu the handle is **upc.edu**)

> :question: **Question 10**: Add the code to `BlueSky_2.py` and your comments to `README.md

<a id="Task24" />

## Task 2.4: Posts pre-processing

The code used in this Lab session is using part of the work done by [Marco Bonzanini](https://marcobonzanini.com/2015/03/02/mining-twitter-data-with-python-part-1/). As Marco indicates, it is far from perfect, but it’s a good starting point to become aware of the complexity of the problem, and it is reasonably easy to extend.

Let’s look at tokenizing a post. This example shows NLTK’s limitations:

```python
from nltk.tokenize import word_tokenize

post = 'RT @JordiTorresBCN: just an example! :D http://JordiTorres.Barcelona #masterMEI'

print(word_tokenize(post))
```
Problem? NLTK doesn’t treat `@mentions`, `#hashtags`, emojis, or URLs as distinct tokens.

For more accurate tokenization, we can borrow ideas from [Marco Bonzanini](https://marcobonzanini.com/2015/03/02/mining-twitter-data-with-python-part-1/) or use this [alternative tokenizer](CedricTokenizer.py) suggested by former student [Cédric Bhihe](https://www.linkedin.com/in/cedricbhihe/).

```python
import re
 
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
 
def tokenize(s):
    return tokens_re.findall(s)
 
def preprocess(s, lowercase=False):
    tokens = tokenize(s)
    if lowercase:
        tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
    return tokens
 
post = 'RT @JordiTorresBCN: just an example! :D http://JordiTorres.Barcelona #masterMEI'
print(preprocess(post))
```

As you can see, @-mentions, URLs, and #hash-tags are now individual tokens. This tokenizer gives you a general idea of how you can tokenize twitter text using regular expressions (regexp), which is a common choice for this type of problem. 

With the previous essential tokenizer code, some particular types of tokens are not captured but split into several other tokens. To overcome this problem, you can improve the regular expressions, or apply more sophisticated techniques such as [*Named Entity Recognition*](https://en.wikipedia.org/wiki/Named-entity_recognition).

In this example, regular expressions are compiled with the flags re.VERBOSE, to ignore spaces in the regexp (see the multi-line emoticons regexp), and re.IGNORECASE to match both upper and lowercase text. The tokenize() function catches all the tokens in a string and returns them as a list. preprocess() uses tokenize() to pre-process the string: in this case, we only add a lowercasing feature for all the tokens that are not emoticons (e.g., :D doesn’t become :d).

Keep track of the execution examining ten different posts extracted using the API, as shown above. In this initial exercise using BlueSky, if you don't want to have extra problems with *special characters* filter posts *in the English language*.

> :question: **Question 11**: Add the code to `BlueSky_3.py` and your comments to `README.md`.

## Submit Your Assignment

> :question: **Question 12:** How much time did you spend on this session?  
  
> :question: **Question 13:** What challenges did you encounter, and how did you overcome them?

Push your updated repository to GitHub https://github.com/CCBDA-UPC/2026_1-2-xx **before the deadline**, including:

- `README.md` with all your responses and documentation
- Any screenshots
- All new Python files required by the tasks

