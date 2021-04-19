# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo


class AvitoParsePipeline:

    def __init__(self):
        client = pymongo.MongoClient(
            "mongodb+srv://1:1@cluster0.eze7q.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
        )
        self.db_mongo = client['Avito_kvartiry_krasnodar']

    def process_item(self, item, spider):
        self.db_mongo[spider.name].insert_one(item)
        return item
