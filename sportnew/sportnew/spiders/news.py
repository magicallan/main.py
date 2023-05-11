import time

import scrapy
from sportnew.items import News
import unicodedata as ucd
from selenium import webdriver
from selenium.webdriver.edge.service import Service


class NewsSpider(scrapy.Spider):
    name = 'news'
    allowed_domains = ['sports.sina.com.cn']
    start_urls = ['https://sports.sina.com.cn']
    ser = Service("..\\MicrosoftWebDriver.exe")
    path = "MicrosoftWebDriver.exe"
    browser = webdriver.Edge(service=ser)

    def parse(self, response, **kwargs):
        link_list = response.xpath("//ul[@class='links']//li/a")
        topic_list = link_list[4:11]
        for topic in topic_list:
            Topic = topic.xpath("./text()").extract_first()
            print(Topic)
            url = topic.xpath("./@href").extract_first()
            print(url)
            yield scrapy.Request(url=url, callback=self.parse_secound, meta={'Topic': Topic, 'url': url})

    def parse_secound(self, response):
        Topic = response.meta["Topic"]
        if Topic == "国际足球":
            page_list = response.xpath("//ul[@class='ul-type1']//li/a")
            for page in page_list:
                title = page.xpath("./text()").extract_first()
                url = page.xpath("./@href").extract_first()
                yield scrapy.Request(url=url, callback=self.parse_third, meta={'title': title, 'url': url,
                                                                               'Topic': Topic})
        elif Topic == "中国足球":
            surl = response.meta['url']
            self.browser.get(surl)
            # js_bottom = 'document.documentElement.scrollTop=100000'
            # self.browser.execute_script(js_bottom)
            # time.sleep(2)
            pageList = self.browser.find_elements(by='xpath', value="//div[@class='feed-card-item']//h2/a")
            self.browser.close()
            for page in pageList:
                title = page.text
                print(title)
                url = page.get_attribute('href')
                print(url)
                self.browser.get(url)
                content = self.browser.find_elements(by='xpath', value="//div[@id='artibody']/p//text()")
                self.browser.close()
                news = News(Topic=Topic, title=title, content=content, url=url)
                yield news


        elif Topic == "中国篮球":
            page_list = response.xpath("//li[@class='item']/p/a")
            for page in page_list:
                title = page.xpath("./text()").extract_first()
                url = page.xpath("./@href").extract_first()
                yield scrapy.Request(url=url, callback=self.parse_third, meta={'title': title, 'url': url,
                                                                               'Topic': Topic})

    def parse_third(self, response):

        content_mlist = []
        content_list = response.xpath("//div[@id='artibody']/p//text()").extract()
        for content in content_list:
            m_content = ucd.normalize('NFKC', content).replace(' ', '')
            if m_content == '':
                continue
            else:
                content_mlist.append(m_content)
        title = response.meta['title']
        url = response.meta['url']
        Topic = response.meta['Topic']
        news = News(Topic=Topic, title=title, content=content_mlist, url=url)
        yield news

    # def gertanotherway(self, url):
    #
    #     self.browser.get(url)
    #     pageList = self.browser.find_elements(by='xpath', value="//div[@class='feed-card-item']/h2/a")
    #     for page in pageList:
    #         print(page.get_attribute('href'))
