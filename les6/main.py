from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess

if __name__ == '__main__':
    cr_settings = Settings()
    cr_settings.setmodule('avito_parse.settings')
    cr_proc = CrawlerProcess(settings=cr_settings)
    # cr_proc.crawl(AvitoparseSpider)
    cr_proc.start()
