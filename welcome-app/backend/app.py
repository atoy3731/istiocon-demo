import os
from flask import Flask, app, jsonify, request
from random import randint
import jwt
import pymongo

app = Flask(__name__)

class NotFoundException(Exception):
    pass

SEED_USERS = [
    {
        'user_id': 'adam.toy',
        'city': 'Washington',
        'state': 'DC',
        'country': 'US'
    }
]

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

    for user in SEED_USERS:
        print(user)
        mongo_collection.insert_one(user)

def _get_user_location(user_id):
    mongo_db = mongo_client[MONGO_DB]
    mongo_collection = mongo_db[MONGO_COLLECTION]

    user = mongo_collection.find_one({'user_id': user_id})
    
    if user is None:
        raise NotFoundException
    
    return  {
        'city': user['city'],
        'state': user['state'],
        'country': user['country']
    }

@app.route('/user')
def get_user():
    if 'Jwt' in request.headers:
        print('Getting user from JWT')
        auth_jwt = request.headers.get('Jwt')
        decoded_auth_jwt = jwt.decode(auth_jwt, options={"verify_signature": False, "verify_aud": False})

        user = {
            'random': False,
            'firstName': decoded_auth_jwt['given_name'],
            'lastName': decoded_auth_jwt['family_name']
        }

        try:
            user.update(_get_user_location(decoded_auth_jwt['preferred_username']))
        except NotFoundException:
            return jsonify({ "error": "UserNotFoundException" }), 500

    else:
        print('Uh oh, no auth token. Returning an empty user.')
        user = {
            'random': True,
            'firstName': None,
            'lastName': None,
            'city': None,
            'state': None,
            'country': None
        }

    return jsonify(user)

if __name__ == '__main__':
    _init_mongo()

    print('Running app on port {}..'.format(APPLICATION_PORT))
    app.run(host=APPLICATION_HOST, port=APPLICATION_PORT)
