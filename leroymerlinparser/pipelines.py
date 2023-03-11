# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
from pymongo import errors


class LeroymerlinparserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.leroy

    def process_item(self, item, spider):
        if len(item['chars_key']) == len(item['chars_value']):
            item['characteristics'] = dict(zip(item['chars_key'], item['chars_value']))

        del item['chars_key']
        del item['chars_value']

        collection = self.mongobase[spider.name]
        try:
            collection.insert_one(item)
        except errors.DuplicateKeyError:
            pass
        return item


class LeroyImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        fold = f"{item.get('_id')}/"
        return fold + super().file_path(request, response=response, info=info, item=item)