# A quick project to load some realtime filtered Twitter API data into Elasticsearch, and then visualize the results in Kibana. Uses an ELK (Elasticsearch/Logstash/Kibana) Docker container for easy reproducibility.

To get Elasticsearch and Kibana up and running quickly, run these docker commands:
docker pull sebp/elk:es235_l234_k454
docker run -p 5601:5601 -p 9200:9200 -p 5044:5044 -p 5000:5000 -it --name elk sebp/elk:es235_l234_k454

After cloning this repo, run pip install to get all of the Python libraries:
pip install -r requirements.txt

For reference:
Python libraries used:
https://github.com/sloria/textblob (https://textblob.readthedocs.io/en/dev/)
https://github.com/tweepy/tweepy (http://tweepy.readthedocs.io/en/v3.5.0/)


