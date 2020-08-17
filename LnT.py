from helper import Helper
from crawler import crawler
from bs4 import BeautifulSoup
from DbOps import DbOperations
import hashlib

class LnT(object):
    def __init__(self,url,body=None,headers=None):
        self.url = url
        self.body = body
        self.headers = headers
    def crawler_news(self):
        response = crawler.MakeRequest(self.url,'Get',postData=self.body,headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        bulk_obj = DbOperations.Get_object_for_bulkop(False,'LnT_news')
        news_data = soup.find('ul', {'class': "newsPressList tabContent"})
        if news_data:
            for news in news_data.find_all('li'):

                news_dict = Helper.get_news_dict()

                title_data = news.find('h3')
                title = title_data.text if title_data else ""

                url_data = news.find('a', {'href': True})
                url = url_data['href'] if url_data else ''

                publish_date_data = news.find('span', {'class': 'date'})
                publish_date = Helper.parse_date(publish_date_data.text) if publish_date_data and publish_date_data.text != '' else ''

                news_dict.update(
                    {"title": title, "news_title_uid": hashlib.md5(title.encode()).hexdigest(),
                     "url": url, "link": url, "news_url_uid": hashlib.md5(url.encode()).hexdigest(),
                     "publishedAt": publish_date, 'date': publish_date, "publishedAt_scrapped": publish_date,
                     "company_id": "LnT", "ticker": "LnT_scrapped", "industry_name": "LnT",
                     "news_provider": "LnT"})

                bulk_obj.insert(news_dict)

                if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) >100:
                    bulk_obj.execute()
                    bulk_obj = DbOperations.Get_object_for_bulkop(False,'LnT_news')

            if len(bulk_obj._BulkOperationBuilder__bulk.__dict__['ops']) > 0:
                bulk_obj.execute()

url = "https://www.larsentoubro.com/corporate/media/news/?year=2020"
news_obj = LnT(url)
news_obj.crawler_news()