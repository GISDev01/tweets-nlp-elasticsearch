'''
A short script (Python 2.7) to ingest Twitter content into Elasticsearch in realtime.
'''

import json
import os.path
import time
import yaml

from elasticsearch import Elasticsearch

from textblob import TextBlob

from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

import logging
from logging import handlers
import sys

# config.yml should exist in the same directory as this file
if not os.path.isfile('config.yml'):
    print 'You need to rename the config.yml.template to config.yml and insert your Twitter creds in the yaml config file'

logs_dir_name = 'log'
if not os.path.exists(logs_dir_name):
    os.makedirs(logs_dir_name)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
LOG_FORMAT = logging.Formatter('%(asctime)-15s %(levelname)s: %(message)s')

stdout_logger = logging.StreamHandler(sys.stdout)
stdout_logger.setFormatter(LOG_FORMAT)
logger.addHandler(stdout_logger)

file_logger = handlers.RotatingFileHandler(os.path.join(logs_dir_name, 'TweetsToES.log'),
                                           maxBytes=(1048576 * 5),
                                           backupCount=5)
file_logger.setFormatter(LOG_FORMAT)
logger.addHandler(file_logger)


es = Elasticsearch()


class TweetStreamListener(StreamListener):
    def on_data(self, data):

        # Load JSON payload into a dict to make it easy to parse out
        tweet_json = json.loads(data)
        tweet_raw_text = tweet_json["text"]

        # Load the text of the tweet into a TextBlob so it can be analyzed
        tweet_text_blob = TextBlob(tweet_raw_text)

        # Value between -1 and 1 - TextBlob Polarity explanation in layman's
        # terms: http://planspace.org/20150607-textblob_sentiment/
        text_polarity = tweet_text_blob.sentiment.polarity
        logger.debug('Tweet Polarity: {}'.format(text_polarity))

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
            "msgid": tweet_json["id_str"],
            "tweet_timestamp_ms": tweet_json["timestamp_ms"],
            "date": tweet_json["created_at"],
            "is_quote_status": tweet_json["is_quote_status"],
            "in_reply_to_status_id": tweet_json["in_reply_to_status_id"],
            "in_reply_to_screen_name": tweet_json["in_reply_to_screen_name"],
            "favorite_count": tweet_json["favorite_count"],
            "author": tweet_json["user"]["screen_name"],
            "tweetMsg": tweet_json["text"],
            "retweeted": tweet_json["retweeted"],
            "retweet_count": tweet_json["retweet_count"],
            "geo": tweet_json["geo"],
            "place": tweet_json["place"],
            "coordinates": tweet_json["coordinates"],
            "polarity": text_polarity,
            "subjectivity": tweet_text_blob.sentiment.subjectivity,
            "sentiment": sentiment,
            "time_ingested": int(time.time())
        }

        # can decide if you want to write the analyzed tweet to ES or a static file (or both)
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


if __name__ == '__main__':
    with open("config.yml", 'r') as yaml_config_file:
        config = yaml.load(yaml_config_file)

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
    # TODO: refactor keywords into config file
    logger.debug('Starting the Filtered Stream')
    tw_stream.filter(track=['python', 'javascript', 'node', 'java', 'elasticsearch'])
