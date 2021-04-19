from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst, Join, Identity
from urllib.parse import urljoin

HH_selectors = {
    'pag': '//div[@data-qa="pager-block"]//a[@class="bloko-button"]/@href',
    'vacancy': '//div[@data-qa="vacancy-serp__results"]//a[@data-qa="vacancy-serp__vacancy-title"]/@href',
    'employer': '//div[@data-qa="vacancy-serp__results"]//a[@data-qa="vacancy-serp__vacancy-employer"]/@href',
    'employer_vacancies': '//div[@class="employer-sidebar-content"]'
                          '//a[@data-qa="employer-page__employer-vacancies-link"]/@href',

}
vacancy_data_query = {
    'title': '//h1[@class="bloko-header-1"]/text()',
    'salary': '//p[@class="vacancy-salary"]//text()',
    'company_name': '//a[@class="vacancy-company-name"]//text()',
    'company_hh_url': '//a[@class="vacancy-company-name"]/@href',
    'skiils_list': '//div[@class="bloko-tag-list"]/div/div[contains(@data-qa, "skills-element")]//text()'
}
employer_standart_data_query = {
    'name': '//div[@class="company-header"]/div/h1/span[@class="company-header-title-name"]/text()',
    'employer_main_url': '//div[@class="employer-sidebar-content"]//a[@data-qa="sidebar-company-site"]/@href',
    'employer_areas': '//div[@class="employer-sidebar"]//p/text()',
    'description': '//div[@data-qa="company-description-text"]/div/p/text()'
}
employer_custom_data_query = {
    'standart_page_check': '//div[@class="main-content"]/div[@id="HH-React-Root"]',
    'url': '//a[contains(text(), ".ru"]/@href',
    'employer_id': '/html/head/link[@rel="canonical"]/@href'
}


def join_employer_url(employer_url):
    return urljoin('https://hh.ru/', employer_url)


class HHvacancyLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_out = Join('')
    company_name_out = Join()
    company_hh_url_in = MapCompose(join_employer_url)
    company_hh_url_out = TakeFirst()
    skills_list_out = Identity()


class HHemployerLoader(ItemLoader):
    default_item_class = dict
    _id_out = TakeFirst()
    url_out = TakeFirst()
    name_out = Join()
    employer_main_url_out = TakeFirst()
    employer_areas_out = Identity()
    description_out = Join('\n')
