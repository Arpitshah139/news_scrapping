import sys
import time
import demjson
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, BulkWriteError, ServerSelectionTimeoutError, OperationFailure
from Environment import *


class MongoThings:
    if LOCAL_ENV:
        ConnUrl = demjson.decode(config['mongo-url']['Url'])[STAGE]

class DbName:
    DsyhMongo = 'news_scrapping'

class DbOperations(object):
    ClientConn = None
    clientid = None
    channelid = None
    def __init__(self):
        DbOperations.ClientConn = DbOperations.GetConnection(DbName.DsyhMongo)

    @staticmethod
    def GetConnection(dbName, count=0):

        clientConn = DbOperations.ClientConn

        try:

            if (clientConn is None):

                try:
                    clientConn = MongoClient(MongoThings.ConnUrl)
                    clientConn.server_info()
                    clientConn = clientConn[dbName]

                except (ServerSelectionTimeoutError, OperationFailure) as e:
                    print (e)
                    if count < 5:
                        time.sleep(5)
                        DbOperations.GetConnection(DbName, count + 1)
                    else:
                        print("Connection is not established")
                        exit(0)
                except Exception as e:
                    print(e)
        except Exception as e:
            print (str(e))

        return clientConn

    @staticmethod
    def InsertIntoMongo(collection, dataToInert, count=0):

        """
        :param collection: name of the collection
        :param dataToInert: list or dict type.
        :return: False when insertion is failed, on successful for one insertion returns inserted_id in ObjectId, for a list returns True
        """

        clientConn = DbOperations.GetConnection(DbName.DsyhMongo)
        returnvalue = {'nInserted': 0, 'inserted_ids': [], 'nDuplicates': 0, 'anyDuplicates': False,
                       'nTotal': len(dataToInert), 'writeErrors': []}

        try:

            if (type(dataToInert) is list):
                val = clientConn[collection].insert_many(dataToInert, ordered=False)
                returnvalue['nInserted'] = len(val.inserted_ids)
                returnvalue['inserted_ids'] = val.inserted_ids
            elif (type(dataToInert) is dict):
                val = clientConn[collection].insert_one(dataToInert)
                returnvalue['nInserted'] = 1
                returnvalue['inserted_ids'] = [val.inserted_id]
            else:
                print ("In insert Nothing")

        except BulkWriteError as e:
            details = e.details
            code = details['writeErrors'][0]['code']
            if code == 11000:
                duplicatevalues = len(dataToInert) - details['nInserted']
                returnvalue['nInserted'] = details['nInserted']
                returnvalue['nDuplicates'] = duplicatevalues
                returnvalue['anyDuplicates'] = True
                returnvalue['writeErrors'] = details['writeErrors']
            else:
                returnvalue['writeErrors'] = details['writeErrors']

        except DuplicateKeyError as er:
            returnvalue['nInserted'] = 0
            returnvalue['nDuplicates'] = 1
            returnvalue['anyDuplicates'] = True
            returnvalue['writeErrors'] = er.details


        except (ServerSelectionTimeoutError, OperationFailure) as e:
            print (e)
            if count < 5:
                time.sleep(5)
                DbOperations.InsertIntoMongo(collection, dataToInert, count + 1)
            else:
                print ("Error while inserting")
                exit(0)

        return returnvalue

