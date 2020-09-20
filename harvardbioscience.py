from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import re
import hashlib
import logging


class harvardbioscience(object):
    def __init__(self, url, body=None, headers=None, logger=None):
        """
        Set initial paramaeters

        :param url: scraping url
        :param body: scraping url body
        :param headers: scraping url header
        :param logger: logger object
        """
        self.url = url
        self.body = body
        self.headers = headers
        self.logger = logger

    def crawler_news(self):

        """
        This function will scrap news page wise for given url
        :return:
        """

        try:
            loop = True
            page = 0
            while loop:
                response = crawler.MakeRequest(self.url.format(page=page), 'Get', postData=self.body,
                                               headers=self.headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                bulk_obj = DbOperations.Get_object_for_bulkop(False, 'harvardbioscience_news')
                news_data = soup.find('tbody')
                if news_data:
                    for news in news_data.find_all('tr'):
                        try:
                            news_dict = Helper.get_news_dict()

                            title_data = news.find('td',{'class':'views-field views-field-field-nir-news-title'}).find('a', {'href': True})
                            title = title_data.text.strip() if title_data else ""

                            url_data = news.find('td',{'class':'views-field views-field-field-nir-news-title'}).find('a', {'href': True})
                            url = "https://investor.harvardbioscience.com" + str(url_data['href']) if url_data else ''

                            publish_date_data = news.find('time', {'class': 'datetime'})
                            publish_date = Helper.parse_date(publish_date_data.text) if publish_date_data else ''

                            url_response = crawler.MakeRequest(url, 'Get', postData=self.body, headers=self.headers)
                            url_soup = BeautifulSoup(url_response.content, 'html.parser')
                            description_data = url_soup.find('div',{'class':'node__content'})

                            description = []
                            regex = re.compile(r'[\n\xa0]')
                            for desc in description_data.find_all('p'):
                                description.append(regex.sub("", str(desc.text)))
                            description = ''.join(description)

                            news_dict.update(
                                {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                                 "url": url, "link": url, "news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                                 "description": description, "text": description,
                                 "publishedAt": publish_date, 'date': publish_date,
                                 "publishedAt_scrapped": publish_date,
                                 "company_id": "harvardbioscience", "ticker": "harvardbioscience_scrapped", "industry_name": "harvardbioscience",
                                 "news_provider": "harvardbioscience"})

                            bulk_obj.insert(news_dict)

                            if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 100:
                                bulk_obj.execute()
                                bulk_obj = DbOperations.Get_object_for_bulkop(False, 'harvardbioscience_news')

                        except Exception as e:
                            self.logger.error(f"Error Occured : \n", exc_info=True)

                    if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                        bulk_obj.execute()

                    page += 1
                else:
                    print("News Not Found")
                    loop = False
        except Exception as e:
            self.logger.error(f"Error Occured : \n", exc_info=True)


# Create and configure logger
logging.basicConfig(filename="harvardbioscience_scraping_logs.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger = logging.getLogger()
url = "https://investor.harvardbioscience.com/press-releases?field_nir_news_date_value%5Bmin%5D=2020&field_nir_news_date_value%5Bmax%5D=2020&items_per_page=10&page={page}"
news_obj = harvardbioscience(url, logger=logger)
news_obj.crawler_news()