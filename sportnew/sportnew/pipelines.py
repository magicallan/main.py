# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class SportnewPipeline:
    def open_spider(self, spider):
        print("爬虫开始")
        self.fp = open('news.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        print("爬虫进行中")
        self.fp.write(str(item))
        return item

    def close_spider(self, spider):
        print("爬虫已完成")
        self.fp.close()

