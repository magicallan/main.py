import re
import time
import scrapy
from httpcore import TimeoutException
# 这里报错不用管
from sportnew.items import News
import unicodedata as ucd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from msedge.selenium_tools import EdgeOptions
from msedge.selenium_tools import Edge


class NewsSpider(scrapy.Spider):
    name = 'news'
    allowed_domains = ['sports.sina.com.cn']
    start_urls = ['https://sports.sina.com.cn']
    edge_options = EdgeOptions()
    edge_options.use_chromium = True
    # 设置无界面模式，也可以添加其它设置
    edge_options.add_argument('headless')
    browser = Edge(options=edge_options)
    china_page = 1
    NBA_page = 1

    def parse(self, response, **kwargs):
        link_list = response.xpath("//ul[@class='links']//li/a")
        topic_list = link_list[4:11]
        for topic in topic_list:
            Topic = topic.xpath("./text()").extract_first()
            url = topic.xpath("./@href").extract_first()
            yield scrapy.Request(url=url, callback=self.parse_secound, meta={'Topic': Topic, 'url': url})

    def parse_secound(self, response):
        Topic = response.meta["Topic"]
        if Topic == "国际足球":
            print(f"正在抓取{Topic}新闻")
            page_list = response.xpath("//ul[@class='ul-type1']//li/a")
            for page in page_list:
                title = page.xpath("./text()").extract_first()
                url = page.xpath("./@href").extract_first()
                yield scrapy.Request(url=url, callback=self.parse_third, meta={'title': title, 'url': url,
                                                                               'Topic': Topic})
        elif Topic == "中国篮球":
            print(f"正在抓取{Topic}新闻")
            page_list = response.xpath("//li[@class='item']/p/a")
            for page in page_list:
                title = page.xpath("./text()").extract_first()
                url = page.xpath("./@href").extract_first()
                yield scrapy.Request(url=url, callback=self.parse_third, meta={'title': title, 'url': url,
                                                                               'Topic': Topic})
        if Topic == "综合":
            page_list = response.xpath("//h2[@class='label']/a")
            topic_list = page_list[2:11]
            for topic in topic_list:
                Topic = topic.xpath("./text()").extract_first()
                url = topic.xpath("./@href").extract_first()
                print(f"正在抓取{Topic}新闻")
                yield scrapy.Request(url=url, callback=self.parse_four, meta={'url': url, 'Topic': Topic})

        elif Topic == "中国足球":
            print(f"正在抓取{Topic}新闻")
            original_url = response.meta['url']
            self.browser.get(original_url)
            print(self.browser.current_url)
            while True:
                # 往下滚动
                self.browser.execute_script("window.scrollBy(0, 50000);")
                # 使用WebDriverWait等待页面加载完成
                try:
                    element_present = EC.presence_of_element_located((By.XPATH, "//div[@class='feed-card-item']//h2/a"))
                    WebDriverWait(self.browser, 10).until(element_present)
                except TimeoutException:
                    break
                # 从滚动加载的内容中查找链接
                next_but = self.browser.find_elements_by_xpath("//span[@class='pagebox_next']")
                if next_but:
                    page_list = self.browser.find_elements_by_xpath("//div[@class='feed-card-item']//h2/a")
                    break

            get_browser = Edge(options=self.edge_options)
            for page in page_list:
                title = page.text
                url = page.get_attribute('href')
                get_browser.get(url)
                # 处理抓取到的链接
                content = []
                content_list = get_browser.find_elements(by='xpath', value="//div[@id='artibody']/p")
                if content_list:
                    for p in content_list:
                        if p.text == '':
                            continue
                        else:
                            content.append(p.text)
                    news = News(Topic=Topic, title=title, content=content, url=url)
                    yield news
                    get_browser.back()

        elif Topic == "NBA":
            print(f"正在抓取{Topic}新闻")
            original_url = response.meta['url']
            self.browser.get(original_url)
            while True:
                # 往下滚动
                self.browser.execute_script("window.scrollBy(0, 50000);")
                # 使用WebDriverWait等待页面加载完成
                try:
                    element_present = EC.presence_of_element_located((By.XPATH, "//div[@class='feed-card-item']//h2/a"))
                    WebDriverWait(self.browser, 10).until(element_present)
                except TimeoutException:
                    break
                # 从滚动加载的内容中查找链接
                next_page = self.browser.find_elements_by_xpath("//span[@class='pagebox_next']/a")
                if next_page:
                    page_list = self.browser.find_elements_by_xpath("//div[@class='feed-card-item']//h2/a")
                    break
            for page in page_list:
                title = page.text
                url = page.get_attribute('href')
                # 处理抓取到的链接
                get_browser = Edge(options=self.edge_options)
                get_browser.get(url)
                content = []
                content_list = get_browser.find_elements(by='xpath', value="//div[@id='artibody']/p")
                if content_list:
                    for p in content_list:
                        if p.text == '':
                            continue
                        else:
                            content.append(p.text)
                    get_browser.close()
                    news = News(Topic=Topic, title=title, content=content, url=url)
                    yield news

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
        if content_mlist:
            news = News(Topic=Topic, title=title, content=content_mlist, url=url)
            yield news

    def parse_four(self, response):

        page_list = response.xpath("//ul[@class='list2']/li/a")
        Topic = response.meta['Topic']
        for page in page_list:
            title = page.xpath("./text()").extract_first()
            url = page.xpath("./@href").extract_first()
            yield scrapy.Request(url=url, callback=self.parse_third, meta={'title': title, 'url': url,
                                                                           'Topic': Topic})
