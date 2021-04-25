import json
import scrapy
from urllib.parse import urlencode
from les7.instagram_parse.items import InstagramParseItem
import datetime as dt


class InstaParseSpider(scrapy.Spider):
    name = 'insta_parse'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    url_login = '/accounts/login/ajax/'
    url_tags = '/explore/tags/'
    graphql_query = '/graphql/query/'
    query_hash = '9b498c08113f1e09617a1703c22b2f32'

    def __init__(self, login, password, tags, *args, **kwargs):
        self.login = login
        self.password = password
        self.tags = tags
        super().__init__(*args, **kwargs)

    def parse(self, response, **kwargs):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                response.urljoin(self.url_login),
                method='POST',
                callback=self.parse,
                formdata={'username': self.login,
                          'enc_password': self.password,
                          'queryParams': {}
                          },
                headers={'X-CSRFToken': js_data['config']['csrf_token']}
            )
        except AttributeError:
            if response.json()['authenticated']:
                for tag in self.tags:
                    yield response.follow(f'{self.url_tags}{tag}/', callback=self.tag_page_parse)

    def tag_page_parse(self, response, **kwargs):
        data_posts_js = self.js_data_extract(response)
        h_tag = HashTag(data_posts_js['entry_data']['TagPage'][0]['graphql']['hashtag'])
        yield h_tag.get_tag_item()
        yield from h_tag.get_posts_items()
        if h_tag.has_next_page:
            yield response.follow(f'{self.graphql_query}?{urlencode(h_tag.get_paginate_dict())}',
                                  callback=self.graph_ql_page_parse)

    def graph_ql_page_parse(self, response, **kwargs):
        data_posts_js = response.json()
        h_tag = HashTag(data_posts_js['data']['hashtag'])
        yield from h_tag.get_posts_items()
        if h_tag.has_next_page:
            yield response.follow(f'{self.graphql_query}?{urlencode(h_tag.get_paginate_dict())}',
                                  callback=self.graph_ql_page_parse)

    def js_data_extract(self, response):
        script = response.xpath(
            "//body/script[contains(text(), 'window._sharedData =')]/text()"
        ).extract_first()
        return json.loads(script.replace("window._sharedData = ", "")[:-1])


class HashTag:

    def __init__(self, hashtag: dict):
        self.h_tag = hashtag
        self.has_next_page = hashtag['edge_hashtag_to_media']['page_info']['has_next_page']

    def get_tag_item(self):
        result_tag_data = {}
        for key, value in self.h_tag.items():
            if not isinstance(value, dict):
                result_tag_data[key] = value
        tag_photo = result_tag_data.pop('profile_pic_url')
        return InstagramParseItem(date_parse=dt.datetime.now(), data=result_tag_data, photos=[tag_photo])

    def get_paginate_dict(self):
        return {'query_hash': InstaParseSpider.query_hash,
                'variables': json.dumps({'tag_name': self.h_tag['name'],
                                         'first': 100,
                                         'after': self.h_tag['edge_hashtag_to_media']['page_info']['end_cursor']
                                         })
                }

    def get_posts_items(self):
        for edge in self.h_tag['edge_hashtag_to_media']['edges']:
            edge_photos = edge['node'].pop('thumbnail_resources')
            for idx, img in enumerate(edge_photos):
                edge_photos[idx] = img['src']
            yield InstagramParseItem(date_parse=dt.datetime.now(), data=edge['node'], photos=edge_photos)
