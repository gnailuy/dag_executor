from pymongo import MongoClient
from pymongo import ReturnDocument
from urllib.parse import quote


def get_mongo(db,
              host='localhost', port=27017,
              user=None, password=None):
    mongo_uri = 'mongodb://'
    if user is not None:
        mongo_uri += '%(user)s' % locals()
        if password is not None:
            mongo_uri += ':' + quote(password)
        mongo_uri += '@'
    mongo_uri += '%(host)s:%(port)s/%(db)s' % locals()

    client = MongoClient(mongo_uri)
    return client[db]


def get_mongo_collection(db, collection,
                         host='localhost', port=27017,
                         user=None, password=None):
    mongo = get_mongo(db=db, host=host, port=port,
                      user=user, password=password)
    return mongo[collection]


def save_raw_response(db, module_name, query, raw_response):
    raw_mongo = db[module_name + '_raw']
    raw_result = query.copy()
    raw_result['response'] = raw_response
    doc = raw_mongo.find_one_and_replace(query, raw_result,
                                         return_document=ReturnDocument.AFTER,
                                         upsert=True)
    return doc['_id']


def save_many_response(mongo, db_fields, payload, response, raw_ref):
    for f in db_fields:
        if f in response:
            query = {'$and': [
                {'key': f},
                {'value': payload[f]},
            ]}

            result = response[f].copy()
            result['key'] = f
            result['value'] = payload[f]
            result['raw_ref'] = raw_ref

            mongo.find_one_and_replace(query, result, upsert=True)

