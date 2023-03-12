from pymongo import MongoClient
import pymongo


class InstaparserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.instagram

    def process_item(self, item, spider):
        print()
        collection = self.mongobase[item['user_parser_name']]
        collection.create_index([('user_id', pymongo.TEXT)], name='unique description', unique=True)
        del item['user_parser_name']
        collection.insert_one(item)
        return item