import json

from configlocal import *

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob

from elasticsearch import Elasticsearch
es = Elasticsearch()



class TweetStreamListener(StreamListener):

    def on_data(self, data):
        
        #Load JSON payload into a dict to make it easy to parse out
        tweetDict = json.loads(data)
        tweetRawText = tweetDict["text"]
        #print tweetRawText
        
        #Load the text of the tweet into a TextBlob so it can be analyzed
        tweetAnalyzed = TextBlob(tweetRawText)
        
        #Value between -1 and 1 - TextBlob Polarity explanation in layman's terms: http://planspace.org/20150607-textblob_sentiment/
        
        tweetPolarity = tweetAnalyzed.sentiment.polarity
        

        if tweetPolarity == 0:
            sentiment = "Neutral"
        elif tweetPolarity < 0:
            sentiment = "Negative"
        elif tweetPolarity > 0:
            sentiment = "Positive"
        else:
            sentiment = "UNKNOWN"
        
        
        print "TextBlob calc'ed Polarity: " + str(tweetPolarity)
        print "TextBlob Analysis Sentiment: " + sentiment

        #Send Analyzed Tweet into ES Index for visualization in Kibana
        es.index(index="twitteranalysis",
                    doc_type="tweet",
                    body={
                        "date": tweetDict["created_at"],
                        "author": tweetDict["user"]["screen_name"],
                        "tweetMsg": tweetDict["text"],
                        "polarity": tweetPolarity,
                        "subjectivity": tweetAnalyzed.sentiment.subjectivity,
                        "sentiment": sentiment
                        }
                )
                
        return True


    def on_error(self, status):
        print status

if __name__ == '__main__':

    #Read twitter API access info from the config file
    twitterAuth = OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    twitterAuth.set_access_token(twitter_access_token, twitter_access_token_secret)

    #Create an instance of the tweepy tweet stream listener
    twitterListener = TweetStreamListener()

    #Create an instance of the tweepy raw stream
    twitterStream = Stream(twitterAuth, twitterListener)

    #Stream that is filered on keywords
    twitterStream.filter(track=['olympics', 'running', 'triathlon'])