import scrapy
from les4.HW.HW_youla_parse.loaders import AutoyoulaLoader


class YoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']
    selectors = {
        'brands': 'div.ColumnItemList_container__5gTrc a.blackLink',
        'pagination': 'div.Paginator_block__2XAPy '
                      'a.Paginator_button__u1e7D.ButtonLink_button__1wyWM.Button_button__3NYks',
        'cars': '#serp article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu'
    }

    data_query = {
        'title': 'div.AdvertCard_advertTitle__1S1Ak::text',
        'price': 'div.AdvertCard_price__3dDCr::text',
        'img_urls': 'script::text',
        'author_id': 'script::text',
        'characteristics': 'div.AdvertSpecs_row__ljPcX',
        'description': 'div.AdvertCard_descriptionInner__KnuRi::text'
    }

    def link_selector(self, response, selector_css, callback, **kwargs):
        for link_selector in response.css(selector_css):
            yield response.follow(link_selector.attrib.get('href'), callback=callback)

    def parse(self, response, **kwargs):
        yield from self.link_selector(response, self.selectors['brands'], callback=self.brand_parse)

    def brand_parse(self, response, **kwargs):
        yield from self.link_selector(response, self.selectors['pagination'], callback=self.brand_parse)
        yield from self.link_selector(response, self.selectors['cars'], callback=self.car_parse)

    def car_parse(self, response, **kwargs):
        loader = AutoyoulaLoader(response=response)
        loader.add_value('url', response.url)
        for key, query in self.data_query.items():
            loader.add_css(key, query)
        yield loader.load_item()
