# Installation


```
sudo apt-get install mongodb-server
```

# Running

First start a mongo server, 
```
mongod --port=27900 --dbpath=/path/to/db/store
```

Alternatively, options can be specified in `/etc/mongod.conf` and the
mongod server can be started as

```
mongod --config /etc/mongod.conf
```

For enabling authorization, in the `.conf` file specify:
```
security
  authorization: enabled
```

In case you are using the conf file and cannot connect from 
other machines (other than the localhost), comment out `bindIp` in the conf file. 

Then connect with the server,
```python
import pymongo
client = pymongo.MongoClient('locahost:27900')
```

Relevant links
```
http://stackoverflow.com/questions/37014186/running-mongodb-on-ubuntu-16-04-lts
```

# Automatic Testing
To install code for running the tests automatically before a commit run
```
./scripts/install-hooks.bash
```

