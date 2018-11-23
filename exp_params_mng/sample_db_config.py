import pymongo

EXP_CLIENT = pymongo.MongoClient('localhost:your-port-number')
EXP_CLIENT['dev'].authenticate('your_user_name', 'your_pwd')
