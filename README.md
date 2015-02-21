# smappPy

*Python package and tools for Twitter data analysis. Contact: SMaPP Lab, NYU.*

smappPy is a Python "package" (a module of modules - basically, a structured collection of code) that addresses common tasks for programming with Tweets and analyzing Twitter data.

This includes:
    
1. interfacing with Twitter to find tweets and user data (based on user, keyword, and/or location)
2. accessing tweets and other twitter data stored in files or MongoDB databases
3. getting information about tweets (contains links/mentions/hashtags/etc, is a retweet, contains location information or not, etc)
4. mining tweet collections for interesting features (popular hashtags, links shared, images tweeted, etc)
5. doing advanced computations on tweet collections, such as modeling topics or building networks

The package is a WIP (eg: eventually, we will include facebook tools). Existing and future functionality is defined below. Examples of how to use library functions to complete common tasks are also coming.

**Contents:**

[Dependencies](#0-dependencies)

1. [Tweets from Twitter](#1-getting-tweets-from-twitter)

2. [User data from Twitter](#2-getting-user-data-from-twitter)

3. [Tweets to/from files and DBs](#3-getting-and-storing-tweets-files-and-databases)

4. [Tweet utilities](#4-tweet-utilities)

5. [Checking out your tweets](#5-checking-out-your-tweets)

6. [Tweeted image utilities](#6-tweeted-image-utilities)

7. [URL utilities](#7-url-utilities)

8. [Text processing utilities](#8-text-processing-utilities)

9. [Other functionality](#9-other-functionality)

10. [Analysis (networks, etc)](#10-analysis-more-fun)

11. [Facebook data](#11-facebook-data)

[Example tasks](#examples-of-what-we-can-do)

## 0 Dependencies

- [tweepy](https://pypi.python.org/pypi/tweepy/2.2) (python interface to the Twitter API)
- [pymongo](https://pypi.python.org/pypi/pymongo/) (python interface to MongoDB)

We recommend using the [Anaconda Python](https://store.continuum.io/cshop/anaconda/) distribution, which contains almost all other prereqs for our code, and a bunch of useful python packages besides (numpy, scipy, matplotlib, networkx, etc).

We also use the [pip](http://www.pip-installer.org/en/latest/) package management tool, which is included in Anaconda python:

    pip install tweepy
    pip install pymongo

*Note: this dependency section is not totally complete. Some functions required additional libraries. This section will be updated as dependencies are remembered. (EG: some URL utility functionality requires additional libraries)*

## 1 Getting tweets from Twitter

### smappPy.get_tweets:
    
    keyword_tweets(oauth_file, keyword_list, limit_per_keyword)
    user_tweets(oauth_file, userid_list, limit_per_user)
    place_tweets(oauth_file, geoloc_list, query, limit_per_location)

These methods query twitter via the REST interface (single-transaction. NOT STREAMING)

*Note: calling these methods can incur a rate limit exception, in the case that too many requests have been made to the Twitter API. This is left for the user to handle. An example will be provided of how to do so.*

Usage of place_tweets and georadius_tweets:

```python

import smappPy.get_tweets as smapp

locations = smapp_get_tweets.place_tweets(api, query="Coffee", place_list=["Manchester"], limit=1)

locations_mult = smapp_get_tweets.place_tweets(api, query="Coffee", place_list=["Glasgow", "Dublin"], limit=1)

locations_from_georadius_single = smapp_get_tweets.georadius_tweets(api, query="Coffee",  georadius_list=[[37.781157,-122.398720,"1mi"]], limit=1)

locations_from_georadius_multiple = smapp_get_tweets.georadius_tweets(api, query="Coffee", georadius_list=[[32.781830, -96.795860,"1mi"], [37.781157,-122.398720,"1mi"]], limit=1)

for iterator in locations:
    for item in iterator:
        print("Single Geoloc England Item:")
        print(item)

for iterator in locations_mult:
    for item in iterator:
        print("Mult Geoloc Scot/Ireland Item:")
        print(item)

for iterator in locations_from_georadius_single:
    for item in iterator:
        print("Location from Radius Single:")
        print(item)

for iterator in locations_from_georadius_multiple:
    for item in iterator:
        print("Location from Radius Multiple:")
        print(item)

```
the "query" parameter is optional and can be omitted. If run with a query="Coffee", it will only pull
tweets about query="Coffee" from the coordinates and radii you give it. If left blank I assume 
you will be pulling the top tweets or some sudo-random kinds of tweets.

### smappPy.streaming:

    stream_listener.SimpleFileListener  # captures live tweets, stores in txt file

    stream_listener.SimpleDBListener    # captures live tweets, stores in MongoDB

Can capture "live" tweets based on keyword, user tweeting, and location. (This is a more complex and detailed system than fetching from the REST API. See the code for more.)

## 2 Getting user data from Twitter

Can capture Twitter user data (including account info, picture, tweet numbers,
friends, followers, etc)

### smappPy.user_data:

    get_user_data(oauth_file, userid_list)  # returns a list of twitter user objects for each ID (if valid)

*Note: twitter user object defined [here](https://dev.twitter.com/docs/platform-objects/users)*

## 3 Getting and Storing tweets (files and databases)

### smappPy.get_tweets

    tweets_from_file(tweetfile)             # returns a list of tweet objects (json/dict)
    tweets_from_file_IT(tweetfile)          # returns an iterator over tweet objects in file (json/dict)
    tweets_from_db(server, port, user, password, database, collection, keywords, number)
    db_tweets_by_date(server, port, user, password, database, collection, start, end, number)
    
### smappPy.store_tweets

    tweets_to_file(tweets, tweet_file, ...)    # stores tweets (in json) in a file
    tweets_to_db(server, port, user, password, database, collection, tweets)

*Note: for more complicated queries for getting tweets from a MongoDB instance, we recommend you read up on [pymongo documentation](http://api.mongodb.org/python/2.7rc0/tutorial.html) and [tweet structure](https://dev.twitter.com/docs/platform-objects/tweets)*

*Note: When we store tweets to a MongoDB instance provided, we add two fields for easier data access: 'random_number' - a random decimal (0,1), making it easy to get a random sample of tweets; and 'timestamp' - a MongoDB Date object / python datetime object (depending on context), making tweets easier to query by datetime. See Tweet utilities section below.*

*Note: to use the 'tweets_to_db' function, the given username must have write privileges to the given database.*

## 4 Tweet utilities

### smappy.transform_tweets

    add_random_to_tweet(tweet)      # adds random_number field to tweets
    add_timestamp_to_tweet(tweet)   # adds timestamp corresponding to 'created_at' to tweet
    transform_collection(collection, create_indexes=True)   # adds timestamp and random fields to a collection of tweets, and creates indexes on collection for faster access to tweets

## 5 Checking out your tweets

### smappPy.retweet

    is_retweet(tweet)           # checks for all types of retweet (RT)
    is_official_retweet(tweet)  # checks for literal retweet via Twitter's retweet button
    is_manual_retweet(tweet)    # checks for manual "RT @someuser ..." type of RT
    is_partial_retweet(tweet)   # checks for manual RTs with additional text (may just be space)

    get_user_retweeted(tweet)   # returns a tuple (user ID, user screen name). If manual RT, id is None
    split_manual_retweet(tweet) # splits a manual Rt into "pre, userRTed, post" text elements

### smappPy.MT

    is_MT(tweet)                # checks for all cases of MT (modified tweets)
    is_initial_MT(tweet)        # if the MT is the whole tweet
    is_interior_MT(tweet)       # if the MT comes with additional tweeter commentary
    split_MT(tweet)             # splits an interior MT into "pre, userMTed, post" elements

### smappPy.entities

    remove_entities_from_text(tweet)    # returns tweet text string with all entity strings removed

    contains_mention(tweet)     # returns True if tweet contains a mention
    num_mentions(tweet)         # returns number of mentions in tweet
    get_users_mentioned(tweet)  # returns a list of users mentioned in the tweet

    contains_hashtag(tweet)     # (same as for mentions)
    num_hashtag(tweet)
    get_hashtags(tweet)

    contains_link(tweet)        # returns True if tweet contains a link (url or media)
    num_links(tweet)

    contains_image(tweet)       # returns True if tweet contains an image post (media)
    get_image_urls(tweet)       # returns a list of all image URLs contained in the tweet

## 6 Tweeted image utilities

### smappPy.image_util

    save_web_image(url, filename)   # given an image's URL, saves that image to filename
    get_image_occurrences(tweets)   # given an iterable of tweets, returns a dictionary of image urls and the number of times the occur in the tweet set.

## 7 URL utilities

    urllib_get_html(url)    # Uses urllib to download a webpage, returns the page's html as a string
    requests_get_html(url)  # (same as above, but with requests module instead of urllib)
    get_html_text(html)     # takes html of a webpage, returns clean plain text of website contents (good for articles!)
    clean_whitespace(string, replacement=" ")   # replaces all whitespace in a string with, by default, a single space

*Note: get_html_text function works via [readability](https://pypi.python.org/pypi/readability-lxml) and [nltk](http://www.nltk.org/)*

## 8 Text processing utilities

### smappPy.text_clean

    remove_punctuation(text)    # translates most punctuation to single spaces
    csv_safe(text)              # replaces csv-breaking characters (comma, tab, and newline) with placeholders
    
    translate_whitespace(text)  # translates all whitespace chars to single spaces
    translate_shorthand(text)   # translate common shorthand to long form (eg: w/ to with)
    translate_acronyms(text)    # translates some common acronyms to long form.
    translate_unicode(text)     # translates unicode that breaks some software into ASCII
    translate_contractions(text)    # translates all unambiguous english language contractions into multiple words

*Note: all translation and removal functions can (and should) be customized in the translation tables at the top of the text_clean.py code*

## 9 Other functionality

    language    # includes python definitions for all Twitter-supported languages
    date        # date functions to translate twitter date strings to Python datetime objects
    json_util   # utilities for reading/writing JSON and MongoDB "bson" files
    oauth       # tools for reading and verifying oauth json files for Twitter authentication
    autoRT      # a tool to autoretweet any of a set of users' tweets during certain timeframes (to show your rowdy students who are tweeting during class that your twitter game is muy strong, and better than theirs)

## 10 Analysis (more fun)

### smappPy.networks

    build_retweet_network(tweets, internal_only=True)       # given a collection of tweets, constructs and returns retweet network
    display_retweet_network(network, outfile="default")     # creates a basic display (via matplotlib) of the RT network

    export_network(outfile?)    # exports a network to Gephi format (for further processing and vis.)

*Note: all network functionality is via the networkx package (included in Anaconda python).*

### smappPy.topics
    
    IN PROGRESS

    utilities.get_topic_string(model, topic_id, top_n)      # Returns a string representing a topic from given model
    utilities.get_short_topic_string(%)                     # Same, different representation
    utilities.get_topic_strings(model, num_topics, top_n, ordered)  # Returns a list of representative topic strings

    utilities.get_doc_topic_strings(corpus, model. num_docs, topic_threshold, min_topics, topic_words)
                                                            # Prints documents in a corpus, the document's topics, and the topic's words

    # All functions above can also be "print"changed, eg: utilities.print_topic_strings(...)

    visualization.topic_barchart(corpus, model, topic_threshold, show, outfile, bar_width, trim)
                                                            # Creates, shows, and saves a barchart representing topic occurence in all corpus docs (if topic is >= threshold for that doc)

## 11 File Formats

OAuth Files should be of the format:

```json
[
    {
        "consumer_key": "YOUR_CONSUMER_KEY",
        "consumer_secret": "YOUR_CONSUMER_SECRET",
        "acces_token": "YOUR _ACCESS_TOKEN",
        "access_token_secret": "YOUR_ACCESS_TOKEN_SECRET"
    },
    {
        "consumer_key": "YOUR_CONSUMER_KEY",
        "consumer_secret": "YOUR_CONSUMER_SECRET",
        "acces_token": "YOUR _ACCESS_TOKEN",
        "access_token_secret": "YOUR_ACCESS_TOKEN_SECRET"
    }
]
```
where there can be any number of JSON objects inside the array. 
The file above could be called "oauth-file.json" for extra clarity. 

## 12 Facebook data

IN PROGRESS. Basic scripts exist to scrape data from facebook pages.

# Examples of what we can do...

These topics come from programming lectures given to SMaPP students. See [Programmer Group](https://github.com/SMAPPNYU/ProgrammerGroup) for the full code.

1. Plot the number of tweets per minute with co-occuring words "Obama" and "Syria"
2. Get a collection of tweets (from DB or twitter), output CSV representation of all tweets with added indicator variables (eg: IsRetweet? HasImage?)
3. Get a collection of tweets, go over all and compute aggregate statistics (eg: number of tweets, tweets/user, number of tweeters, tweets per day)
4. Access DataScienceToolkit services, measure basic sentiment of tweet. Compute aggregate sentiment (basic measure) of tweets per keyword-topic.
5. Plot sentiment-per-day of tweets on a certain topic (again, basic sentiment analysis)
6. Collect streaming, real-time tweets by keywords, users, or geolocations - EG, collect all tweets coming from Kyiv (very specific location). Plot them on a map via OpenHeatMap
7. Create "networks" from tweets - user retweet network, tweet-retweet network, etc
8. Get the top N tweeted images in a certain date range (or any set of tweets). Same for hashtags, links, base-linked domains, etc.
9. etc. Any functionality you can put together with these tools and other resources
