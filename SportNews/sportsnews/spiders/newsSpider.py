import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from sportsnews.items import News


class NewsSpider(CrawlSpider):
    name = 'newsSpider'
    allowed_domains = ['sports.sohu.com']
    start_urls = ['http://sports.sohu.com']

    rules = (
        Rule(LinkExtractor(restrict_xpaths=r""),
             callback='parse_item',
             follow=False),
    )

    def parse_item(self, response):
        news = News()
        topic_list = response.xpath("//div[@class='banner-block']/div[@id]//a")
        for topic in topic_list:
            news.Topic = topic.xpath('./text()').extract_first()
            herf = topic.xpath('./@herf').extract_first()

            url = herf
            print(herf)

        yield news
