# Installation


```
sudo apt-get install mongodb-server
```

# Running

First start a mongo server, 
```
mongod --port=27900 --dbpath=/path/to/db/store
```

Then connect with the server,
```python
import pymongo
client = pymongo.MongoClient('locahost:27900')
```

Relevant links
```
http://stackoverflow.com/questions/37014186/running-mongodb-on-ubuntu-16-04-lts
```

