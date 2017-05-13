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


