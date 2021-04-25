# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request


class InstagramParsePipeline:

    def __init__(self):
        client = MongoClient('mongodb+srv://1:1@cluster0.eze7q.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
        self.db_mongo = client['datamining_GB']

    def process_item(self, item, spider):
        self.db_mongo[spider.name].insert_one(item)
        return item


class InstagramDownloadPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for url in item.get('photos', []):
            yield Request(url)

    def item_completed(self, results, item, info):
        if 'photos' in item:
            item['photos'] = [itm[1] for itm in results]
        return item
