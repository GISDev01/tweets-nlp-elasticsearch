# A quick Py2.7 project to load some realtime filtered Twitter API data into Elasticsearch, and then visualize the results in Kibana. 
Uses an ELK (Elasticsearch/Logstash/Kibana) 5.3.0 Docker container for easy reproducibility. Tested with Python 2.7 (Anaconda Distro) on Win10.

To get Elasticsearch and Kibana up and running locally quickly, run these 2 docker commands.
Note: If we're going to run this docker container, make sure we have at least 4GB of RAM assigned to Docker. Second, we must increase the limit on mmap counts equal to 262,144 or more on Mac or Nix. See here for more info on this: http://elk-docker.readthedocs.io/
```
docker pull sebp/elk:530
docker run -p 5601:5601 -p 9200:9200 -p 5044:5044 -p 5000:5000 -it --name elk sebp/elk:530
```
More info on this Docker container can be found here: https://hub.docker.com/r/sebp/elk/

After the Docker container is up and running, you should be able to hit these 2 URLs if everything is working properly:

Elasticsearch: [http://localhost:9200/]
Should return a similar response to this:
{
name: "randomstring",
cluster_name: "elasticsearch",
cluster_uuid: "randomstring",
version: {
number: "5.3.0",
build_hash: "3adb13b",
build_date: "2017-03-23T03:31:50.652Z",
build_snapshot: false,
lucene_version: "6.4.1"
},
tagline: "You Know, for Search"
}

Kibana: http://localhost:5601/
Should return the Kibana Web GUI
When we first open the Kibana Web GUI, we need to enter the text 'twitteranalysis' where it asks for the Index name or pattern on the Management tab (on the left).

After cloning this repo, we can run pip install to get all of the Python libraries:
`pip install -r requirements.txt`

Python libraries used:
https://github.com/sloria/textblob
https://github.com/tweepy/tweepy
https://elasticsearch-py.readthedocs.io/en/master/api.html

After filling in your Twitter API credentials in the config.yml (rename the config.yml.template to config.yml), you can let the script run for a few minutes and load up the Index in Elasticsearch. After some data is loaded up in Elasticsearch, try a few URLs like this:

http://localhost:9200/twitteranalysis/_search?q=python
http://localhost:9200/twitteranalysis/_search?q=sentiment:Positive&message=python

Feel free to email me if you have any problems getting this up and running. 