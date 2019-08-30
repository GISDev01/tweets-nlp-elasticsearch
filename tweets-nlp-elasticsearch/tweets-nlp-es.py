"""
Purpose: Insert tweets into Elasticsearch cluster and visualize the results in Kibana.
Python 3.6
1. pip install -r requirements
2. cp ./config/config.yml.template ./config/config.yml
3. nano ./config/config.yml
4. Paste your Twitter API credentials into the config.yml
5. Make sure the ELK 7.x stack is up and running.
6. Run this script to ingest filtered tweets into Elasticsearch in realtime
7. Visualize the NLP results in Kibana
"""

import json
import logging
import os.path
import sys
import time

from logging import handlers

import yaml

from elasticsearch import Elasticsearch

from textblob import TextBlob

from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

# config.yml should exist in the same directory as this file
if not os.path.isfile(os.path.join('config', 'config.yml')):
    print('config.yml was not found. You probably need to rename the config.yml.template to config.yml ' +
          'and insert your Twitter credentials in this config file')
    sys.exit()

logs_dir_name = 'log'
if not os.path.exists(logs_dir_name):
    os.makedirs(logs_dir_name)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
LOG_FORMAT = logging.Formatter('%(asctime)-15s %(levelname)s: %(message)s')

stdout_logger = logging.StreamHandler(sys.stdout)
stdout_logger.setFormatter(LOG_FORMAT)
logger.addHandler(stdout_logger)

file_logger = handlers.RotatingFileHandler(os.path.join(logs_dir_name, 'tweets-nlp-es.log'),
                                           maxBytes=(1048576 * 5),
                                           backupCount=3)
file_logger.setFormatter(LOG_FORMAT)
logger.addHandler(file_logger)

es = Elasticsearch()


class TweetStreamListener(StreamListener):
    def on_data(self, data):

        # Load JSON payload into a dict to make it easy to parse out
        tweet_json = json.loads(data)

        # short-circuit exit if no text is found in the tweet item
        if 'text' not in tweet_json.keys():
            logger.warning('Text not found in this tweet. Skipping it.')
            return True

        tweet_raw_text = tweet_json["text"]

        # Load the text of the tweet into a TextBlob so it can be analyzed
        tweet_text_blob = TextBlob(tweet_raw_text)

        # Value between -1 and 1 - TextBlob Polarity explanation in layman's
        # terms: http://planspace.org/20150607-textblob_sentiment/
        text_polarity = tweet_text_blob.sentiment.polarity
        logger.debug(
            'Tweet Polarity: {} - on Tweet Text: {}'.format(text_polarity,
                                                            tweet_raw_text.encode('UTF-8', 'replace')))

        if text_polarity == 0:
            sentiment = "Neutral"
        elif text_polarity < 0:
            sentiment = "Negative"
        elif text_polarity > 0:
            sentiment = "Positive"
        else:
            sentiment = "UNKNOWN"

        logger.debug('TextBlob Analysis Sentiment: {}'.format(sentiment))

        analyzed_tweet = {
            "tweet_id": tweet_json["id_str"],
            "tweet_timestamp_ms": tweet_json["timestamp_ms"],
            "tweet_date": tweet_json["created_at"],
            "is_quote_status": tweet_json["is_quote_status"],
            "in_reply_to_status_id": tweet_json["in_reply_to_status_id"],
            "in_reply_to_screen_name": tweet_json["in_reply_to_screen_name"],
            "favorite_count": tweet_json["favorite_count"],
            "author": tweet_json["user"]["screen_name"],
            "tweet_text": tweet_json["text"],
            "retweeted": tweet_json["retweeted"],
            "retweet_count": tweet_json["retweet_count"],
            "geo": tweet_json["geo"],
            "place": tweet_json["place"],
            "coordinates": tweet_json["coordinates"],
            "polarity": text_polarity,
            "subjectivity": tweet_text_blob.sentiment.subjectivity,
            "sentiment": sentiment,
            "epoch_time_ingested": int(time.time())
        }

        # can decide if we want to write the analyzed tweet to ES or a static file (or both)
        write_tweet_to_json_file(analyzed_tweet)
        write_analyzed_tweet_to_es(analyzed_tweet)

        return True

    def on_error(self, status):
        logger.error("Fatal Error: {}".format(status))
        # Disconnect the stream
        return False


# helper functions for dealing with the processed tweet data
def write_tweet_to_json_file(tweet_data):
    try:
        with open('tweetstream.json', 'a') as out_file:
            out_file.write(str(tweet_data))
    except BaseException as err:
        logger.exception("Exception writing tweet to JSON file: {}".format(err))


def write_analyzed_tweet_to_es(tweet_data):
    try:
        # Send Analyzed Tweet into ES Index for visualization in Kibana
        es.index(index="twitteranalysis",
                 doc_type="tweet",
                 body=tweet_data
                 )
    except BaseException as err:
        logger.exception("Exception writing tweet to ES: {}".format(err))


def get_config():
    try:
        with open(os.path.join("config", "config.yml"), "r") as yaml_config_file:
            _config = yaml.load(yaml_config_file)
        return _config
    except:
        logger.exception('config.yml file cannot be found or read. '
                         'You might need to fill in the the config.yml.template and then rename it to config.yml')


if __name__ == '__main__':
    config = get_config()

    # Read twitter API access info from the config file
    twitter_auth = OAuthHandler(config['twitter_consumer_key'], config['twitter_consumer_secret'])
    twitter_auth.set_access_token(config['twitter_access_token'], config['twitter_access_token_secret'])

    logger.debug('Creating Listener')
    # Create an instance of the tweepy tweet stream listener
    twitter_listener = TweetStreamListener()

    logger.debug('Creating Stream')
    # Create an instance of the tweepy raw stream
    tw_stream = Stream(twitter_auth, twitter_listener)

    # Stream that is filtered on keywords
    logger.debug('Starting the Filtered Stream')

    twitter_terms_to_track = config['twitter_terms_to_track']
    logger.info('Tracking Terms: {}'.format(twitter_terms_to_track))

    tw_stream.filter(track=twitter_terms_to_track, languages=['en'])
