from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess

from les5.GB_parsing.spiders.hh_parse import HHParseSpider

if __name__ == '__main__':
    cr_settings = Settings()
    cr_settings.setmodule('GB_parsing.settings')
    cr_proc = CrawlerProcess(cr_settings)
    cr_proc.crawl(HHParseSpider)
    cr_proc.start()
