import dotenv
import os
from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess
from les7.instagram_parse.spiders.insta_parse import InstaParseSpider


if __name__ == '__main__':
    dotenv.load_dotenv(r'C:\Users\ga.artemov\Documents\GeekBrains\datamining\les7\instagram_parse\.env')
    cr_set = Settings()
    cr_set.setmodule('instagram_parse.settings')
    cr_proc = CrawlerProcess(settings=cr_set)
    login = os.getenv('USERNAME')
    password = os.getenv('ENC_PASSWORD')
    cr_proc.crawl(InstaParseSpider,
                  login='89959905851',  # Жду предложений о работе :)
                  password=os.getenv('ENC_PASSWORD'),
                  tags=["python", "programming"]
                  )
    cr_proc.start()
