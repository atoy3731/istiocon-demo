import os
import pymongo
from flask import Flask, app, jsonify
from random import randint

app = Flask(__name__)

FIRST_NAMES = [ "John", "David", "Anna", "Sarah" ]
LAST_NAMES = [ "Smith", "Doe", "Parker", "Robinson" ]

MONGO_HOST = os.environ.get('MONGODB_HOST', 'localhost')
MONGO_PORT = os.environ.get('MONGODB_PORT', '27017')
MONGO_USER = os.environ.get('MONGODB_USER', 'mongo')
MONGO_PASS = os.environ.get('MONGODB_PASS', 'mongo')
MONGO_DB = os.environ.get('MONGODB_DB', 'mongo')
MONGO_COLLECTION = os.environ.get('MONGODB_COLLECTION', 'mongo')

APPLICATION_HOST = os.environ.get('APPLICATION_HOST', '0.0.0.0')
APPLICATION_PORT = int(os.environ.get('APPLICATION_PORT', '5000'))

ENTRY_NUMBER = int(os.environ.get('ENTRY_NUMBER', '10'))

mongo_connect_string = 'mongodb://{0}:{1}@{2}:{3}'.format(MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT)
print(mongo_connect_string)
mongo_client = pymongo.MongoClient(mongo_connect_string)

def _init_mongo():
    # Drop the DB
    try:
        print('Dropping DB if it exists..')
        mongo_client.drop_database(MONGO_DB)
    except:
        pass

    # Create a database and inject some test data
    print('Creating and seeding DB..')
    mongo_db = mongo_client[MONGO_DB]
    mongo_collection = mongo_db[MONGO_COLLECTION]

    for x in range(0, ENTRY_NUMBER):
        entry = { "firstName": FIRST_NAMES[randint(0, len(FIRST_NAMES)-1)], "lastName": LAST_NAMES[randint(0, len(LAST_NAMES)-1)] }
        mongo_collection.insert_one(entry)

@app.route('/user')
def get_user():
    print('Getting user')
    mongo_db = mongo_client[MONGO_DB]
    mongo_collection = mongo_db[MONGO_COLLECTION]

    response = mongo_collection.aggregate([{ "$sample": { "size": 1 } } ])
    user = None

    for r in response:
        user = {
            'firstName': r['firstName'],
            'lastName': r['lastName']
        }
        return jsonify(user)

if __name__ == '__main__':
    _init_mongo()

    app.run(host=APPLICATION_HOST, port=APPLICATION_PORT)
