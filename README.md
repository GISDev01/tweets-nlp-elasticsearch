# A Python 2.7 project to load realtime filtered Twitter API data into Elasticsearch, and then visualize the results in Kibana. 
Uses an ELK (Elasticsearch/Logstash/Kibana) 6.3.2 Docker container for easy reproducibility. 
Tested with Python 2.7 (Anaconda Distro) on Win10 and MacOS 10.13.3.

To get Elasticsearch and Kibana up and running locally quickly, run these 2 docker commands.

Note: Make sure you have at least 4GB of RAM assigned to Docker. Second, increase the limit on mmap counts equal to 262,144 or more on Mac or Linux (I implement this workaround in the below Mac command). See here for more info on this:
http://elk-docker.readthedocs.io/
Warning: Do not pull this public image on a low-bandwidth or metered Internet connection. It pulls down well over 5GB of traffic, total.
```
docker pull sebp/elk:632
```
Windows:
```
docker run -p 5601:5601 -p 9200:9200 -p 5044:5044 -p 5000:5000 -it --name elk sebp/elk:632
```
Mac:
```
docker run -p 5601:5601 -p 9200:9200 -p 5044:5044 -p 5000:5000 -e MAX_MAP_COUNT="262144" -it --name elk sebp/elk:632
```
More info on this Docker container can be found here: https://hub.docker.com/r/sebp/elk/

After the Docker container is up and running, you should be able to hit these 2 URLs if everything is working properly:

Elasticsearch: http://localhost:9200/

Should return a similar response to this:
~~~
{
  "name" : "randomstring",
  "cluster_name" : "elasticsearch",
  "cluster_uuid" : "randomstring2",
  "version" : {
    "number" : "6.3.2",
    "build_flavor" : "default",
    "build_type" : "tar",
    "build_hash" : "053779d",
    "build_date" : "2018-07-20T05:20:23.451332Z",
    "build_snapshot" : false,
    "lucene_version" : "7.3.1",
    "minimum_wire_compatibility_version" : "5.6.0",
    "minimum_index_compatibility_version" : "5.0.0"
  },
  "tagline" : "You Know, for Search"
}
~~~

Kibana: http://localhost:5601/

Should return the Kibana Web GUI
When we first open the Kibana Web GUI, we need to enter the text 'twitteranalysis' where it asks for the Index name or pattern on the Management tab (on the left).

After cloning this repo, we can run pip install to get all of the Python libraries:
`pip install -r requirements.txt`

Python libraries used:
~~~
https://github.com/sloria/textblob
https://github.com/tweepy/tweepy
https://elasticsearch-py.readthedocs.io/en/master/api.html
~~~
After filling in your Twitter API credentials in the config.yml (rename the config.yml.template to config.yml), you can let the script run for a few minutes and load up the Index in Elasticsearch. After some data is loaded up in Elasticsearch, try a few URLs like this:

http://localhost:9200/twitteranalysis/_search?q=python
http://localhost:9200/twitteranalysis/_search?q=sentiment:Positive&message=python

Feel free to open an issue if you have any problems getting this up and running, and I will help you out.
