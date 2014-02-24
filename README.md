# `smappPy`

*Python package and tools for Twitter data analysis. Contact: SMaPP Lab, NYU.*

# Introduction

Tweetstream is a Python "package" (a module of modules - basically, a structured collection of code) that addresses common tasks for programming with Tweets and analyzing Twitter data.

This includes:
    
1. interfacing with Twitter to find tweets and user data (based on user, keyword, and/or location)
2. accessing tweets and other twitter data stored in MongoDB databases
3. getting information about those tweets (contains links/mentions/hashtags/etc, is a retweet, contains location information or not, etc)
4. mining tweet collections for interesting features (most popular hashtags, links shared, images tweeted, etc)
5. doing advanced computations on tweet collections, such as modeling topics or building retweet networks

The package is a WIP. Existing and future functionality is defined below. Examples of how to use library functions to complete common tasks are also coming.

# Functionality

## Getting tweets from Twitter

### smappPy.get_tweets:
    
    keyword_tweets(oauth_file, keyword_list, limit_per_keyword)

    user_tweets(oauth_file, userid_list, limit_per_user)

    geo_tweets(oauth_file, geoloc_list, limit_per_location)


These methods query twitter via the REST interface (single-transaction. NOT STREAMING)

Also, for many users/keywords/locations and many tweets, these methods WILL hit twitter rate limits. The code will wait for rate limits to reset by itself, but it may take a while.

### smappPy.streaming:

    stream_listener.SimpleFileListener  - captures live tweets, stores in txt file

    stream_listener.SimpleDBListener     - caputes live tweets, stores in MongoDB

Can capture "live" tweets based on keyword, user tweeting, and location. (This is a more complex and detailed system than fetching from the REST API. See the code for more.)

## Getting user data

Can capture Twitter user data (including account info, picture, tweet numbers,
friends, followers, etc)

### smappPy.user_data:

    get_user_data(oauth_file, userid_list)

## Utilities for getting tweets

### smappPy.utilities

    read_tweets_from_file(tweet_file)   - returns a list of tweet objects (json/dict)

    write_tweets_to_file(tweet_file, tweets)    - stores tweets (in json) in a file

    get_tweets_from_db(server, port, user, password, database, collection, keywords, number)

    store_tweets_in_db(server, port, user, password, database, collection, tweets)

## Checking out your tweets

### smappPy.retweet

    is_retweet(tweet)
    is_official_retweet(tweet)
    is_manual_retweet(tweet)

    get_user_retweeted(tweet)
    split_manual_retweet(tweet) - returns the "before and after" text of a manual RT

### smappPy.mention

    contains_mention(tweet)
    get_users_mentioned(tweet)  - returns a list of users mentioned in the tweet

### smappPy.tweet_image

    contains_image(tweet)
    get_image_url(tweet)
    save_image_to_file(tweet, img_file)   - saves image in tweet to a file

.. etc ..

## Analysis (more fun)

### smappPy.networks

    build_retweet_network(tweets, internal_only?)
    display_retweet_network(network, outfile?, )

    export_network(outfile?)    - exports a network to Gephi format (for prettyness)

### smappPy.topics  - IN PROGRESS

# Examples of what we can do...

These topics come from programming lectures given to SMaPP students. See [Programmer Group](https://github.com/SMAPPNYU/ProgrammerGroup) for the full code.

1. Plot the number of tweets per minute with co-occuring words "Obama" and "Syria"
2. Get a collection of tweets (from DB or twitter), output CSV representation of all tweets with added indicator variables (eg: IsRetweet? HasImage?)
3. Get a collection of tweets, go over all and compute aggregate statistics (eg: number of tweets, tweets/user, number of tweeters, tweets per day)
4. Access DataScienceToolkit services, measure sentiment of tweet. Compute aggregate sentiment (basic measure) of tweets per topic.
5. Plot sentiment-per-day of tweets on a certain topic (again, basic sentiment analysis)
6. Collect streaming, real-time tweets by keywords, users, or geolocations - EG, collect all tweets coming from Kyiv (very specific location). Plot them on a map via OpenHeatMap
7. Create "networks" from tweets - user retweet network, tweet-retweet network, etc

