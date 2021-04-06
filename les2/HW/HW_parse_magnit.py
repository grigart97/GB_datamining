import datetime
from time import sleep
import requests
import bs4
import pymongo
from urllib.parse import urljoin


class ParseMagnit:

    def __init__(self, start_url, mongo_client):
        self.start_url = start_url
        self.db = mongo_client["gb_data_mining_les2"]
        self.collection = self.db["magnit_products"]

    def get_response_from(self, url) -> requests.Response:
        response = requests.get(url)
        if response.status_code in (200, 301, 304):
            return response
        sleep(1)

    def get_soup_from(self, url):
        return bs4.BeautifulSoup(self.get_response_from(url).text, 'lxml')

    def run(self):
        soup = self.get_soup_from(self.start_url)
        catalog = soup.find('div', attrs={'class': 'сatalogue__main'})
        for product in catalog.find_all('a', attrs={'class': 'card-sale_catalogue'}):
            product_data = self.parse_product(product)
            self.save_to_mongo(product_data)

    def parse_product(self, data):
        product_data = {}
        for key, funk in self.product_template.items():
            try:
                product_data[key] = funk(data)
            except (AttributeError, ValueError):
                pass
        return product_data

    @property
    def product_template(self):
        return {
            'url': lambda data: urljoin(self.start_url, data.attrs.get('href', '')),
            'image_url': lambda data: urljoin(self.start_url, data.find('img').attrs.get('data-src', '')),
            'old_price': lambda data: float('.'.join(data.find('div',
                                                               attrs={'class': 'label__price_old'}).text.split())),
            'new_price': lambda data: float('.'.join(data.find('div',
                                                               attrs={'class': 'label__price_new'}).text.split())),
            'promo_name': lambda data: data.find('div', attrs={'class': 'card-sale__header'}).text,
            'product_name': lambda data: data.find('div', attrs={'class': 'card-sale__title'}).text,
            'date_from': lambda data: self.get_sale_date
            (data.find('div', attrs={'class': 'card-sale__date'}).text.split())[0],
            'date_to': lambda data: self.get_sale_date
            (data.find('div', attrs={'class': 'card-sale__date'}).text.split())[1]
        }

    def get_sale_date(self, sale_date):
        calendar = {'янв': 1, 'фев': 2, 'мар': 3,
                    'апр': 4, 'май': 5, 'мая': 5, 'июн': 6,
                    'июл': 7, 'авг': 8, 'сен': 9,
                    'окт': 10, 'ноя': 11, 'дек': 12}
        sale_from = datetime.datetime(datetime.datetime.now().year, calendar[sale_date[2][:3]], int(sale_date[1]))
        sale_to = datetime.datetime(datetime.datetime.now().year, calendar[sale_date[-1][:3]], int(sale_date[-2]))
        if sale_from.month == 12 and sale_to.month == 1:
            if datetime.datetime.now().year == sale_to.year:
                sale_from.replace(year=datetime.datetime.now().year - 1)
            else:
                sale_to.replace(year=datetime.datetime.now().year + 1)
        result = [sale_from, sale_to]
        return result

    def save_to_mongo(self, product_data):
        self.collection.insert_one(product_data)


if __name__ == '__main__':
    url = 'https://magnit.ru/promo/?geo=moskva'
    mongo_client = \
        pymongo.MongoClient("mongodb+srv://1:1@cluster0.eze7q.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    parser = ParseMagnit(url, mongo_client)
    parser.run()
