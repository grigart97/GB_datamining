import re
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from urllib.parse import unquote


def price_to_num(price):
    try:
        result = float(price.replace('\u2009', ''))
    except ValueError:
        result = None
    return result


def get_author_id(text):
    re_pattern_dealer = re.compile(r'youlaId%22%2C%(\w+)%22%2C%22badges')
    re_pattern_user = re.compile(r'youlaId%22%2C%(\w+)%22%2C%22avatar')
    return re_pattern_user.findall(text) or re_pattern_dealer.findall(text)


def get_img_urls(item: str):
    text = unquote(item)
    re_pattern = re.compile(r'https://static.am/automobile_m3/document/s/\w/\w\w/\w+.jpg')
    result = re_pattern.findall(text)
    print(1)
    if not result:
        return None
    else:
        return result


def get_characteristics(text):
    selector = Selector(text=text)
    return {
        'name': selector.css('div.AdvertSpecs_label__2JHnS::text').extract_first(),
        'value': selector.css('div.AdvertSpecs_data__xK2Qx::text').extract_first()
                 or selector.css('div.AdvertSpecs_data__xK2Qx::text').extract_first()
    }


class AutoyoulaLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    price_in = MapCompose(price_to_num)
    price_out = TakeFirst()
    author_id_in = MapCompose(get_author_id)
    author_id_out = TakeFirst()
    img_urls_out = MapCompose(get_img_urls)
    description_out = TakeFirst()
    characteristics_out = MapCompose(get_characteristics)
