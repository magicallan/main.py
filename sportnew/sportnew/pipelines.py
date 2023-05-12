# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import os

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json

class SportnewPipeline:

    def __init__(self):
        self.json_file = None

    def open_spider(self, spider):
        self.json_file = codecs.open('news.json', 'w', encoding='UTF-8')
        print("爬虫开始")
        self.json_file.write('[\n')

    def process_item(self, item, spider):
        print("爬虫进行中")
        item_jason = json.dumps(dict(item), ensure_ascii=False)
        self.json_file.write('\t' + item_jason + ',\n')
        return item

    def close_spider(self, spider):
        print("爬虫已完成")
        self.json_file.seek(-2, os.SEEK_END)
        self.json_file.truncate()
        self.json_file.write('\n]')
        self.json_file.close()

