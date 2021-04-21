from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst
from scrapy.selector import Selector

xpath_selectors = {
    'to_post': '//div[@data-marker="catalog-serp"]'
               '//div[contains(@class, "iva-item-titleStep")]/a[@target="_blank"]/@href',
    'pag': '//div[contains(@class,"pagination-hidden")]//a[@class="pagination-page"]/@href'
}
post_data_query = {
    # '_id': '//a[contains(@class,"add-favorite-button")]/@href',
    'title': '//h1[@class="title-info-title"]/span/text()',
    'price': '//div[@id="price-value"]//span[@class="js-item-price"]/@content',
    'parameters': '//ul[@class="item-params-list"]/li[@class="item-params-list-item"]',
    'seller_url': '//div[@class="seller-info-name js-seller-info-name"]//@href',
    'address': '//div[@itemprop="address"]//text()',
}


def params_to_dict(param):
    selector = Selector(text=param)
    return {
        'name': selector.xpath('//li/span/text()').extract_first().replace(': ', ':'),
        'value': selector.xpath('//li/a/text()').extract_first()
                 or
                 ''.join(selector.xpath('//li/text()').extract())[1:-1].replace('\xa0', ' ')
    }


def del_spaces(text: str):
    return text.replace('\n ', '')


# def ge_id(text):
#     return text.split('/')[-1]


def ge_price(text):
    return float(text)


class AvitoLoader(ItemLoader):
    default_item_class = dict
    # _id_in = MapCompose(ge_id)
    # _id_out = TakeFirst()
    url_out = TakeFirst()
    title_out = TakeFirst()
    price_in = MapCompose()
    price_out = TakeFirst()
    parameters_in = MapCompose(params_to_dict)
    seller_url_out = TakeFirst()
    address_in = MapCompose(del_spaces)
    address_out = TakeFirst()
