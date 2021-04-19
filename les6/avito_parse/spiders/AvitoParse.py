import scrapy
from les6.avito_parse.loader import xpath_selectors, AvitoLoader, post_data_query


class AvitoparseSpider(scrapy.Spider):
    name = 'AvitoParse'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/krasnodar/kvartiry/prodam']

    def link_selector(self, response, selector, callback):
        for link in response.xpath(selector):
            yield response.follow(link, callback=callback)

    def sell_check(self, response, selector, callback):
        pass

    def parse(self, response, **kwargs):
        yield from self.link_selector(response, xpath_selectors['to_post'], self.post_parse)
        yield from self.link_selector(response, xpath_selectors['pag'], self.parse)

    def post_parse(self, response, **kwargs):
        loader = AvitoLoader(response=response)
        loader.add_value('url', response.url)
        for key, selector in post_data_query.items():
            loader.add_xpath(key, selector)
        loader.load_item()
