import scrapy
from les6.HW.avito.loaders import xpath_selectors, AvitoLoader, post_data_query


class AvitoparseSpider(scrapy.Spider):
    name = 'AvitoParse'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/krasnodar/kvartiry']

    def link_selector(self, response, selector, callback):
        for link in response.xpath(selector):
            yield response.follow(link, callback=callback)

    def parse(self, response, **kwargs):
        return response.follow('/krasnodar/kvartiry/prodam', callback=self.prodam_parse)

    def prodam_parse(self, response, **kwargs):
        yield from self.link_selector(response, xpath_selectors['to_post'], self.post_parse)
        yield from self.link_selector(response, xpath_selectors['pag'], self.parse)

    def post_parse(self, response, **kwargs):
        loader = AvitoLoader(response=response)
        loader.add_value('url', response.url)
        for key, selector in post_data_query.items():
            loader.add_xpath(key, selector)
        yield loader.load_item()
