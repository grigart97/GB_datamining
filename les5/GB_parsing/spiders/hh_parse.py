import scrapy
from les5.GB_parsing.Loaders import HHvacancyLoader, HHemployerLoader, HH_selectors, vacancy_data_query, \
    employer_standart_data_query, employer_custom_data_query


class HHParseSpider(scrapy.Spider):
    name = 'hh_parse'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    def link_selector(self, response, selector, callback):
        for link in response.xpath(selector):
            yield response.follow(link, callback=callback)

    def parse(self, response, **kwargs):
        yield from self.link_selector(response, HH_selectors['vacancy'], self.vacancy_parse)
        yield from self.link_selector(response, HH_selectors['pag'], self.parse)
        yield from self.link_selector(response, HH_selectors['employer'], self.employer_parse)

    def vacancy_parse(self, response, **kwargs):
        loader = HHvacancyLoader(response=response)
        loader.add_value('url', response.url)
        for key, selector in vacancy_data_query.items():
            loader.add_xpath(key, selector)
        yield loader.load_item()

    def employer_parse(self, response, **kwargs):
        print(1)
        loader = HHemployerLoader(response=response)
        loader.add_value('url', response.url)
        employer_id = response.xpath('/html/head/link[@rel="canonical"]/@href').extract_first().split('/')[-1]
        if employer_custom_data_query['standart_page_check']:
            loader.add_value('_id', employer_id)
            for key, selector in employer_standart_data_query.items():
                loader.add_xpath(key, selector)
            yield from self.link_selector(response, HH_selectors['employer_vacancies'], self.parse)
        else:
            yield from response.follow(
                f'/vacancy?st=searchVacancy&from=employerPage&employer_id={employer_id}', self.parse
            )
        yield loader.load_item()
