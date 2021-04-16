import scrapy


class HHParseSpider(scrapy.Spider):
    name = 'hh_parse'
    allowed_domains = ['hh.ru/']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    def link_selector(self, response, selector, callback):
        for link in response.xpath(selector):
            yield response.follow(link, callback=callback)

    def parse(self, response, **kwargs):
        pass
