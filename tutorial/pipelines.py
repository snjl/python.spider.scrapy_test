# -*- coding: utf-8 -*-
import pymongo
import json
from scrapy.exceptions import DropItem


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class TutorialPipeline(object):
    def __init__(self):
        self.limit = 50

    def process_item(self, item, spider):
        if item['text']:
            if len(item['text']) > self.limit:
                item['text'] = item['text'][0:self.limit].rstrip() + '...'
            return item
        else:
            print('text is null')
            return DropItem("Missing Text")


# MongoDB存储数据管道
class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    # 从settings中拿到配置
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    # 爬虫启动时需要进行的操作，初始化MongoDB对象
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        spider.logger.info("mongodb start!")

    # 最重要的process_item
    def process_item(self, item, spider):
        # 使用这样的name比较灵活
        name = item.__class__.__name__
        self.db[name].insert(dict(item))
        return item

    # 管道完毕时自动运行
    def close_spider(self, spider):
        self.client.close()
        spider.logger.info("mongodb close!")


class JsonWriterPipeline(object):
    def __init__(self):
        self.file = open('items.jl', 'a+')
        print("file open!")

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()
        spider.logger.info("file close!")
